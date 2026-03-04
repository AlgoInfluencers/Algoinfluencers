from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.graph import network_graph
from app.models.diffusion import independent_cascade, linear_threshold

router = APIRouter(prefix="/api/simulation", tags=["Influence Simulation"])

class SimulationRequest(BaseModel):
    model_type: str  # "ic" or "lt"
    seed_nodes: List[int]
    probability: Optional[float] = 0.1
    steps: Optional[int] = 10

@router.post("/run")
async def run_simulation(req: SimulationRequest):
    """
    Run an influence diffusion simulation using either Independent Cascade (ic) or Linear Threshold (lt).
    """
    # Verify nodes exist
    for node in req.seed_nodes:
        if node not in network_graph.G:
            raise HTTPException(status_code=400, detail=f"Node {node} does not exist in graph")
            
    if req.model_type.lower() == "ic":
        result = independent_cascade(
            network_graph.G, 
            req.seed_nodes, 
            prob=req.probability, 
            steps=req.steps
        )
        return result
    
    elif req.model_type.lower() == "lt":
        result = linear_threshold(
            network_graph.G, 
            req.seed_nodes, 
            steps=req.steps
        )
        return result
        
    else:
        raise HTTPException(status_code=400, detail="Invalid model_type. Use 'ic' or 'lt'.")
