from datetime import datetime, timezone
import pandas as pd
from .config import DEFAULT_MODEL_ARTIFACT, FEATURE_COLUMNS, FORECAST_HORIZON_HOURS, HAZARD_TYPE, RISK_THRESHOLDS
from .data_loader import load_active_gauges
from .preprocess import validate_location, parse_observation_time, is_within_india_domain
from .features import build_feature_row
from .model import load_model_artifact
from hazard_cyclone.geo import haversine_km


def map_score_to_risk_level(score):
    score = max(0.0, min(100.0, float(score)))
    for lvl, (low, high) in RISK_THRESHOLDS.items():
        if lvl == "Critical":
            if low <= score <= high:
                return lvl
        else:
            if low <= score < high:
                return lvl
    return "Critical"


def assess_risk(location, observation_time=None, *, active_gauges_source=None, model_artifact_path=DEFAULT_MODEL_ARTIFACT):
    loc = validate_location(location)
    valid_dt = parse_observation_time(observation_time)
    assessed_dt = datetime.now(timezone.utc)

    artifact = load_model_artifact(model_artifact_path)
    estimator = artifact["model"]
    f_cols = artifact.get("feature_columns", FEATURE_COLUMNS)

    gauges, src = load_active_gauges(active_gauges_source)
    in_domain = is_within_india_domain(loc["lat"], loc["lon"])

    if not gauges or not in_domain:
        b_score = 4.0 if in_domain else 1.0
        return {
            "hazard_type": HAZARD_TYPE,
            "location": loc,
            "assessed_at": assessed_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valid_for": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "forecast_horizon_hours": FORECAST_HORIZON_HOURS,
            "risk_score": round(b_score, 2),
            "risk_level": map_score_to_risk_level(b_score),
            "confidence": 0.55 if in_domain else 0.25,
            "key_indicators": {"active_gauges_count": 0, "basin_status": "Normal Flow"},
            "model_info": {
                "model_name": artifact["model_name"],
                "model_version": artifact["model_version"],
                "trained_on": artifact["trained_on"],
            },
            "data_source": src,
            "limitations": ["No active river gauge observations found; returning baseline seasonal flow assessment."],
        }

    best = None
    for g in gauges:
        f_row = build_feature_row(g)
        prob = float(estimator.predict_proba(pd.DataFrame([f_row])[f_cols])[0, 1])
        wl_ratio = g["water_level_m"] / max(0.1, g["danger_level_m"])
        score = max(0.0, min(100.0, 100.0 * (0.70 * prob + 0.30 * min(1.3, wl_ratio / 1.1))))
        dist = haversine_km(loc["lat"], loc["lon"], g["lat"], g["lon"])

        if best is None or score > best["score"]:
            best = {"gauge": g, "feat": f_row, "prob": prob, "score": score, "dist": dist}

    g, score = best["gauge"], best["score"]
    lvl = map_score_to_risk_level(score)
    return {
        "hazard_type": HAZARD_TYPE,
        "location": loc,
        "assessed_at": assessed_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_for": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "forecast_horizon_hours": FORECAST_HORIZON_HOURS,
        "risk_score": round(score, 2),
        "risk_level": lvl,
        "confidence": 0.85 if best["dist"] <= 100 else 0.65,
        "key_indicators": {
            "active_gauges_count": len(gauges),
            "nearest_station_id": g["station_id"],
            "station_name": g["name"],
            "station_distance_km": round(best["dist"], 1),
            "water_level_m": g["water_level_m"],
            "danger_level_m": g["danger_level_m"],
            "rainfall_24h_mm": g["rainfall_24h_mm"],
            "river_discharge_cumecs": g["river_discharge_cumecs"],
            "probability_flood_24h": round(best["prob"], 4),
        },
        "model_info": {
            "model_name": artifact["model_name"],
            "model_version": artifact["model_version"],
            "trained_on": artifact["trained_on"],
        },
        "data_source": src,
        "limitations": ["Evaluates 24h river basin flood risk from gauge water level, rainfall, discharge, and terrain features."],
    }
