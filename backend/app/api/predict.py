from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.models.ml_predictor import ml_predictor

router = APIRouter(prefix="/api/predict", tags=["Viral Prediction"])

class PredictionRequest(BaseModel):
    # Core engagement metrics
    views: int = Field(default=100000, description="Number of views/impressions")
    likes: int = Field(default=5000, description="Number of likes")
    comments: int = Field(default=500, description="Number of comments")
    shares: int = Field(default=200, description="Number of shares/retweets")
    engagement_rate: float = Field(default=0.08, description="Engagement rate (0 to 1)")
    sentiment_score: float = Field(default=0.0, description="Sentiment score from -1.0 to 1.0")

    # Post metadata
    platform: str = Field(default="X", description="Platform: 'X', 'Instagram', 'TikTok', 'YouTube Shorts'")
    content_type: str = Field(default="text", description="Content type: 'text', 'image', 'video', 'carousel'")
    topic: str = Field(default="Technology", description="Topic: 'Sports', 'Technology', 'Politics', 'Education', 'Entertainment', 'Lifestyle'")
    hashtags: Optional[str] = Field(default="", description="Hashtags string, e.g. '#tech #ai'")
    posting_hour: int = Field(default=12, description="Hour of the day (0-23)")
    posting_month: int = Field(default=6, description="Month of the year (1-12)")


@router.post("/")
async def predict_virality(req: PredictionRequest):
    """
    Predicts the probability of social media content going viral
    based on engagement metrics, platform, content type, and topic.

    Trained on Kaggle's Social Media Viral Content & Engagement Metrics dataset.
    """
    features = req.model_dump()
    result = ml_predictor.predict(features)

    return {
        "input_features": features,
        "prediction": result
    }
