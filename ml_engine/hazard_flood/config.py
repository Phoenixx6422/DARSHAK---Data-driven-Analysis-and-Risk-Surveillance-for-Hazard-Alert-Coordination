from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_FLOOD_CSV = DEFAULT_DATA_DIR / "flood_risk_dataset_india.csv"
DEFAULT_CWC_CSV = DEFAULT_DATA_DIR / "cwc_flood_stations.csv"
DEFAULT_GAUGES_JSON = DEFAULT_DATA_DIR / "active_gauges.json"
DEFAULT_MODEL_ARTIFACT = PROJECT_ROOT / "models" / "flood_risk_model.joblib"

HAZARD_TYPE = "flood"
FORECAST_HORIZON_HOURS = 24

RISK_THRESHOLDS = {
    "Low": (0.0, 25.0),
    "Moderate": (25.0, 50.0),
    "High": (50.0, 75.0),
    "Critical": (75.0, 100.0),
}

INDIA_BOUNDS = {"lat_min": 6.5, "lat_max": 37.0, "lon_min": 68.0, "lon_max": 97.5}

FEATURE_COLUMNS = [
    "water_level_m",
    "danger_level_m",
    "level_ratio_danger",
    "rainfall_24h_mm",
    "river_discharge_cumecs",
    "humidity_pct",
    "temperature_c",
    "elevation_m",
    "population_density",
    "has_infrastructure",
    "historical_floods",
    "land_cover_code",
    "soil_type_code",
    "target_lat",
    "target_lon",
]

LAND_COVER_MAP = {
    "urban": 1.0,
    "water body": 2.0,
    "agricultural": 3.0,
    "forest": 4.0,
    "desert": 5.0,
}

SOIL_TYPE_MAP = {
    "clay": 1.0,
    "silt": 2.0,
    "peat": 3.0,
    "loam": 4.0,
    "sandy": 5.0,
}

MODEL_VERSION = "1.1.0"
RANDOM_SEED = 42
