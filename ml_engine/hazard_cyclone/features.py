import math
import numpy as np
import pandas as pd
from .config import FEATURE_COLUMNS, IMD_INTENSITY_CLASSES, PEAK_SEASON_MONTHS
from .geo import haversine_km, initial_bearing_deg, relative_approach_cosine, approximate_distance_to_coast_km, classify_sub_basin

def classify_imd_intensity(wind_kt):
    for th, label, fac in IMD_INTENSITY_CLASSES:
        if wind_kt <= th: return label, fac
    return "Super Cyclonic Storm", 1.0

def build_feature_row(storm, tlat, tlon, month):
    slat, slon = float(storm["lat"]), float(storm["lon"])
    wind = float(storm.get("max_wind_kt", storm.get("storm_wind_kt", 0)))
    pres = float(storm.get("central_pressure_mb", storm.get("storm_pressure_mb", 1005)))
    w_chg = float(storm.get("wind_change_24h_kt", 0))
    p_chg = float(storm.get("pressure_change_24h_mb", 0))
    spd = float(storm.get("forward_speed_kt", 10))
    hdg = float(storm.get("heading_deg", 315))

    dist = haversine_km(slat, slon, tlat, tlon)
    bearing = initial_bearing_deg(slat, slon, tlat, tlon)
    rel_cos = relative_approach_cosine(slat, slon, hdg, tlat, tlon)
    coast_d = approximate_distance_to_coast_km(tlat, tlon)
    _, is_bob = classify_sub_basin(slat, slon)
    angle = 2.0 * math.pi * (month / 12.0)

    return {
        "distance_km": float(dist), "bearing_deg": float(bearing),
        "relative_approach_cos": float(rel_cos), "storm_wind_kt": float(wind),
        "storm_pressure_mb": float(pres), "wind_change_24h_kt": float(w_chg),
        "pressure_change_24h_mb": float(p_chg), "forward_speed_kt": float(spd),
        "heading_deg": float(hdg), "target_lat": float(tlat), "target_lon": float(tlon),
        "dist_to_coast_km": float(coast_d), "month_sin": float(math.sin(angle)),
        "month_cos": float(math.cos(angle)), "is_peak_season": 1.0 if month in PEAK_SEASON_MONTHS else 0.0,
        "is_bay_of_bengal": float(is_bob),
    }

def build_feature_matrix(samples_df):
    rows = []
    for r in samples_df.itertuples(index=False):
        s_dict = {
            "lat": r.storm_lat, "lon": r.storm_lon, "storm_wind_kt": r.storm_wind_kt,
            "storm_pressure_mb": r.storm_pressure_mb, "wind_change_24h_kt": r.wind_change_24h_kt,
            "pressure_change_24h_mb": r.pressure_change_24h_mb, "forward_speed_kt": r.forward_speed_kt,
            "heading_deg": r.heading_deg,
        }
        rows.append(build_feature_row(s_dict, r.target_lat, r.target_lon, int(r.month)))
    return pd.DataFrame(rows)[FEATURE_COLUMNS].astype(np.float64)
