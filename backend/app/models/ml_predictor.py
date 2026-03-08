"""
Viral Prediction Model — loads a pre-trained model from disk.

Trained on Kaggle's Social Media Viral Content & Engagement Metrics dataset.
Run training: python -m app.models.train_model
"""

import numpy as np
import json
from pathlib import Path
import joblib

SAVE_DIR = Path(__file__).resolve().parent / "saved"


class ViralPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = None
        self.label_encoders = None
        self.is_trained = False
        self._load_model()

    def _load_model(self):
        """Load the pre-trained model, scaler, encoders, and metadata."""
        model_path = SAVE_DIR / "model.joblib"
        scaler_path = SAVE_DIR / "scaler.joblib"
        encoders_path = SAVE_DIR / "label_encoders.joblib"
        metadata_path = SAVE_DIR / "metadata.json"

        if model_path.exists() and scaler_path.exists():
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            self.is_trained = True
            model_type = self.metadata.get("model_type", "Unknown") if self.metadata else "Unknown"
            auc = self.metadata.get("auc_roc", "N/A") if self.metadata else "N/A"
            print(f"✅ Loaded pre-trained {model_type} model (AUC: {auc})")
        else:
            print("⚠️  No pre-trained model found. Run: python -m app.models.train_model")
            self.is_trained = False

    def _encode_categorical(self, col_name: str, value: str) -> int:
        """Safely encode a categorical value using the saved label encoder."""
        if self.label_encoders and col_name in self.label_encoders:
            le = self.label_encoders[col_name]
            if value in le.classes_:
                return int(le.transform([value])[0])
        return 0  # Default encoding for unknown values

    def predict(self, features: dict) -> dict:
        """
        Predict the viral probability of a social media post.

        features: dict with keys like:
            - views, likes, comments, shares (engagement numbers)
            - engagement_rate, sentiment_score
            - platform ('Instagram', 'X', 'TikTok', 'YouTube Shorts')
            - content_type ('text', 'image', 'video', 'carousel')
            - topic ('Sports', 'Technology', 'Politics', 'Education', 'Entertainment', 'Lifestyle')
            - hashtags (string like '#tech #ai')
            - posting_hour (0-23), posting_month (1-12)
        """
        if not self.is_trained:
            return {
                "viral": False,
                "probability": 0.0,
                "score": 0,
                "error": "Model not trained. Run: python -m app.models.train_model"
            }

        # Extract features with sensible defaults
        views = features.get('views', 100000)
        likes = features.get('likes', 5000)
        comments = features.get('comments', 500)
        shares = features.get('shares', 200)
        engagement_rate = features.get('engagement_rate', 0.08)
        sentiment_score = features.get('sentiment_score', 0.0)

        # Categorical features
        platform = features.get('platform', 'X')
        content_type = features.get('content_type', 'text')
        topic = features.get('topic', 'Technology')

        platform_encoded = self._encode_categorical('platform', platform)
        content_type_encoded = self._encode_categorical('content_type', content_type)
        topic_encoded = self._encode_categorical('topic', topic)

        # Derived features
        hashtags_str = features.get('hashtags', '')
        num_hashtags = len([h for h in hashtags_str.split() if h.startswith('#')]) if hashtags_str else features.get('num_hashtags', 2)
        posting_hour = features.get('posting_hour', 12)
        posting_month = features.get('posting_month', 6)

        # Engineered features (must match training pipeline)
        log_views = np.log1p(views)
        log_likes = np.log1p(likes)
        like_share_ratio = likes / (shares + 1)
        comment_rate = comments / (views + 1)

        import pandas as pd
        feature_names = [
            'views', 'likes', 'comments', 'shares',
            'engagement_rate', 'sentiment_score',
            'num_hashtags', 'posting_hour', 'posting_month',
            'platform_encoded', 'content_type_encoded', 'topic_encoded',
            'log_views', 'log_likes', 'like_share_ratio', 'comment_rate'
        ]
        feature_df = pd.DataFrame([[
            views, likes, comments, shares,
            engagement_rate, sentiment_score,
            num_hashtags, posting_hour, posting_month,
            platform_encoded, content_type_encoded, topic_encoded,
            log_views, log_likes, like_share_ratio, comment_rate
        ]], columns=feature_names)

        features_scaled = self.scaler.transform(feature_df)

        probability = float(self.model.predict_proba(features_scaled)[0][1])
        is_viral = bool(self.model.predict(features_scaled)[0])

        return {
            "viral": is_viral,
            "probability": round(probability, 4),
            "score": int(probability * 100),
            "model_type": self.metadata.get("model_type", "Unknown") if self.metadata else "Unknown",
            "model_auc": self.metadata.get("auc_roc", None) if self.metadata else None
        }


# Singleton instance
ml_predictor = ViralPredictor()
