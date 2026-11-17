import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss

def evaluate_probabilistic_classifier(y_true, y_prob):
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    return {
        "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5, 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob)), 4),
        "positive_rate": round(float(np.mean(y_true)), 4),
    }
