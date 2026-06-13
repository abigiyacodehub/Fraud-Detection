"""Model training and evaluation utilities for Interim 2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score


@dataclass(frozen=True)
class ModelResult:
    """Evaluation result for a fitted fraud model."""

    dataset: str
    model_name: str
    auc_pr: float
    f1_score: float
    tn: int
    fp: int
    fn: int
    tp: int
    best_params: dict[str, Any]


def predict_fraud_scores(model, X):
    """Return fraud-class probabilities when available, otherwise decision scores."""

    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        return (scores - scores.min()) / (scores.max() - scores.min())
    raise ValueError("Model does not expose predict_proba or decision_function")


def evaluate_classifier(dataset: str, model_name: str, model, X_test, y_test) -> ModelResult:
    """Evaluate one classifier with AUC-PR, F1-score, and confusion matrix."""

    scores = predict_fraud_scores(model, X_test)
    predictions = (scores >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    best_params = getattr(model, "best_params_", {})
    return ModelResult(
        dataset=dataset,
        model_name=model_name,
        auc_pr=float(average_precision_score(y_test, scores)),
        f1_score=float(f1_score(y_test, predictions, zero_division=0)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        best_params=dict(best_params),
    )


def results_to_frame(results: list[ModelResult]) -> pd.DataFrame:
    """Convert model results into a comparison table."""

    return pd.DataFrame([result.__dict__ for result in results]).sort_values(
        ["dataset", "auc_pr", "f1_score"], ascending=[True, False, False]
    )
