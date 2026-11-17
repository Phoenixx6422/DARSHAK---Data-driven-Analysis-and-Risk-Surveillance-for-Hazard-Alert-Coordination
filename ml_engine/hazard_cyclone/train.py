from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from .config import DEFAULT_IBTRACS_CSV, DEFAULT_MODEL_ARTIFACT, FEATURE_COLUMNS, MODEL_VERSION, RANDOM_SEED
from .data_loader import load_training_tracks
from .preprocess import build_supervised_training_samples
from .features import build_feature_matrix
from .model import build_candidate_models, save_model_artifact
from .evaluate import evaluate_probabilistic_classifier

def train_and_select_model(csv_path=DEFAULT_IBTRACS_CSV, artifact_path=DEFAULT_MODEL_ARTIFACT, allow_fallback=True, seed=RANDOM_SEED):
    tracks_df, src = load_training_tracks(csv_path, allow_fallback)
    samples_df = build_supervised_training_samples(tracks_df, samples_per_point=3, seed=seed)
    
    X = build_feature_matrix(samples_df)
    y = samples_df["label"].to_numpy(dtype=int)
    groups = samples_df["SID"].to_numpy()
    
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    tr_idx, te_idx = next(splitter.split(X, y, groups=groups))
    
    X_tr, y_tr = X.iloc[tr_idx], y[tr_idx]
    X_te, y_te = X.iloc[te_idx], y[te_idx]
    
    models = build_candidate_models(seed)
    evals = {}
    for name, model in models.items():
        model.fit(X_tr, y_tr)
        prob = model.predict_proba(X_te)[:, 1]
        evals[name] = evaluate_probabilistic_classifier(y_te, prob)
        
    best_name = max(evals.keys(), key=lambda m: evals[m]["pr_auc"])
    best_model = build_candidate_models(seed)[best_name]
    best_model.fit(X, y)
    
    artifact = {
        "model": best_model, "model_name": best_name, "model_version": MODEL_VERSION,
        "trained_on": f"NIO Cyclone Tracks ({src})", "training_data_source": src,
        "trained_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "feature_columns": FEATURE_COLUMNS, "validation_metrics": evals,
    }
    save_model_artifact(artifact, artifact_path)
    return artifact
