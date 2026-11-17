import json
from pathlib import Path
import numpy as np
import pandas as pd

from .config import (
    DEFAULT_CWC_CSV,
    DEFAULT_DATA_DIR,
    DEFAULT_FLOOD_CSV,
    DEFAULT_GAUGES_JSON,
    RANDOM_SEED,
)
from .errors import DataNotAvailableError, InvalidInputError
from .preprocess import prepare_flood_training_dataframe


def generate_synthetic_flood_records(n_samples: int = 800, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    basins = [
        (25.5, 82.0), (26.5, 92.5), (17.5, 81.2),
        (16.5, 79.5), (21.2, 83.8), (22.8, 77.4),
    ]
    rows = []
    for idx in range(n_samples):
        b_lat, b_lon = basins[idx % len(basins)]
        lat = float(b_lat + rng.normal(0, 2.5))
        lon = float(b_lon + rng.normal(0, 3.0))
        dl = float(rng.uniform(7.0, 12.0))
        wl = float(rng.uniform(2.0, 14.0))
        rain = float(rng.exponential(80.0))
        discharge = float(rng.exponential(3500.0))
        hist = int(rng.random() < 0.45)
        infra = int(rng.random() < 0.50)

        risk_signal = (wl / dl) * 0.55 + (rain / 250.0) * 0.30 + hist * 0.15 - infra * 0.10
        label = 1 if (risk_signal + rng.normal(0, 0.08)) >= 0.72 else 0

        rows.append({
            "target_lat": round(lat, 3),
            "target_lon": round(lon, 3),
            "water_level_m": round(wl, 2),
            "danger_level_m": round(dl, 2),
            "rainfall_24h_mm": round(rain, 1),
            "river_discharge_cumecs": round(discharge, 1),
            "humidity_pct": round(float(rng.uniform(45.0, 99.0)), 1),
            "temperature_c": round(float(rng.uniform(18.0, 38.0)), 1),
            "elevation_m": round(float(rng.uniform(5.0, 600.0)), 1),
            "population_density": round(float(rng.uniform(50.0, 1500.0)), 1),
            "has_infrastructure": float(infra),
            "historical_floods": float(hist),
            "land_cover_code": float(rng.integers(1, 6)),
            "soil_type_code": float(rng.integers(1, 6)),
            "label": label,
        })
    return pd.DataFrame(rows)


def _find_any_flood_csv(explicit_path=None) -> Path | None:
    if explicit_path is not None and Path(explicit_path).exists():
        return Path(explicit_path)
    for candidate in [DEFAULT_FLOOD_CSV, DEFAULT_CWC_CSV]:
        if candidate.exists():
            return candidate
    if DEFAULT_DATA_DIR.exists():
        for csv_file in sorted(DEFAULT_DATA_DIR.glob("*.csv")):
            name_low = csv_file.name.lower()
            if "flood" in name_low or "cwc" in name_low:
                return csv_file
    return None


def load_training_samples(csv_path=None, allow_fallback=True):
    found_csv = _find_any_flood_csv(csv_path)
    if found_csv is not None:
        raw_df = pd.read_csv(found_csv, low_memory=False)
        return prepare_flood_training_dataframe(raw_df), "real", found_csv.name
    if allow_fallback:
        return generate_synthetic_flood_records(), "simulated", "synthetic_flood_generator"
    raise DataNotAvailableError("No flood CSV dataset found in data/ and synthetic fallback is disabled.")


def load_active_gauges(source=None):
    if source is None:
        path = DEFAULT_GAUGES_JSON
        if not path.exists():
            return [], "simulated"
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    elif isinstance(source, (str, Path)):
        with Path(source).open("r", encoding="utf-8") as f:
            payload = json.load(f)
    elif isinstance(source, dict):
        payload = source
    else:
        raise InvalidInputError("Invalid active gauges source.")

    gauges = []
    for g in payload.get("gauges", []):
        gauges.append({
            "station_id": str(g.get("station_id", "GAUGE_1")),
            "name": str(g.get("name", "River Gauge")),
            "lat": float(g["lat"]),
            "lon": float(g["lon"]),
            "water_level_m": float(g["water_level_m"]),
            "danger_level_m": float(g.get("danger_level_m", 8.0)),
            "rainfall_24h_mm": float(g.get("rainfall_24h_mm", 45.0)),
            "river_discharge_cumecs": float(g.get("river_discharge_cumecs", 1800.0)),
            "humidity_pct": float(g.get("humidity_pct", 78.0)),
            "temperature_c": float(g.get("temperature_c", 27.0)),
            "elevation_m": float(g.get("elevation_m", 120.0)),
            "population_density": float(g.get("population_density", 450.0)),
            "has_infrastructure": float(g.get("has_infrastructure", 1.0)),
            "historical_floods": float(g.get("historical_floods", 1.0)),
            "land_cover": str(g.get("land_cover", "Agricultural")),
            "soil_type": str(g.get("soil_type", "Silt")),
            "updated_at": g.get("updated_at"),
        })
    return gauges, payload.get("data_source", "real")
