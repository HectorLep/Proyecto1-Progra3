import matplotlib.pyplot as plt
import networkx as nx
from model.graph import Graph

def graph_to_networkx(graph):
    """Convert custom Graph to NetworkX DiGraph"""
    G = nx.DiGraph()
    
    # Add nodes with their types
    for vertex in graph.vertices():
        node_id = vertex.element()
        node_type = vertex.type()
        G.add_node(node_id, type=node_type)
    
    # Add edges
    for edge in graph.edges():
        u, v = edge.endpoints()
        weight = edge.element()
        G.add_edge(u.element(), v.element(), weight=weight)
    
    return G

def create_network_visualization(graph, highlighted_route=None, figsize=(12, 10)):
    """Create a comprehensive network visualization with enhanced features"""
    G = graph_to_networkx(graph)
    
    # Use different layout algorithms based on graph size
    num_nodes = len(G.nodes())
    if num_nodes < 20:
        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    elif num_nodes < 50:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)
    
    # Create the figure with larger size
    plt.figure(figsize=figsize)
    
    # Color nodes according to their type with enhanced colors
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'client')
        if node_type == 'warehouse':
            node_colors.append('#8B4513')  # Brown
            node_sizes.append(800)  # Larger for warehouses
        elif node_type == 'recharge':
            node_colors.append('#FFA500')  # Orange
            node_sizes.append(600)  # Medium for recharge stations
        else:  # client
            node_colors.append('#32CD32')  # Green
            node_sizes.append(400)  # Smaller for clients
    
    # Draw the nodes with enhanced styling
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors, 
                          node_size=node_sizes,
                          alpha=0.8,
                          edgecolors='black',
                          linewidths=1.5)
    
    # Prepare edge colors and widths
    edge_colors = []
    edge_widths = []
    
    for edge in G.edges():
        edge_colors.append('#888888')  # Default gray
        edge_widths.append(1.0)  # Default width
    
    # Highlight the route in red if provided
    if highlighted_route:
        route_edges = [(highlighted_route[i], highlighted_route[i+1]) 
                      for i in range(len(highlighted_route)-1)]
        
        for i, edge in enumerate(G.edges()):
            if edge in route_edges or (edge[1], edge[0]) in route_edges:
                edge_colors[i] = '#FF0000'  # Red for highlighted route
                edge_widths[i] = 3.0  # Thicker for highlighted route
    
    # Draw edges with enhanced styling
    nx.draw_networkx_edges(G, pos, 
                          edge_color=edge_colors, 
                          width=edge_widths,
                          arrows=True, 
                          arrowsize=20,
                          arrowstyle='->', 
                          alpha=0.7,
                          connectionstyle="arc3,rad=0.1")
    
    # Draw node labels with better formatting
    nx.draw_networkx_labels(G, pos, 
                           font_size=9, 
                           font_weight='bold',
                           font_color='white',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='black', 
                                   alpha=0.7))
    
    # Draw edge labels (weights) with improved positioning
    edge_labels = nx.get_edge_attributes(G, 'weight')
    # Format edge labels to show only 2 decimal places
    formatted_edge_labels = {k: f"{v:.1f}" for k, v in edge_labels.items()}
    
    nx.draw_networkx_edge_labels(G, pos, 
                                edge_labels=formatted_edge_labels, 
                                font_size=7,
                                font_color='darkblue',
                                bbox=dict(boxstyle="round,pad=0.2", 
                                        facecolor='white', 
                                        alpha=0.8))
    
    # Enhanced title
    title = "Drone Delivery Network"
    if highlighted_route:
        title += f" - Route: {' → '.join(highlighted_route)}"
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Remove axes
    plt.axis('off')
    
    # Create enhanced legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Warehouse', 
               markerfacecolor='#8B4513', markersize=12, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Recharge Station', 
               markerfacecolor='#FFA500', markersize=10, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Client', 
               markerfacecolor='#32CD32', markersize=8, markeredgecolor='black'),
        Line2D([0], [0], color='#888888', label='Regular Route', linewidth=2),
    ]
    
    if highlighted_route:
        legend_elements.append(
            Line2D([0], [0], color='#FF0000', label='Highlighted Route', linewidth=3)
        )
    
    plt.legend(handles=legend_elements, 
              loc='upper left', 
              bbox_to_anchor=(0.02, 0.98),
              fontsize=10,
              frameon=True,
              fancybox=True,
              shadow=True)
    
    # Add network statistics as text
    stats_text = f"Nodes: {len(G.nodes())} | Edges: {len(G.edges())}"
    if highlighted_route:
        route_cost = sum(G[highlighted_route[i]][highlighted_route[i+1]]['weight'] 
                        for i in range(len(highlighted_route)-1))
        stats_text += f" | Route Cost: {route_cost:.2f}"
    
    plt.figtext(0.02, 0.02, stats_text, fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return plt.gcf()

def create_route_comparison_visualization(graph, routes_list, route_labels=None):
    """Create a visualization comparing multiple routes"""
    G = graph_to_networkx(graph)
    pos = nx.spring_layout(G, k=1.0, iterations=100, seed=42)
    
    # Create subplots for each route
    num_routes = len(routes_list)
    fig, axes = plt.subplots(1, num_routes, figsize=(6*num_routes, 6))
    
    if num_routes == 1:
        axes = [axes]
    
    colors = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFFF00']
    
    for idx, (route, ax) in enumerate(zip(routes_list, axes)):
        # Color nodes according to their type
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type', 'client')
            if node_type == 'warehouse':
                node_colors.append('#8B4513')
                node_sizes.append(600)
            elif node_type == 'recharge':
                node_colors.append('#FFA500')
                node_sizes.append(450)
            else:
                node_colors.append('#32CD32')
                node_sizes.append(300)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors, 
                              node_size=node_sizes,
                              alpha=0.8,
                              ax=ax)
        
        # Draw all edges in gray
        nx.draw_networkx_edges(G, pos, 
                              edge_color='#CCCCCC', 
                              arrows=True, 
                              arrowsize=15,
                              alpha=0.5,
                              ax=ax)
        
        # Highlight current route
        if route:
            route_edges = [(route[i], route[i+1]) for i in range(len(route)-1)]
            nx.draw_networkx_edges(G, pos,
                                  edgelist=route_edges,
                                  edge_color=colors[idx % len(colors)],
                                  width=3.0,
                                  arrows=True,
                                  arrowsize=20,
                                  ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
        
        # Set title
        title = route_labels[idx] if route_labels else f"Route {idx+1}"
        if route:
            route_cost = sum(G[route[i]][route[i+1]]['weight'] 
                           for i in range(len(route)-1))
            title += f" (Cost: {route_cost:.2f})"
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    return fig

def analyze_network_properties(graph):
    """Analyze and return network properties"""
    G = graph_to_networkx(graph)
    
    properties = {
        'num_nodes': len(G.nodes()),
        'num_edges': len(G.edges()),
        'density': nx.density(G),
        'is_connected': nx.is_weakly_connected(G),
        'num_components': nx.number_weakly_connected_components(G),
        'average_degree': sum(dict(G.degree()).values()) / len(G.nodes()) if len(G.nodes()) > 0 else 0,
        'clustering_coefficient': nx.average_clustering(G.to_undirected()),
        'diameter': nx.diameter(G.to_undirected()) if nx.is_connected(G.to_undirected()) else 'N/A (disconnected)',
        'node_types': {
            'warehouse': len([n for n, d in G.nodes(data=True) if d.get('type') == 'warehouse']),
            'recharge': len([n for n, d in G.nodes(data=True) if d.get('type') == 'recharge']),
            'client': len([n for n, d in G.nodes(data=True) if d.get('type') == 'client'])
        }
    }
    
    return properties

def create_network_analysis_report(graph):
    """Generate a comprehensive network analysis report"""
    properties = analyze_network_properties(graph)
    
    report = f"""
    📊 NETWORK ANALYSIS REPORT
    ========================
    
    🔢 Basic Statistics:
    - Total Nodes: {properties['num_nodes']}
    - Total Edges: {properties['num_edges']}
    - Graph Density: {properties['density']:.3f}
    - Average Degree: {properties['average_degree']:.2f}
    
    🔗 Connectivity:
    - Is Connected: {properties['is_connected']}
    - Number of Components: {properties['num_components']}
    - Clustering Coefficient: {properties['clustering_coefficient']:.3f}
    - Diameter: {properties['diameter']}
    
    🏢 Node Distribution:
    - Warehouse Nodes: {properties['node_types']['warehouse']}
    - Recharge Stations: {properties['node_types']['recharge']}
    - Client Nodes: {properties['node_types']['client']}
    
    📈 Ratios:
    - Warehouses: {properties['node_types']['warehouse']/properties['num_nodes']*100:.1f}%
    - Recharge Stations: {properties['node_types']['recharge']/properties['num_nodes']*100:.1f}%
    - Clients: {properties['node_types']['client']/properties['num_nodes']*100:.1f}%
    """
    
    return report

def get_shortest_paths_analysis(graph, source_nodes=None):
    """Analyze shortest paths from source nodes to all other nodes"""
    G = graph_to_networkx(graph)
    
    if source_nodes is None:
        # Use all warehouse nodes as sources
        source_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'warehouse']
    
    analysis = {}
    
    for source in source_nodes:
        try:
            # Calculate shortest paths from source to all other nodes
            lengths = nx.single_source_dijkstra_path_length(G, source, weight='weight')
            paths = nx.single_source_dijkstra_path(G, source, weight='weight')
            
            analysis[source] = {
                'reachable_nodes': len(lengths),
                'total_nodes': len(G.nodes()),
                'avg_path_length': sum(lengths.values()) / len(lengths) if lengths else 0,
                'max_path_length': max(lengths.values()) if lengths else 0,
                'paths_to_clients': {node: {'length': length, 'path': paths[node]} 
                                   for node, length in lengths.items() 
                                   if G.nodes[node].get('type') == 'client'}
            }
        except nx.NetworkXNoPath:
            analysis[source] = {
                'reachable_nodes': 0,
                'total_nodes': len(G.nodes()),
                'avg_path_length': float('inf'),
                'max_path_length': float('inf'),
                'paths_to_clients': {}
            }
    
    return analysis

def create_degree_distribution_plot(graph):
    """Create a degree distribution plot"""
    G = graph_to_networkx(graph)
    
    # Calculate degree distribution
    degrees = [G.degree(n) for n in G.nodes()]
    
    plt.figure(figsize=(10, 6))
    plt.hist(degrees, bins=max(1, len(set(degrees))), color='#45b7d1', alpha=0.7, edgecolor='black')
    plt.title('Node Degree Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Degree', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    avg_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0
    min_degree = min(degrees) if degrees else 0
    
    stats_text = f'Avg: {avg_degree:.2f}, Max: {max_degree}, Min: {min_degree}'
    plt.text(0.7, 0.9, stats_text, transform=plt.gca().transAxes, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return plt.gcf()

def create_node_type_distribution_plot(graph):
    """Create a plot showing the distribution of node types"""
    G = graph_to_networkx(graph)
    
    # Count node types
    type_counts = {'warehouse': 0, 'recharge': 0, 'client': 0}
    for node, data in G.nodes(data=True):
        node_type = data.get('type', 'client')
        type_counts[node_type] += 1
    
    # Create pie chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Pie chart
    colors = ['#8B4513', '#FFA500', '#32CD32']
    labels = ['Warehouse', 'Recharge', 'Client']
    sizes = [type_counts['warehouse'], type_counts['recharge'], type_counts['client']]
    
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Node Type Distribution', fontsize=14, fontweight='bold')
    
    # Bar chart
    ax2.bar(labels, sizes, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_title('Node Type Counts', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Count')
    
    # Add value labels on bars
    for i, v in enumerate(sizes):
        ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig