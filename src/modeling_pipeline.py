import os
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

# Ensure the package path is available when the module is executed directly.
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

warnings.filterwarnings('ignore')


def load_processed_creditcard_data(processed_dir='data/processed'):
    path = ROOT_DIR / processed_dir / 'creditcard_processed.csv'
    if not path.exists():
        raise FileNotFoundError(
            f"Processed credit card data not found at '{path}'. "
            "Run `python3 -m src.data_preprocessing` first."
        )
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to load credit card data from '{path}': {exc}") from exc


def load_processed_fraud_data(processed_dir='data/processed'):
    path = ROOT_DIR / processed_dir / 'fraud_data_processed.csv'
    if not path.exists():
        raise FileNotFoundError(
            f"Processed fraud data not found at '{path}'. "
            "Run `python3 -m src.data_preprocessing` first."
        )
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to load fraud data from '{path}': {exc}") from exc


def prepare_creditcard_dataset(processed_dir='data/processed'):
    df = load_processed_creditcard_data(processed_dir)
    X = df.drop(columns=['Class'])
    y = df['Class'].astype('int64')
    return X, y


def prepare_fraud_dataset(processed_dir='data/processed'):
    df = load_processed_fraud_data(processed_dir)
    X = df.drop(columns=['class'])
    y = df['class'].astype('int64')
    return X, y


def describe_dataset(name: str, X: pd.DataFrame, y: pd.Series) -> None:
    print(f'### Dataset: {name}')
    print(f'Rows: {len(X):,}, Features: {X.shape[1]}')
    print('Target class distribution:')
    distribution = y.value_counts().sort_index()
    print(distribution.to_string())
    print('Percent distribution:')
    print((distribution / len(y) * 100).round(3).to_string())
    print(f'Imbalance ratio (normal : fraud) = {distribution.iloc[0] / distribution.iloc[1]:.1f} : 1')


def split_scale_resample(X: pd.DataFrame, y: pd.Series, random_state=42, test_size=0.2):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    smote = SMOTE(random_state=random_state)
    X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)  # type: ignore

    print('Training set before resampling:', np.bincount(y_train.values))
    print('Training set after SMOTE:', np.bincount(y_train_res))
    print('-' * 72)

    return X_train_scaled, X_test_scaled, y_train, y_test, X_train_res, y_train_res, scaler


def evaluate_model(clf, X_test, y_test, model_name: str, dataset_name: str):
    try:
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]
    except Exception as exc:
        raise RuntimeError(f"Prediction failed for {model_name} on {dataset_name}: {exc}") from exc

    ap = average_precision_score(y_test, y_proba)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    print(f'{dataset_name} | {model_name} | AP: {ap:.4f} | F1: {f1:.4f} | ROC-AUC: {roc:.4f}')
    print('Confusion matrix:')
    print(cm)
    print('-' * 72)

    return {
        'dataset': dataset_name,
        'model': model_name,
        'average_precision': ap,
        'f1_score': f1,
        'roc_auc': roc,
        'tn': cm[0, 0],
        'fp': cm[0, 1],
        'fn': cm[1, 0],
        'tp': cm[1, 1],
    }


def cross_validate_model(X: pd.DataFrame,
                         y: pd.Series,
                         base_model,
                         n_splits=5,
                         random_state=42):
    metrics = {'average_precision': [], 'f1_score': [], 'roc_auc': []}
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), start=1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)

        smote = SMOTE(random_state=random_state)
        X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)  # type: ignore

        model = clone(base_model)
        try:
            model.fit(X_train_res, y_train_res)
        except Exception as exc:
            raise RuntimeError(f"Model training failed on fold {fold}: {exc}") from exc

        y_val_pred = model.predict(X_val_scaled)
        y_val_proba = model.predict_proba(X_val_scaled)[:, 1]

        metrics['average_precision'].append(average_precision_score(y_val, y_val_proba))
        metrics['f1_score'].append(f1_score(y_val, y_val_pred))
        metrics['roc_auc'].append(roc_auc_score(y_val, y_val_proba))
        print(f'  Fold {fold} | AP {metrics["average_precision"][-1]:.4f} | F1 {metrics["f1_score"][-1]:.4f} | ROC-AUC {metrics["roc_auc"][-1]:.4f}')

    return {
        'mean_average_precision': np.mean(metrics['average_precision']),
        'std_average_precision': np.std(metrics['average_precision']),
        'mean_f1_score': np.mean(metrics['f1_score']),
        'std_f1_score': np.std(metrics['f1_score']),
        'mean_roc_auc': np.mean(metrics['roc_auc']),
        'std_roc_auc': np.std(metrics['roc_auc']),
    }


def tune_xgboost(X: pd.DataFrame, y: pd.Series, random_state=42):
    param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [3, 5, 7],
    }
    best_score = -1
    best_params = {}

    for n_est in param_grid['n_estimators']:
        for max_d in param_grid['max_depth']:
            model = XGBClassifier(
                n_estimators=n_est,
                max_depth=max_d,
                use_label_encoder=False,
                eval_metric='logloss',
                n_jobs=-1,
                random_state=random_state,
            )
            try:
                summary = cross_validate_model(X, y, model, n_splits=5, random_state=random_state)
            except Exception as exc:
                print(f"  Skipping params n_estimators={n_est}, max_depth={max_d}: {exc}")
                continue

            if summary['mean_average_precision'] > best_score:
                best_score = summary['mean_average_precision']
                best_params = {'n_estimators': n_est, 'max_depth': max_d}

    print(f'Best XGBoost params: {best_params} (CV AP={best_score:.4f})')
    return best_params


def plot_feature_importance(model, feature_names, top_n=10, save_path=None):
    if not hasattr(model, 'feature_importances_'):
        raise ValueError('Model does not expose feature importances.')

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_features[::-1], top_importances[::-1])
    ax.set_xlabel('Feature Importance (Gain)')
    ax.set_title(f'Top {top_n} Feature Importances')
    plt.tight_layout()

    if save_path:
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        except Exception as exc:
            print(f"Warning: could not save feature importance plot to '{save_path}': {exc}")
    plt.show()

    return pd.Series(importances, index=feature_names).sort_values(ascending=False)


def shap_explainability(model, X_test, y_test, feature_names, save_dir=None, sample_size=1000):
    """Generate SHAP summary and force plots for TP, FP, and FN predictions.

    Parameters
    ----------
    model       : Trained tree model (XGBoost, RandomForest, etc.)
    X_test      : Test feature DataFrame (scaled, columns = feature_names)
    y_test      : True labels (Series or array, aligned with X_test)
    feature_names : List of feature name strings
    save_dir    : Directory to save generated SHAP plots (default: None)
    sample_size : Number of samples to use for SHAP analysis (default: 1000)
    """
    sample_idx = np.random.RandomState(42).choice(
        X_test.shape[0], min(sample_size, X_test.shape[0]), replace=False)
    X_sample = X_test.iloc[sample_idx] if hasattr(X_test, 'iloc') else X_test[sample_idx]

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
    except Exception as exc:
        raise RuntimeError(f"SHAP TreeExplainer failed: {exc}") from exc

    # --- Summary plot ---
    plt.figure()
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
    if save_dir:
        try:
            save_dir_path = Path(save_dir)
            save_dir_path.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_dir_path / 'shap_summary_plot.png', dpi=150, bbox_inches='tight')
        except Exception as exc:
            print(f"Warning: could not save SHAP summary plot: {exc}")
    plt.show()

    # --- Force plots: TP, FP, FN ---
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    selected = {}
    for label, cond in [
        ('true_positive', (y_test == 1) & (pd.Series(y_pred, index=y_test.index) == 1)),
        ('false_positive', (y_test == 0) & (pd.Series(y_pred, index=y_test.index) == 1)),
        ('false_negative', (y_test == 1) & (pd.Series(y_pred, index=y_test.index) == 0)),
    ]:
        indices = np.where(cond)[0]
        if len(indices) == 0:
            print(f'Warning: No {label} instances found — skipping force plot.')
            continue

        idx = indices[0]
        selected[label] = idx
        instance = X_test.iloc[[idx]] if hasattr(X_test, 'iloc') else X_test[[idx]]

        if idx in sample_idx:
            instance_shap_values = shap_values[np.where(sample_idx == idx)[0][0]]
        else:
            try:
                instance_shap_values = explainer.shap_values(instance)[0]
            except Exception as exc:
                print(f"Warning: SHAP force plot computation failed for {label}: {exc}")
                continue

        try:
            shap.force_plot(
                explainer.expected_value,
                instance_shap_values,
                instance,
                feature_names=feature_names,
                matplotlib=True,
                show=False,
            )
            plt.tight_layout()
            if save_dir:
                plt.savefig(save_dir_path / f'shap_force_plot_{label}.png', dpi=150, bbox_inches='tight')
            plt.show()
        except Exception as exc:
            print(f"Warning: could not render force plot for {label}: {exc}")

    return {
        'feature_names': feature_names,
        'shap_values': shap_values,
        'selected_instances': selected,
        'confusion_matrix': cm,
    }


def run_pipeline():
    results = []
    output_dir = ROOT_DIR / 'models' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_configs = [
        ('CreditCard', prepare_creditcard_dataset),
        ('FraudData', prepare_fraud_dataset),
    ]

    for dataset_name, prepare_fn in dataset_configs:
        X, y = prepare_fn('data/processed')
        describe_dataset(dataset_name, X, y)

        X_train_scaled, X_test_scaled, y_train, y_test, X_train_res, y_train_res, scaler = \
            split_scale_resample(X, y)

        baseline = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
        try:
            baseline.fit(X_train_res, y_train_res)
        except Exception as exc:
            raise RuntimeError(f"Logistic Regression training failed on {dataset_name}: {exc}") from exc
        results.append(evaluate_model(baseline, X_test_scaled, y_test, 'LogisticRegression', dataset_name))

        best_params = tune_xgboost(X, y)
        ensemble = XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            n_jobs=-1,
            random_state=42,
            **best_params,  # type: ignore
        )
        try:
            ensemble.fit(X_train_res, y_train_res)
        except Exception as exc:
            raise RuntimeError(f"XGBoost training failed on {dataset_name}: {exc}") from exc
        results.append(evaluate_model(ensemble, X_test_scaled, y_test, 'XGBoost', dataset_name))

        feature_names = X.columns.tolist()
        importance = plot_feature_importance(
            ensemble, feature_names,
            save_path=output_dir / f'{dataset_name}_feature_importance.png'
        )
        importance.to_csv(output_dir / f'{dataset_name}_feature_importance.csv')

        if dataset_name == 'FraudData':
            import joblib
            try:
                joblib.dump(ensemble, ROOT_DIR / 'models' / 'best_fraud_xgb.joblib')
                print('Saved FraudData ensemble model artifact.')
            except Exception as exc:
                print(f"Warning: could not save model artifact: {exc}")

            shap_dir = ROOT_DIR / 'models' / 'shap_fraud'
            X_test_df = pd.DataFrame(X_test_scaled, columns=feature_names)
            shap_explainability(ensemble, X_test_df, y_test.reset_index(drop=True), feature_names, shap_dir)

    summary_df = pd.DataFrame(results)
    summary_path = output_dir / 'model_comparison_summary.csv'
    try:
        summary_df.to_csv(summary_path, index=False)
        print(f'Saved model comparison summary to {summary_path}')
    except Exception as exc:
        print(f"Warning: could not save model comparison summary: {exc}")
    print(summary_df)


if __name__ == '__main__':
    run_pipeline()
