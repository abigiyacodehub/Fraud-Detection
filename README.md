# Fraud Detection for E-Commerce and Bank Transactions

Interim submission repository for improving fraud detection across two transaction
domains:

- `fraud_data.csv`: e-commerce account, purchase, device, browser, source, and IP data.
- `creditcard.csv`: bank/card transaction data with amount, risk, card age, and class labels.
- `IpAddress_to_Country.csv`: IP range lookup table used to enrich e-commerce transactions.

The repository now covers Interim 1, Interim 2, and model interpretation:
data analysis, preprocessing, geolocation integration, feature engineering,
model building, model comparison, saved model artifacts, and SHAP-oriented
explainability.

## Repository Structure

```text
.
|-- .github/workflows/       # CI unit test workflow
|-- data/
|   |-- raw/                 # Local raw data, ignored by Git
|   `-- processed/           # Generated Task 1 features, ignored by Git
|-- models/                  # Tracked .joblib model artifacts
|-- notebooks/
|   |-- eda-fraud-data.ipynb
|   |-- eda-creditcard.ipynb
|   |-- geolocation.ipynb
|   |-- feature-engineering.ipynb
|   |-- modeling.ipynb
|   `-- shap-explainability.ipynb
|-- reports/                 # Generated model comparison and task summaries
|-- scripts/
|   |-- run_task1_pipeline.py
|   |-- train_task2_models.py
|   `-- explain_task3_models.py
|-- src/
|   |-- eda_utils.py
|   |-- geolocation.py
|   |-- preprocessing.py
|   |-- feature_engineering.py
|   |-- modeling.py
|   `-- interpretability.py
`-- tests/
    `-- test_task1_features.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run The Pipelines

```bash
python scripts/run_task1_pipeline.py
python scripts/train_task2_models.py
python scripts/explain_task3_models.py
python -m unittest discover -s tests
```

Task 1 outputs are written to `data/processed/` and `reports/`. Task 2 model
artifacts are saved to `models/`, and model comparison outputs are saved to
`reports/`. Task 3 interpretation outputs are saved to `reports/` as global
importance tables, local explanation tables, method summaries, and PNG plots.

## Rubric Evidence Map

| Rubric area | Repository evidence |
| --- | --- |
| Task 1 data cleaning | `src/preprocessing.py` documents duplicate removal, missing-value checks, required-column validation, and type corrections for both datasets. |
| Task 1 EDA | `notebooks/eda-fraud-data.ipynb` and `notebooks/eda-creditcard.ipynb` contain univariate/bivariate analysis and class imbalance checks. |
| Task 1 geolocation | `src/geolocation.py`, `src/feature_engineering.py`, and `notebooks/geolocation.ipynb` convert IP values to integers, use range-based matching, and support country fraud analysis. |
| Task 1 feature engineering | `src/feature_engineering.py` and `notebooks/feature-engineering.ipynb` create `transaction_velocity`, `time_since_signup`, `hour_of_day`, `day_of_week`, shared-device/IP flags, and credit-card risk features. |
| Task 1 transformation and imbalance | `build_preprocessor()` applies `StandardScaler` and `OneHotEncoder`; `apply_training_resampling()` applies SMOTE or undersampling after a train-test split. |
| Task 2 data preparation | `scripts/train_task2_models.py` and `notebooks/modeling.ipynb` use stratified train-test splits for both datasets. |
| Task 2 baseline model | Logistic Regression training and AUC-PR, F1-score, and confusion matrix evaluation are implemented in `scripts/train_task2_models.py` and `src/modeling.py`. |
| Task 2 ensemble model | Random Forest training with `GridSearchCV` hyperparameter tuning is implemented in `scripts/train_task2_models.py`. |
| Task 2 model comparison | `reports/model_comparison.csv` and `reports/task2_modeling_summary.md` compare model metrics across both datasets. |
| Task 2 saved artifacts | Trained model files are saved under `models/` as `.joblib` artifacts. |
| Task 3 SHAP interpretation | `src/interpretability.py`, `scripts/explain_task3_models.py`, and `notebooks/shap-explainability.ipynb` implement SHAP-first global and local explanations. |
| Task 3 global explanations | `reports/shap_global_feature_importance.csv` and the `*_importance.png` plots summarize top model drivers. |
| Task 3 local explanations | `reports/shap_local_explanations.csv` gives transaction-level feature contributions similar in purpose to force-plot explanations. |
| Task 3 business interpretation | `reports/task3_interpretability_summary.md` explains model behavior for fraud analysts and notes interpretability limitations from the SHAP lecture. |
| Repository best practices | `.gitignore`, `requirements.txt`, CI workflow, clean folders, notebook separation, source scripts, reports, and models are organized by responsibility. |
| Code best practices | Preprocessing, feature engineering, modeling, evaluation, geolocation, and interpretability are modularized with basic error handling around file loading, type conversion, model scoring, resampling choices, and explanation generation. |

## Interim 2 Modeling Approach

- Baseline model: Logistic Regression.
- Ensemble model: Random Forest with `GridSearchCV`.
- Metrics: AUC-PR, F1-score, and confusion matrix values.
- Data split: stratified train-test split for both e-commerce and credit-card datasets.
- Imbalance handling: applied to the training set only so test-set evaluation remains realistic.

## Model Interpretation Approach

- SHAP-first implementation: TreeSHAP for Random Forest and LinearSHAP for Logistic Regression when `shap` is installed.
- Reproducible fallback: model-native Random Forest importance and Logistic Regression coefficient contributions when SHAP is unavailable.
- Global explanation outputs: ranked feature importance tables and PNG plots.
- Local explanation outputs: top transaction-level feature contributions for sampled validation records.
- Interpretation caution: explanations describe model behavior, not guaranteed causal relationships.

## Data Source Notes

The raw datasets are challenge-provided training files and are intentionally kept
under `data/raw/` locally but excluded from Git. To reproduce the pipelines,
place these files inside `data/raw/`:

- `fraud_data.csv`
- `creditcard.csv`
- `IpAddress_to_Country.csv`
