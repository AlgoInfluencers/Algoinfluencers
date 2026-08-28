from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.network import router as network_router
from app.api.simulation import router as simulation_router
from app.api.predict import router as predict_router

app = FastAPI(
    title="AlgoInfluencers API",
    description="Backend API for the AlgoInfluencers influence propagation and viral content prediction platform.",
    version="1.0.0"
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(network_router)
app.include_router(simulation_router)
app.include_router(predict_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the AlgoInfluencers API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "algoinfluencers-backend"}
