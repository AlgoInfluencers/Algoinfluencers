import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class ViralPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self._train_mock_model()

    def _generate_synthetic_data(self, samples=1000):
        """
        Generates synthetic training data for the viral prediction model.
        Features: followers, engagement_rate, past_interactions, content_sentiment, posting_hour
        """
        np.random.seed(42)
        
        followers = np.random.lognormal(mean=8.0, sigma=1.5, size=samples)
        engagement_rate = np.random.uniform(0.01, 0.20, size=samples)
        past_interactions = np.random.poisson(lam=50, size=samples)
        content_sentiment = np.random.uniform(-1.0, 1.0, size=samples) 
        posting_hour = np.random.randint(0, 24, size=samples)
        
        # Calculate a latent "virality score" to create labels
        # Assuming higher followers, engagement, and positive sentiment increase virality
        # Peak hours (e.g., 9-11 AM, 6-8 PM) also help
        peak_hour_bonus = np.where((posting_hour >= 9) & (posting_hour <= 11) | (posting_hour >= 18) & (posting_hour <= 20), 1.5, 1.0)
        
        latent_score = (
            np.log1p(followers) * 0.3 + 
            (engagement_rate * 100) * 0.4 + 
            np.log1p(past_interactions) * 0.1 + 
            (content_sentiment + 1) * 0.1
        ) * peak_hour_bonus
        
        # Label as viral (1) if in the top 15% of the score
        threshold = np.percentile(latent_score, 85)
        is_viral = (latent_score >= threshold).astype(int)
        
        df = pd.DataFrame({
            'followers': followers,
            'engagement_rate': engagement_rate,
            'past_interactions': past_interactions,
            'content_sentiment': content_sentiment,
            'posting_hour': posting_hour,
            'target': is_viral
        })
        
        return df

    def _train_mock_model(self):
        """
        Trains the RandomForest model on synthetic data.
        """
        df = self._generate_synthetic_data()
        X = df.drop('target', axis=1)
        y = df['target']
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict(self, features):
        """
        Predicts the viral probability of a given post.
        features: dict containing 'followers', 'engagement_rate', 'past_interactions', 'content_sentiment', 'posting_hour'
        """
        if not self.is_trained:
            self._train_mock_model()
            
        # Ensure correct order
        feature_array = np.array([[
            features.get('followers', 1000),
            features.get('engagement_rate', 0.05),
            features.get('past_interactions', 10),
            features.get('content_sentiment', 0.0),
            features.get('posting_hour', 12)
        ]])
        
        features_scaled = self.scaler.transform(feature_array)
        
        probability = self.model.predict_proba(features_scaled)[0][1] # Probability of class 1 (viral)
        is_viral = bool(self.model.predict(features_scaled)[0])
        
        return {
            "viral": is_viral,
            "probability": round(float(probability), 4),
            "score": int(probability * 100)
        }

# Singleton instance
ml_predictor = ViralPredictor()
