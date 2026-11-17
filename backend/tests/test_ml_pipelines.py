"""
Unit Tests for Layer 3 AI/ML Hazard Pipelines
Integration: Mune Harshvardhan Jagdish (ML/Hazard Research) & Tushar Kanaujiya (Testing)
"""
import sys
import os
import pytest

# Add ml_engine to path
ml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml_engine"))
if ml_path not in sys.path:
    sys.path.insert(0, ml_path)

from hazard_cyclone.assess import assess_risk as assess_cyclone_risk
from hazard_flood.assess import assess_risk as assess_flood_risk
from risk_engine.aggregator import assess_location_risk, get_system_status

def test_cyclone_hazard_pipeline():
    """Verify that the North Indian Ocean Cyclone ML pipeline runs and returns valid risk telemetry."""
    loc = {"lat": 16.216, "lon": 77.356, "name": "Coastal Raichur Sector 4"}
    res = assess_cyclone_risk(loc)
    assert "risk_score" in res
    assert "risk_level" in res
    assert 0.0 <= res["risk_score"] <= 100.0
    assert res["risk_level"] in ["Low", "Moderate", "High", "Critical"]
    assert "confidence" in res

def test_flood_hazard_pipeline():
    """Verify that the CWC Basin Flood ML pipeline runs and returns valid risk telemetry."""
    loc = {"lat": 16.300, "lon": 77.400, "name": "Krishna River Basin Zone B"}
    res = assess_flood_risk(loc)
    assert "risk_score" in res
    assert "risk_level" in res
    assert 0.0 <= res["risk_score"] <= 100.0
    assert res["risk_level"] in ["Low", "Moderate", "High", "Critical"]

def test_multi_hazard_aggregator():
    """Verify multi-hazard aggregator computes SafetyScore = 100 - combined_risk without authority intervention."""
    loc = {"latitude": 16.216, "longitude": 77.356, "region_name": "Coastal Raichur Sector 4"}
    res = assess_location_risk(loc)
    assert "safety_score" in res
    assert "combined_risk_score" in res
    assert "risk_level" in res
    assert "trigger_automated_alert" in res
    assert res["system_governance"]["authority_approval_required"] is False
    assert res["system_governance"]["workflow_type"] == "fully_automated"

def test_ml_system_status():
    """Verify operational status and governance of active pipelines."""
    status = get_system_status()
    assert status["status"] == "operational"
    assert "hazard_cyclone" in status["active_pipelines"]
    assert "hazard_flood" in status["active_pipelines"]
