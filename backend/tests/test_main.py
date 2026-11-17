import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify that root endpoint returns active service status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "PDEWS Integrated API"
    assert data["status"] == "active"
    assert "Himanshu Shukla" in data["database_monitoring"]
    assert "Vaibhav Rawat" in data["backend_apis"]

def test_health_check_endpoint():
    """Verify health endpoint reports healthy database and monitoring."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["monitoring"] == "active"

def test_get_alerts_all():
    """Verify fetching all disaster alerts."""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 2
    
    # Validate fields on the first alert
    alert = alerts[0]
    required_keys = {"id", "disaster_type", "severity", "location", "latitude", "longitude", "description", "timestamp"}
    assert required_keys.issubset(alert.keys())

def test_get_alerts_filter_by_severity():
    """Verify filtering disaster alerts by severity (case-insensitive)."""
    response = client.get("/api/v1/alerts?severity=Critical")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "Critical"
    assert alerts[0]["disaster_type"] == "Cyclone"

    # Lowercase check
    response_lower = client.get("/api/v1/alerts?severity=high")
    assert response_lower.status_code == 200
    alerts_lower = response_lower.json()
    assert len(alerts_lower) == 1
    assert alerts_lower[0]["severity"] == "High"

def test_evaluate_risk_success():
    """Verify risk evaluation with valid location input."""
    payload = {
        "region_name": "Coastal Raichur Sector 4",
        "latitude": 16.2160,
        "longitude": 77.3566
    }
    response = client.post("/api/v1/risk/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["region_name"] == "Coastal Raichur Sector 4"
    assert "safety_score" in data
    assert data["risk_classification"] == "High"
    assert data["automated_notification_triggered"] is True

def test_evaluate_risk_validation_error():
    """Verify 422 Unprocessable Entity when required fields are missing."""
    invalid_payload = {
        "latitude": 16.2160
        # missing longitude and region_name
    }
    response = client.post("/api/v1/risk/evaluate", json=invalid_payload)
    assert response.status_code == 422

def test_get_user_profile():
    """Verify user profile details."""
    response = client.get("/api/v1/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Himanshu Shukla"
    assert "iiitraichur.ac.in" in data["email"]
    assert "blood_group" in data
    assert "emergency_contact" in data

def test_websocket_alerts():
    """Verify WebSocket alert connection and message echoing."""
    with client.websocket_connect("/ws/alerts") as websocket:
        websocket.send_text("Ping sensor check")
        data = websocket.receive_text()
        assert "Broadcast acknowledgment: Ping sensor check" in data
