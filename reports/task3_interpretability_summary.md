# Task 3 Model Interpretation Summary

The interpretation workflow follows the SHAP concepts in the course material: global feature importance, local sample-level explanations, and stakeholder-facing business interpretation. When `shap` is installed, the script uses TreeSHAP for Random Forest and LinearSHAP for Logistic Regression. In restricted environments, it falls back to model-native feature importance and coefficient contributions so the evidence remains reproducible.

## Methods Used

```csv
dataset,model_name,interpretation_method
ecommerce,Logistic Regression,linear_coefficient_contribution
ecommerce,Random Forest,model_native_feature_importance
creditcard,Logistic Regression,linear_coefficient_contribution
creditcard,Random Forest,model_native_feature_importance
```

## Top Features

```csv
dataset,model_name,feature,importance
ecommerce,Logistic Regression,num__device_transaction_count,3.1341882462528954
ecommerce,Logistic Regression,num__ip_transaction_count,3.1221270560122267
ecommerce,Logistic Regression,num__transaction_velocity,1.8512062976391601
ecommerce,Logistic Regression,cat__sex_M,0.04103545355703393
ecommerce,Logistic Regression,cat__source_SEO,0.038519041224459205
ecommerce,Random Forest,num__device_transaction_count,0.40371573879371836
ecommerce,Random Forest,num__time_since_signup,0.2523572920119592
ecommerce,Random Forest,num__transaction_velocity,0.21995254672324807
ecommerce,Random Forest,num__ip_transaction_count,0.0783243755626176
ecommerce,Random Forest,num__purchase_value,0.009127206016167462
creditcard,Logistic Regression,num__international,0.4169225400189675
creditcard,Logistic Regression,num__online_order,0.39864611936988753
creditcard,Logistic Regression,num__Time,0.31118500608528155
creditcard,Logistic Regression,num__risk_score_mean,0.15368196264096312
creditcard,Logistic Regression,num__device_risk,0.14471016072356513
creditcard,Random Forest,num__international,0.18720706296728262
creditcard,Random Forest,num__device_risk,0.1480752070530732
creditcard,Random Forest,num__risk_score_mean,0.13878347405760658
creditcard,Random Forest,num__merchant_risk,0.09994033178217687
creditcard,Random Forest,num__Time,0.09863489523622902
```

## Business Interpretation

- E-commerce explanations emphasize account velocity, device/IP reuse, purchase timing, and country/source/browser signals.
- Credit-card explanations emphasize merchant/device risk, card age, transaction amount, and online/international context.
- These explanations support analyst trust, debugging, threshold review, and compliance-friendly model narratives.
