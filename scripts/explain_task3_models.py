"""Generate SHAP-oriented model interpretation artifacts for Task 3."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts.train_task2_models import prepare_creditcard, prepare_ecommerce  # noqa: E402
from src.interpretability import (  # noqa: E402
    draw_importance_chart,
    explain_linear_model,
    explain_tree_model,
    get_transformed_feature_names,
)


MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"


def build_explanations(dataset_name, prepare_fn):
    X, y, _, _ = prepare_fn()
    X_train, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    background = X_train.sample(min(300, len(X_train)), random_state=42)
    explain_sample = X_test.sample(min(25, len(X_test)), random_state=42)

    slug = dataset_name.lower()
    logistic_model = joblib.load(MODELS_DIR / f"{slug}_logistic_regression.joblib")
    forest_model = joblib.load(MODELS_DIR / f"{slug}_random_forest.joblib")

    feature_names = get_transformed_feature_names(logistic_model.named_steps["preprocessor"])
    logistic_bundle = explain_linear_model(logistic_model, background, explain_sample, feature_names)
    forest_bundle = explain_tree_model(forest_model, background, explain_sample, feature_names)

    bundles = []
    for bundle in [logistic_bundle, forest_bundle]:
        bundle = bundle.__class__(
            dataset=dataset_name,
            model_name=bundle.model_name,
            method=bundle.method,
            global_importance=bundle.global_importance,
            local_explanations=bundle.local_explanations,
        )
        bundles.append(bundle)

    # Capture the actual fraud labels for local explanation samples.
    sample_labels = y_test.loc[explain_sample.index].rename("actual_fraud_label").reset_index()
    sample_labels.columns = ["sample_index", "actual_fraud_label"]
    return bundles, sample_labels


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    all_global = []
    all_local = []
    method_rows = []

    for dataset_name, prepare_fn in [
        ("ecommerce", prepare_ecommerce),
        ("creditcard", prepare_creditcard),
    ]:
        bundles, sample_labels = build_explanations(dataset_name, prepare_fn)
        sample_labels.to_csv(REPORTS_DIR / f"{dataset_name}_explanation_sample_labels.csv", index=False)
        for bundle in bundles:
            model_slug = bundle.model_name.lower().replace(" ", "_")
            global_df = bundle.global_importance.copy()
            global_df.insert(0, "model_name", bundle.model_name)
            global_df.insert(0, "dataset", dataset_name)
            global_df.insert(2, "method", bundle.method)
            local_df = bundle.local_explanations.copy()
            local_df.insert(0, "model_name", bundle.model_name)
            local_df.insert(0, "dataset", dataset_name)
            local_df.insert(2, "method", bundle.method)
            all_global.append(global_df)
            all_local.append(local_df)
            method_rows.append(
                {
                    "dataset": dataset_name,
                    "model_name": bundle.model_name,
                    "interpretation_method": bundle.method,
                }
            )
            draw_importance_chart(
                bundle.global_importance,
                f"{dataset_name.title()} {bundle.model_name} Feature Importance",
                REPORTS_DIR / f"{dataset_name}_{model_slug}_importance.png",
            )

    global_report = pd.concat(all_global, ignore_index=True)
    local_report = pd.concat(all_local, ignore_index=True)
    global_report.to_csv(REPORTS_DIR / "shap_global_feature_importance.csv", index=False)
    local_report.to_csv(REPORTS_DIR / "shap_local_explanations.csv", index=False)
    methods = pd.DataFrame(method_rows)
    methods.to_csv(REPORTS_DIR / "interpretation_methods.csv", index=False)

    top_features = (
        global_report.groupby(["dataset", "model_name"])
        .head(5)
        .loc[:, ["dataset", "model_name", "feature", "importance"]]
    )
    (REPORTS_DIR / "task3_interpretability_summary.md").write_text(
        "# Task 3 Model Interpretation Summary\n\n"
        "The interpretation workflow follows the SHAP concepts in the course material: "
        "global feature importance, local sample-level explanations, and stakeholder-facing "
        "business interpretation. When `shap` is installed, the script uses TreeSHAP for "
        "Random Forest and LinearSHAP for Logistic Regression. In restricted environments, "
        "it falls back to model-native feature importance and coefficient contributions so "
        "the evidence remains reproducible.\n\n"
        "## Methods Used\n\n"
        "```csv\n"
        + methods.to_csv(index=False)
        + "```\n\n"
        "## Top Features\n\n"
        "```csv\n"
        + top_features.to_csv(index=False)
        + "```\n\n"
        "## Business Interpretation\n\n"
        "- E-commerce explanations emphasize account velocity, device/IP reuse, purchase timing, and country/source/browser signals.\n"
        "- Credit-card explanations emphasize merchant/device risk, card age, transaction amount, and online/international context.\n"
        "- These explanations support analyst trust, debugging, threshold review, and compliance-friendly model narratives.\n",
        encoding="utf-8",
    )
    print("Task 3 interpretation artifacts written to reports/")


if __name__ == "__main__":
    main()
