"""
AlgoInfluencers - Viral Prediction Model Training

This version:
1. Removes post-performance variables that can cause data leakage.
2. Uses One-Hot Encoding for categorical variables.
3. Creates time and hashtag features.
4. Compares Random Forest and Gradient Boosting.
5. Evaluates accuracy, precision, recall, F1 and AUC.
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "social_media_viral_content_dataset.csv"
)

SAVE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "app"
    / "models"
    / "saved"
)

SAVE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "is_viral"

# These variables describe post performance.
# We exclude them to avoid target leakage.

LEAKAGE_FEATURES = [
    "views",
    "likes",
    "comments",
    "shares",
    "engagement_rate",
]

ID_FEATURES = [
    "post_id",
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("\n📂 Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(
        f"   Dataset shape: "
        f"{df.shape[0]} rows × {df.shape[1]} columns"
    )

    print("\n   Columns:")

    for column in df.columns:
        print(f"   • {column}")

    return df


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):

    print("\n🧹 Cleaning dataset...")

    df = df.copy()

    # Remove duplicate rows
    before = len(df)

    df = df.drop_duplicates()

    print(
        f"   Removed duplicates: "
        f"{before - len(df)}"
    )

    # Make target numeric
    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce"
    )

    # Remove rows with missing target
    before = len(df)

    df = df.dropna(
        subset=[TARGET]
    )

    print(
        f"   Removed rows with missing target: "
        f"{before - len(df)}"
    )

    df[TARGET] = df[TARGET].astype(int)

    # Convert datetime
    df["post_datetime"] = pd.to_datetime(
        df["post_datetime"],
        errors="coerce"
    )

    # Remove invalid dates
    before = len(df)

    df = df.dropna(
        subset=["post_datetime"]
    )

    print(
        f"   Removed rows with invalid dates: "
        f"{before - len(df)}"
    )

    # Fill categorical missing values
    categorical_columns = [
        "platform",
        "content_type",
        "topic",
        "language",
        "region",
    ]

    for column in categorical_columns:

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
        )

    # Fill missing hashtags
    df["hashtags"] = (
        df["hashtags"]
        .fillna("")
        .astype(str)
    )

    # Convert sentiment to numeric
    df["sentiment_score"] = pd.to_numeric(
        df["sentiment_score"],
        errors="coerce"
    )

    # Fill missing sentiment with median
    df["sentiment_score"] = (
        df["sentiment_score"]
        .fillna(
            df["sentiment_score"].median()
        )
    )

    print(
        f"   Final cleaned dataset: "
        f"{len(df)} rows"
    )

    return df


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def engineer_features(df):

    print("\n🔧 Engineering features...")

    df = df.copy()

    # --------------------------------------------------------
    # TIME FEATURES
    # --------------------------------------------------------

    df["posting_hour"] = (
        df["post_datetime"].dt.hour
    )

    df["posting_day"] = (
        df["post_datetime"].dt.day
    )

    df["posting_dayofweek"] = (
        df["post_datetime"].dt.dayofweek
    )

    df["posting_month"] = (
        df["post_datetime"].dt.month
    )

    df["is_weekend"] = (
        df["posting_dayofweek"] >= 5
    ).astype(int)

    # --------------------------------------------------------
    # HASHTAG COUNT
    # --------------------------------------------------------

    def count_hashtags(value):

        if not value:
            return 0

        value = value.replace(",", " ")

        return sum(
            word.startswith("#")
            for word in value.split()
        )

    df["num_hashtags"] = (
        df["hashtags"]
        .apply(count_hashtags)
    )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    numeric_features = [
        "sentiment_score",
        "num_hashtags",
        "posting_hour",
        "posting_day",
        "posting_dayofweek",
        "posting_month",
        "is_weekend",
    ]

    categorical_features = [
        "platform",
        "content_type",
        "topic",
        "language",
        "region",
    ]

    X = df[
        numeric_features +
        categorical_features
    ].copy()

    y = df[TARGET].copy()

    print(
        f"\n📊 Numeric features "
        f"({len(numeric_features)}):"
    )

    for feature in numeric_features:
        print(f"   • {feature}")

    print(
        f"\n📊 Categorical features "
        f"({len(categorical_features)}):"
    )

    for feature in categorical_features:
        print(f"   • {feature}")

    return (
        X,
        y,
        numeric_features,
        categorical_features
    )


# ============================================================
# CREATE PREPROCESSOR
# ============================================================

def create_preprocessor(
    numeric_features,
    categorical_features
):

    # Numeric columns:
    # StandardScaler puts values onto a similar scale.

    numeric_transformer = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    # Categorical columns:
    # OneHotEncoder converts categories into 0/1 columns.

    categorical_transformer = Pipeline(
        steps=[
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
                numeric_features
            ),
            (
                "categorical",
                categorical_transformer,
                categorical_features
            ),
        ]
    )

    return preprocessor


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(
    model,
    X_test,
    y_test,
    model_name
):

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    print(
        f"\n📋 {model_name} — Test Results"
    )

    print(
        f"   Accuracy : {accuracy:.4f}"
    )

    print(
        f"   Precision: {precision:.4f}"
    )

    print(
        f"   Recall   : {recall:.4f}"
    )

    print(
        f"   F1 Score : {f1:.4f}"
    )

    print(
        f"   AUC-ROC  : {auc:.4f}"
    )

    print("\n   Classification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Not Viral",
                "Viral"
            ],
            zero_division=0
        )
    )

    tn, fp, fn, tp = (
        confusion_matrix(
            y_test,
            predictions
        ).ravel()
    )

    print(
        f"   Confusion Matrix: "
        f"TN={tn} "
        f"FP={fp} "
        f"FN={fn} "
        f"TP={tp}"
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "auc": auc,
    }


# ============================================================
# TRAIN MODELS
# ============================================================

def train_and_evaluate():

    print("=" * 65)

    print(
        "🚀 AlgoInfluencers — Viral Prediction Model Training"
    )

    print(
        "   Leakage-controlled + One-Hot Encoding"
    )

    print("=" * 65)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_dataset()

    # --------------------------------------------------------
    # CLEAN
    # --------------------------------------------------------

    df = clean_data(df)

    # --------------------------------------------------------
    # EXCLUDED VARIABLES
    # --------------------------------------------------------

    print(
        "\n🚫 Excluded from prediction:"
    )

    for feature in ID_FEATURES:
        print(
            f"   • {feature} "
            f"(identifier)"
        )

    for feature in LEAKAGE_FEATURES:
        print(
            f"   • {feature} "
            f"(post-performance / leakage risk)"
        )

    # --------------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------------

    (
        X,
        y,
        numeric_features,
        categorical_features
    ) = engineer_features(df)

    # --------------------------------------------------------
    # TARGET DISTRIBUTION
    # --------------------------------------------------------

    print("\n🎯 Target distribution:")

    print(
        y.value_counts()
        .sort_index()
    )

    # --------------------------------------------------------
    # TRAIN / TEST SPLIT
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print(
        f"\n📐 Split: "
        f"{len(X_train)} train / "
        f"{len(X_test)} test"
    )

# ============================================================
# MAJORITY-CLASS BASELINE
# ============================================================

    majority_class = y_train.mode()[0]

    baseline_predictions = np.full(
        len(y_test),
        majority_class
    )

    baseline_accuracy = accuracy_score(
        y_test,
        baseline_predictions
    )

    print("\n" + "=" * 60)
    print("MAJORITY-CLASS BASELINE")
    print("=" * 60)

    print(f"Majority class: {majority_class}")
    print(f"Baseline Accuracy: {baseline_accuracy:.4f}")

    # --------------------------------------------------------
    # PREPROCESSOR
    # --------------------------------------------------------

    preprocessor = create_preprocessor(
        numeric_features,
        categorical_features
    )

    # --------------------------------------------------------
    # RANDOM FOREST PIPELINE
    # --------------------------------------------------------

    print(
        "\n🌲 Training RandomForest..."
    )

    random_forest = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    min_samples_split=4,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1
                )
            )
        ]
    )

    random_forest.fit(
        X_train,
        y_train
    )

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    cv_auc = cross_val_score(
        random_forest,
        X_train,
        y_train,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1
    )

    print(
        f"   CV AUC-ROC: "
        f"{cv_auc.mean():.4f} "
        f"± {cv_auc.std():.4f}"
    )

    rf_metrics = evaluate_model(
        random_forest,
        X_test,
        y_test,
        "RandomForest"
    )

    # --------------------------------------------------------
    # GRADIENT BOOSTING
    # --------------------------------------------------------

    print(
        "\n🌳 Training GradientBoosting..."
    )

    gradient_boosting = Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor(
                    numeric_features,
                    categorical_features
                )
            ),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=42
                )
            )
        ]
    )

    gradient_boosting.fit(
        X_train,
        y_train
    )

    gb_metrics = evaluate_model(
        gradient_boosting,
        X_test,
        y_test,
        "GradientBoosting"
    )

    # --------------------------------------------------------
    # SELECT BEST MODEL
    # --------------------------------------------------------

    if rf_metrics["auc"] >= gb_metrics["auc"]:

        best_model = random_forest
        best_name = "RandomForest"
        best_metrics = rf_metrics

    else:

        best_model = gradient_boosting
        best_name = "GradientBoosting"
        best_metrics = gb_metrics

    print(
        f"\n✅ Best model: "
        f"{best_name}"
    )

    print(
        f"   AUC-ROC: "
        f"{best_metrics['auc']:.4f}"
    )

    # --------------------------------------------------------
    # SAVE COMPLETE PIPELINE
    # --------------------------------------------------------

    model_path = SAVE_DIR / "model.joblib"
    metadata_path = SAVE_DIR / "metadata.json"

    # The pipeline contains:
    # preprocessing + model

    joblib.dump(
        best_model,
        model_path
    )

    metadata = {
        "model_name": best_name,
        "target": TARGET,
        "prediction_type": "early_virality_prediction",
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "excluded_features": ID_FEATURES + LEAKAGE_FEATURES,
        "metrics": {
            key: float(value)
            for key, value in best_metrics.items()
        },
        "dataset_rows": int(len(df)),
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "random_state": 42,
    }

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print(
        "\n💾 Saved:"
    )

    print(
        f"   • {model_path}"
    )

    print(
        f"   • {metadata_path}"
    )

    print(
        "\n🎉 Training complete!"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    train_and_evaluate()