from pathlib import Path
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from .config import DEFAULT_MODEL_ARTIFACT, RANDOM_SEED
from .errors import DataNotAvailableError

def build_candidate_models(seed=RANDOM_SEED):
    logreg = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", HistGradientBoostingClassifier(random_state=seed))
    ])
    hgb = CalibratedClassifierCV(
        estimator=HistGradientBoostingClassifier(max_iter=150, learning_rate=0.06, random_state=seed),
        method="sigmoid", cv=3
    )
    return {"calibrated_hist_gbdt": hgb, "logistic_regression": logreg}

def save_model_artifact(artifact, path=DEFAULT_MODEL_ARTIFACT):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, p)
    return p

def load_model_artifact(path=DEFAULT_MODEL_ARTIFACT):
    p = Path(path)
    if not p.exists():
        raise DataNotAvailableError(f"Cyclone model artifact not found at {p}. Train model first.")
    return joblib.load(p)
