"""Run Task 1 data cleaning, EDA summaries, feature engineering, and prep checks.

This script creates observable repository evidence for the interim rubric:
processed datasets, country-level fraud analysis, class imbalance summaries,
and train-only resampling documentation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.feature_engineering import (  # noqa: E402
    add_creditcard_features,
    add_ecommerce_time_velocity_features,
    add_geolocation_features,
    country_fraud_summary,
)
from src.preprocessing import (  # noqa: E402
    apply_training_resampling,
    build_preprocessor,
    clean_creditcard_data,
    clean_fraud_data,
    load_csv,
)


RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"


def class_distribution(y: pd.Series) -> pd.DataFrame:
    counts = y.value_counts().sort_index()
    return pd.DataFrame(
        {
            "class": counts.index,
            "count": counts.values,
            "percent": (counts.values / counts.sum()) * 100,
        }
    )


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    fraud_raw = load_csv(RAW_DIR / "fraud_data.csv")
    credit_raw = load_csv(RAW_DIR / "creditcard.csv")
    ip_ranges = load_csv(RAW_DIR / "IpAddress_to_Country.csv")

    fraud_clean, fraud_quality = clean_fraud_data(fraud_raw)
    credit_clean, credit_quality = clean_creditcard_data(credit_raw)

    fraud_features = add_geolocation_features(fraud_clean, ip_ranges)
    fraud_features = add_ecommerce_time_velocity_features(fraud_features)
    credit_features = add_creditcard_features(credit_clean)

    fraud_features.to_csv(PROCESSED_DIR / "fraud_data_features.csv", index=False)
    credit_features.to_csv(PROCESSED_DIR / "creditcard_features.csv", index=False)
    country_fraud_summary(fraud_features).to_csv(
        REPORTS_DIR / "country_fraud_summary.csv", index=False
    )

    ecommerce_numeric = [
        "purchase_value",
        "age",
        "time_since_signup",
        "hour_of_day",
        "day_of_week",
        "transaction_velocity",
        "device_transaction_count",
        "ip_transaction_count",
    ]
    ecommerce_categorical = ["source", "browser", "sex", "country"]
    preprocessor = build_preprocessor(ecommerce_numeric, ecommerce_categorical)

    X = fraud_features[ecommerce_numeric + ecommerce_categorical]
    y = fraud_features["class"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train_prepared = preprocessor.fit_transform(X_train)
    X_test_prepared = preprocessor.transform(X_test)
    X_train_resampled, y_train_resampled = apply_training_resampling(
        X_train_prepared, y_train, method="smote", random_state=42
    )

    before = class_distribution(y_train)
    before["stage"] = "train_before_smote"
    after = class_distribution(pd.Series(y_train_resampled))
    after["stage"] = "train_after_smote"
    imbalance_report = pd.concat([before, after], ignore_index=True)
    imbalance_report.to_csv(REPORTS_DIR / "class_imbalance_train_only.csv", index=False)

    quality_report = pd.DataFrame(
        [
            {"dataset": "fraud_data.csv", **fraud_quality.__dict__},
            {"dataset": "creditcard.csv", **credit_quality.__dict__},
        ]
    )
    quality_report.to_csv(REPORTS_DIR / "data_quality_report.csv", index=False)

    summary = REPORTS_DIR / "task1_pipeline_summary.md"
    summary.write_text(
        "# Task 1 Pipeline Summary\n\n"
        "This script cleans both datasets, engineers geolocation/time/velocity features, "
        "builds a StandardScaler + OneHotEncoder transformation pipeline, and applies "
        "SMOTE to the training set only after a stratified train/test split.\n\n"
        "## Outputs\n\n"
        "- `data/processed/fraud_data_features.csv`\n"
        "- `data/processed/creditcard_features.csv`\n"
        "- `reports/country_fraud_summary.csv`\n"
        "- `reports/class_imbalance_train_only.csv`\n"
        "- `reports/data_quality_report.csv`\n\n"
        f"Prepared train matrix shape: {X_train_prepared.shape}\n\n"
        f"Prepared test matrix shape: {X_test_prepared.shape}\n\n"
        f"Resampled train matrix shape: {X_train_resampled.shape}\n",
        encoding="utf-8",
    )
    print(f"Task 1 outputs written to {PROCESSED_DIR} and {REPORTS_DIR}")


if __name__ == "__main__":
    main()
