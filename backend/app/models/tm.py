"""
Train the viral prediction model on the Kaggle Social Media Viral Content dataset.

Usage:
    cd backend
    .venv/bin/python -m app.models.train_model

This script:
1. Loads dataset/social_media_viral_content_dataset.csv
2. Cleans, encodes categoricals, and engineers features
3. Trains RandomForest and GradientBoosting classifiers
4. Evaluates (classification report + AUC-ROC)
5. Saves the best model + scaler + metadata to backend/app/models/saved/
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
import json

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = PROJECT_ROOT / "dataset" / "social_media_viral_content_dataset.csv"
SAVE_DIR = Path(__file__).resolve().parent / "saved"

TARGET = 'is_viral'

# Features that the API will accept for prediction
API_FEATURES = [
    'views', 'likes', 'comments', 'shares',
    'engagement_rate', 'sentiment_score',
    'num_hashtags', 'posting_hour', 'posting_month',
    'platform_encoded', 'content_type_encoded', 'topic_encoded',
    'log_views', 'log_likes', 'like_share_ratio', 'comment_rate'
]


def load_and_preprocess(path: Path):
    """Load the Kaggle CSV and engineer features."""
    df = pd.read_csv(path)
    print(f"📂 Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Viral: {df[TARGET].sum()} ({df[TARGET].mean()*100:.1f}%) | Non-viral: {(~df[TARGET].astype(bool)).sum()} ({(1-df[TARGET].mean())*100:.1f}%)")

    # --- Data Cleaning ---
    # Clip extreme engagement_rate outliers (some values > 1.0 look like data errors)
    q99 = df['engagement_rate'].quantile(0.99)
    n_clipped = (df['engagement_rate'] > q99).sum()
    df['engagement_rate'] = df['engagement_rate'].clip(upper=q99)
    if n_clipped > 0:
        print(f"   ✂️  Clipped {n_clipped} engagement_rate outliers (> {q99:.4f})")

    # --- Feature Engineering ---

    # Count hashtags from the hashtags string
    df['num_hashtags'] = df['hashtags'].fillna('').apply(lambda x: len([h for h in x.split() if h.startswith('#')]))

    # Extract posting hour and month from datetime
    df['post_datetime'] = pd.to_datetime(df['post_datetime'], errors='coerce')
    df['posting_hour'] = df['post_datetime'].dt.hour
    df['posting_month'] = df['post_datetime'].dt.month

    # Encode categorical columns
    label_encoders = {}
    for col in ['platform', 'content_type', 'topic']:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].fillna('unknown'))
        label_encoders[col] = le
        print(f"   📌 {col}: {list(le.classes_)}")

    # Log transforms for skewed numerical features
    df['log_views'] = np.log1p(df['views'])
    df['log_likes'] = np.log1p(df['likes'])

    # Ratio features
    df['like_share_ratio'] = df['likes'] / (df['shares'] + 1)
    df['comment_rate'] = df['comments'] / (df['views'] + 1)

    X = df[API_FEATURES].copy()
    y = df[TARGET].copy()

    return X, y, label_encoders, df.shape[0]


def train_and_evaluate():
    """Full training pipeline."""
    print("=" * 60)
    print("🚀 AlgoInfluencers — Viral Prediction Model Training")
    print("   Dataset: Kaggle Social Media Viral Content")
    print("=" * 60)

    # 1. Load data
    X, y, label_encoders, total_rows = load_and_preprocess(DATASET_PATH)
    feature_names = list(X.columns)
    print(f"\n📊 Features ({len(feature_names)}):")
    for f in feature_names:
        print(f"   • {f}")

    # 2. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n📐 Split: {X_train.shape[0]} train / {X_test.shape[0]} test")

    # 3. Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train RandomForest
    print("\n🌲 Training RandomForest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)

    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
    print(f"   CV AUC-ROC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # 5. Evaluate on test set
    y_pred_rf = rf_model.predict(X_test_scaled)
    y_proba_rf = rf_model.predict_proba(X_test_scaled)[:, 1]
    auc_rf = roc_auc_score(y_test, y_proba_rf)

    print(f"\n📋 RandomForest — Test Set Results:")
    print(classification_report(y_test, y_pred_rf, target_names=["Not Viral", "Viral"]))
    print(f"   Test AUC-ROC: {auc_rf:.4f}")

    cm = confusion_matrix(y_test, y_pred_rf)
    print(f"   Confusion Matrix: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")

    # 6. Train GradientBoosting
    print("\n🌳 Training GradientBoosting...")
    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42
    )
    gb_model.fit(X_train_scaled, y_train)
    y_proba_gb = gb_model.predict_proba(X_test_scaled)[:, 1]
    auc_gb = roc_auc_score(y_test, y_proba_gb)
    print(f"   GradientBoosting Test AUC-ROC: {auc_gb:.4f}")

    # 7. Pick best model
    if auc_rf >= auc_gb:
        best_model, best_name, best_auc = rf_model, "RandomForest", auc_rf
        importances = rf_model.feature_importances_
    else:
        best_model, best_name, best_auc = gb_model, "GradientBoosting", auc_gb
        importances = gb_model.feature_importances_

    print(f"\n✅ Best model: {best_name} (AUC: {best_auc:.4f})")

    # 8. Feature importance
    sorted_idx = np.argsort(importances)[::-1]
    print(f"\n🏆 Feature Importance:")
    for i in sorted_idx:
        bar = "█" * int(importances[i] * 50)
        print(f"   {feature_names[i]:25s} {importances[i]:.4f} {bar}")

    # 9. Save everything
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    model_path = SAVE_DIR / "model.joblib"
    scaler_path = SAVE_DIR / "scaler.joblib"
    encoders_path = SAVE_DIR / "label_encoders.joblib"
    metadata_path = SAVE_DIR / "metadata.json"

    joblib.dump(best_model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(label_encoders, encoders_path)

    # Save encoder mappings as JSON-friendly format
    encoder_mappings = {}
    for col, le in label_encoders.items():
        encoder_mappings[col] = {label: int(idx) for idx, label in enumerate(le.classes_)}

    metadata = {
        "model_type": best_name,
        "auc_roc": round(best_auc, 4),
        "dataset": "social_media_viral_content_dataset.csv",
        "dataset_rows": total_rows,
        "features": feature_names,
        "feature_importances": {
            feature_names[i]: round(float(importances[i]), 4) for i in sorted_idx
        },
        "label_encoders": encoder_mappings,
        "n_train_samples": int(X_train.shape[0]),
        "n_test_samples": int(X_test.shape[0])
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n💾 Saved to: {SAVE_DIR}/")
    print(f"   • model.joblib ({model_path.stat().st_size / 1024:.1f} KB)")
    print(f"   • scaler.joblib")
    print(f"   • label_encoders.joblib")
    print(f"   • metadata.json")
    print("\n🎉 Training complete!")


if __name__ == "__main__":
    train_and_evaluate()
