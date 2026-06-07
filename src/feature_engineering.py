"""Feature engineering utilities for Task 1 fraud detection work."""

from __future__ import annotations

import pandas as pd

from .geolocation import map_ip_to_country


def add_geolocation_features(
    fraud_df: pd.DataFrame,
    ip_df: pd.DataFrame,
    ip_col: str = "ip_address",
) -> pd.DataFrame:
    """Convert IP addresses to integers and map them to countries."""

    df = fraud_df.copy()
    df["ip_int"] = pd.to_numeric(df[ip_col], errors="coerce").astype("int64")
    return map_ip_to_country(df, ip_df, ip_int_col="ip_int")


def add_ecommerce_time_velocity_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create velocity and calendar features for Fraud_Data.csv.

    Required rubric features:
    - transaction velocity
    - time_since_signup
    - hour_of_day
    - day_of_week
    """

    out = df.copy()
    out["signup_time"] = pd.to_datetime(out["signup_time"], errors="coerce")
    out["purchase_time"] = pd.to_datetime(out["purchase_time"], errors="coerce")

    out["time_since_signup"] = (
        out["purchase_time"] - out["signup_time"]
    ).dt.total_seconds()
    out["hour_of_day"] = out["purchase_time"].dt.hour
    out["day_of_week"] = out["purchase_time"].dt.dayofweek
    out["day_name"] = out["purchase_time"].dt.day_name()

    out["device_transaction_count"] = out.groupby("device_id")["device_id"].transform("size")
    out["ip_transaction_count"] = out.groupby("ip_int")["ip_int"].transform("size")
    out["transaction_velocity"] = out["device_transaction_count"] / (
        (out["time_since_signup"].clip(lower=1) / 3600) + 1
    )
    out["fast_purchase_flag"] = (out["time_since_signup"] <= 10).astype(int)
    out["shared_device_flag"] = (out["device_transaction_count"] > 1).astype(int)
    out["shared_ip_flag"] = (out["ip_transaction_count"] > 1).astype(int)
    return out


def add_creditcard_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lightweight model features for credit-card transactions."""

    out = df.copy()
    out["amount_log1p"] = out["Amount"].clip(lower=0).map(lambda value: __import__("math").log1p(value))
    out["hour_of_day"] = ((out["Time"] // 3600) % 24).astype(int)
    out["risk_score_mean"] = out[["merchant_risk", "device_risk"]].mean(axis=1)
    return out


def country_fraud_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate fraud volume and rate by country."""

    return (
        df.groupby("country")
        .agg(transactions=("class", "size"), fraud_cases=("class", "sum"), fraud_rate=("class", "mean"))
        .sort_values(["fraud_rate", "transactions"], ascending=[False, False])
        .reset_index()
    )
