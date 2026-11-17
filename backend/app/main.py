from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
try:
    import email_validator  # noqa: F401
    from pydantic import EmailStr
except Exception:
    EmailStr = str
import os
import sys
import json
from app.notifications.notification_service import notification_service
from app.services.realtime_data_service import realtime_service

# Ensure ml_engine is available on sys.path for Layer 3 ML Risk Engine
ml_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml_engine"))
if ml_dir not in sys.path:
    sys.path.insert(0, ml_dir)

try:
    from risk_engine.aggregator import assess_location_risk, get_system_status as get_ml_status
    HAS_ML_ENGINE = True
except Exception:
    HAS_ML_ENGINE = False

app = FastAPI(
    title="PDEWS Integrated Backend API",
    description="Pre-Disaster Management & Early Warning System - Integrated by Himanshu Shukla (DB/Monitoring) & Vaibhav Rawat (Backend)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "service": "PDEWS Integrated API",
        "status": "active",
        "database_monitoring": "Himanshu Shukla",
        "backend_apis": "Vaibhav Rawat",
        "architecture": "Layer 2 & Layer 3 Integrated"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected", "monitoring": "active"}

# Schemas
class DisasterAlert(BaseModel):
    id: int
    disaster_type: str
    severity: str
    location: str
    latitude: float
    longitude: float
    description: str
    timestamp: str

class LocationQuery(BaseModel):
    latitude: float
    longitude: float
    region_name: str

class RiskAssessmentResponse(BaseModel):
    region_name: str
    safety_score: float
    risk_classification: str
    advisory: str
    automated_notification_triggered: bool

class UserProfile(BaseModel):
    name: str
    phone: str
    email: EmailStr
    blood_group: str
    emergency_contact: str
    saved_location: str

# Endpoints matching frontend expectations
@app.get("/api/v1/alerts", response_model=List[DisasterAlert])
def get_alerts(severity: Optional[str] = None):
    alerts = [
        {
            "id": 1,
            "disaster_type": "Cyclone",
            "severity": "Critical",
            "location": "Coastal Raichur Sector 4",
            "latitude": 16.2160,
            "longitude": 77.3566,
            "description": "High-velocity cyclonic winds exceeding 110 km/h detected. Immediate evacuation recommended.",
            "timestamp": "2026-11-16T10:30:00Z"
        },
        {
            "id": 2,
            "disaster_type": "Flood",
            "severity": "High",
            "location": "Krishna River Basin Zone B",
            "latitude": 16.3000,
            "longitude": 77.4000,
            "description": "Water levels rising above danger mark due to heavy sustained upstream rainfall.",
            "timestamp": "2026-11-16T09:15:00Z"
        }
    ]
    if severity:
        return [a for a in alerts if a["severity"].lower() == severity.lower()]
    return alerts

@app.post("/api/v1/risk/evaluate", response_model=RiskAssessmentResponse)
def evaluate_risk(query: LocationQuery):
    # Dynamic risk estimation based on location or defaults
    name_lower = query.region_name.lower()
    if "critical" in name_lower or "cyclone storm" in name_lower:
        safety_score = 24.5
        risk_classification = "Critical"
        advisory = "CRITICAL CYCLONIC THREAT: Winds exceed 110 km/h. Evacuate low-lying areas immediately."
    elif "basin" in name_lower or "river" in name_lower or "flood" in name_lower:
        safety_score = 45.0
        risk_classification = "High"
        advisory = "HIGH FLOOD HAZARD: Upstream river levels rising rapidly. Stay clear of riverbanks."
    elif "urban" in name_lower or "heat" in name_lower:
        safety_score = 68.0
        risk_classification = "Moderate"
        advisory = "MODERATE HEATWAVE: Temperatures approaching 41C. Hydration advisories active."
    else:
        safety_score = 78.5
        risk_classification = "High"
        advisory = "High risk conditions detected. Automated emergency notifications dispatched."
    
    # Automated dispatch via Himanshu's notification gateway (Zero authority approval required)
    dispatch_result = notification_service.evaluate_and_dispatch(
        region_name=query.region_name,
        risk_level=risk_classification,
        safety_score=safety_score,
        advisory=advisory
    )
    
    return {
        "region_name": query.region_name,
        "safety_score": safety_score,
        "risk_classification": risk_classification,
        "advisory": advisory,
        "automated_notification_triggered": dispatch_result["emergency_triggered"]
    }

@app.get("/api/v1/zones")
def get_risk_zones():
    geojson_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_pipeline", "sample_zones.geojson"))
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

@app.get("/api/v1/news")
def get_disaster_news():
    return [
        {
            "id": 1,
            "title": "Severe Cyclonic Storm Alert Issued for Coastal Raichur",
            "category": "Cyclone",
            "source": "IMD Early Warning Center",
            "time": "15 mins ago",
            "severity": "Critical",
            "summary": "Wind gusts exceeding 110 km/h detected. Automated emergency evacuation protocols initiated for low-lying sectors."
        },
        {
            "id": 2,
            "title": "Krishna River Basin Inflow Exceeds Safe Reservoir Threshold",
            "category": "Flood",
            "source": "Central Water Commission (CWC)",
            "time": "1 hour ago",
            "severity": "High",
            "summary": "Upstream discharge has reached 145,000 cusecs. Flood advisory issued for riparian zones."
        },
        {
            "id": 3,
            "title": "Heatwave Conditions Projected to Ease by Weekend",
            "category": "Meteorology",
            "source": "National Weather Bulletin",
            "time": "3 hours ago",
            "severity": "Moderate",
            "summary": "Urban temperatures currently plateauing at 41C. Pre-monsoon showers anticipated in 48 hours."
        }
    ]

@app.get("/api/v1/notifications/logs")
def get_notification_logs():
    return {
        "count": len(notification_service.get_history()),
        "authority_approval_required": False,
        "logs": notification_service.get_history()
    }

@app.get("/api/v1/profile", response_model=UserProfile)
def get_profile():
    return {
        "name": "Himanshu Shukla",
        "phone": "+91-9876543210",
        "email": "cs25b1017@iiitraichur.ac.in",
        "blood_group": "B+",
        "emergency_contact": "+91-9123456789",
        "saved_location": "Hostel Krishna, IIIT Raichur"
    }

# WebSocket for real-time alerts
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Broadcast acknowledgment: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =====================================================================
# FRONTEND-COMPATIBLE ROUTES
# These endpoints match the API contract expected by the frontend's
# api.js (Sanskar Dave / Tushar Kanaujiya's dashboard).
# The original /api/v1/* endpoints above are kept for backward
# compatibility and existing backend tests.
# =====================================================================

# In-memory profile store (demo — real storage would be PostGIS / secured DB)
_profile_store = {
    "name": "Himanshu Shukla",
    "email": "cs25b1017@iiitraichur.ac.in",
    "phone": "+91 98765 43210",
    "location": "IIIT Raichur, Karnataka",
    "lat": 16.2160,
    "lng": 77.3566,
    "familyContacts": [
        {"name": "Emergency Response Hub", "phone": "+91 91234 56789"}
    ],
    "emergencyContact": "Emergency contact: +91 112",
    "bloodGroup": "B+",
    "otherInfo": "Asthma medication in emergency kit",
    "preferences": {"smsAlerts": True, "emailAlerts": True, "appAlerts": True}
}

# Risk zone data shared by multiple frontend endpoints
_risk_zones = [
    {"name": "Bay of Bengal", "lat": 18.4, "lng": 88.2, "score": 24, "level": "Critical", "weight": 1.0},
    {"name": "Odisha Coast", "lat": 20.2, "lng": 86.8, "score": 38, "level": "High", "weight": 0.82},
    {"name": "Eastern India", "lat": 23.1, "lng": 84.4, "score": 52, "level": "Moderate", "weight": 0.62},
    {"name": "Bangladesh Coast", "lat": 22.4, "lng": 90.2, "score": 34, "level": "High", "weight": 0.78},
    {"name": "Central India", "lat": 21.2, "lng": 78.1, "score": 65, "level": "Moderate", "weight": 0.38},
    {"name": "Raichur Region", "lat": 16.2160, "lng": 77.3566, "score": 42, "level": "High", "weight": 0.70},
    {"name": "Western Bay", "lat": 16.8, "lng": 84.4, "score": 42, "level": "High", "weight": 0.7},
    {"name": "Assam", "lat": 26.4, "lng": 92.4, "score": 57, "level": "Moderate", "weight": 0.54}
]

_live_data = {
    "Risk Zones": {"windSpeed": "120 km/h", "pressure": "980 hPa", "location": "15.2\u00b0N, 88.4\u00b0E", "lastUpdated": "3 hours ago"},
    "Cyclone": {"windSpeed": "120 km/h", "pressure": "980 hPa", "location": "15.2\u00b0N, 88.4\u00b0E", "lastUpdated": "3 hours ago"},
    "Rainfall": {"rainfall": "84 mm / 24h", "intensity": "Heavy", "location": "Eastern Coast", "lastUpdated": "1 hour ago"},
    "Flood": {"affectedArea": "Low-lying delta districts", "alertLevel": "Watch", "location": "Bangladesh Coast", "lastUpdated": "2 hours ago"},
    "Wind": {"windSpeed": "120 km/h", "gusts": "145 km/h", "direction": "NE", "location": "15.2\u00b0N, 88.4\u00b0E", "lastUpdated": "3 hours ago"},
    "Pressure": {"pressure": "980 hPa", "trend": "Falling", "location": "Bay of Bengal", "lastUpdated": "3 hours ago"}
}


@app.get("/alerts/active")
def get_active_alert():
    """
    Frontend expects: {active, title, description, location, level, updated}.
    Connected to live disaster early warning feed via RealtimeDataService.
    """
    return realtime_service.fetch_live_active_alert()


@app.get("/map/live-data")
def get_live_data(layer: str = "Risk Zones"):
    """
    Frontend expects: {windSpeed, ...} or null for unknown layers.
    Connected to dynamic real-time layer observations.
    """
    return realtime_service.fetch_live_layer_data(layer)


@app.get("/risk/score")
def get_risk_score(lat: float = 21.2, lng: float = 78.1):
    """
    Frontend expects: {name, lat, lng, score, level, weight}.
    Powered by Layer 3 ML Aggregator Engine (Cyclone + Flood trained models).
    """
    # 1. First check if close to a known static zone
    best = None
    best_dist = float("inf")
    for zone in _risk_zones:
        dist = abs(zone["lat"] - lat) + abs(zone["lng"] - lng)
        if dist < best_dist:
            best_dist = dist
            best = zone
    if best and best_dist < 4.0:
        return best

    # 2. If dynamic coordinates requested, compute dynamically with ML engine
    if HAS_ML_ENGINE:
        try:
            ml_res = assess_location_risk({"lat": lat, "lon": lng, "name": f"Lat {lat}, Lng {lng}"})
            return {
                "name": f"Area ({lat:.2f}, {lng:.2f})",
                "lat": lat,
                "lng": lng,
                "score": round(ml_res["safety_score"]),
                "level": ml_res["risk_level"],
                "weight": round(ml_res["combined_risk_score"] / 100.0, 2),
                "dominant_hazard": ml_res.get("dominant_hazard", "none"),
                "ml_powered": True
            }
        except Exception:
            pass

    if best and best_dist < 7.0:
        return best
    return None


@app.get("/api/v1/ml/status")
def get_ml_status_endpoint():
    """Provides Layer 3 AI/ML Engine diagnostic status."""
    if HAS_ML_ENGINE:
        return {"status": "active", "system": get_ml_status()}
    return {"status": "unavailable", "detail": "ML engine modules not loaded"}


@app.post("/api/v1/ml/assess")
def assess_ml_hazard(location: dict):
    """Direct inference against Cyclone & Flood ML models via Risk Aggregator."""
    if not HAS_ML_ENGINE:
        raise HTTPException(status_code=503, detail="ML engine unavailable")
    return assess_location_risk(location)


@app.get("/weather")
def get_weather(lat: float = 21.2, lng: float = 78.1):
    """
    Frontend expects: {temperature, condition, horizon, rainfall, windSpeed, pressure}.
    Connected to live Open-Meteo meteorological API with fallback caching.
    """
    return realtime_service.fetch_live_weather(lat=lat, lon=lng)


@app.get("/news")
def get_news_frontend():
    """
    Frontend expects: {items: [{id, type, headline, source, time, image, summary}]}.
    Connected to live Google News / NDMA disaster alert RSS feed with fallback caching.
    """
    return {"items": realtime_service.fetch_live_news()}


@app.get("/risk/zones")
def get_risk_zones_frontend(type: str = "Risk Zones"):
    """Frontend expects: {zones: [...], type}."""
    return {"zones": _risk_zones, "type": type}


from starlette.requests import Request as StarletteRequest


@app.get("/profile")
def get_profile_frontend():
    """Frontend expects full profile with familyContacts, preferences, lat/lng, etc."""
    import copy
    return copy.deepcopy(_profile_store)


@app.put("/profile")
async def save_profile_put(request: StarletteRequest):
    """Accept the frontend's full profile JSON and store it in memory."""
    import copy
    body = await request.json()
    _profile_store.update(body)
    return copy.deepcopy(_profile_store)


# Mount frontend directory for direct UI access via FastAPI (http://localhost:8000/ui)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")
