"""Train and evaluate Interim 2 fraud models for both datasets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.feature_engineering import (  # noqa: E402
    add_creditcard_features,
    add_ecommerce_time_velocity_features,
    add_geolocation_features,
)
from src.modeling import evaluate_classifier, results_to_frame  # noqa: E402
from src.preprocessing import (  # noqa: E402
    apply_training_resampling,
    build_preprocessor,
    clean_creditcard_data,
    clean_fraud_data,
    load_csv,
)


RAW_DIR = ROOT / "data" / "raw"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"


def prepare_ecommerce():
    fraud_raw = load_csv(RAW_DIR / "fraud_data.csv")
    ip_ranges = load_csv(RAW_DIR / "IpAddress_to_Country.csv")
    fraud_clean, _ = clean_fraud_data(fraud_raw)
    fraud_features = add_geolocation_features(fraud_clean, ip_ranges)
    fraud_features = add_ecommerce_time_velocity_features(fraud_features)

    numeric_features = [
        "purchase_value",
        "age",
        "time_since_signup",
        "hour_of_day",
        "day_of_week",
        "transaction_velocity",
        "device_transaction_count",
        "ip_transaction_count",
    ]
    categorical_features = ["source", "browser", "sex", "country"]
    X = fraud_features[numeric_features + categorical_features]
    y = fraud_features["class"]
    return X, y, numeric_features, categorical_features


def prepare_creditcard():
    credit_raw = load_csv(RAW_DIR / "creditcard.csv")
    credit_clean, _ = clean_creditcard_data(credit_raw)
    credit_features = add_creditcard_features(credit_clean)

    numeric_features = [
        "Time",
        "Amount",
        "merchant_risk",
        "device_risk",
        "international",
        "card_age_days",
        "num_items",
        "online_order",
        "amount_log1p",
        "hour_of_day",
        "risk_score_mean",
    ]
    categorical_features: list[str] = []
    X = credit_features[numeric_features]
    y = credit_features["Class"]
    return X, y, numeric_features, categorical_features


def train_models_for_dataset(dataset_name, X, y, numeric_features, categorical_features):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    X_train_prepared = preprocessor.fit_transform(X_train)
    X_test_prepared = preprocessor.transform(X_test)

    # Resampling is intentionally after the split, so validation/test data remains natural.
    X_train_balanced, y_train_balanced = apply_training_resampling(
        X_train_prepared, y_train, method="undersample", random_state=42
    )

    logistic_model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="liblinear",
        random_state=42,
    )
    logistic_model.fit(X_train_balanced, y_train_balanced)

    random_forest_search = GridSearchCV(
        estimator=RandomForestClassifier(
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),
        param_grid={
            "n_estimators": [50, 100],
            "max_depth": [6, 10],
            "min_samples_leaf": [1, 5],
        },
        scoring="average_precision",
        cv=3,
        n_jobs=-1,
    )
    random_forest_search.fit(X_train_balanced, y_train_balanced)

    logistic_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", logistic_model),
        ]
    )
    random_forest_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", random_forest_search.best_estimator_),
        ]
    )

    results = [
        evaluate_classifier(dataset_name, "Logistic Regression", logistic_model, X_test_prepared, y_test),
        evaluate_classifier(dataset_name, "Random Forest", random_forest_search, X_test_prepared, y_test),
    ]

    slug = dataset_name.lower().replace(" ", "_")
    joblib.dump(logistic_pipeline, MODELS_DIR / f"{slug}_logistic_regression.joblib")
    joblib.dump(random_forest_pipeline, MODELS_DIR / f"{slug}_random_forest.joblib")

    split_report = {
        "dataset": dataset_name,
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "train_fraud_rate": float(pd.Series(y_train).mean()),
        "test_fraud_rate": float(pd.Series(y_test).mean()),
        "balanced_train_rows": int(len(y_train_balanced)),
        "balanced_train_fraud_rate": float(pd.Series(y_train_balanced).mean()),
    }
    return results, split_report


def main() -> None:
    MODELS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    all_results = []
    split_reports = []
    for dataset_name, prepare_fn in [
        ("Ecommerce", prepare_ecommerce),
        ("CreditCard", prepare_creditcard),
    ]:
        X, y, numeric_features, categorical_features = prepare_fn()
        results, split_report = train_models_for_dataset(
            dataset_name, X, y, numeric_features, categorical_features
        )
        all_results.extend(results)
        split_reports.append(split_report)

    comparison = results_to_frame(all_results)
    comparison.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
    (REPORTS_DIR / "task2_split_and_resampling.json").write_text(
        json.dumps(split_reports, indent=2), encoding="utf-8"
    )
    (REPORTS_DIR / "task2_modeling_summary.md").write_text(
        "# Task 2 Modeling Summary\n\n"
        "Both datasets use stratified train-test splits. Logistic Regression is the baseline model. "
        "Random Forest is the ensemble model and is tuned with `GridSearchCV` using AUC-PR scoring. "
        "AUC-PR, F1-score, and confusion matrix values are saved in `model_comparison.csv`. "
        "Model artifacts are saved in `models/` as `.joblib` files.\n\n"
        "```csv\n"
        + comparison.to_csv(index=False)
        + "```\n",
        encoding="utf-8",
    )
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
