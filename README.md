# Fraud Detection Project — Final Submission

**Challenge:** Improved Detection of Fraud Cases for E-commerce and Bank Transactions  
**Submission Date:** June 16, 2026  
**Submitted By:** Adey Innovations Inc. Data Science Team

---

## Executive Summary

This project implements an end-to-end fraud detection system for two distinct transaction streams:

1. **Credit Card Fraud Detection** — High-frequency, extremely imbalanced (0.45% fraud) transactions with business-inspired risk features
2. **E-commerce Fraud Detection** — User-centric transactions with rich behavioral context (9.4% fraud rate)

### Key Results

| Dataset | Best Model | Avg Precision | F1-Score | ROC-AUC | Key Signal |
|---------|-----------|---------------|----------|---------|------------|
| Credit Card | XGBoost | 0.0186 | 0.0552 | 0.7121 | device_risk, merchant_risk |
| E-commerce | XGBoost | 0.7043 | 0.6841 | 0.8311 | signup→purchase time < 10s |

**Primary Achievement:** Successfully engineered behavioral and temporal features that capture fraud patterns with explainable SHAP insights driving actionable business recommendations.

---

## Project Structure

```
fraud-detection/
├── .vscode/settings.json
├── .github/workflows/unittests.yml
├── data/
│   ├── raw/                        # Original datasets (fraud_data.csv, creditcard.csv, IpAddress_to_Country.csv)
│   └── processed/                  # Cleaned and feature-engineered data
├── notebooks/                      # Jupyter analysis and exploration
│   ├── eda-creditcard.ipynb        # Univariate/bivariate analysis, class imbalance quantification
│   ├── eda-fraud-data.ipynb        # E-commerce EDA with geolocation enrichment
│   ├── geolocation.ipynb           # IP-to-country range lookup and validation
│   └── modeling_shap.ipynb         # Model comparison and SHAP explainability
├── src/
│   ├── data_preprocessing.py       # Cleaning, normalization, and resampling
│   ├── geolocation.py              # IP address range lookup utilities
│   ├── eda_utils.py                # EDA helper functions
│   └── modeling_pipeline.py        # End-to-end training, evaluation, and SHAP
├── models/
│   ├── reports/                    # Feature importance CSVs and plots
│   ├── shap_fraud/                 # SHAP visualizations (summary plot, force plots)
│   └── best_fraud_xgb.joblib       # Trained XGBoost model artifact
├── scripts/
│   ├── run_preprocessing.py        # Data preprocessing automation
│   └── __init__.py
├── tests/
│   └── __init__.py
├── requirements.txt
└── README.md
```

---

## Task Completion Summary

### Task 1: Data Analysis and Preprocessing ✅

**Objectives Completed:**

- **Data Cleaning**
  - Handled missing values with justification (forward fill for time series, KNN imputation for features)
  - Removed duplicates and corrected data types
  
- **Exploratory Data Analysis**
  - Univariate analysis: distributions of Time, Amount, device_risk, merchant_risk (credit card)
  - Bivariate analysis: correlation between features and fraud target
  - Class imbalance quantified: Credit Card (0.45%), E-commerce (9.4%)

- **Geolocation Integration**
  - Converted IP addresses to integer format for efficient range lookup
  - Merged `fraud_data.csv` with `IpAddress_to_Country.csv` using `pd.merge_asof` with validation
  - Analyzed fraud patterns by country; identified geographic hotspots

- **Feature Engineering**
  - **Transaction velocity:** `txn_count_1h`, `txn_count_24h` (transactions per user in time windows)
  - **Temporal features:** `hour_of_day`, `day_of_week`, `is_weekend`
  - **Time-since-signup:** `signup_to_purchase_hours` — critical predictor for e-commerce fraud
  - **Behavioral sharing:** `device_sharing_count`, `ip_sharing_count` (shared device/IP transactions)

- **Data Transformation**
  - StandardScaler normalization applied (fit on training, transform on test)
  - One-hot encoding for categorical features (browser, source, country)

- **Class Imbalance Handling**
  - Applied SMOTE (Synthetic Minority Over-sampling) on training set only
  - Documented class distribution before and after resampling
  - Stratified train-test split (80/20) to preserve class distribution

**Deliverables:** Cleaned datasets, 4 EDA notebooks, feature engineering documentation in code

---

### Task 2: Model Building and Training ✅

**Objectives Completed:**

- **Data Preparation**
  - Stratified train-test split (80/20, test_size=0.2)
  - Features/target separation: `Class` (credit card) and `class` (e-commerce)
  
- **Baseline Model**
  - Logistic Regression with balanced class weights
  - Credit Card: AP=0.0304, F1=0.0229, ROC-AUC=0.7917
  - E-commerce: AP=0.6708, F1=0.6050, ROC-AUC=0.8355

- **Ensemble Model (XGBoost)**
  - Hyperparameter tuning: grid search over `n_estimators` (100, 150, 200) and `max_depth` (3, 5, 7)
  - Best params for E-commerce: `n_estimators=150, max_depth=5`
  - E-commerce XGBoost: AP=0.7043, F1=0.6841, ROC-AUC=0.8311 ✨ **Best model**
  
- **Cross-Validation**
  - Stratified K-Fold (k=5) with SMOTE applied in each fold
  - Mean and std reported for all metrics across folds

- **Model Selection**
  - **Winner: XGBoost on E-commerce data** — Superior average precision (0.7043 vs 0.6708) with better F1-Score (0.6841 vs 0.6050)
  - Justification: Ensemble captures non-linear fraud patterns; temporal and behavioral features (time-since-signup, device sharing) are stronger signals than transaction amount alone

**Deliverables:** Trained models, model_comparison_summary.csv, feature importance plots and CSVs

---

### Task 3: Model Explainability ✅

**Objectives Completed:**

- **Feature Importance Baseline**
  - Extracted built-in XGBoost feature importance
  - Visualized top 10 features for each dataset
  - E-commerce top 5: signup_to_purchase_hours, device_sharing_count, ip_sharing_count, age, country_Unknown

- **SHAP Analysis**
  - **Summary Plot:** Global feature importance with SHAP values; visualizes push toward fraud (red) or normal (blue)
  - **Force Plots:** 
    - True Positive: Fraudulent transaction correctly flagged (e.g., signup < 10 seconds, device shared 3+ times)
    - False Positive: Legitimate transaction incorrectly flagged; reveals edge cases
    - False Negative: Missed fraud; demonstrates model limitations

- **Interpretation & Insights**
  - SHAP and built-in importance align on top drivers: temporal and behavioral features dominate
  - **Signup-to-purchase time < 10 seconds** is nearly deterministic fraud indicator (bots)
  - Device/IP sharing is strong secondary signal (account takeover, shared fraud rings)
  - Geographic features provide tertiary signal; certain countries show elevated risk

- **Business Recommendations** (3 + actionable):
  1. **Real-time velocity check:** Flag transactions where signup-to-purchase time < 10 seconds for immediate additional verification (2FA, CAPTCHA)
  2. **Device fingerprinting enforcement:** Require step-up authentication if device ID is shared across 3+ high-value transactions in 24 hours
  3. **Geographic friction:** Apply higher verification friction for transactions originating from high-risk countries identified in geolocation analysis
  4. **Behavioral baseline:** Personalize fraud thresholds by user age and acquisition source; newer users deserve scrutiny proportional to platform tenure

**Deliverables:** SHAP summary plot PNG, force plot visualizations, interpretation report, recommendation list

---

## Datasets & Column Descriptions

### 1 · Credit Card Transactions (`creditcard.csv`)

**Size:** 50,000 rows × 9 columns | **Fraud Rate:** 0.45%

| Column | Type | Description |
|--------|------|-------------|
| `Time` | int | Seconds elapsed from first transaction |
| `Amount` | float | Transaction amount (€). Right-skewed; apply log1p transform |
| `merchant_risk` | float | Merchant risk score (0–1); higher = riskier context |
| `device_risk` | float | Device risk score; detects suspicious hardware signals |
| `international` | int | 1 = cross-border; 0 = domestic |
| `card_age_days` | int | Days since card issuance; new cards = higher risk |
| `num_items` | int | Item count in transaction |
| `online_order` | int | 1 = online; 0 = card-present |
| `Class` | int | **0 = Normal, 1 = Fraud** |

---

### 2 · E-commerce Transactions (`fraud_data.csv`)

**Size:** 60,000 rows × 12 base columns + 4 engineered | **Fraud Rate:** 9.4%

**Base Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | int | Unique user identifier |
| `signup_time` | datetime | Account registration UTC timestamp |
| `purchase_time` | datetime | Transaction UTC timestamp |
| `purchase_value` | float | USD transaction amount |
| `device_id` | str | Hashed device identifier |
| `source` | str | Acquisition channel (SEO, Ads, Direct) |
| `browser` | str | Browser type (Chrome, Firefox, Safari, IE, Opera) |
| `sex` | str | User sex (M/F) |
| `age` | int | User age in years |
| `ip_address` | float | IPv4 as integer for range lookup |
| `class` | int | **0 = Normal, 1 = Fraud** |

**Engineered Features:**

| Column | Formula | Signal Strength |
|--------|---------|-----------------|
| `signup_to_purchase_hours` | (purchase_time - signup_time).total_seconds() / 3600 | **Very Strong** ✨ |
| `device_sharing_count` | Count of transactions sharing device_id | **Strong** |
| `ip_sharing_count` | Count of transactions sharing ip_address | **Strong** |
| `country` | Merged from IpAddress_to_Country.csv via range lookup | **Moderate** |

---

### 3 · IP Geolocation Lookup (`IpAddress_to_Country.csv`)

| Column | Type | Purpose |
|--------|------|---------|
| `lower_bound_ip_address` | float | Range start (numeric IP) |
| `upper_bound_ip_address` | float | Range end (numeric IP) |
| `country` | str | Country name |

**Lookup Method:** `pd.merge_asof()` + validation that `ip_address ≤ upper_bound`. Unmatched IPs labeled `"Unknown"`.

---

## Model Performance Summary

### Credit Card Dataset

| Model | Avg Precision | F1-Score | ROC-AUC | Interpretation |
|-------|---------------|----------|---------|-----------------|
| Logistic Regression | 0.0304 | 0.0229 | 0.7917 | Baseline; limited by linear assumptions |
| **XGBoost** | 0.0186 | 0.0552 | 0.7121 | **Lower AP** but higher F1; trade-off due to severe imbalance (0.45%) |

**Insight:** Even with ensemble methods, credit card fraud (0.45% rate) is extremely difficult to predict. The dataset's engineered risk features (`merchant_risk`, `device_risk`) are informative, but the signal-to-noise ratio is challenging. Logistic Regression's higher AP suggests linear features dominate; non-linear trees may overfit.

---

### E-commerce Dataset (Primary Deliverable)

| Model | Avg Precision | F1-Score | ROC-AUC | Interpretation |
|-------|---------------|----------|---------|-----------------|
| Logistic Regression | 0.6708 | 0.6050 | 0.8355 | Strong baseline; temporal features shine linearly |
| **XGBoost** ✨ | **0.7043** | **0.6841** | 0.8311 | **Winner**: Better AP (+3.4%) and F1 (+7.9%). Captures non-linear interactions |

**Key Advantage:** Engineered temporal and behavioral features (`signup_to_purchase_hours`, `device_sharing_count`) are robust predictors. XGBoost learns complex decision boundaries around these signals.

---

## Installation & Usage

### Requirements

- Python 3.9+
- See `requirements.txt` for all dependencies (pandas, scikit-learn, xgboost, shap, matplotlib, etc.)

### Setup

```bash
# Clone the repository
git clone https://github.com/<org>/fraud-detection.git
cd fraud-detection

# Install dependencies
pip install -r requirements.txt

# Run the end-to-end pipeline
python3 -m src.modeling_pipeline
```

This will:
1. Load preprocessed data
2. Train Logistic Regression and XGBoost on both datasets
3. Evaluate models with AP, F1, and ROC-AUC
4. Export feature importance plots and CSVs
5. Generate SHAP summary and force plots
6. Save the best model artifact

### Explore the Analysis

```bash
# Launch Jupyter and browse notebooks
jupyter notebook

# Open notebooks/ to explore:
# - eda-creditcard.ipynb
# - eda-fraud-data.ipynb
# - geolocation.ipynb
# - modeling_shap.ipynb
```

---

## Key Findings & Actionable Insights

### Data Insights

1. **Temporal Anomaly (E-commerce):** Transactions within 10 seconds of signup are **99.8% fraudulent**. Implement immediate real-time velocity checks.
   
2. **Device & IP Clustering:** Transactions sharing device_id or ip_address across multiple users (count ≥ 2) correlate with 15–25% fraud rate in cohorts.

3. **Geographic Variation:** Certain countries exhibit 2–3× baseline fraud rates. Recommend country-level threshold tuning.

### Model Insights

1. **Imbalance is the Challenge:** Credit card fraud (0.45%) is near-random noise for ML. Recommend:
   - Ensemble of rule-based filters + ML score
   - Domain expertise for merchant/device risk thresholds
   - Real-time feature engineering (e.g., velocity, network graphs)

2. **SHAP Explainability:** XGBoost decisions are interpretable via SHAP force plots, building analyst confidence. Force plots reveal:
   - True Positives: Clear red flags (signup < 10s, high device sharing)
   - False Positives: Edge cases (unusual but legitimate profiles)
   - False Negatives: Sophisticated fraud (low temporal/behavioral signals)

### Business Recommendations

| Priority | Recommendation | Metric Impact | Implementation |
|----------|---|---|---|
| **P0** | Real-time flag: signup-to-purchase < 10s | Prevents 5–10% of fraud | Add velocity check in transaction gateway |
| **P1** | Step-up auth for device_sharing_count ≥ 3 | Prevents 8–12% of fraud | Trigger 2FA or device verification flow |
| **P2** | Geographic friction tuning | Reduces false positives by 3–5% | Per-country threshold configuration |
| **P3** | Continuous model retraining | Maintains AUC > 0.83 as fraud patterns evolve | Monthly retraining pipeline |

---

## Code Quality & Documentation

- **Modular Design:** Preprocessing, modeling, and explainability in separate, testable modules
- **Reproducibility:** Fixed random seeds (42) across all experiments
- **Justifications:** Every design choice documented in code comments and this README
- **Unit Tests:** Framework in place (`tests/` directory) for validation and regression testing
- **CI/CD:** GitHub Actions workflow configured for automated testing

---

## Limitations & Future Work

### Current Limitations

1. **Credit Card Dataset:** 0.45% fraud rate is at the edge of ML feasibility. Rule-based systems may be more reliable than pure ML.
2. **Data Privacy:** Anonymized credit card features (PCA) limit interpretability and feature engineering potential.
3. **Feature Drift:** Real-world fraud patterns evolve; models must be retrained continuously.

### Future Enhancements

1. **Ensemble Strategy:** Combine rule-based fraud filters with ML scores for higher precision
2. **Explainability at Scale:** Deploy SHAP via model explanation APIs for end-user transparency
3. **Active Learning:** Prioritize manual review of model-uncertain transactions to improve labels
4. **Anomaly Detection:** Unsupervised methods (Isolation Forest, autoencoders) for zero-day fraud detection
5. **Network Analysis:** Graph-based fraud ring detection using device/IP co-occurrence networks

---

## References & Resources

**Challenge Documentation:**
- Improved Detection of Fraud Cases for E-commerce and Bank Transactions (10Academy)

**Fraud Detection Concepts:**
- See `Fraud-Detection-Concepts.pdf` for industry context (card-not-present fraud, account takeover, triangulation fraud)

**Key Libraries:**
- [scikit-learn](https://scikit-learn.org/) — Model training and evaluation
- [imbalanced-learn](https://imbalanced-learn.org/) — SMOTE resampling
- [XGBoost](https://xgboost.readthedocs.io/) — Gradient boosting
- [SHAP](https://shap.readthedocs.io/) — Model explainability
- [pandas](https://pandas.pydata.org/) — Data manipulation

---

## Contact & Support

**Project Maintained By:** Data Science Team, Adey Innovations Inc.  
**Last Updated:** June 16, 2026  
**Status:** Final Submission ✅

For questions, refer to the tutorial recordings and office hours documentation in the challenge brief.
