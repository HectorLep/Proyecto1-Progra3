import streamlit as st
from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import avl_insert
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator

def run_simulation(num_nodes, num_edges, num_orders):
    # Crear un grafo aleatorio
    g = Graph(directed=True)
    g.generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    
    #gestores y simuladores
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    simulator.process_orders(num_orders)
    
    route_patterns = optimizer.analyze_route_patterns()
    optimization_reports = optimizer.get_optimization_report()
    
    return g, route_patterns, optimization_reports

def graph_to_dot(graph):
    dot_str = "digraph G {\n"
    for vertex_id, vertex in graph.vertices.items():
        dot_str += f'    "{vertex_id}" [label="{vertex.name}"];\n'
    for edge in graph.edges:
        dot_str += f'    "{edge.start_node.id}" -> "{edge.end_node.id}" [label="{edge.weight}"];\n'
    dot_str += "}"
    return dot_str

# Streamlit Interface
st.title("Simulador de Logística de Órdenes")
st.write("Esta aplicación simula el procesamiento de órdenes y optimiza las rutas de entrega.")

# User inputs
num_nodes = st.slider("Número de Nodos", min_value=10, max_value=200, value=150)
num_edges = st.slider("Número de Aristas", min_value=10, max_value=400, value=300)
num_orders = st.slider("Número de Órdenes", min_value=10, max_value=1000, value=500)

if st.button("Ejecutar Simulación"):
    graph, route_patterns, optimization_reports = run_simulation(num_nodes, num_edges, num_orders)
    
    st.write("=== Visualización del Grafo ===")
    graph_dot = graph_to_dot(graph)
    st.graphviz_chart(graph_dot)
    
    st.write("=== Patrones de Ruta ===")
    for pattern in route_patterns:
        st.write(pattern)
        
    st.write("=== Reportes de Optimización ===")
    for report in optimization_reports:
        st.write(report)

# To run this application:
# 1. Open your terminal or command prompt.
# 2. Navigate to the 'Proyecto Progra 3' directory.
# 3. Run the command: streamlit run app.py
