# Deployment Guide

This project serves trained fraud models through a FastAPI application.

## Run Locally

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

Open:

- API root: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Run With Docker

```bash
docker compose up --build
```

## Endpoints

- `GET /health`: service status and available model artifacts
- `GET /model/info`: model names, threshold, and serving notes
- `POST /predict`: one transaction
- `POST /predict/batch`: multiple transactions from one dataset

## E-Commerce Example

```json
{
  "dataset": "ecommerce",
  "transaction": {
    "purchase_value": 45,
    "age": 31,
    "time_since_signup": 8,
    "hour_of_day": 2,
    "day_of_week": 5,
    "transaction_velocity": 1.8,
    "device_transaction_count": 4,
    "ip_transaction_count": 3,
    "source": "Ads",
    "browser": "Chrome",
    "sex": "M",
    "country": "Unknown"
  }
}
```

## Credit-Card Example

```json
{
  "dataset": "creditcard",
  "transaction": {
    "Time": 43000,
    "Amount": 120.50,
    "merchant_risk": 0.82,
    "device_risk": 0.76,
    "international": 1,
    "card_age_days": 45,
    "num_items": 3,
    "online_order": 1
  }
}
```

## Notes

The API serves the Random Forest models by default because they are the ensemble
models from the final training workflow. The response includes the fraud
probability, a binary prediction using the default `0.5` threshold, and a simple
risk label.
