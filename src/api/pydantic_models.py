"""Pydantic schemas for fraud model serving."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EcommerceTransaction(BaseModel):
    """Feature payload for the trained e-commerce fraud model."""

    purchase_value: float = Field(..., ge=0)
    age: int = Field(..., ge=13, le=120)
    time_since_signup: float = Field(..., ge=0)
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    transaction_velocity: float = Field(..., ge=0)
    device_transaction_count: int = Field(..., ge=1)
    ip_transaction_count: int = Field(..., ge=1)
    source: str
    browser: str
    sex: str
    country: str = "Unknown"


class CreditCardTransaction(BaseModel):
    """Raw feature payload for the trained credit-card fraud model."""

    Time: float = Field(..., ge=0)
    Amount: float = Field(..., ge=0)
    merchant_risk: float = Field(..., ge=0, le=1)
    device_risk: float = Field(..., ge=0, le=1)
    international: int = Field(..., ge=0, le=1)
    card_age_days: int = Field(..., ge=0)
    num_items: int = Field(..., ge=1)
    online_order: int = Field(..., ge=0, le=1)


class PredictionRequest(BaseModel):
    """Single transaction prediction request."""

    dataset: Literal["ecommerce", "creditcard"]
    transaction: EcommerceTransaction | CreditCardTransaction


class BatchPredictionRequest(BaseModel):
    """Batch prediction request for one dataset."""

    dataset: Literal["ecommerce", "creditcard"]
    transactions: list[EcommerceTransaction | CreditCardTransaction]


class PredictionResponse(BaseModel):
    """Fraud prediction response."""

    dataset: str
    model_name: str
    fraud_probability: float
    prediction: int
    risk_label: str


class BatchPredictionResponse(BaseModel):
    """Batch fraud prediction response."""

    dataset: str
    model_name: str
    predictions: list[PredictionResponse]


class HealthResponse(BaseModel):
    """API health response."""

    status: str
    loaded_models: list[str]


class ModelInfoResponse(BaseModel):
    """Model metadata response."""

    available_models: dict[str, str]
    default_threshold: float
    notes: str
