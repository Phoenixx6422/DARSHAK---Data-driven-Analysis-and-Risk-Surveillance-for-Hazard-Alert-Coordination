"""
Integration tests for Frontend-Backend direct contract wiring.
Ensures that all endpoints required by the dashboard UI (Sanskar Dave / Tushar Kanaujiya)
are fully served with valid status codes and conforming data shapes by the FastAPI backend.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_frontend_active_alert():
    response = client.get("/alerts/active")
    assert response.status_code == 200
    data = response.json()
    assert "active" in data
    assert "title" in data
    assert "level" in data
    assert "description" in data

def test_frontend_risk_score():
    response = client.get("/risk/score?lat=16.2160&lng=77.3566")
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert "name" in data
    assert "score" in data
    assert "level" in data

def test_frontend_weather():
    response = client.get("/weather?lat=21.2&lng=78.1")
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "windSpeed" in data
    assert "rainfall" in data
    assert "pressure" in data

def test_frontend_news():
    response = client.get("/news")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    assert "headline" in data["items"][0]

def test_frontend_risk_zones():
    response = client.get("/risk/zones?type=Risk Zones")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert "type" in data
    assert len(data["zones"]) >= 5

def test_frontend_live_data():
    response = client.get("/map/live-data?layer=Cyclone")
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert "windSpeed" in data

def test_frontend_profile_get_and_put():
    # Test GET
    response = client.get("/profile")
    assert response.status_code == 200
    profile = response.json()
    assert "name" in profile
    assert "email" in profile

    # Test PUT update
    update_payload = dict(profile)
    update_payload["otherInfo"] = "Updated emergency contact preferences."
    put_response = client.put("/profile", json=update_payload)
    assert put_response.status_code == 200
    updated_profile = put_response.json()
    assert updated_profile["otherInfo"] == "Updated emergency contact preferences."

def test_frontend_static_serving():
    response = client.get("/ui/index.html")
    assert response.status_code == 200
    assert "<!doctype html>" in response.text.lower()
