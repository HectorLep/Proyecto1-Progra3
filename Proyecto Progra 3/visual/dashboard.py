import streamlit as st
import pandas as pd
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
from visual.networkx_adapter import create_network_visualization
from visual.AVLVisualizer import create_pie_chart, create_bar_chart, create_horizontal_bar_chart
import numpy as np
import io
import sys

st.set_page_config(
    page_title="🚁 Drone Logistics Simulator - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for tab persistence
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

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

@st.cache_data
def run_simulation(num_nodes, num_edges, num_orders):
    """Execute the main simulation and return results"""
    g = Graph(directed=True)
    g.generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    # Capture simulation output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    simulator.process_orders(num_orders)
    
    sys.stdout = old_stdout
    simulation_output = captured_output.getvalue()
    
    # Get statistics
    route_patterns = optimizer.analyze_route_patterns()
    optimization_reports = optimizer.get_optimization_report()
    
    # Graph statistics
    node_stats = {
        'warehouse': len([v for v in g.vertices() if v.type() == 'warehouse']),
        'recharge': len([v for v in g.vertices() if v.type() == 'recharge']),
        'client': len([v for v in g.vertices() if v.type() == 'client'])
    }
    
    return g, route_patterns, optimization_reports, simulation_output, tracker, node_stats

def render_simulation_tab(params, node_stats, simulation_output):
    """Render the simulation results tab"""
    st.header("📊 Simulation Results")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Nodes", params['num_nodes'], delta=None)
    with col2:
        st.metric("Total Edges", params['num_edges'], delta=None)
    with col3:
        st.metric("Orders Processed", params['num_orders'], delta=None)
    with col4:
        successful_orders = simulation_output.count("Estado: Entregado")
        st.metric("Successful Deliveries", successful_orders, 
                 delta=f"{(successful_orders/params['num_orders'])*100:.1f}%" if params['num_orders'] > 0 else "0%")
    
    # Node distribution
    st.subheader("📊 Node Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig_pie = create_pie_chart(
            values=list(node_stats.values()),
            labels=['Warehouse', 'Recharge', 'Client'],
            title="Node Type Distribution",
            colors=['#8B4513', '#FFA500', '#32CD32']
        )
        st.pyplot(fig_pie)
    
    with col2:
        # Bar chart
        fig_bar = create_bar_chart(
            x_data=['Warehouse', 'Recharge', 'Client'],
            y_data=list(node_stats.values()),
            title="Node Count by Type",
            colors=['#8B4513', '#FFA500', '#32CD32'],
            xlabel="Node Type",
            ylabel="Count"
        )
        st.pyplot(fig_bar)

def render_network_tab(graph):
    """Render the network exploration tab"""
    st.header("🌐 Network Visualization")
    
    # Initialize route calculation state
    if 'calculated_route' not in st.session_state:
        st.session_state.calculated_route = None
    if 'route_message' not in st.session_state:
        st.session_state.route_message = ""
    
    # Create and show Matplotlib visualization
    highlighted_route = st.session_state.calculated_route.path if st.session_state.calculated_route else None
    fig = create_network_visualization(graph, highlighted_route=highlighted_route)
    st.pyplot(fig)
    
    # Route calculation panel
    st.subheader("🧭 Calculate Route")
    
    # Get available nodes
    warehouses = [v.element() for v in graph.vertices() if v.type() == 'warehouse']
    clients = [v.element() for v in graph.vertices() if v.type() == 'client']
    
    # Create a form to prevent rerunning on each selection
    with st.form("route_calculation_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            origin_node = st.selectbox("Origin Node", options=warehouses, key="origin_form")
        with col2:
            dest_node = st.selectbox("Destination Node", options=clients, key="dest_form")
        with col3:
            calculate_button = st.form_submit_button("🔍 Calculate Route", type="secondary")
    
    # Handle route calculation
    if calculate_button:
        if origin_node and dest_node:
            manager = RouteManager(graph)
            es_valido, mensaje_error = validar_calculo_ruta(graph, origin_node, dest_node)
            if not es_valido:
                st.session_state.route_message = f"❌ {mensaje_error}"
                st.session_state.calculated_route = None
            else:
                route = manager.find_route_with_recharge(origin_node, dest_node)
                if route:
                    st.session_state.calculated_route = route
                    route_path = ' → '.join(route.path)
                    st.session_state.route_message = f"✅ Route found: {route_path}\n💰 Total cost: {route.total_cost}"
                    if route.recharge_stops:
                        st.session_state.route_message += f"\n🔋 Recharge stops: {', '.join(route.recharge_stops)}"
                else:
                    st.session_state.route_message = "❌ No valid route found!"
                    st.session_state.calculated_route = None
            # Force rerun to update visualization
            st.rerun()
    
    # Display route message
    if st.session_state.route_message:
        if "✅" in st.session_state.route_message:
            st.success(st.session_state.route_message)
        else:
            st.error(st.session_state.route_message)

def render_clients_orders_tab(tracker):
    """Render the clients and orders tab"""
    st.header("👥 Clients & Orders")
    
    # Client statistics
    client_stats = tracker.get_client_stats()
    if client_stats:
        st.subheader("📊 Top Clients by Orders")
        client_df = pd.DataFrame(client_stats, columns=['Client ID', 'Total Orders'])
        st.dataframe(client_df.head(10), use_container_width=True)
        
        # Client chart
        top_clients = client_df.head(10)
        fig_clients = create_bar_chart(
            x_data=top_clients['Client ID'].astype(str),
            y_data=top_clients['Total Orders'],
            title='Top 10 Clients by Order Volume',
            colors=['#007bff'] * len(top_clients),
            xlabel='Client ID',
            ylabel='Total Orders'
        )
        st.pyplot(fig_clients)
    
    # Order statistics
    order_stats = tracker.get_order_stats()
    if order_stats:
        st.subheader("💰 Orders by Cost")
        order_data = [(oid, order.total_cost, order.status) for oid, order in order_stats[:10]]
        order_df = pd.DataFrame(order_data, columns=['Order ID', 'Total Cost', 'Status'])
        st.dataframe(order_df, use_container_width=True)
        
        # Order cost chart
        if len(order_df) > 0:
            fig_orders = create_bar_chart(
                x_data=order_df['Order ID'].astype(str),
                y_data=order_df['Total Cost'],
                title='Top 10 Orders by Cost',
                colors=['#28a745' if status == 'Delivered' else '#dc3545' 
                       for status in order_df['Status']],
                xlabel='Order ID',
                ylabel='Total Cost'
            )
            st.pyplot(fig_orders)

def render_route_analytics_tab(tracker):
    """Render the route analytics tab"""
    st.header("📊 Route Analytics")
    
    # Show route patterns
    st.subheader("🛣️ Route Frequency & History")
    
    # Most frequent routes
    frequent_routes = tracker.get_most_frequent_routes(10)
    if frequent_routes:
        st.subheader("🔥 Most Frequent Routes")
        for i, (route, freq) in enumerate(frequent_routes, 1):
            st.markdown(f"""
            <div class="route-card">
                <strong>{i}. Route hash:</strong> {route} | <span style="color: #007bff;">Frequency: {freq}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Route frequency chart
        if len(frequent_routes) > 0:
            route_labels = [f"Route {i+1}" for i in range(len(frequent_routes))]
            route_frequencies = [freq for _, freq in frequent_routes]
            
            fig_routes = create_horizontal_bar_chart(
                x_data=route_frequencies,
                y_data=route_labels,
                title='Most Frequent Routes',
                color='#ff6b6b'
            )
            st.pyplot(fig_routes)
    
    # Node visit statistics
    node_visits = tracker.get_node_visit_stats()
    if node_visits:
        st.subheader("📍 Most Visited Nodes")
        visit_df = pd.DataFrame(node_visits[:10], columns=['Node', 'Visits'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(visit_df, use_container_width=True)
        with col2:
            fig_visits = create_bar_chart(
                x_data=visit_df['Node'].astype(str),
                y_data=visit_df['Visits'],
                title='Node Visit Frequency',
                colors=['#4ecdc4'] * len(visit_df),
                xlabel='Node',
                ylabel='Visits'
            )
            st.pyplot(fig_visits)

def render_statistics_tab(graph, route_patterns, optimization_reports, simulation_output):
    """Render the statistics tab"""
    st.header("📈 Statistics")
    
    # Advanced metrics
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
    
    # Degree distribution analysis
    st.subheader("📊 Degree Distribution Analysis")
    
    # Calculate degree distribution
    degrees = []
    for vertex in graph.vertices():
        in_degree = len(list(graph.incident_edges(vertex, outgoing=False)))
        out_degree = len(list(graph.incident_edges(vertex, outgoing=True)))
        degrees.append(in_degree + out_degree)
    
    if degrees:
        # Degree distribution histogram
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(degrees, bins=max(1, len(set(degrees))), color='#45b7d1', alpha=0.7, edgecolor='black')
        ax.set_title('Node Degree Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Degree', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Detailed analysis
    st.subheader("📋 Detailed Analysis")
    
    if route_patterns:
        with st.expander("🔍 Route Pattern Analysis", expanded=True):
            for pattern in route_patterns:
                st.text(pattern)
    
    # Simulation log
    with st.expander("📜 Simulation Log"):
        st.text_area("Simulation Output", simulation_output, height=300)
    
    # Optimization reports
    if optimization_reports:
        with st.expander("⚡ Optimization Reports"):
            for report in optimization_reports:
                st.text(report)

def main():
    """Main dashboard application"""
    # Main title
    st.markdown("""
    <div class="main-header">
        <h1>🚁 Drone Logistics Simulator - Correos Chile</h1>
        <p>Advanced Route Optimization and Network Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
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
    
    # Initialize session state for simulation data
    if 'simulation_data' not in st.session_state:
        st.session_state.simulation_data = None
    
    # Main content
    if run_button:
        with st.spinner("Initializing simulation..."):
            # Execute simulation and save in session state
            st.session_state.simulation_data = run_simulation(num_nodes, num_edges, num_orders)
            st.session_state.simulation_params = {
                'num_nodes': num_nodes,
                'num_edges': num_edges,
                'num_orders': num_orders
            }
    
    # Check if simulation data exists
    if st.session_state.simulation_data is not None:
        graph, route_patterns, optimization_reports, simulation_output, tracker, node_stats = st.session_state.simulation_data
        params = st.session_state.simulation_params
        
        # Tab navigation with session state
        tab_names = ["🎯 Run Simulation", "🌐 Explore Network", "👥 Clients & Orders", "📊 Route Analytics", "📈 Statistics"]
        
        # Create tabs but handle selection manually
        selected_tab = st.selectbox("Select Tab:", tab_names, 
                                   index=st.session_state.active_tab,
                                   key="tab_selector")
        
        # Update active tab in session state
        if selected_tab != tab_names[st.session_state.active_tab]:
            st.session_state.active_tab = tab_names.index(selected_tab)
        
        st.markdown("---")
        
        # Render appropriate tab
        if st.session_state.active_tab == 0:  # Run Simulation
            render_simulation_tab(params, node_stats, simulation_output)
        elif st.session_state.active_tab == 1:  # Explore Network
            render_network_tab(graph)
        elif st.session_state.active_tab == 2:  # Clients & Orders
            render_clients_orders_tab(tracker)
        elif st.session_state.active_tab == 3:  # Route Analytics
            render_route_analytics_tab(tracker)
        elif st.session_state.active_tab == 4:  # Statistics
            render_statistics_tab(graph, route_patterns, optimization_reports, simulation_output)
    
    else:
        # Initial screen
        st.info("👈 Configure the simulation parameters in the sidebar and click 'Start Simulation' to begin!")
        
        # System information
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

if __name__ == "__main__":
    main()