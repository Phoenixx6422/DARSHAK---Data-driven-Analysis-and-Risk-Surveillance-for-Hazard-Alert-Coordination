from datetime import datetime, timezone
import pandas as pd
from .config import DEFAULT_MODEL_ARTIFACT, FEATURE_COLUMNS, FORECAST_HORIZON_HOURS, HAZARD_TYPE, RISK_THRESHOLDS, PEAK_SEASON_MONTHS
from .data_loader import load_active_storms
from .preprocess import validate_location, parse_observation_time, is_within_nio_domain
from .geo import approximate_distance_to_coast_km, classify_sub_basin
from .features import build_feature_row, classify_imd_intensity
from .model import load_model_artifact

def map_score_to_risk_level(score):
    score = max(0.0, min(100.0, float(score)))
    for lvl, (low, high) in RISK_THRESHOLDS.items():
        if lvl == "Critical":
            if low <= score <= high: return lvl
        else:
            if low <= score < high: return lvl
    return "Critical"

def assess_risk(location, observation_time=None, *, active_storms_source=None, model_artifact_path=DEFAULT_MODEL_ARTIFACT):
    loc = validate_location(location)
    valid_dt = parse_observation_time(observation_time)
    assessed_dt = datetime.now(timezone.utc)
    
    artifact = load_model_artifact(model_artifact_path)
    estimator = artifact["model"]
    f_cols = artifact.get("feature_columns", FEATURE_COLUMNS)
    
    storms, src = load_active_storms(active_storms_source)
    in_domain = is_within_nio_domain(loc["lat"], loc["lon"])
    coast_km = approximate_distance_to_coast_km(loc["lat"], loc["lon"])
    sub_basin, _ = classify_sub_basin(loc["lat"], loc["lon"])
    
    if not storms or not in_domain:
        is_peak = valid_dt.month in PEAK_SEASON_MONTHS
        b_score = 5.0 if (in_domain and is_peak and coast_km <= 300) else 1.5
        return {
            "hazard_type": HAZARD_TYPE, "location": loc,
            "assessed_at": assessed_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valid_for": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "forecast_horizon_hours": FORECAST_HORIZON_HOURS,
            "risk_score": round(b_score, 2), "risk_level": map_score_to_risk_level(b_score),
            "confidence": 0.60 if in_domain else 0.30,
            "key_indicators": {"active_storms_count": 0, "distance_to_coast_km": round(coast_km, 1), "sub_basin": sub_basin},
            "model_info": {"model_name": artifact["model_name"], "model_version": artifact["model_version"], "trained_on": artifact["trained_on"]},
            "data_source": src, "limitations": ["No active cyclone present; baseline seasonal assessment."]
        }
        
    best = None
    for s in storms:
        f_row = build_feature_row(s, loc["lat"], loc["lon"], valid_dt.month)
        prob = float(estimator.predict_proba(pd.DataFrame([f_row])[f_cols])[0, 1])
        cat, fac = classify_imd_intensity(s["max_wind_kt"])
        score = max(0.0, min(100.0, 100.0 * prob * fac))
        if best is None or score > best["score"]:
            best = {"storm": s, "feat": f_row, "prob": prob, "cat": cat, "score": score}
            
    s, f, score = best["storm"], best["feat"], best["score"]
    lvl = map_score_to_risk_level(score)
    return {
        "hazard_type": HAZARD_TYPE, "location": loc,
        "assessed_at": assessed_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_for": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "forecast_horizon_hours": FORECAST_HORIZON_HOURS,
        "risk_score": round(score, 2), "risk_level": lvl,
        "confidence": 0.82 if f["distance_km"] <= 700 else 0.68,
        "key_indicators": {
            "active_storms_count": len(storms), "dominant_storm_id": s["storm_id"],
            "dominant_storm_name": s["name"], "nearest_storm_distance_km": round(f["distance_km"], 1),
            "max_wind_kt": s["max_wind_kt"], "probability_50kt_48h": round(best["prob"], 4),
            "distance_to_coast_km": round(f["dist_to_coast_km"], 1), "sub_basin": sub_basin
        },
        "model_info": {"model_name": artifact["model_name"], "model_version": artifact["model_version"], "trained_on": artifact["trained_on"]},
        "data_source": src, "limitations": ["Evaluates 48h wind impact probability for existing active NIO storms."]
    }
