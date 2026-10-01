"""
Generate a synthetic social network edge list.

Creates a reproducible directed social network with:
- 500 users
- 2500 connections
- Community structure
- Every user has at least one outgoing connection

Output:
dataset/edges_large.txt
"""

import networkx as nx
import random
from pathlib import Path


def generate_social_network(
    num_nodes=500,
    num_edges=2500,
    num_communities=8,
    seed=42
):
    random.seed(seed)

    # --------------------------------------------------
    # 1. Create community-based social network
    # --------------------------------------------------

    base_size = num_nodes // num_communities
    sizes = [base_size] * num_communities

    # Distribute remaining nodes
    for i in range(num_nodes - sum(sizes)):
        sizes[i] += 1

    probabilities = []

    for i in range(num_communities):
        row = []

        for j in range(num_communities):

            if i == j:
                # Higher probability inside a community
                row.append(0.04)
            else:
                # Lower probability between communities
                row.append(0.004)

        probabilities.append(row)

    G = nx.stochastic_block_model(
        sizes,
        probabilities,
        seed=seed,
        directed=True
    )

    # --------------------------------------------------
    # 2. Ensure every node exists and has an edge
    # --------------------------------------------------

    for node in range(num_nodes):

        if G.out_degree(node) == 0:

            target = random.choice(
                [n for n in range(num_nodes) if n != node]
            )

            G.add_edge(node, target)

    # --------------------------------------------------
    # 3. Add edges until we reach desired number
    # --------------------------------------------------

    while G.number_of_edges() < num_edges:

        source = random.randint(0, num_nodes - 1)
        target = random.randint(0, num_nodes - 1)

        # No self-loop
        if source == target:
            continue

        # No duplicate edge
        if G.has_edge(source, target):
            continue

        G.add_edge(source, target)

    # --------------------------------------------------
    # 4. Remove excess edges if necessary
    #    while keeping at least one outgoing edge
    #    for every node
    # --------------------------------------------------

    while G.number_of_edges() > num_edges:

        source, target = random.choice(list(G.edges()))

        # Only remove if source has another
        # outgoing connection
        if G.out_degree(source) > 1:
            G.remove_edge(source, target)

    return G


def save_edge_list(G):

    # generate_graph_dataset.py is inside backend/app
    project_root = Path(__file__).resolve().parents[3]

    dataset_dir = project_root / "dataset"
    dataset_dir.mkdir(exist_ok=True)

    output_path = dataset_dir / "edges_large.txt"

    with open(output_path, "w") as f:
        for source, target in G.edges():
            f.write(f"{source} {target}\n")

    return output_path


if __name__ == "__main__":

    print("Generating social network...")

    G = generate_social_network(
        num_nodes=500,
        num_edges=2500,
        num_communities=8,
        seed=42
    )

    output_path = save_edge_list(G)

    print("\nDataset generated successfully!")

    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    print("Number of communities: 8")

    print("\nSaved to:")
    print(output_path)