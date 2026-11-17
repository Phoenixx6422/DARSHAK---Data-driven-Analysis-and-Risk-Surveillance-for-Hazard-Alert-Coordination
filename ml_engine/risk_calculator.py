"""
Risk Assessment Engine - Baseline Algorithm
Owner: Mune Harshvardhan Jagdish (Hazard/Domain & Data Research)
Used by: Vaibhav Rawat (Backend) & Himanshu Shukla (Notification Trigger)
"""
from typing import Dict, Any

def calculate_safetyscore_and_risk(
    rainfall_mmh: float = 0.0,
    wind_speed_kmh: float = 0.0,
    temperature_c: float = 30.0,
    river_water_level_m: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates numerical SafetyScore (0 to 100) and classifies risk.
    Higher hazard values reduce SafetyScore.
    SafetyScore <= 30.0: Critical
    SafetyScore 30.1 - 60.0: High
    SafetyScore 60.1 - 80.0: Moderate
    SafetyScore 80.1 - 100.0: Low
    """
    penalty = 0.0
    
    # Wind speed penalties (Cyclone)
    if wind_speed_kmh >= 100:
        penalty += 55.0
    elif wind_speed_kmh >= 70:
        penalty += 35.0
    elif wind_speed_kmh >= 45:
        penalty += 15.0

    # Rainfall penalties (Flood)
    if rainfall_mmh >= 60:
        penalty += 50.0
    elif rainfall_mmh >= 35:
        penalty += 30.0
    elif rainfall_mmh >= 20:
        penalty += 15.0

    # River water level penalties
    if river_water_level_m >= 8.0:
        penalty += 30.0
    elif river_water_level_m >= 6.0:
        penalty += 15.0

    # Safety score calculation bounded between 0 and 100
    safety_score = max(5.0, min(100.0, round(100.0 - penalty, 2)))

    if safety_score <= 30.0:
        classification = "Critical"
        advisory = "CRITICAL HAZARD DETECTED: Life-threatening weather conditions. Evacuate designated danger zones immediately."
        automated_warning = True
    elif safety_score <= 60.0:
        classification = "High"
        advisory = "HIGH RISK: Severe meteorological indicators active. Automated emergency notifications triggered."
        automated_warning = True
    elif safety_score <= 80.0:
        classification = "Moderate"
        advisory = "MODERATE ADVISORY: Heightened environmental activity. Stay informed through official weather channels."
        automated_warning = False
    else:
        classification = "Low"
        advisory = "LOW RISK: Environmental indicators within normal thresholds."
        automated_warning = False

    return {
        "safety_score": safety_score,
        "risk_classification": classification,
        "advisory": advisory,
        "automated_warning_triggered": automated_warning
    }

if __name__ == "__main__":
    # Self-test baseline
    res = calculate_safetyscore_and_risk(rainfall_mmh=45, wind_speed_kmh=110)
    print("Test Calculation:", res)
