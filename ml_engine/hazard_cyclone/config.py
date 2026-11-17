from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_IBTRACS_CSV = DEFAULT_DATA_DIR / "ibtracs.NI.list.v04r01.csv"
DEFAULT_ACTIVE_STORMS_JSON = DEFAULT_DATA_DIR / "active_storms.json"
DEFAULT_MODEL_ARTIFACT = PROJECT_ROOT / "models" / "cyclone_risk_model.joblib"

HAZARD_TYPE = "cyclone"
FORECAST_HORIZON_HOURS = 48
DAMAGING_WIND_THRESHOLD_KT = 50.0
DAMAGING_WIND_RADIUS_KM = 200.0

RISK_THRESHOLDS = {
    "Low": (0.0, 25.0),
    "Moderate": (25.0, 50.0),
    "High": (50.0, 75.0),
    "Critical": (75.0, 100.0),
}
NIO_BOUNDS = {"lat_min": 0.0, "lat_max": 32.0, "lon_min": 40.0, "lon_max": 100.0}
IMD_INTENSITY_CLASSES = [
    (17.0, "Low Pressure Area", 0.15),
    (27.0, "Depression", 0.30),
    (33.0, "Deep Depression", 0.45),
    (47.0, "Cyclonic Storm", 0.65),
    (63.0, "Severe Cyclonic Storm", 0.80),
    (89.0, "Very Severe Cyclonic Storm", 0.90),
    (119.0, "Extremely Severe Cyclonic Storm", 0.96),
    (float("inf"), "Super Cyclonic Storm", 1.00),
]
PEAK_SEASON_MONTHS = {4, 5, 6, 10, 11, 12}
FEATURE_COLUMNS = [
    "distance_km", "bearing_deg", "relative_approach_cos", "storm_wind_kt",
    "storm_pressure_mb", "wind_change_24h_kt", "pressure_change_24h_mb",
    "forward_speed_kt", "heading_deg", "target_lat", "target_lon",
    "dist_to_coast_km", "month_sin", "month_cos", "is_peak_season", "is_bay_of_bengal",
]
MODEL_VERSION = "1.0.0"
RANDOM_SEED = 42
