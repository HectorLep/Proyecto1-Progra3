# prueba.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx
from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import avl_insert
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator
import random
import time
from validaciones.validaciones import *
from visual.networkx_adapter import create_network_visualization  # New import

# Configuración de la página
st.set_page_config(
    page_title="🚁 Drone Logistics Simulator - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
    .route-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Función principal de simulación
@st.cache_data
def run_simulation(num_nodes, num_edges, num_orders):
    # Crear un grafo aleatorio
    g = Graph(directed=True)
    g.generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    
    # Gestores y simuladores
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    # Capturar la salida de la simulación
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    simulator.process_orders(num_orders)
    
    sys.stdout = old_stdout
    simulation_output = captured_output.getvalue()
    
    # Obtener estadísticas
    route_patterns = optimizer.analyze_route_patterns()
    optimization_reports = optimizer.get_optimization_report()
    
    # Estadísticas del grafo
    node_stats = {
        'warehouse': len([v for v in g.vertices() if v.type() == 'warehouse']),
        'recharge': len([v for v in g.vertices() if v.type() == 'recharge']),
        'client': len([v for v in g.vertices() if v.type() == 'client'])
    }
    
    return g, route_patterns, optimization_reports, simulation_output, tracker, node_stats

# Título principal
st.markdown("""
<div class="main-header">
    <h1>🚁 Drone Logistics Simulator - Correos Chile</h1>
    <p>Advanced Route Optimization and Network Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Initialize Simulation")
    
    st.subheader("Node Role Proportions")
    warehouse_pct = st.slider("📦 Storage Nodes", 10, 40, 20, help="Percentage of warehouse nodes")
    recharge_pct = st.slider("🔋 Recharge Nodes", 10, 40, 20, help="Percentage of recharge stations")
    client_pct = 100 - warehouse_pct - recharge_pct
    st.info(f"👥 Client Nodes: {client_pct}%")
    
    st.subheader("Network Parameters")
    num_nodes = st.slider("Number of Nodes", 10, 150, 15, step=5)
    num_edges = st.slider("Number of Edges", 10, 300, 28, step=2)
    num_orders = st.slider("Number of Orders", 10, 500, 10, step=5)
    
    st.subheader("Derived Client Nodes")
    derived_clients = int(num_nodes * 0.6)
    st.metric("Estimated Client Nodes", f"{derived_clients} (60% of {num_nodes})")
    
    run_button = st.button("🚀 Start Simulation", type="primary", use_container_width=True)

# Contenido principal
if run_button:
    with st.spinner("Initializing simulation..."):
        # Ejecutar simulación
        graph, route_patterns, optimization_reports, simulation_output, tracker, node_stats = run_simulation(
            num_nodes, num_edges, num_orders
        )
    
    # Crear pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Run Simulation", 
        "🌐 Explore Network", 
        "👥 Clients & Orders", 
        "📊 Route Analytics", 
        "📈 Statistics"
    ])
    
    with tab1:
        st.header("📊 Simulation Results")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodes", num_nodes, delta=None)
        with col2:
            st.metric("Total Edges", num_edges, delta=None)
        with col3:
            st.metric("Orders Processed", num_orders, delta=None)
        with col4:
            successful_orders = simulation_output.count("Estado: Entregado")
            st.metric("Successful Deliveries", successful_orders, 
                     delta=f"{(successful_orders/num_orders)*100:.1f}%" if num_orders > 0 else "0%")
        
        # Distribución de nodos
        st.subheader("📊 Node Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pastel
            fig_pie = px.pie(
                values=list(node_stats.values()),
                names=['Warehouse', 'Recharge', 'Client'],
                title="Node Type Distribution",
                color_discrete_sequence=['#8B4513', '#FFA500', '#32CD32']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras
            fig_bar = px.bar(
                x=['Warehouse', 'Recharge', 'Client'],
                y=list(node_stats.values()),
                title="Node Count by Type",
                color=['Warehouse', 'Recharge', 'Client'],
                color_discrete_sequence=['#8B4513', '#FFA500', '#32CD32']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.header("🌐 Network Visualization")
        
        # Create and show Matplotlib visualization
        fig = create_network_visualization(graph)
        st.pyplot(fig)
        
        # Panel de cálculo de rutas
        st.subheader("🧭 Calculate Route")
        col1, col2, col3 = st.columns(3)
        
        # Obtener nodos disponibles
        all_nodes = [v.element() for v in graph.vertices()]
        warehouses = [v.element() for v in graph.vertices() if v.type() == 'warehouse']
        clients = [v.element() for v in graph.vertices() if v.type() == 'client']
        
        with col1:
            origin_node = st.selectbox("Origin Node", options=warehouses, key="origin")
        with col2:
            dest_node = st.selectbox("Destination Node", options=clients, key="dest")
        with col3:
            if st.button("🔍 Calculate Route", type="secondary"):
                if origin_node and dest_node:
                    manager = RouteManager(graph)
                    es_valido, mensaje_error = validar_calculo_ruta(graph, origin_node, dest_node)
                    if not es_valido:
                        st.error(mensaje_error)
                        st.stop()
                    route = manager.find_route_with_recharge(origin_node, dest_node)
                    if route:
                        st.success(f"Route found: {' → '.join(route.path)}")
                        st.info(f"Total cost: {route.total_cost}")
                        if route.recharge_stops:
                            st.warning(f"Recharge stops: {', '.join(route.recharge_stops)}")
                        # Redraw the graph with the highlighted route
                        fig = create_network_visualization(graph, highlighted_route=route.path)
                        st.pyplot(fig)
                    else:
                        st.error("No valid route found!")
    
    with tab3:
        st.header("👥 Clients & Orders")
        
        # Estadísticas de clientes
        client_stats = tracker.get_client_stats()
        if client_stats:
            st.subheader("📊 Top Clients by Orders")
            client_df = pd.DataFrame(client_stats, columns=['Client ID', 'Total Orders'])
            st.dataframe(client_df.head(10), use_container_width=True)
            
            # Gráfico de clientes
            fig_clients = px.bar(
                client_df.head(10),
                x='Client ID',
                y='Total Orders',
                title='Top 10 Clients by Order Volume'
            )
            st.plotly_chart(fig_clients, use_container_width=True)
        
        # Estadísticas de órdenes
        order_stats = tracker.get_order_stats()
        if order_stats:
            st.subheader("💰 Orders by Cost")
            order_data = [(oid, order.total_cost, order.status) for oid, order in order_stats[:10]]
            order_df = pd.DataFrame(order_data, columns=['Order ID', 'Total Cost', 'Status'])
            st.dataframe(order_df, use_container_width=True)
    
    with tab4:
        st.header("📊 Route Analytics")
        
        # Mostrar patrones de rutas
        st.subheader("🛣️ Route Frequency & History")
        
        # Rutas más frecuentes
        frequent_routes = tracker.get_most_frequent_routes(10)
        if frequent_routes:
            st.subheader("🔥 Most Frequent Routes")
            for i, (route, freq) in enumerate(frequent_routes, 1):
                st.markdown(f"""
                <div class="route-card">
                    <strong>{i}. Route hash:</strong> {route} | <span style="color: #007bff;">Frequency: {freq}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Estadísticas de nodos visitados
        node_visits = tracker.get_node_visit_stats()
        if node_visits:
            st.subheader("📍 Most Visited Nodes")
            visit_df = pd.DataFrame(node_visits[:10], columns=['Node', 'Visits'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(visit_df, use_container_width=True)
            with col2:
                fig_visits = px.bar(
                    visit_df,
                    x='Node',
                    y='Visits',
                    title='Node Visit Frequency'
                )
                st.plotly_chart(fig_visits, use_container_width=True)
    
    with tab5:
        st.header("📈 Statistics")
        
        # Métricas avanzadas
        col1, col2, col3 = st.columns(3)
        
        total_edges = len(list(graph.edges()))
        total_vertices = len(list(graph.vertices()))
        
        with col1:
            st.metric("Graph Density", f"{(total_edges / (total_vertices * (total_vertices - 1))):.3f}")
        with col2:
            avg_degree = (2 * total_edges) / total_vertices if total_vertices > 0 else 0
            st.metric("Average Degree", f"{avg_degree:.2f}")
        with col3:
            connectivity = "Connected" if graph.is_connected() else "Disconnected"
            st.metric("Graph Connectivity", connectivity)
        
        # Análisis detallado
        st.subheader("📋 Detailed Analysis")
        
        if route_patterns:
            with st.expander("🔍 Route Pattern Analysis", expanded=True):
                for pattern in route_patterns:
                    st.text(pattern)
        
        # Log de simulación
        with st.expander("📜 Simulation Log"):
            st.text_area("Simulation Output", simulation_output, height=300)
        
        # Reportes de optimización
        if optimization_reports:
            with st.expander("⚡ Optimization Reports"):
                for report in optimization_reports:
                    st.text(report)

else:
    # Pantalla inicial
    st.info("👈 Configure the simulation parameters in the sidebar and click 'Start Simulation' to begin!")
    
    # Información del sistema
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 📦 Storage Nodes
        - Warehouse facilities
        - Package distribution centers
        - Initial delivery points
        """)
    
    with col2:
        st.markdown("""
        ### 🔋 Recharge Nodes  
        - Battery charging stations
        - Drone maintenance hubs
        - Energy supply points
        """)
    
    with col3:
        st.markdown("""
        ### 👥 Client Nodes
        - Delivery destinations
        - Customer locations
        - Final delivery points
        """)

# Footer
st.markdown("---")
st.markdown("**🚁 Drone Logistics Simulator** - Advanced logistics optimization for Correos Chile")