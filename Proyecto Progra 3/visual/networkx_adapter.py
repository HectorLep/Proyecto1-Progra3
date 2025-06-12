import matplotlib.pyplot as plt
import networkx as nx
from model.graph import Graph

def graph_to_networkx(graph):
    G = nx.DiGraph()
    
    # Agregar nodos con sus tipos
    for vertex in graph.vertices():
        node_id = vertex.element()
        node_type = vertex.type()
        G.add_node(node_id, type=node_type)
    
    # Agregar aristas
    for edge in graph.edges():
        u, v = edge.endpoints()
        weight = edge.element()
        G.add_edge(u.element(), v.element(), weight=weight)
    
    return G

def create_network_visualization(graph, highlighted_route=None):
    G = graph_to_networkx(graph)
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Crear la figura
    plt.figure(figsize=(10, 8))
    
    # Colorear nodos según su tipo
    node_colors = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type')
        if node_type == 'warehouse':
            node_colors.append('#8B4513')  # Brown
        elif node_type == 'recharge':
            node_colors.append('#FFA500')  # Orange
        else:  # client
            node_colors.append('#32CD32')  # Green
    
    # Dibujar los nodos
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)
    
    # Dibujar las aristas (gris por defecto)
    edge_colors = ['#888888' for _ in G.edges()]
    
    # Resaltar la ruta en rojo si se proporciona
    if highlighted_route:
        route_edges = [(highlighted_route[i], highlighted_route[i+1]) for i in range(len(highlighted_route)-1)]
        for i, edge in enumerate(G.edges()):
            if edge in route_edges or (edge[1], edge[0]) in route_edges:
                edge_colors[i] = '#FF0000'  # Rojo para la ruta destacada
    
    # Dibujar aristas con pesos
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=15)
    
    # Dibujar etiquetas de los nodos
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Dibujar etiquetas de las aristas (pesos)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Agregar título y leyenda
    plt.title("Drone Delivery Network\nWarehouse (Brown) | Recharge (Orange) | Client (Green)")
    plt.axis('off')  # Ocultar ejes
    
    # Crear leyenda personalizada
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Warehouse', markerfacecolor='#8B4513', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Recharge', markerfacecolor='#FFA500', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Client', markerfacecolor='#32CD32', markersize=10),
        Line2D([0], [0], color='#888888', label='Regular Edge'),
        Line2D([0], [0], color='#FF0000', label='Highlighted Route') if highlighted_route else None
    ]
    legend_elements = [elem for elem in legend_elements if elem is not None]
    plt.legend(handles=legend_elements, loc='upper right')
    
    return plt.gcf()

def show_network_visualization():
    plt.show()
