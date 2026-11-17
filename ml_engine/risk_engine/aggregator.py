"""Central SafetyScore aggregator and automated alert decision engine."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from hazard_cyclone import assess_risk as assess_cyclone_risk
from hazard_flood import assess_risk as assess_flood_risk


def _map_combined_risk_to_level(risk_score: float) -> str:
    score = max(0.0, min(100.0, float(risk_score)))
    if score < 25.0:
        return "Low"
    elif score < 50.0:
        return "Moderate"
    elif score < 75.0:
        return "High"
    else:
        return "Critical"


def assess_location_risk(
    location: dict,
    observation_time: str | None = None,
    *,
    active_storms_source: Optional[Dict[str, Any] | Path | str] = None,
    active_gauges_source: Optional[Dict[str, Any] | Path | str] = None,
    cyclone_model_path: Optional[Path | str] = None,
    flood_model_path: Optional[Path | str] = None,
) -> dict:
    """
    Assess multi-hazard risk for a geographic location by combining Cyclone and Flood pipelines.
    Computes SafetyScore = 100 - combined_risk, and triggers automated alerts if risk >= 50 (High/Critical).
    Zero Disaster Management Authority approval or human intervention is involved.
    """
    # Normalize coordinate keys if needed
    loc = dict(location)
    if "latitude" in loc and "lat" not in loc:
        loc["lat"] = loc["latitude"]
    if "longitude" in loc and "lon" not in loc:
        loc["lon"] = loc["longitude"]

    # 1. Run individual hazard assessments
    cyclone_kwargs = {"active_storms_source": active_storms_source}
    if cyclone_model_path:
        cyclone_kwargs["model_artifact_path"] = cyclone_model_path

    flood_kwargs = {"active_gauges_source": active_gauges_source}
    if flood_model_path:
        flood_kwargs["model_artifact_path"] = flood_model_path

    try:
        cyclone_res = assess_cyclone_risk(loc, observation_time, **cyclone_kwargs)
    except Exception as e:
        cyclone_res = {
            "risk_score": 0.0,
            "risk_level": "Low",
            "confidence": 0.5,
            "key_indicators": {},
            "data_source": "unavailable",
            "limitations": [f"Cyclone model assessment failed or unavailable: {e}"],
        }

    try:
        flood_res = assess_flood_risk(loc, observation_time, **flood_kwargs)
    except Exception:
        flood_res = {
            "risk_score": 0.0,
            "risk_level": "Low",
            "confidence": 0.5,
            "key_indicators": {},
            "data_source": "unavailable",
            "limitations": ["Flood model assessment failed or unavailable."],
        }

    c_score = float(cyclone_res.get("risk_score", 0.0))
    f_score = float(flood_res.get("risk_score", 0.0))

    # 2. Combined risk strategy: Dominant hazard weight + secondary boost (worst-case oriented)
    dominant_score = max(c_score, f_score)
    secondary_score = min(c_score, f_score)
    combined_risk = min(100.0, dominant_score * 0.75 + secondary_score * 0.25)

    # 3. Compute SafetyScore (Project invariant: SafetyScore = 100 - combined_risk)
    safety_score = max(0.0, min(100.0, 100.0 - combined_risk))
    risk_level = _map_combined_risk_to_level(combined_risk)

    # 4. Automated alert rule: Triggered when risk >= 50 (High or Critical) with NO authority approval
    trigger_automated_alert = combined_risk >= 50.0
    alert_severity = risk_level if trigger_automated_alert else "None"

    # Determine dominant hazard type
    dominant_hazard = "cyclone" if c_score >= f_score else "flood"

    assessed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "location": cyclone_res.get("location", location),
        "assessed_at": assessed_at,
        "valid_for": cyclone_res.get("valid_for", assessed_at),
        "safety_score": round(safety_score, 2),
        "combined_risk_score": round(combined_risk, 2),
        "risk_level": risk_level,
        "dominant_hazard": dominant_hazard,
        "trigger_automated_alert": trigger_automated_alert,
        "alert_severity": alert_severity,
        "hazard_assessments": {
            "cyclone": cyclone_res,
            "flood": flood_res,
        },
        "system_governance": {
            "authority_approval_required": False,
            "workflow_type": "fully_automated",
        },
    }


def get_system_status() -> dict:
    return {
        "status": "operational",
        "active_pipelines": ["hazard_cyclone", "hazard_flood"],
        "governance": "Fully automated warning generation (No authority intervention required)",
    }
