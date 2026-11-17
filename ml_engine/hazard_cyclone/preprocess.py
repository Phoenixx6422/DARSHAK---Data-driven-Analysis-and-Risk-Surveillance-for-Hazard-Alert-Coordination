import math
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from .config import NIO_BOUNDS, FORECAST_HORIZON_HOURS, DAMAGING_WIND_THRESHOLD_KT, DAMAGING_WIND_RADIUS_KM
from .errors import InvalidInputError
from .geo import haversine_km

def validate_location(location):
    if not isinstance(location, dict) or "lat" not in location or "lon" not in location:
        raise InvalidInputError("location must be a dict with 'lat' and 'lon'.")
    lat, lon = float(location["lat"]), float(location["lon"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise InvalidInputError(f"Coordinates out of bounds: lat={lat}, lon={lon}.")
    return {"lat": lat, "lon": lon, "name": str(location.get("name")) if location.get("name") else None}

def parse_observation_time(obs):
    if obs is None: return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(obs.strip().replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception as e:
        raise InvalidInputError(f"Invalid observation_time: {obs}") from e

def is_within_nio_domain(lat, lon):
    return NIO_BOUNDS["lat_min"] <= lat <= NIO_BOUNDS["lat_max"] and NIO_BOUNDS["lon_min"] <= lon <= NIO_BOUNDS["lon_max"]

def clean_ibtracs_dataframe(df):
    df = df.copy()
    if "SID" in df.columns:
        df = df[df["SID"].astype(str).str.strip().str.len() > 3].copy()
    df["ISO_TIME"] = pd.to_datetime(df["ISO_TIME"], errors="coerce", utc=True)
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    
    wind_cols = [c for c in ["WMO_WIND", "USA_WIND", "NEWDELHI_WIND"] if c in df.columns]
    w_series = pd.Series(np.nan, index=df.index, dtype=float)
    for c in wind_cols:
        v = pd.to_numeric(df[c], errors="coerce").where(lambda x: x > 0, np.nan)
        w_series = w_series.fillna(v)
    df["WIND_KT"] = w_series

    pres_cols = [c for c in ["WMO_PRES", "USA_PRES", "NEWDELHI_PRES"] if c in df.columns]
    p_series = pd.Series(np.nan, index=df.index, dtype=float)
    for c in pres_cols:
        v = pd.to_numeric(df[c], errors="coerce").where(lambda x: (x >= 850) & (x <= 1030), np.nan)
        p_series = p_series.fillna(v)
    df["PRES_MB"] = p_series

    df["STORM_SPEED"] = pd.to_numeric(df.get("STORM_SPEED", np.nan), errors="coerce")
    df["STORM_DIR"] = pd.to_numeric(df.get("STORM_DIR", np.nan), errors="coerce")
    df = df.dropna(subset=["SID", "ISO_TIME", "LAT", "LON", "WIND_KT", "PRES_MB"]).sort_values(["SID", "ISO_TIME"]).reset_index(drop=True)
    return df

def build_supervised_training_samples(tracks_df, samples_per_point=3, seed=42):
    rng = np.random.default_rng(seed)
    records = []
    for sid, group in tracks_df.groupby("SID", sort=False):
        group = group.sort_values("ISO_TIME").reset_index(drop=True)
        n = len(group)
        if n < 3: continue
        times = group["ISO_TIME"].to_numpy()
        lats = group["LAT"].to_numpy(dtype=float)
        lons = group["LON"].to_numpy(dtype=float)
        winds = group["WIND_KT"].to_numpy(dtype=float)
        pressures = group["PRES_MB"].to_numpy(dtype=float)
        speeds = group["STORM_SPEED"].to_numpy(dtype=float)
        dirs = group["STORM_DIR"].to_numpy(dtype=float)

        for i in range(n - 1):
            t0 = times[i]
            t_horizon = t0 + np.timedelta64(FORECAST_HORIZON_HOURS, "h")
            fut_idx = np.where((times > t0) & (times <= t_horizon))[0]
            if len(fut_idx) == 0: continue
            
            past_mask = (times[:i+1] >= t0 - np.timedelta64(24, "h")) & (times[:i+1] <= t0)
            p_idx = np.where(past_mask)[0]
            ref_idx = p_idx[0] if len(p_idx) > 0 else i
            w_chg = float(winds[i] - winds[ref_idx])
            p_chg = float(pressures[i] - pressures[ref_idx])
            
            spd = speeds[i]
            hdg = dirs[i]
            if np.isnan(spd) or np.isnan(hdg):
                dt_h = max(1.0, float((times[i+1] - t0) / np.timedelta64(1, "h")))
                dist_nm = haversine_km(lats[i], lons[i], lats[i+1], lons[i+1]) / 1.852
                spd = dist_nm / dt_h
                from .geo import initial_bearing_deg
                hdg = initial_bearing_deg(lats[i], lons[i], lats[i+1], lons[i+1])

            future_pick = fut_idx[rng.integers(0, len(fut_idx))]
            coords = [(lats[future_pick] + rng.normal(0, 0.5), lons[future_pick] + rng.normal(0, 0.5))]
            for _ in range(samples_per_point - 1):
                coords.append((lats[i] + rng.uniform(-6, 6), lons[i] + rng.uniform(-6, 6)))

            obs_dt = pd.Timestamp(t0).to_pydatetime()
            for tlat, tlon in coords:
                lbl = 0
                for fi in fut_idx:
                    if winds[fi] >= DAMAGING_WIND_THRESHOLD_KT:
                        if haversine_km(tlat, tlon, lats[fi], lons[fi]) <= DAMAGING_WIND_RADIUS_KM:
                            lbl = 1
                            break
                records.append({
                    "SID": sid, "storm_lat": lats[i], "storm_lon": lons[i],
                    "storm_wind_kt": winds[i], "storm_pressure_mb": pressures[i],
                    "wind_change_24h_kt": w_chg, "pressure_change_24h_mb": p_chg,
                    "forward_speed_kt": float(spd), "heading_deg": float(hdg),
                    "target_lat": tlat, "target_lon": tlon, "month": obs_dt.month, "label": lbl
                })
    return pd.DataFrame(records)
