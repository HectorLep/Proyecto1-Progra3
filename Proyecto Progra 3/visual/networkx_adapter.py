# visual/networkx_adapter.py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px

class NetworkXAdapter:
    def __init__(self, custom_graph):
        self.custom_graph = custom_graph
        self.nx_graph = None
        self._convert_to_networkx()
    
    def _convert_to_networkx(self):
        """Convert custom graph to NetworkX format."""
        self.nx_graph = nx.DiGraph() if self.custom_graph.is_directed() else nx.Graph()
        
        # Add nodes with attributes
        for vertex in self.custom_graph.vertices():
            node_id = vertex.element()
            node_type = vertex.type()
            self.nx_graph.add_node(node_id, type=node_type, vertex_obj=vertex)
        
        # Add edges with weights
        for edge in self.custom_graph.edges():
            u, v = edge.endpoints()
            weight = edge.element()
            self.nx_graph.add_edge(u.element(), v.element(), weight=weight, edge_obj=edge)
    
    def get_networkx_graph(self):
        """Return the NetworkX graph."""
        return self.nx_graph
    
    def calculate_network_metrics(self):
        """Calculate various network metrics."""
        metrics = {}
        
        # Basic metrics
        metrics['num_nodes'] = self.nx_graph.number_of_nodes()
        metrics['num_edges'] = self.nx_graph.number_of_edges()
        metrics['density'] = nx.density(self.nx_graph)
        
        # Connectivity
        if self.nx_graph.is_directed():
            metrics['is_strongly_connected'] = nx.is_strongly_connected(self.nx_graph)
            metrics['is_weakly_connected'] = nx.is_weakly_connected(self.nx_graph)
        else:
            metrics['is_connected'] = nx.is_connected(self.nx_graph)
        
        # Centrality measures (for undirected version)
        undirected = self.nx_graph.to_undirected()
        metrics['degree_centrality'] = nx.degree_centrality(undirected)
        metrics['betweenness_centrality'] = nx.betweenness_centrality(undirected)
        metrics['closeness_centrality'] = nx.closeness_centrality(undirected)
        
        # Path metrics
        if nx.is_connected(undirected):
            metrics['average_shortest_path_length'] = nx.average_shortest_path_length(undirected)
            metrics['diameter'] = nx.diameter(undirected)
        
        return metrics
    
    def find_shortest_paths(self, source, target):
        """Find shortest paths between nodes."""
        try:
            # Simple shortest path
            shortest_path = nx.shortest_path(self.nx_graph, source, target, weight='weight')
            shortest_length = nx.shortest_path_length(self.nx_graph, source, target, weight='weight')
            
            # All shortest paths
            all_paths = list(nx.all_shortest_paths(self.nx_graph, source, target, weight='weight'))
            
            return {
                'shortest_path': shortest_path,
                'shortest_length': shortest_length,
                'all_shortest_paths': all_paths,
                'path_count': len(all_paths)
            }
        except nx.NetworkXNoPath:
            return None
    
    def analyze_node_importance(self):
        """Analyze node importance based on various metrics."""
        undirected = self.nx_graph.to_undirected()
        
        # Get centrality measures
        degree_cent = nx.degree_centrality(undirected)
        betweenness_cent = nx.betweenness_centrality(undirected)
        closeness_cent = nx.closeness_centrality(undirected)
        
        # Combine metrics for overall importance
        importance_scores = {}
        for node in self.nx_graph.nodes():
            # Weighted combination of centrality measures
            importance = (
                0.4 * degree_cent.get(node, 0) +
                0.4 * betweenness_cent.get(node, 0) +
                0.2 * closeness_cent.get(node, 0)
            )
            importance_scores[node] = importance
        
        # Sort by importance
        sorted_importance = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'importance_scores': importance_scores,
            'ranked_nodes': sorted_importance,
            'degree_centrality': degree_cent,
            'betweenness_centrality': betweenness_cent,
            'closeness_centrality': closeness_cent
        }
    
    def create_matplotlib_visualization(self, layout='spring', highlight_path=None, 
                                      highlight_nodes=None, figsize=(12, 8)):
        """Create matplotlib visualization with customization options."""
        fig, ax = plt.subplots(figsize=figsize)
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.nx_graph, k=3, iterations=50, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(self.nx_graph)
        elif layout == 'random':
            pos = nx.random_layout(self.nx_graph, seed=42)
        else:
            pos = nx.spring_layout(self.nx_graph)
        
        # Node colors and sizes by type
        node_colors = []
        node_sizes = []
        for node in self.nx_graph.nodes():
            node_type = self.nx_graph.nodes[node].get('type', 'client')
            
            if node in (highlight_nodes or []):
                # Highlighted nodes
                node_colors.append('#FF0000')
                node_sizes.append(1000)
            elif node_type == 'warehouse':
                node_colors.append('#8B4513')
                node_sizes.append(800)
            elif node_type == 'recharge':
                node_colors.append('#FFA500')
                node_sizes.append(600)
            else:  # client
                node_colors.append('#32CD32')
                node_sizes.append(400)
        
        # Draw edges
        nx.draw_networkx_edges(self.nx_graph, pos, edge_color='lightgray', 
                              arrows=True, arrowsize=15, width=1, ax=ax, alpha=0.6)
        
        # Highlight specific path
        if highlight_path and len(highlight_path) > 1:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                         for i in range(len(highlight_path)-1)]
            valid_edges = [(u, v) for u, v in path_edges if self.nx_graph.has_edge(u, v)]
            
            if valid_edges:
                nx.draw_networkx_edges(self.nx_graph, pos, edgelist=valid_edges,