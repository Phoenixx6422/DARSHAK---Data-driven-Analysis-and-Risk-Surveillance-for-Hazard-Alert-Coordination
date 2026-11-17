from datetime import datetime, timezone
from sklearn.model_selection import StratifiedKFold
from .config import DEFAULT_MODEL_ARTIFACT, FEATURE_COLUMNS, MODEL_VERSION, RANDOM_SEED
from .data_loader import load_training_samples
from .features import build_feature_matrix
from .model import build_candidate_models, save_model_artifact
from .evaluate import evaluate_probabilistic_classifier


def train_and_select_model(csv_path=None, artifact_path=DEFAULT_MODEL_ARTIFACT, allow_fallback=True, seed=RANDOM_SEED):
    samples_df, src, source_name = load_training_samples(csv_path=csv_path, allow_fallback=allow_fallback)

    X = build_feature_matrix(samples_df)
    y = samples_df["label"].to_numpy(dtype=int)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    tr_idx, te_idx = next(skf.split(X, y))

    X_tr, y_tr = X.iloc[tr_idx], y[tr_idx]
    X_te, y_te = X.iloc[te_idx], y[te_idx]

    models = build_candidate_models(seed)
    evals = {}
    for name, model in models.items():
        model.fit(X_tr, y_tr)
        prob = model.predict_proba(X_te)[:, 1]
        evals[name] = evaluate_probabilistic_classifier(y_te, prob)

    best_name = max(evals.keys(), key=lambda m: (evals[m]["pr_auc"], -evals[m]["brier_score"]))
    best_model = build_candidate_models(seed)[best_name]
    best_model.fit(X, y)

    artifact = {
        "model": best_model,
        "model_name": best_name,
        "model_version": MODEL_VERSION,
        "trained_on": f"{source_name} ({len(samples_df)} records)",
        "training_data_source": src,
        "trained_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "feature_columns": FEATURE_COLUMNS,
        "validation_metrics": evals,
    }
    save_model_artifact(artifact, artifact_path)
    return artifact
