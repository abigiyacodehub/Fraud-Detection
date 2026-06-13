"""Model interpretation helpers for SHAP-oriented fraud analysis.

The primary path uses SHAP when the package is installed. A dependency-light
fallback creates model-native global importance and local contribution tables so
the repository remains reproducible in restricted environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class ExplanationBundle:
    """Global and local explanation outputs for one fitted model."""

    dataset: str
    model_name: str
    method: str
    global_importance: pd.DataFrame
    local_explanations: pd.DataFrame


def get_transformed_feature_names(preprocessor) -> list[str]:
    """Return fitted preprocessor feature names with readable prefixes."""

    if hasattr(preprocessor, "get_feature_names_out"):
        return [str(name) for name in preprocessor.get_feature_names_out()]
    names: list[str] = []
    for transformer_name, _, columns in preprocessor.transformers_:
        if transformer_name == "remainder":
            continue
        names.extend([f"{transformer_name}__{column}" for column in columns])
    return names


def explain_tree_model(model, X_background, X_explain, feature_names: list[str]) -> ExplanationBundle:
    """Explain a tree model with SHAP when available, otherwise feature importances."""

    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    X_background_prepared = preprocessor.transform(X_background)
    X_explain_prepared = preprocessor.transform(X_explain)

    try:
        import shap

        explainer = shap.TreeExplainer(classifier, X_background_prepared)
        shap_values = explainer.shap_values(X_explain_prepared)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        method = "TreeSHAP"
        global_scores = np.abs(shap_values).mean(axis=0)
        local_scores = shap_values
    except Exception:
        method = "model_native_feature_importance"
        global_scores = getattr(classifier, "feature_importances_", np.zeros(len(feature_names)))
        local_scores = np.zeros((X_explain_prepared.shape[0], len(feature_names)))

    global_importance = pd.DataFrame(
        {"feature": feature_names, "importance": np.asarray(global_scores)}
    ).sort_values("importance", ascending=False)

    local_explanations = _top_local_rows(X_explain, local_scores, feature_names)
    return ExplanationBundle("", "Random Forest", method, global_importance, local_explanations)


def explain_linear_model(model, X_background, X_explain, feature_names: list[str]) -> ExplanationBundle:
    """Explain a linear model with SHAP when available, otherwise coefficient contributions."""

    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    X_background_prepared = preprocessor.transform(X_background)
    X_explain_prepared = preprocessor.transform(X_explain)

    try:
        import shap

        explainer = shap.LinearExplainer(classifier, X_background_prepared)
        shap_values = explainer.shap_values(X_explain_prepared)
        method = "LinearSHAP"
        local_scores = np.asarray(shap_values)
    except Exception:
        method = "linear_coefficient_contribution"
        coefficients = classifier.coef_.ravel()
        local_scores = X_explain_prepared.toarray() if hasattr(X_explain_prepared, "toarray") else X_explain_prepared
        local_scores = local_scores * coefficients

    global_scores = np.abs(local_scores).mean(axis=0)
    global_importance = pd.DataFrame(
        {"feature": feature_names, "importance": np.asarray(global_scores)}
    ).sort_values("importance", ascending=False)

    local_explanations = _top_local_rows(X_explain, local_scores, feature_names)
    return ExplanationBundle("", "Logistic Regression", method, global_importance, local_explanations)


def _top_local_rows(X_explain, local_scores, feature_names: list[str], top_n: int = 5) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    local_array = np.asarray(local_scores)
    for row_number in range(min(len(X_explain), local_array.shape[0])):
        row_scores = local_array[row_number]
        top_indices = np.argsort(np.abs(row_scores))[-top_n:][::-1]
        for rank, feature_index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "sample_index": int(X_explain.index[row_number]) if hasattr(X_explain, "index") else row_number,
                    "rank": rank,
                    "feature": feature_names[feature_index],
                    "contribution": float(row_scores[feature_index]),
                }
            )
    return pd.DataFrame(rows)


def draw_importance_chart(df: pd.DataFrame, title: str, output_path: str | Path, top_n: int = 10) -> None:
    """Create a simple PNG bar chart without requiring matplotlib."""

    top = df.head(top_n).copy()
    width, height = 1200, 720
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("arial.ttf", 34)
        label_font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        title_font = label_font = ImageFont.load_default()

    draw.text((40, 30), title, fill="#1f2933", font=title_font)
    max_value = float(top["importance"].max()) if not top.empty else 1.0
    max_value = max(max_value, 1e-12)
    y_start = 105
    for i, (_, row) in enumerate(top.iterrows()):
        y = y_start + i * 55
        label = str(row["feature"]).replace("num__", "").replace("cat__", "")[:46]
        value = float(row["importance"])
        bar_width = int((value / max_value) * 610)
        draw.text((40, y + 6), label, fill="#243447", font=label_font)
        draw.rounded_rectangle([430, y, 430 + bar_width, y + 30], radius=4, fill="#2f6f7e")
        draw.text((1055, y + 5), f"{value:.4f}", fill="#243447", font=label_font)
    image.save(output_path)
