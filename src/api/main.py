"""FastAPI app for serving fraud detection models."""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # Allows helper tests in environments without FastAPI.
    FastAPI = None
    HTTPException = ValueError

from src.api.pydantic_models import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)


ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "models"
DEFAULT_THRESHOLD = 0.5
MODEL_FILES = {
    "ecommerce": "ecommerce_random_forest.joblib",
    "creditcard": "creditcard_random_forest.joblib",
}


def create_app():
    """Create and configure the FastAPI app."""

    if FastAPI is None:
        raise ImportError("FastAPI is not installed. Run `pip install -r requirements.txt`.")

    app = FastAPI(
        title="Fraud Detection Model API",
        version="1.0.0",
        description="Real-time fraud risk scoring for e-commerce and credit-card transactions.",
    )

    @app.get("/", response_model=HealthResponse)
    def root():
        return health()

    @app.get("/health", response_model=HealthResponse)
    def health_endpoint():
        return health()

    @app.get("/model/info", response_model=ModelInfoResponse)
    def model_info_endpoint():
        return model_info()

    @app.post("/predict", response_model=PredictionResponse)
    def predict_endpoint(request: PredictionRequest):
        return predict_one(request.dataset, request.transaction)

    @app.post("/predict/batch", response_model=BatchPredictionResponse)
    def predict_batch_endpoint(request: BatchPredictionRequest):
        predictions = [predict_one(request.dataset, transaction) for transaction in request.transactions]
        return BatchPredictionResponse(
            dataset=request.dataset,
            model_name=MODEL_FILES[request.dataset],
            predictions=predictions,
        )

    return app


def health() -> HealthResponse:
    """Return simple service health information."""

    available = [dataset for dataset, file_name in MODEL_FILES.items() if (MODELS_DIR / file_name).exists()]
    return HealthResponse(status="ok", loaded_models=available)


def model_info() -> ModelInfoResponse:
    """Return model metadata used by API clients."""

    return ModelInfoResponse(
        available_models=MODEL_FILES,
        default_threshold=DEFAULT_THRESHOLD,
        notes="Random Forest models are served by default; training and comparison evidence is in reports/.",
    )


@lru_cache(maxsize=2)
def load_model(dataset: str):
    """Load and cache a trained model pipeline."""

    if dataset not in MODEL_FILES:
        raise HTTPException(status_code=400, detail=f"Unsupported dataset: {dataset}")
    model_path = MODELS_DIR / MODEL_FILES[dataset]
    if not model_path.exists():
        raise HTTPException(status_code=503, detail=f"Model artifact not found: {model_path}")
    return joblib.load(model_path)


def predict_one(dataset: str, transaction: Any) -> PredictionResponse:
    """Score one transaction and return risk probability plus label."""

    model = load_model(dataset)
    features = transaction_to_frame(dataset, transaction)
    probability = float(model.predict_proba(features)[0, 1])
    prediction = int(probability >= DEFAULT_THRESHOLD)
    return PredictionResponse(
        dataset=dataset,
        model_name=MODEL_FILES[dataset],
        fraud_probability=probability,
        prediction=prediction,
        risk_label=risk_label(probability),
    )


def transaction_to_frame(dataset: str, transaction: Any) -> pd.DataFrame:
    """Convert a validated request payload into the model feature frame."""

    payload = _to_dict(transaction)
    if dataset == "ecommerce":
        expected = [
            "purchase_value",
            "age",
            "time_since_signup",
            "hour_of_day",
            "day_of_week",
            "transaction_velocity",
            "device_transaction_count",
            "ip_transaction_count",
            "source",
            "browser",
            "sex",
            "country",
        ]
        return pd.DataFrame([{key: payload[key] for key in expected}])
    if dataset == "creditcard":
        payload["amount_log1p"] = math.log1p(payload["Amount"])
        payload["hour_of_day"] = int((payload["Time"] // 3600) % 24)
        payload["risk_score_mean"] = (payload["merchant_risk"] + payload["device_risk"]) / 2
        expected = [
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
        return pd.DataFrame([{key: payload[key] for key in expected}])
    raise HTTPException(status_code=400, detail=f"Unsupported dataset: {dataset}")


def risk_label(probability: float) -> str:
    """Map fraud probability to an operational risk band."""

    if probability >= 0.8:
        return "high"
    if probability >= 0.5:
        return "medium"
    return "low"


def _to_dict(model_or_dict: Any) -> dict[str, Any]:
    """Support Pydantic v1, Pydantic v2, and plain dictionaries."""

    if isinstance(model_or_dict, dict):
        return dict(model_or_dict)
    if hasattr(model_or_dict, "model_dump"):
        return model_or_dict.model_dump()
    if hasattr(model_or_dict, "dict"):
        return model_or_dict.dict()
    raise TypeError(f"Cannot convert transaction payload to dict: {type(model_or_dict)!r}")


app = create_app() if FastAPI is not None else None
