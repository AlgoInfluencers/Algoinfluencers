import random
from app.models.graph import network_graph

def independent_cascade(graph, seed_nodes, prob=0.1, steps=10):
    """
    Simulates the Independent Cascade model.
    A node has a single chance to activate its inactive neighbors.
    """
    active_nodes = set(seed_nodes)
    newly_active = set(seed_nodes)
    
    cascade_history = [{"step": 0, "new_activations": list(newly_active), "total_active": len(active_nodes)}]
    
    for step in range(1, steps + 1):
        if not newly_active:
            break
            
        current_step_activations = set()
        
        for node in newly_active:
            neighbors = set(graph.neighbors(node))
            inactive_neighbors = neighbors - active_nodes
            
            for neighbor in inactive_neighbors:
                # Each edge has a probability 'prob' of succeeding in transmission
                # Better realism: Use node's engagement rate as probability modifier
                base_prob = prob
                if 'engagement_rate' in graph.nodes[node]:
                    base_prob = min(0.9, prob + graph.nodes[node]['engagement_rate'] * 0.5)
                
                if random.random() < base_prob:
                    current_step_activations.add(neighbor)
                    
        active_nodes.update(current_step_activations)
        newly_active = current_step_activations
        
        cascade_history.append({
            "step": step, 
            "new_activations": list(newly_active), 
            "total_active": len(active_nodes)
        })
        
    return {
        "model": "Independent Cascade",
        "seed_nodes": seed_nodes,
        "total_activated": len(active_nodes),
        "reach_percentage": round((len(active_nodes) / graph.number_of_nodes()) * 100, 2),
        "history": cascade_history
    }


def linear_threshold(graph, seed_nodes, steps=10):
    """
    Simulates the Linear Threshold model.
    A node becomes active if the sum of weights from its active neighbors exceeds a threshold.
    """
    # Initialize thresholds if not present
    for node in graph.nodes():
        if 'threshold' not in graph.nodes[node]:
            # Random threshold between 0.1 and 0.5 for each user
            graph.nodes[node]['threshold'] = random.uniform(0.1, 0.5)
            
    active_nodes = set(seed_nodes)
    newly_active = set(seed_nodes)
    
    cascade_history = [{"step": 0, "new_activations": list(newly_active), "total_active": len(active_nodes)}]
    
    for step in range(1, steps + 1):
        if not newly_active:
            break
            
        current_step_activations = set()
        
        # Consider all currently inactive nodes that have at least one active neighbor
        inactive_nodes = set(graph.nodes()) - active_nodes
        
        for node in inactive_nodes:
            neighbors = list(graph.neighbors(node))
            if not neighbors:
                continue
                
            active_neighbors = [n for n in neighbors if n in active_nodes]
            if not active_neighbors:
                continue
                
            # In a basic unweighted graph, we can use the fraction of active neighbors
            # or assign random weights to edges that sum to <= 1
            # Here, we use fraction of total degree as weight
            influence_sum = len(active_neighbors) / len(neighbors)
            
            if influence_sum >= graph.nodes[node]['threshold']:
                current_step_activations.add(node)
                
        active_nodes.update(current_step_activations)
        newly_active = current_step_activations
        
        cascade_history.append({
            "step": step, 
            "new_activations": list(newly_active), 
            "total_active": len(active_nodes)
        })
        
    return {
        "model": "Linear Threshold",
        "seed_nodes": seed_nodes,
        "total_activated": len(active_nodes),
        "reach_percentage": round((len(active_nodes) / graph.number_of_nodes()) * 100, 2),
        "history": cascade_history
    }
