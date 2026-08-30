import networkx as nx
import random
from pathlib import Path

class SocialNetworkGraph:
    def __init__(self, edge_list_path=None):
        """
        Load a directed social network from a space-separated edge list.
        """
        if edge_list_path is None:
            project_root = Path(__file__).resolve().parents[3]
            edge_list_path = project_root / "dataset" / "edges.txt"

        self.edge_list_path = Path(edge_list_path)
        if not self.edge_list_path.is_file():
            raise FileNotFoundError(f"Network edge list not found: {self.edge_list_path}")

        project_root = Path(__file__).resolve().parents[3]
        if self.edge_list_path.is_relative_to(project_root):
            self.source_label = str(self.edge_list_path.relative_to(project_root))
        else:
            self.source_label = self.edge_list_path.name

        self.G = nx.read_edgelist(
            self.edge_list_path,
            nodetype=int,
            create_using=nx.DiGraph,
        )
        self.num_nodes = self.G.number_of_nodes()

        # Add attributes to nodes for the dashboard and influencer ranking.
        self._populate_node_attributes()

    def _populate_node_attributes(self):
        """
        Add synthetic attributes to each user (node).
        """
        for i in self.G.nodes():
            degree = self.G.degree(i)
            # Followers correlate with degree but with some noise
            followers = int(degree * random.uniform(50, 200)) + random.randint(10, 100)
            
            # Engagement rate (e.g., 0.01 to 0.15), slightly negatively correlated with massive follower counts for realism
            engagement_rate = max(0.01, random.uniform(0.05, 0.15) - (degree * 0.0001))
            
            self.G.nodes[i]['id'] = i
            self.G.nodes[i]['username'] = f"user_{i}"
            self.G.nodes[i]['followers'] = followers
            self.G.nodes[i]['engagement_rate'] = round(engagement_rate, 4)

    def calculate_influence_metrics(self):
        """
        Calculate various centrality metrics to identify influential users.
        """
        # PageRank is great for social networks
        pagerank = nx.pagerank(self.G, alpha=0.85)
        
        # Degree Centrality
        degree_cen = nx.degree_centrality(self.G)
        
        # Betweenness Centrality (bridges between clusters)
        betweenness_cen = nx.betweenness_centrality(self.G, k=min(100, self.num_nodes)) # approximation for speed
        
        for i in self.G.nodes():
            self.G.nodes[i]['pagerank'] = pagerank[i]
            self.G.nodes[i]['degree_centrality'] = degree_cen[i]
            self.G.nodes[i]['betweenness'] = betweenness_cen[i]
            
            # Create a composite influence score
            # Normalize followers to 0-1 proxy roughly
            norm_followers = min(1.0, self.G.nodes[i]['followers'] / 10000.0)
            
            # High influence = High PageRank + High Engagement + Many Followers
            score = (pagerank[i] * 100) * 0.4 + (self.G.nodes[i]['engagement_rate'] * 0.3) + (norm_followers * 0.3)
            self.G.nodes[i]['influence_score'] = round(score, 4)

    def get_graph_data(self):
        """
        Export graph data for frontend visualization (e.g., react-force-graph).
        Returns a dict with 'nodes' and 'links'.
        """
        nodes = []
        for i, data in self.G.nodes(data=True):
            nodes.append(data)
            
        links = []
        for u, v in self.G.edges():
            links.append({"source": u, "target": v})
            
        return {"nodes": nodes, "links": links}

    def get_top_influencers(self, limit=10):
        """
        Returns the top influential users based on the calculated influence score.
        """
        nodes_data = [data for _, data in self.G.nodes(data=True)]
        if 'influence_score' not in nodes_data[0]:
            self.calculate_influence_metrics()
            nodes_data = [data for _, data in self.G.nodes(data=True)]
            
        sorted_influencers = sorted(nodes_data, key=lambda x: x.get('influence_score', 0), reverse=True)
        return sorted_influencers[:limit]

# Singleton instance for the API to use
network_graph = SocialNetworkGraph()
network_graph.calculate_influence_metrics()
