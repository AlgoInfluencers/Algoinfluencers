from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.models.ml_predictor import ml_predictor

router = APIRouter(prefix="/api/predict", tags=["Viral Prediction"])

class PredictionRequest(BaseModel):
    followers: int = Field(default=5000, description="Number of followers of the author")
    engagement_rate: float = Field(default=0.08, description="Average engagement rate (0 to 1)")
    past_interactions: int = Field(default=120, description="Average interactions on past posts")
    content_sentiment: float = Field(default=0.5, description="Sentiment score from -1.0 (negative) to 1.0 (positive)")
    posting_hour: int = Field(default=19, description="Hour of the day (0-23)")

@router.post("/")
async def predict_virality(req: PredictionRequest):
    """
    Predicts the probability of content going viral based on user characteristics and post metadata.
    """
    features = req.model_dump()
    result = ml_predictor.predict(features)
    
    return {
        "input_features": features,
        "prediction": result
    }
