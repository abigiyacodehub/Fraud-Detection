# Fraud Detection for E-Commerce and Bank Transactions

Interim submission repository for improving fraud detection across two transaction
domains:

- `fraud_data.csv`: e-commerce account, purchase, device, browser, source, and IP data.
- `creditcard.csv`: bank/card transaction data with amount, risk, card age, and class labels.
- `IpAddress_to_Country.csv`: IP range lookup table used to enrich e-commerce transactions.

The Task 1 work focuses on data analysis, preprocessing, geolocation integration,
feature engineering, data transformation, and class imbalance handling.

## Repository Structure

```text
.
├── .github/workflows/       # CI unit test workflow
├── data/
│   ├── raw/                 # Local raw data, ignored by Git
│   └── processed/           # Generated features, ignored by Git
├── models/                  # Generated model artifacts, ignored by Git
├── notebooks/
│   ├── eda-fraud-data.ipynb
│   ├── eda-creditcard.ipynb
│   ├── geolocation.ipynb
│   └── feature-engineering.ipynb
├── reports/                 # Tracked README plus generated summaries
├── scripts/
│   └── run_task1_pipeline.py
├── src/
│   ├── eda_utils.py
│   ├── geolocation.py
│   ├── preprocessing.py
│   └── feature_engineering.py
└── tests/
    └── test_task1_features.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run Task 1 Pipeline

```bash
python scripts/run_task1_pipeline.py
python -m unittest discover -s tests
```

The pipeline writes reproducible outputs to `data/processed/` and `reports/`.
Generated CSV/model/data files are ignored by Git to keep the repository light.

## Rubric Evidence Map

| Rubric area | Repository evidence |
| --- | --- |
| Data cleaning | `src/preprocessing.py` documents duplicate removal, missing-value checks, required-column validation, and type corrections for both `fraud_data.csv` and `creditcard.csv`. |
| EDA | `notebooks/eda-fraud-data.ipynb` and `notebooks/eda-creditcard.ipynb` contain univariate/bivariate analysis and class imbalance checks for both datasets. |
| Geolocation integration | `src/geolocation.py`, `src/feature_engineering.py`, and `notebooks/geolocation.ipynb` convert IP addresses to integers, perform range-based country matching, and support country-level fraud analysis. |
| Feature engineering | `src/feature_engineering.py` and `notebooks/feature-engineering.ipynb` create `transaction_velocity`, `time_since_signup`, `hour_of_day`, `day_of_week`, shared-device/IP flags, and credit-card risk features. |
| Data transformation | `build_preprocessor()` in `src/preprocessing.py` applies `StandardScaler` to numeric features and `OneHotEncoder` to categorical features. |
| Class imbalance handling | `apply_training_resampling()` in `src/preprocessing.py` applies SMOTE or undersampling after the train/test split; `scripts/run_task1_pipeline.py` writes before/after training-set class distributions. |
| Repository best practices | `.gitignore`, `requirements.txt`, CI workflow, `notebooks/`, `src/`, `scripts/`, `data/`, `tests/`, `models/`, and `reports/` are organized by responsibility. |
| Code best practices | Preprocessing, feature engineering, EDA utilities, and geolocation logic are modularized; file loading, type conversion, and merge inputs include basic validation/error handling. |

## Key Interim Findings

- E-commerce fraud is materially less rare than credit-card fraud in the provided data, but both datasets are imbalanced enough that accuracy is not an appropriate primary metric.
- Short signup-to-purchase time, shared devices, shared IPs, and country/IP intelligence are important e-commerce fraud signals.
- Credit-card fraud modeling should include transaction amount, merchant risk, device risk, international transaction status, card age, and engineered hour/risk features.
- Recommended model evaluation metrics are PR-AUC, recall, F1-score, confusion-matrix review, and ROC-AUC as a secondary metric.

## Data Source Notes

The raw datasets are challenge-provided training files and are intentionally kept
under `data/raw/` locally but excluded from Git. To reproduce the pipeline, place:

- `fraud_data.csv`
- `creditcard.csv`
- `IpAddress_to_Country.csv`

inside `data/raw/`, then run `python scripts/run_task1_pipeline.py`.
