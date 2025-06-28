import streamlit as st
import pandas as pd
from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import AVLTree # Changed
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator # RouteTracker needed for type hint
import random
import time
from visual.AVLVisualizer import AVLTreeVisualizer
from visual.AVLVisualizer import get_tree_traversals
from validaciones.validaciones import *
from visual.networkx_adapter import crear_visualizacion_red
from visual.AVLVisualizer import create_pie_chart, create_bar_chart, create_horizontal_bar_chart
import numpy as np
import io
import sys
# Import for API data sharing
from api.shared_simulation_state import update_simulation_data


# Remove the st.set_page_config() call from here since it's already in app.py

# Inicializar estado de sesión para persistencia de pestañas
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

# @st.cache_data # Caching might be problematic if we want fresh simulations & shared state updates
def ejecutar_simulacion_completa(num_nodos, num_aristas, num_ordenes):
    """Ejecutar la simulación principal y retornar todos los resultados relevantes."""
    # 1. Create and generate graph
    # Assuming undirected graph for logistics network, or symmetric edges if directed.
    # The new generate_random_graph includes geo-coordinates and role assignment.
    g = Graph(directed=False)
    g.generate_random_graph(num_nodes=num_nodos, num_edges_target=num_aristas, ensure_connectivity=True)

    # 2. Initialize simulation components
    route_manager = RouteManager(g)
    route_tracker = RouteTracker() # Fresh tracker for each simulation
    # RouteOptimizer might not be strictly needed for Phase 2 requirements beyond analysis
    route_optimizer = RouteOptimizer(route_tracker, route_manager)
    order_simulator = OrderSimulator(route_manager, route_tracker)

    # 3. Capture stdout for simulation log
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    # 4. Generate clients and process orders
    # OrderSimulator's generate_clients uses the graph to create Client objects
    # and process_orders simulates order deliveries, populating the RouteTracker.
    order_simulator.generate_clients(g) # Generates clients based on graph nodes
    order_simulator.process_orders(num_ordenes) # Simulates orders
    
    # 5. Restore stdout and get simulation log
    sys.stdout = old_stdout
    salida_simulacion_log = captured_output.getvalue()
    
    # 6. Create and populate AVL Tree for route analytics
    avl_tree_rutas = AVLTree()
    route_history = route_tracker.get_route_history()
    for route_record in route_history:
        avl_tree_rutas.insert(route_record['route']) # 'route' is the string like "N1->N2"

    # 7. Get other statistics and summaries
    # patrones_ruta_analisis = route_optimizer.analyze_route_patterns() # Optional analysis
    # reportes_optimizacion_detalle = route_optimizer.get_optimization_report() # Optional
    simulation_summary_text = order_simulator.get_simulation_summary()

    # Node distribution statistics (for Pestaña 1 display)
    node_counts_by_type = {'warehouse': 0, 'recharge': 0, 'client': 0}
    for v_obj in g.vertices():
        v_type = v_obj.type()
        if v_type in node_counts_by_type:
            node_counts_by_type[v_type] += 1
        else: # Should not happen if types are constrained
            node_counts_by_type[v_type] = node_counts_by_type.get(v_type,0) + 1

    # Data to be returned
    return {
        "graph": g,
        "route_tracker": route_tracker,
        "avl_tree": avl_tree_rutas,
        "simulation_log": salida_simulacion_log,
        "clients_list": order_simulator.clients, # List of Client domain objects
        "orders_list": order_simulator.orders,   # List of Order domain objects
        "simulation_summary": simulation_summary_text,
        "node_counts": node_counts_by_type # For display in Sim tab
        # "patrones_ruta": patrones_ruta_analisis, # If needed
        # "reportes_optimizacion": reportes_optimizacion_detalle # If needed
    }

# This function is kept as it's used by renderizar_pestana_analisis_rutas
# However, the AVL tree should ideally be built once during ejecutar_simulacion_completa
# and then accessed from session_state.
# Let's assume renderizar_pestana_analisis_rutas will get the pre-built avl_tree from session_state.
# So, this specific `crear_avl_desde_rutas` might become redundant if AVL is always from simulation run.
# For now, keeping it but noting its potential redundancy.
def crear_avl_desde_rutas(tracker: RouteTracker): # This function might be deprecated
    """Crear un árbol AVL con las rutas. (Potentially deprecated if AVL comes from session_state)"""
    avl_tree = AVLTree()

    # Populate AVL tree from individual route occurrences
    route_history = tracker.get_route_history() # list of dicts like {'route': "N1->N2", ...}

    for route_record in route_history:
        route_str = route_record['route']
        avl_tree.insert(route_str)

    return avl_tree # Return the AVLTree instance

def renderizar_pestana_simulacion(parametros, estadisticas_nodos, salida_simulacion):
    """Renderizar la pestaña de resultados de simulación"""
    st.header("📊 Resultados de la Simulación")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Nodos", parametros['num_nodos'], delta=None)
    with col2:
        st.metric("Total de Aristas", parametros['num_aristas'], delta=None)
    with col3:
        st.metric("Órdenes Procesadas", parametros['num_ordenes'], delta=None)
    with col4:
        entregas_exitosas = salida_simulacion.count("Estado: Entregado")
        st.metric("Entregas Exitosas", entregas_exitosas, 
                 delta=f"{(entregas_exitosas/parametros['num_ordenes'])*100:.1f}%" if parametros['num_ordenes'] > 0 else "0%")
    
    # Distribución de nodos
    st.subheader("📊 Distribución de Nodos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico circular
        fig_pie = create_pie_chart(
            values=list(estadisticas_nodos.values()),
            labels=['Almacén', 'Recarga', 'Cliente'],
            title="Distribución por Tipo de Nodo",
            colors=['#8B4513', '#FFA500', '#32CD32']
        )
        st.pyplot(fig_pie)
    
    with col2:
        # Gráfico de barras
        fig_bar = create_bar_chart(
            x_data=['Almacén', 'Recarga', 'Cliente'], # Use keys from node_counts for labels
            y_data=list(estadisticas_nodos.values()), # Ensure order matches labels
            title="Cantidad de Nodos por Tipo",
            colors=['#8B4513', '#FFA500', '#32CD32'], # Colors should map to warehouse, recharge, client
            xlabel="Tipo de Nodo",
            ylabel="Cantidad"
        )
        st.pyplot(fig_bar)

# Imports for Folium map tab
from streamlit_folium import st_folium
from visual.map_utils import create_empty_map, add_nodes_to_map, add_edges_to_map, highlight_path_on_map, highlight_mst_on_map

def renderizar_pestana_explorar_red(grafo: Graph, tracker: RouteTracker, avl_tree_obj: AVLTree):
    """Renderizar la pestaña de exploración de red con Folium."""
    st.header("🌐 Explorar Red Logística (Temuco)")

    if not grafo or not list(grafo.vertices()):
        st.warning("⚠️ No hay datos del grafo para mostrar. Por favor, ejecute una simulación primero.")
        return

    # Initialize session state for this tab if not already present
    if 'map_center' not in st.session_state:
        # Calculate center of current graph nodes or use default
        lats = [v.latitude() for v in grafo.vertices()]
        lons = [v.longitude() for v in grafo.vertices()]
        st.session_state.map_center = [sum(lats) / len(lats), sum(lons) / len(lons)] if lats and lons else [-38.7359, -72.5904]

    if 'selected_route_details' not in st.session_state: st.session_state.selected_route_details = None
    if 'show_mst_on_map' not in st.session_state: st.session_state.show_mst_on_map = False
    if 'folium_map_key' not in st.session_state: st.session_state.folium_map_key = 0 # To force map refresh

    # Layout columns for controls and map
    col_controls, col_map = st.columns([1, 2])

    with col_controls:
        st.subheader("⚙️ Controles de Red")

        # Selectors for origin and destination
        almacen_nodes = [v.element() for v in grafo.vertices() if v.type() == 'warehouse']
        client_nodes = [v.element() for v in grafo.vertices() if v.type() == 'client']

        if not almacen_nodes: st.warning("No hay nodos de Almacenamiento en el grafo."); return
        if not client_nodes: st.warning("No hay nodos Cliente en el grafo."); return

        selected_origin = st.selectbox("Punto de Origen (Almacén):", options=almacen_nodes, key="map_origin")
        selected_destination = st.selectbox("Punto de Destino (Cliente):", options=client_nodes, key="map_destination")

        # Algorithm selector (Dijkstra is used by RouteManager, Floyd-Warshall for all-pairs info)
        # For now, "Calculate Route" will use the enhanced Dijkstra in RouteManager.
        # Floyd-Warshall could be a separate display of all-pairs shortest paths table if desired.
        # Let's keep it simple: RouteManager's find_route_with_recharge is the primary.
        # algo_choice = st.radio("Algoritmo de Ruta:", ("Dijkstra (con autonomía)", "Floyd-Warshall (info general)"), key="map_algo")

        if st.button("🗺️ Calcular Ruta Óptima", key="calc_route_map"):
            st.session_state.show_mst_on_map = False # Hide MST if showing route
            st.session_state.selected_route_details = None # Reset previous
            if selected_origin and selected_destination:
                manager = RouteManager(grafo)
                # Using the autonomy-aware route finding from RouteManager
                # max_battery is 50 as per requirements
                route_obj = manager.find_route_with_recharge(selected_origin, selected_destination, max_battery=50)
                if route_obj:
                    st.session_state.selected_route_details = {
                        "path": route_obj.path,
                        "cost": route_obj.total_cost,
                        "recharges": route_obj.recharge_stops
                    }
                    st.success(f"Ruta calculada: {' -> '.join(route_obj.path)} (Costo: {route_obj.total_cost})")
                    if route_obj.recharge_stops:
                        st.info(f"Paradas de recarga: {', '.join(route_obj.recharge_stops)}")
                else:
                    st.error("No se pudo encontrar una ruta válida que cumpla con la autonomía.")
            else:
                st.warning("Por favor, seleccione origen y destino.")
            st.session_state.folium_map_key += 1 # Force map refresh

        if st.button("🌳 Mostrar Árbol de Expansión Mínima (Kruskal)", key="show_mst"):
            st.session_state.selected_route_details = None # Hide route if showing MST
            st.session_state.show_mst_on_map = not st.session_state.show_mst_on_map # Toggle
            st.session_state.folium_map_key += 1 # Force map refresh

        if st.session_state.show_mst_on_map:
            st.info("Mostrando MST. Para calcular una ruta, desactive MST o presione 'Calcular Ruta Óptima'.")

        # Display route/MST details
        if st.session_state.selected_route_details:
            st.subheader("Detalles de Ruta Calculada:")
            details = st.session_state.selected_route_details
            st.markdown(f"**Camino:** `{' -> '.join(details['path'])}`")
            st.markdown(f"**Costo Total:** `{details['cost']}`")
            if details['recharges']:
                st.markdown(f"**Estaciones de Recarga en Ruta:** `{', '.join(details['recharges'])}`")

        # "Complete Delivery and Create Order" button
        # This button simulates an action based on the currently displayed route.
        if st.session_state.selected_route_details and tracker and avl_tree_obj:
            if st.button("🚚 Completar Entrega y Registrar Orden", key="complete_delivery_map"):
                # This is a simplified simulation action for demonstration
                route_info = st.session_state.selected_route_details
                # Create a dummy Order object or find the client associated with destination
                client_obj = next((c for c in st.session_state.sim_clients if c.node_id == selected_destination), None)
                if not client_obj: client_obj = Client("TEMP_CLIENT", "Temporary Client", selected_destination)

                order_id = f"ORD_MAP_{int(time.time())}"
                temp_order = Order(order_id, client_obj, selected_origin, selected_destination, 1.0, "normal")
                temp_order.total_cost = route_info['cost']
                temp_order.status = "delivered" # Mark as delivered for this simulation

                # Track this simulated route and order
                # Create a Route domain object to pass to tracker
                domain_route = Route(path=route_info['path'], total_cost=route_info['cost'],
                                     recharge_stops=route_info['recharges'], segments=[]) # Segments data not fully available here easily

                tracker.track_route(domain_route)
                tracker.track_client_order(client_obj.id)
                tracker.track_order(order_id, temp_order)

                # Update AVL Tree with the new route usage
                avl_tree_obj.insert(" -> ".join(domain_route.path))

                # Update shared API state (important if API is to reflect this immediately)
                # This assumes sim_clients and sim_orders in session_state are lists that can be appended to
                # or that the tracker itself is the source of truth for the API for these dynamic updates.
                # For simplicity, let's assume tracker and avl_tree are updated, and API reads from them.
                # A full update_simulation_data might be needed if lists of clients/orders need to be passed.
                # For now, focus on tracker and AVL. The API reads from tracker/AVL.

                st.success(f"Entrega simulada y orden {order_id} registrada. Ruta utilizada: {' -> '.join(route_info['path'])}.")
                st.session_state.folium_map_key += 1 # Refresh map potentially
                # Consider if st.rerun() is needed to update other tabs that use tracker/AVL data.

    with col_map:
        st.subheader("🗺️ Mapa Interactivo de la Red")
        m = create_empty_map(location=st.session_state.map_center, zoom_start=12)

        add_nodes_to_map(m, list(grafo.vertices()))
        add_edges_to_map(m, grafo, list(grafo.edges()))

        if st.session_state.selected_route_details:
            path_elems = st.session_state.selected_route_details["path"]
            highlight_path_on_map(m, grafo, path_elems, color="red", line_weight=5)

        if st.session_state.show_mst_on_map:
            mst_edges = grafo.kruskal_mst()
            if mst_edges:
                highlight_mst_on_map(m, mst_edges, color="purple", dash_array="5, 10")
            else:
                st.warning("No se pudo calcular el MST (o el grafo es vacío/no conectable).")

        # Use the key to force re-render if data changes significantly
        st_folium(m, width=700, height=500, key=f"folium_map_{st.session_state.folium_map_key}")


def renderizar_pestana_clientes_ordenes(tracker):
    """Renderizar la pestaña de clientes y órdenes"""
    st.header("👥 Clientes y Órdenes")
    
    # Obtener nodos disponibles
    almacenes = [v.element() for v in grafo.vertices() if v.type() == 'warehouse']
    clientes = [v.element() for v in grafo.vertices() if v.type() == 'client']
    
    # Crear un formulario para evitar re-ejecución en cada selección
    with st.form("formulario_calculo_ruta"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nodo_origen = st.selectbox("Nodo de Origen", options=almacenes, key="origen_form")
        with col2:
            nodo_destino = st.selectbox("Nodo de Destino", options=clientes, key="destino_form")
        with col3:
            boton_calcular = st.form_submit_button("🔍 Calcular Ruta", type="secondary")
    
    # Manejar cálculo de ruta
    if boton_calcular:
        if nodo_origen and nodo_destino:
            manager = RouteManager(grafo)
            es_valido, mensaje_error = validar_calculo_ruta(grafo, nodo_origen, nodo_destino)
            if not es_valido:
                st.session_state.mensaje_ruta = f"❌ {mensaje_error}"
                st.session_state.ruta_calculada = None
            else:
                ruta = manager.find_route_with_recharge(nodo_origen, nodo_destino)
                if ruta:
                    st.session_state.ruta_calculada = ruta
                    camino_ruta = ' → '.join(ruta.path)
                    st.session_state.mensaje_ruta = f"✅ Ruta encontrada: {camino_ruta}\n💰 Costo total: {ruta.total_cost}"
                    if ruta.recharge_stops:
                        st.session_state.mensaje_ruta += f"\n🔋 Paradas de recarga: {', '.join(ruta.recharge_stops)}"
                else:
                    st.session_state.mensaje_ruta = "❌ ¡No se encontró una ruta válida!"
                    st.session_state.ruta_calculada = None
            # Forzar re-ejecución para actualizar visualización
            st.rerun()
    
    # Mostrar mensaje de ruta
    if st.session_state.mensaje_ruta:
        if "✅" in st.session_state.mensaje_ruta:
            st.success(st.session_state.mensaje_ruta)
        else:
            st.error(st.session_state.mensaje_ruta)

def renderizar_pestana_clientes_ordenes(tracker):
    """Renderizar la pestaña de clientes y órdenes"""
    st.header("👥 Clientes y Órdenes")
    
    # Estadísticas de clientes
    estadisticas_clientes = tracker.get_client_stats()
    if estadisticas_clientes:
        st.subheader("📊 Mejores Clientes por Órdenes")
        df_clientes = pd.DataFrame(estadisticas_clientes, columns=['ID Cliente', 'Total Órdenes'])
        st.dataframe(df_clientes.head(10), use_container_width=True)
        
        # Gráfico de clientes
        mejores_clientes = df_clientes.head(10)
        fig_clientes = create_bar_chart(
            x_data=mejores_clientes['ID Cliente'].astype(str),
            y_data=mejores_clientes['Total Órdenes'],
            title='Top 10 Clientes por Volumen de Órdenes',
            colors=['#007bff'] * len(mejores_clientes),
            xlabel='ID Cliente',
            ylabel='Total Órdenes'
        )
        st.pyplot(fig_clientes)
    else:
        st.info("No hay estadísticas de clientes disponibles. Ejecute una simulación.")
        
    st.markdown("---") # Separator

    # Lista de Órdenes (raw data from st.session_state.sim_orders)
    st.subheader("📋 Lista Completa de Órdenes")
    orders_list = st.session_state.get('sim_orders', []) # Get from session state
    if orders_list:
        # Displaying as JSON-like expandable sections
        for order_obj in orders_list:
            order_dict = {
                "order_id": order_obj.order_id,
                "client_id": order_obj.client.id if hasattr(order_obj.client, 'id') else order_obj.client_id, # client_id is on Order
                "origin": order_obj.origin,
                "destination": order_obj.destination,
                "weight": f"{order_obj.weight:.2f} kg",
                "priority": order_obj.priority,
                "status": order_obj.status,
                "creation_date": order_obj.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                "delivery_date": order_obj.delivery_date.strftime('%Y-%m-%d %H:%M:%S') if order_obj.delivery_date else "N/A",
                "total_cost": f"{order_obj.total_cost:.2f}"
            }
            with st.expander(f"Orden ID: {order_obj.order_id} (Cliente: {order_dict['client_id']}, Estado: {order_obj.status})"):
                st.json(order_dict)
    else:
        st.info("No hay órdenes para mostrar. Ejecute una simulación.")


def renderizar_pestana_analisis_rutas(tracker: RouteTracker, avl_tree_obj: AVLTree): # Added avl_tree_obj
    """Renderizar la pestaña de análisis de rutas con visualización AVL"""
    st.header("📊 Analítica de Rutas")
    
    # Mostrar información general de rutas
    st.subheader("🛣️ Información General de Rutas")
    
    # Rutas más frecuentes
    rutas_frecuentes = tracker.get_most_frequent_routes(10)
    if rutas_frecuentes:
        st.subheader("🔥 Rutas Más Frecuentes")
        for i, (ruta, freq) in enumerate(rutas_frecuentes, 1):
            st.markdown(f"""
            <div class="route-card">
                <strong>{i}. Hash de ruta:</strong> {ruta} | <span style="color: #007bff;">Frecuencia: {freq}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Visualización del Árbol AVL
    st.subheader("🌳 Árbol AVL de Rutas")
    
    # Crear el árbol AVL con las rutas
    avl_tree_instance = crear_avl_desde_rutas(tracker) # Now returns AVLTree instance
    
    if avl_tree_instance and avl_tree_instance.root is not None: # Check if tree has a root
        # Crear visualizador AVL
        visualizador = AVLTreeVisualizer() # Assuming AVLTreeVisualizer can take the root node
        
        # Get the root node for the visualizer
        # The visualizer expects nodes to have 'route', 'left', 'right', 'height', 'balance_factor'.
        # Our AVLNode has 'route_key'. AVLVisualizer will need to be adapted to use 'route_key'.
        # For now, we pass the root. We will adapt AVLVisualizer.py in a subsequent step.
        # The create_sample_tree logic in visualizer might also need to be revisited or bypassed
        # if we are visualizing the actual tree.
        
        # For now, let's try to visualize the actual tree's root
        actual_avl_root_for_viz = avl_tree_instance.get_root_for_visualizer()

        if actual_avl_root_for_viz:
            fig_avl = visualizador.visualize_tree(actual_avl_root_for_viz, title="Árbol AVL de Rutas (Real)")
            
            if fig_avl is not None:
                st.pyplot(fig_avl)
                
                # Información adicional sobre el AVL (directamente desde AVLTree instance if possible)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Height of the actual tree
                    altura_arbol = visualizador._get_height(actual_avl_root_for_viz)
                    st.metric("Altura del Árbol", altura_arbol)
                
                with col2:
                    # Count nodes in the actual tree
                    def count_nodes(node): # This helper can stay
                        if not node:
                            return 0
                        return 1 + count_nodes(node.left) + count_nodes(node.right)
                    total_nodos = count_nodes(actual_avl_root_for_viz)
                    st.metric("Total de Nodos", total_nodos)
                
                with col3:
                    # Balance factor of the root of the actual tree
                    factor_balance = actual_avl_root_for_viz.balance_factor if hasattr(actual_avl_root_for_viz, 'balance_factor') else visualizador._get_balance(actual_avl_root_for_viz)
                    # visualizer._get_balance might be safer if balance_factor is not always set on raw nodes by visualizer
                    st.metric("Factor de Balance (raíz)", factor_balance)
                
                # Mostrar información detallada del árbol
                with st.expander("🔍 Información Detallada del Árbol AVL"):
                    st.markdown("**Características del Árbol AVL:**")
                    st.markdown("- **Balanceado**: El árbol mantiene el balance automáticamente.")
                    st.markdown("- **Clave**: String de Ruta (ej: 'N1->N2->N3').")
                    st.markdown("- **Valor**: Frecuencia de uso de la ruta.")
                    st.markdown("- **Ordenamiento**: Por string de ruta (orden lexicográfico).")
                    
                    # Mostrar recorridos del árbol (using the actual tree)
                    st.markdown("**Recorridos del Árbol (Primeros 50 Nodos):**")
                    
                    # Get traversals from the actual tree's root
                    # The get_tree_traversals expects a visualizer and a root node.
                    # It also expects 'route' not 'route_key'. This will need adjustment in AVLVisualizer.py
                    # For now, this might show node objects or hashes if 'route' is not found.
                    traversals = get_tree_traversals(visualizador, actual_avl_root_for_viz, max_nodes=50)
                    
                    # Recorrido inorden
                    st.text(f"Inorden (claves): {traversals['inorder_keys']}")
                    
                    # Recorrido preorden
                    st.text(f"Preorden: {traversals['preorder']}")
                    
                    # Recorrido postorden
                    st.text(f"Postorden: {traversals['postorder']}")
            else:
                st.warning("No se pudo generar la visualización del árbol AVL")
        else:
            st.info("No hay rutas suficientes para visualizar")
    else:
        st.info("No hay suficientes datos de rutas para construir el árbol AVL")
    
    # Estadísticas de visitas a nodos (mantener esta sección)
    visitas_nodos = tracker.get_node_visit_stats()
    if visitas_nodos:
        st.subheader("📍 Nodos Más Visitados")
        df_visitas = pd.DataFrame(visitas_nodos[:10], columns=['Nodo', 'Visitas'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df_visitas, use_container_width=True)
        with col2:
            fig_visitas = create_bar_chart(
                x_data=df_visitas['Nodo'].astype(str),
                y_data=df_visitas['Visitas'],
                title='Frecuencia de Visitas por Nodo',
                colors=['#4ecdc4'] * len(df_visitas),
                xlabel='Nodo',
                ylabel='Visitas'
            )
            st.pyplot(fig_visitas)

def renderizar_pestana_estadisticas(grafo, patrones_ruta, reportes_optimizacion, salida_simulacion):
    """Renderizar la pestaña de estadísticas"""
    st.header("📈 Estadísticas")
    
    # Métricas avanzadas
    col1, col2, col3 = st.columns(3)
    
    total_aristas = len(list(grafo.edges()))
    total_vertices = len(list(grafo.vertices()))
    
    with col1:
        st.metric("Densidad del Grafo", f"{(total_aristas / (total_vertices * (total_vertices - 1))):.3f}")
    with col2:
        grado_promedio = (2 * total_aristas) / total_vertices if total_vertices > 0 else 0
        st.metric("Grado Promedio", f"{grado_promedio:.2f}")
    with col3:
        conectividad = "Conectado" if grafo.is_connected() else "Desconectado"
        st.metric("Conectividad del Grafo", conectividad)
    
    # Análisis de distribución de grados
    st.subheader("📊 Análisis de Distribución de Grados")
    
    # Calcular distribución de grados
    grados = []
    for vertice in grafo.vertices():
        grado_entrada = len(list(grafo.incident_edges(vertice, outgoing=False)))
        grado_salida = len(list(grafo.incident_edges(vertice, outgoing=True)))
        grados.append(grado_entrada + grado_salida)
    
    if grados:
        # Histograma de distribución de grados
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(grados, bins=max(1, len(set(grados))), color='#45b7d1', alpha=0.7, edgecolor='black')
        ax.set_title('Distribución de Grados de Nodos', fontsize=14, fontweight='bold')
        ax.set_xlabel('Grado', fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Análisis detallado
    st.subheader("📋 Análisis Detallado")
    
    if patrones_ruta:
        with st.expander("🔍 Análisis de Patrones de Ruta", expanded=True):
            for patron in patrones_ruta:
                st.text(patron)
    
    # Registro de simulación
    with st.expander("📜 Registro de Simulación"):
        st.text_area("Salida de Simulación", salida_simulacion, height=300)
    
    # Reportes de optimización
    if reportes_optimizacion:
        with st.expander("⚡ Reportes de Optimización"):
            for reporte in reportes_optimizacion:
                st.text(reporte)

def main():
    """Aplicación principal del dashboard"""
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    # Título principal
    st.markdown("""
    <div class="main-header">
        <h1>🚁 Simulador de Logística con Drones - Correos Chile</h1>
        <p>Optimización Avanzada de Rutas y Análisis de Redes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra lateral para configuración
    with st.sidebar:
        st.header("⚙️ Inicializar Simulación")
        
        st.subheader("Proporciones de Roles de Nodos")
        porcentaje_almacen = st.slider("📦 Nodos de Almacén", 10, 40, 20, help="Porcentaje de nodos almacén")
        porcentaje_recarga = st.slider("🔋 Nodos de Recarga", 10, 40, 20, help="Porcentaje de estaciones de recarga")
        porcentaje_cliente = 100 - porcentaje_almacen - porcentaje_recarga
        st.info(f"👥 Nodos Cliente: {porcentaje_cliente}%")
        
        st.subheader("Parámetros de Red")
        num_nodos = st.slider("Número de Nodos", 10, 150, 15, step=5)
        num_aristas = st.slider("Número de Aristas", 10, 300, 28, step=2)
        num_ordenes = st.slider("Número de Órdenes", 10, 500, 10, step=5)
        
        st.subheader("Nodos Cliente Derivados")
        clientes_derivados = int(num_nodos * 0.6)
        st.metric("Nodos Cliente Estimados", f"{clientes_derivados} (60% de {num_nodos})")
        
        boton_ejecutar = st.button("🚀 Iniciar Simulación", type="primary", use_container_width=True)
    
    # Inicializar estado de sesión para datos de simulación
    # These will store the results from ejecutar_simulacion_completa
    if 'sim_graph' not in st.session_state: st.session_state.sim_graph = None
    if 'sim_tracker' not in st.session_state: st.session_state.sim_tracker = None
    if 'sim_avl_tree' not in st.session_state: st.session_state.sim_avl_tree = None
    if 'sim_log' not in st.session_state: st.session_state.sim_log = ""
    if 'sim_clients' not in st.session_state: st.session_state.sim_clients = []
    if 'sim_orders' not in st.session_state: st.session_state.sim_orders = []
    if 'sim_summary' not in st.session_state: st.session_state.sim_summary = ""
    if 'sim_node_counts' not in st.session_state: st.session_state.sim_node_counts = {}
    if 'sim_params' not in st.session_state: st.session_state.sim_params = {} # For num_nodos, etc.
    
    # Contenido principal
    if boton_ejecutar:
        with st.spinner("🚀 Inicializando y ejecutando simulación completa... Por favor espere."):
            sim_results = ejecutar_simulacion_completa(num_nodos, num_aristas, num_ordenes)

            # Store results in session state
            st.session_state.sim_graph = sim_results["graph"]
            st.session_state.sim_tracker = sim_results["route_tracker"]
            st.session_state.sim_avl_tree = sim_results["avl_tree"]
            st.session_state.sim_log = sim_results["simulation_log"]
            st.session_state.sim_clients = sim_results["clients_list"]
            st.session_state.sim_orders = sim_results["orders_list"]
            st.session_state.sim_summary = sim_results["simulation_summary"]
            st.session_state.sim_node_counts = sim_results["node_counts"]

            st.session_state.sim_params = {
                'num_nodos': num_nodos, 'num_aristas': num_aristas, 'num_ordenes': num_ordenes
            }

            # Update shared state for API
            update_simulation_data(
                graph=st.session_state.sim_graph,
                clients=st.session_state.sim_clients,
                orders=st.session_state.sim_orders,
                tracker=st.session_state.sim_tracker,
                avl=st.session_state.sim_avl_tree,
                summary=st.session_state.sim_summary
            )

            st.session_state.ruta_calculada = None # Reset any previously calculated route
            st.session_state.mensaje_ruta = ""
            st.success("✅ Simulación completada y datos actualizados!")
            # st.rerun() # Consider if rerun is needed or if drawing below is sufficient

    # Verificar si existen datos de simulación (using sim_graph as a proxy)
    if st.session_state.sim_graph is not None:
        # Retrieve data from session state for rendering tabs
        grafo = st.session_state.sim_graph
        tracker = st.session_state.sim_tracker
        # avl_tree = st.session_state.sim_avl_tree # Used in render_pestana_analisis_rutas
        salida_simulacion = st.session_state.sim_log
        # clients_list = st.session_state.sim_clients # Used in render_pestana_clientes_ordenes
        # orders_list = st.session_state.sim_orders   # Used in render_pestana_clientes_ordenes
        # sim_summary_text = st.session_state.sim_summary
        estadisticas_nodos = st.session_state.sim_node_counts # Renamed from previous structure
        parametros = st.session_state.sim_params
        
        # Placeholder for patrones_ruta, reportes_optimizacion if they are re-introduced
        patrones_ruta = []
        reportes_optimizacion = []

        # Navegación por pestañas con estado de sesión
        nombres_pestanas = ["🎯 Simulación Actual", "🌐 Explorar Red", "👥 Clientes y Órdenes", "📊 Analítica de Rutas", "📈 Estadísticas Generales"]
        
        # Crear pestañas pero manejar selección manualmente
        pestana_seleccionada = st.selectbox("Seleccionar Pestaña:", nombres_pestanas, 
                                           index=st.session_state.active_tab,
                                           key="selector_pestana")
        
        # Actualizar pestaña activa en estado de sesión
        if pestana_seleccionada != nombres_pestanas[st.session_state.active_tab]:
            st.session_state.active_tab = nombres_pestanas.index(pestana_seleccionada)
        
        st.markdown("---")
        
        # Renderizar pestaña apropiada
        if st.session_state.active_tab == 0:  # Simulación Actual
            renderizar_pestana_simulacion(
                parametros, # from st.session_state.sim_params
                st.session_state.sim_node_counts, # from st.session_state.sim_node_counts
                salida_simulacion # from st.session_state.sim_log
            )
        elif st.session_state.active_tab == 1:  # Explorar Red
            renderizar_pestana_explorar_red(
                st.session_state.sim_graph,
                st.session_state.sim_tracker,
                st.session_state.sim_avl_tree # Pass the AVL tree instance
            )
        elif st.session_state.active_tab == 2:  # Clientes y Órdenes
            renderizar_pestana_clientes_ordenes(
                st.session_state.sim_tracker # This tab uses tracker for client/order stats
            )
        elif st.session_state.active_tab == 3:  # Analítica de Rutas
            renderizar_pestana_analisis_rutas(
                st.session_state.sim_tracker, # Passes tracker
                st.session_state.sim_avl_tree  # Passes AVL tree instance
            )
        elif st.session_state.active_tab == 4:  # Estadísticas Generales
            # Ensure all required params for renderizar_pestana_estadisticas are available
            # It currently expects: grafo, patrones_ruta, reportes_optimizacion, salida_simulacion
            # We have st.session_state.sim_graph and st.session_state.sim_log
            # patrones_ruta and reportes_optimizacion are currently empty lists.
            renderizar_pestana_estadisticas(
                st.session_state.sim_graph,
                patrones_ruta, # Placeholder, can be enhanced if RouteOptimizer is used more
                reportes_optimizacion, # Placeholder
                st.session_state.sim_log
            )
    
    else:
        # Pantalla inicial
        st.info("👈 Configura los parámetros de simulación en la barra lateral y haz clic en 'Iniciar Simulación' para comenzar!")
        
        # Información del sistema
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 📦 Nodos de Almacén
            - Instalaciones de almacén
            - Centros de distribución de paquetes
            - Puntos de entrega inicial
            """)
        
        with col2:
            st.markdown("""
            ### 🔋 Nodos de Recarga  
            - Estaciones de carga de baterías
            - Centros de mantenimiento de drones
            - Puntos de suministro de energía
            """)
        
        with col3:
            st.markdown("""
            ### 👥 Nodos Cliente
            - Destinos de entrega
            - Ubicaciones de clientes
            - Puntos de entrega final
            """)
    
    # Pie de página
    st.markdown("---")
    st.markdown("**🚁 Simulador de Logística con Drones** - Optimización logística avanzada para Correos Chile")

if __name__ == "__main__":
    main()