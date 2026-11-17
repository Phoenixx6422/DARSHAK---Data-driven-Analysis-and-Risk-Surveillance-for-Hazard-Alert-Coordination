import numpy as np
import pandas as pd
from .config import FEATURE_COLUMNS, LAND_COVER_MAP, SOIL_TYPE_MAP


def build_feature_row(gauge: dict) -> dict:
    wl = float(gauge.get("water_level_m", 0.0))
    dl = float(gauge.get("danger_level_m", 8.0))
    ratio_danger = wl / max(0.1, dl)

    lc_raw = str(gauge.get("land_cover", "")).strip().lower()
    st_raw = str(gauge.get("soil_type", "")).strip().lower()

    lc_code = float(gauge["land_cover_code"]) if "land_cover_code" in gauge else LAND_COVER_MAP.get(lc_raw, 3.0)
    st_code = float(gauge["soil_type_code"]) if "soil_type_code" in gauge else SOIL_TYPE_MAP.get(st_raw, 2.0)

    return {
        "water_level_m": wl,
        "danger_level_m": dl,
        "level_ratio_danger": float(ratio_danger),
        "rainfall_24h_mm": float(gauge.get("rainfall_24h_mm", 45.0)),
        "river_discharge_cumecs": float(gauge.get("river_discharge_cumecs", 1500.0)),
        "humidity_pct": float(gauge.get("humidity_pct", 75.0)),
        "temperature_c": float(gauge.get("temperature_c", 28.0)),
        "elevation_m": float(gauge.get("elevation_m", 150.0)),
        "population_density": float(gauge.get("population_density", 400.0)),
        "has_infrastructure": float(gauge.get("has_infrastructure", 0.0)),
        "historical_floods": float(gauge.get("historical_floods", 0.0)),
        "land_cover_code": lc_code,
        "soil_type_code": st_code,
        "target_lat": float(gauge.get("lat", gauge.get("target_lat", 22.0))),
        "target_lon": float(gauge.get("lon", gauge.get("target_lon", 80.0))),
    }


def build_feature_matrix(samples_df: pd.DataFrame) -> pd.DataFrame:
    rows = [build_feature_row(row._asdict()) for row in samples_df.itertuples(index=False)]
    return pd.DataFrame(rows)[FEATURE_COLUMNS].astype(np.float64)
