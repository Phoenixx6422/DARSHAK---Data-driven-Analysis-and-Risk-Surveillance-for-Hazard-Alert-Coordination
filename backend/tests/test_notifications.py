import pytest
from app.notifications.notification_service import NotificationService

def test_notification_dispatch_on_critical_risk():
    """Verify that Critical risk triggers emergency dispatch with authority intervention bypassed."""
    service = NotificationService()
    result = service.evaluate_and_dispatch(
        region_name="Coastal Raichur Sector 4",
        risk_level="Critical",
        safety_score=24.5,
        advisory="Immediate evacuation recommended."
    )
    assert result["emergency_triggered"] is True
    assert result["dispatches_count"] > 0
    assert result["authority_intervention"] is False
    assert any(d["channel"] == "SMS" for d in result["dispatches"])
    assert any(d["channel"] == "EMAIL" for d in result["dispatches"])

def test_notification_dispatch_on_high_risk():
    """Verify that High risk triggers emergency dispatch."""
    service = NotificationService()
    result = service.evaluate_and_dispatch(
        region_name="Krishna River Basin Zone B",
        risk_level="High",
        safety_score=45.0,
        advisory="Water levels rising above danger mark."
    )
    assert result["emergency_triggered"] is True
    assert result["dispatches_count"] > 0

def test_notification_suppression_on_moderate_and_low_risk():
    """Verify that Moderate/Low risk logs advisory only and does NOT trigger emergency dispatches."""
    service = NotificationService()
    result_mod = service.evaluate_and_dispatch(
        region_name="Raichur Urban Zone 1",
        risk_level="Moderate",
        safety_score=72.0,
        advisory="Stay hydrated during peak heat."
    )
    assert result_mod["emergency_triggered"] is False
    assert result_mod["dispatches_count"] == 0

    result_low = service.evaluate_and_dispatch(
        region_name="Raichur Plateau Plains Sector 3",
        risk_level="Low",
        safety_score=95.0,
        advisory="Normal conditions."
    )
    assert result_low["emergency_triggered"] is False
    assert result_low["dispatches_count"] == 0
