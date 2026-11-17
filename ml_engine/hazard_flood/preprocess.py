from datetime import datetime, timezone
import re
import numpy as np
import pandas as pd

from .config import INDIA_BOUNDS, LAND_COVER_MAP, SOIL_TYPE_MAP
from .errors import InvalidInputError


def validate_location(location):
    if not isinstance(location, dict) or "lat" not in location or "lon" not in location:
        raise InvalidInputError("location must be a dict with 'lat' and 'lon'.")
    lat, lon = float(location["lat"]), float(location["lon"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise InvalidInputError(f"Coordinates out of bounds: lat={lat}, lon={lon}.")
    return {"lat": lat, "lon": lon, "name": str(location.get("name")) if location.get("name") else None}


def parse_observation_time(obs):
    if obs is None:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(obs.strip().replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception as e:
        raise InvalidInputError(f"Invalid observation_time: {obs}") from e


def is_within_india_domain(lat, lon):
    return (
        INDIA_BOUNDS["lat_min"] <= lat <= INDIA_BOUNDS["lat_max"]
        and INDIA_BOUNDS["lon_min"] <= lon <= INDIA_BOUNDS["lon_max"]
    )


def _encode_category(series: pd.Series, mapping: dict, default: float = 0.0) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
        .fillna(default)
        .astype(float)
    )


def _normalize_col_name(col: str) -> str:
    """Normalize column names by stripping parenthetical units, spaces, and special symbols."""
    cleaned = re.sub(r"\(.*?\)", "", str(col)).strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")
    return cleaned


def prepare_flood_training_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize either:
      - Kaggle 'Flood Risk in India' (e.g. 'Latitude', 'Longitude', 'Water Level (m)', 'Flood Occurred', etc.)
      - CWC Station CSV (station_id, lat, lon, water_level_m, danger_level_m)
    into a unified supervised training DataFrame with explicit `label` (0 or 1).
    """
    df = raw_df.copy()
    norm_map = {_normalize_col_name(c): c for c in df.columns}

    # Case A: Kaggle s3programmer/flood-risk-in-india schema (handles spaces & parenthetical units)
    if "latitude" in norm_map and "flood_occurred" in norm_map:
        lat_col = norm_map["latitude"]
        lon_col = norm_map["longitude"]
        wl_col = norm_map.get("water_level") or norm_map.get("water_level_m")
        target_col = norm_map["flood_occurred"]

        if wl_col is None:
            raise ValueError(f"Could not find water level column in {list(df.columns)}")

        out = pd.DataFrame()
        out["target_lat"] = pd.to_numeric(df[lat_col], errors="coerce")
        out["target_lon"] = pd.to_numeric(df[lon_col], errors="coerce")
        out["water_level_m"] = pd.to_numeric(df[wl_col], errors="coerce")

        # Infer regional danger threshold from 85th percentile of non-flood water levels
        non_flood_wl = out.loc[pd.to_numeric(df[target_col], errors="coerce") == 0, "water_level_m"].dropna()
        inferred_danger = float(non_flood_wl.quantile(0.85)) if len(non_flood_wl) > 10 else 7.5
        out["danger_level_m"] = max(1.0, round(inferred_danger, 2))

        rain_col = norm_map.get("rainfall") or norm_map.get("rainfall_mm")
        out["rainfall_24h_mm"] = pd.to_numeric(df[rain_col], errors="coerce").fillna(50.0) if rain_col else 50.0

        dis_col = norm_map.get("river_discharge") or norm_map.get("river_discharge_m3_s")
        out["river_discharge_cumecs"] = pd.to_numeric(df[dis_col], errors="coerce").fillna(1500.0) if dis_col else 1500.0

        hum_col = norm_map.get("humidity") or norm_map.get("humidity_pct")
        out["humidity_pct"] = pd.to_numeric(df[hum_col], errors="coerce").fillna(70.0) if hum_col else 70.0

        temp_col = norm_map.get("temperature") or norm_map.get("temperature_c")
        out["temperature_c"] = pd.to_numeric(df[temp_col], errors="coerce").fillna(28.0) if temp_col else 28.0

        elev_col = norm_map.get("elevation") or norm_map.get("elevation_m")
        out["elevation_m"] = pd.to_numeric(df[elev_col], errors="coerce").fillna(150.0) if elev_col else 150.0

        pop_col = norm_map.get("population_density")
        out["population_density"] = pd.to_numeric(df[pop_col], errors="coerce").fillna(400.0) if pop_col else 400.0

        inf_col = norm_map.get("infrastructure")
        out["has_infrastructure"] = pd.to_numeric(df[inf_col], errors="coerce").fillna(0.0) if inf_col else 0.0

        hist_col = norm_map.get("historical_floods")
        out["historical_floods"] = pd.to_numeric(df[hist_col], errors="coerce").fillna(0.0) if hist_col else 0.0

        lc_col = norm_map.get("land_cover")
        out["land_cover_code"] = _encode_category(df[lc_col], LAND_COVER_MAP) if lc_col else 0.0

        st_col = norm_map.get("soil_type")
        out["soil_type_code"] = _encode_category(df[st_col], SOIL_TYPE_MAP) if st_col else 0.0

        out["label"] = pd.to_numeric(df[target_col], errors="coerce")

        out = out.dropna(subset=["target_lat", "target_lon", "water_level_m", "label"]).reset_index(drop=True)
        out["label"] = (out["label"] > 0).astype(int)
        return out

    # Case B: CWC Station CSV schema
    if "lat" in norm_map and ("water_level_m" in norm_map or "water_level" in norm_map) and ("danger_level_m" in norm_map or "danger_level" in norm_map):
        wl_col = norm_map.get("water_level_m") or norm_map.get("water_level")
        dl_col = norm_map.get("danger_level_m") or norm_map.get("danger_level")
        out = pd.DataFrame()
        out["target_lat"] = pd.to_numeric(df[norm_map["lat"]], errors="coerce")
        out["target_lon"] = pd.to_numeric(df[norm_map["lon"]], errors="coerce")
        out["water_level_m"] = pd.to_numeric(df[wl_col], errors="coerce")
        out["danger_level_m"] = pd.to_numeric(df[dl_col], errors="coerce")
        rain_col = norm_map.get("rainfall_24h_mm") or norm_map.get("rainfall")
        out["rainfall_24h_mm"] = pd.to_numeric(df[rain_col], errors="coerce").fillna(40.0) if rain_col else 40.0
        dis_col = norm_map.get("river_discharge_cumecs") or norm_map.get("river_discharge")
        out["river_discharge_cumecs"] = pd.to_numeric(df[dis_col], errors="coerce").fillna(2000.0) if dis_col else 2000.0
        out["humidity_pct"] = 75.0
        out["temperature_c"] = 27.0
        out["elevation_m"] = 120.0
        out["population_density"] = 450.0
        out["has_infrastructure"] = 1.0
        out["historical_floods"] = 1.0
        out["land_cover_code"] = 3.0
        out["soil_type_code"] = 2.0
        if "label" in norm_map:
            out["label"] = (pd.to_numeric(df[norm_map["label"]], errors="coerce") > 0).astype(int)
        else:
            out["label"] = (out["water_level_m"] >= out["danger_level_m"]).astype(int)
        return out.dropna(subset=["target_lat", "target_lon", "water_level_m", "danger_level_m"]).reset_index(drop=True)

    raise ValueError(
        f"Unrecognized flood CSV columns: {list(df.columns)}. Expected Kaggle 'Flood Risk in India' or CWC station columns."
    )
