# Final Submission Summary

This repository contains the final fraud detection submission for e-commerce and
credit-card transactions.

## Completed Scope

### Task 1: Data Analysis and Preprocessing

- Cleaning for both datasets with missing-value checks, duplicate handling, and type corrections.
- EDA notebooks for e-commerce and credit-card fraud data.
- IP-to-integer conversion and range-based country mapping.
- Country-level fraud analysis.
- Feature engineering for transaction velocity, time since signup, hour of day, and day of week.
- Scaling, one-hot encoding, and training-only imbalance handling.

### Task 2: Model Building and Training

- Stratified train-test split for both datasets.
- Logistic Regression baseline model.
- Tuned Random Forest ensemble model.
- AUC-PR, F1-score, and confusion matrix evaluation.
- Model comparison table in `reports/model_comparison.csv`.
- Saved model artifacts in `models/`.

### Task 3: Model Interpretation

- SHAP-first interpretation code for tree and linear models.
- Reproducible fallback explanations when SHAP is unavailable.
- Global feature importance tables and PNG plots.
- Local transaction-level explanation table.
- Business interpretation summary in `reports/task3_interpretability_summary.md`.

### Final Deployment

- FastAPI serving app in `src/api/main.py`.
- Pydantic schemas in `src/api/pydantic_models.py`.
- Real-time and batch prediction endpoints.
- Health and model-info endpoints.
- Dockerfile and Docker Compose configuration.
- Deployment guide in `DEPLOYMENT.md`.

## Validation

Run:

```bash
python -m unittest discover -s tests
```

Current local validation passed with all tests.

### Validation Certification (Final Submission)

The full test suite was executed against installed dependencies and passed:

```text
Ran 11 tests in 0.038s

OK
```

Covered test modules:

- `tests/test_task1_features.py` — Task 1 cleaning, type correction, geolocation, and velocity features.
- `tests/test_modeling.py` — Task 2 evaluation metrics and model comparison ordering.
- `tests/test_interpretability.py` — Task 3 transformed feature naming and importance report schema.
- `tests/test_api_helpers.py` — serving feature construction and risk-label thresholds.

This confirms the repository is complete across Task 1, Task 2, Task 3, and the
final FastAPI deployment layer, and is submitted as the final version.

## Main Commands

```bash
python scripts/run_task1_pipeline.py
python scripts/train_task2_models.py
python scripts/explain_task3_models.py
uvicorn src.api.main:app --reload
```

## GitHub Repository

https://github.com/abigiyacodehub/Fraud-Detection
