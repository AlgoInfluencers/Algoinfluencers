from fastapi import APIRouter
from app.models.graph import network_graph

router = APIRouter(prefix="/api/network", tags=["Network Graph"])

@router.get("/")
async def get_network():
    """
    Returns the full social network graph (nodes and links) for visualization.
    """
    return network_graph.get_graph_data()

@router.get("/influencers")
async def get_top_influencers(limit: int = 10):
    """
    Returns the top influential users in the network based on PageRank and Engagement.
    """
    return network_graph.get_top_influencers(limit=limit)

@router.get("/stats")
async def get_network_stats():
    """
    Returns high-level statistics about the social network graph.
    """
    nodes = network_graph.num_nodes
    edges = network_graph.G.number_of_edges()
    return {
        "total_nodes": nodes,
        "total_edges": edges,
        "density": edges / (nodes * (nodes - 1) / 2) if nodes > 1 else 0
    }
