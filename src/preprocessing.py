"""Preprocessing utilities for the fraud detection interim submission.

The functions in this module make Task 1 evidence explicit: missing-value
checks, duplicate handling, type corrections, scaling/encoding, and
training-only imbalance handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class DataQualityReport:
    """Compact summary of the cleaning checks applied to a dataset."""

    rows_before: int
    rows_after: int
    duplicate_rows_removed: int
    missing_values_before: int
    missing_values_after: int
    type_corrections: tuple[str, ...]


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file with a clear error when the file is missing."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    return pd.read_csv(csv_path)


def clean_fraud_data(df: pd.DataFrame) -> tuple[pd.DataFrame, DataQualityReport]:
    """Clean Fraud_Data.csv style e-commerce transactions."""

    rows_before = len(df)
    missing_before = int(df.isna().sum().sum())
    cleaned = df.drop_duplicates().copy()

    required = ["signup_time", "purchase_time", "ip_address", "class"]
    missing_columns = sorted(set(required) - set(cleaned.columns))
    if missing_columns:
        raise ValueError(f"Fraud data missing required columns: {missing_columns}")

    type_corrections: list[str] = []
    for col in ["signup_time", "purchase_time"]:
        cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
        type_corrections.append(f"{col}->datetime")
    cleaned["ip_address"] = pd.to_numeric(cleaned["ip_address"], errors="coerce")
    cleaned["class"] = pd.to_numeric(cleaned["class"], errors="coerce").astype("Int64")
    type_corrections.extend(["ip_address->numeric", "class->integer"])

    cleaned = cleaned.dropna(subset=required)
    cleaned["class"] = cleaned["class"].astype(int)

    return cleaned, DataQualityReport(
        rows_before=rows_before,
        rows_after=len(cleaned),
        duplicate_rows_removed=rows_before - len(df.drop_duplicates()),
        missing_values_before=missing_before,
        missing_values_after=int(cleaned.isna().sum().sum()),
        type_corrections=tuple(type_corrections),
    )


def clean_creditcard_data(df: pd.DataFrame) -> tuple[pd.DataFrame, DataQualityReport]:
    """Clean creditcard.csv transactions and enforce numeric feature types."""

    rows_before = len(df)
    missing_before = int(df.isna().sum().sum())
    cleaned = df.drop_duplicates().copy()

    if "Class" not in cleaned.columns:
        raise ValueError("Credit-card data missing required target column: Class")

    type_corrections: list[str] = []
    for col in cleaned.columns:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
        type_corrections.append(f"{col}->numeric")

    cleaned = cleaned.dropna(subset=["Class"])
    cleaned["Class"] = cleaned["Class"].astype(int)
    feature_cols = [col for col in cleaned.columns if col != "Class"]
    cleaned[feature_cols] = cleaned[feature_cols].fillna(cleaned[feature_cols].median(numeric_only=True))

    return cleaned, DataQualityReport(
        rows_before=rows_before,
        rows_after=len(cleaned),
        duplicate_rows_removed=rows_before - len(df.drop_duplicates()),
        missing_values_before=missing_before,
        missing_values_after=int(cleaned.isna().sum().sum()),
        type_corrections=tuple(type_corrections),
    )


def build_preprocessor(numeric_features: Iterable[str], categorical_features: Iterable[str]):
    """Create a scaler + one-hot encoder ColumnTransformer.

    Imports stay inside the function so data-quality tests can run even before
    optional modeling dependencies are installed.
    """

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, list(numeric_features)),
            ("cat", categorical_pipeline, list(categorical_features)),
        ]
    )


def apply_training_resampling(X_train, y_train, method: str = "smote", random_state: int = 42):
    """Apply imbalance handling to the training set only.

    SMOTE is preferred for the e-commerce dataset because it preserves the
    available majority class while synthesizing minority examples. Random
    undersampling is available for quick baselines where training speed matters.
    """

    if method == "smote":
        from imblearn.over_sampling import SMOTE

        sampler = SMOTE(random_state=random_state)
    elif method == "undersample":
        from imblearn.under_sampling import RandomUnderSampler

        sampler = RandomUnderSampler(random_state=random_state)
    else:
        raise ValueError("method must be either 'smote' or 'undersample'")

    return sampler.fit_resample(X_train, y_train)
