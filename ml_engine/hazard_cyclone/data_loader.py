import json
import math
from pathlib import Path
import pandas as pd
import numpy as np
from .config import DEFAULT_IBTRACS_CSV, DEFAULT_ACTIVE_STORMS_JSON, RANDOM_SEED
from .errors import DataNotAvailableError, InvalidInputError
from .preprocess import clean_ibtracs_dataframe

def generate_synthetic_tracks(n_storms=100, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    rows = []
    peak_m = [4, 5, 6, 10, 11, 12]
    off_m = [1, 2, 3, 7, 8, 9]
    for idx in range(n_storms):
        sid = f"SYN_{2005 + (idx % 20)}_{idx:04d}"
        is_bob = rng.random() < 0.75
        lat = float(rng.uniform(8.0, 14.0))
        lon = float(rng.uniform(83.0, 92.0) if is_bob else rng.uniform(65.0, 72.0))
        dlat_b, dlon_b = float(rng.uniform(0.2, 0.4)), float(rng.uniform(-0.3, 0.1))
        m = int(rng.choice(peak_m if rng.random() < 0.8 else off_m))
        start_t = pd.Timestamp(f"{2015 + (idx % 8)}-{m:02d}-{int(rng.integers(1, 25)):02d} 00:00:00", tz="UTC")
        steps = int(rng.integers(16, 32))
        peak_s = int(steps * rng.uniform(0.5, 0.75))
        p_wind = float(rng.uniform(40.0, 120.0))
        
        for step in range(steps):
            t = start_t + pd.Timedelta(hours=3 * step)
            if step <= peak_s:
                wind = 20.0 + (p_wind - 20.0) * (step / max(1, peak_s))**1.2
            else:
                wind = max(18.0, p_wind * (1.0 - 0.7 * (step - peak_s) / max(1, steps - peak_s)))
            wind += float(rng.normal(0, 1.5))
            pres = 1010.0 - 0.55 * max(0.0, wind - 15.0) + float(rng.normal(0, 1))
            lat = min(25.0, max(5.0, lat + dlat_b + rng.normal(0, 0.03)))
            lon = min(95.0, max(58.0, lon + dlon_b + 0.007 * step + rng.normal(0, 0.04)))
            rows.append({
                "SID": sid, "ISO_TIME": t, "LAT": round(lat, 3), "LON": round(lon, 3),
                "WIND_KT": round(max(15, wind), 1), "PRES_MB": round(pres, 1),
                "STORM_SPEED": 12.0, "STORM_DIR": 320.0
            })
    return pd.DataFrame(rows)

def load_training_tracks(csv_path=DEFAULT_IBTRACS_CSV, allow_fallback=True):
    path = Path(csv_path)
    if path.exists():
        return clean_ibtracs_dataframe(pd.read_csv(path, low_memory=False)), "real"
    if allow_fallback:
        return generate_synthetic_tracks(), "simulated"
    raise DataNotAvailableError(f"IBTrACS file not found at {path}.")

def load_active_storms(source=None):
    if source is None:
        path = DEFAULT_ACTIVE_STORMS_JSON
        if not path.exists(): return [], "simulated"
        with path.open("r", encoding="utf-8") as f: payload = json.load(f)
    elif isinstance(source, (str, Path)):
        with Path(source).open("r", encoding="utf-8") as f: payload = json.load(f)
    elif isinstance(source, dict):
        payload = source
    else:
        raise InvalidInputError("Invalid active storms source.")
    
    storms = []
    for s in payload.get("storms", []):
        w = float(s["max_wind_kt"])
        storms.append({
            "storm_id": str(s.get("storm_id", "STORM_1")),
            "name": str(s.get("name", "UNNAMED")),
            "lat": float(s["lat"]), "lon": float(s["lon"]),
            "max_wind_kt": w,
            "central_pressure_mb": float(s.get("central_pressure_mb", 1010 - 0.55*max(0, w-15))),
            "wind_change_24h_kt": float(s.get("wind_change_24h_kt", 0)),
            "pressure_change_24h_mb": float(s.get("pressure_change_24h_mb", 0)),
            "forward_speed_kt": float(s.get("forward_speed_kt", 11)),
            "heading_deg": float(s.get("heading_deg", 320)),
            "updated_at": s.get("updated_at")
        })
    return storms, payload.get("data_source", "real")
