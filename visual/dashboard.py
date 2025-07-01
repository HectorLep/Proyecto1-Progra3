import streamlit as st
import pandas as pd
from model.graph import Graph
<<<<<<< Updated upstream
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import avl_insert
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator
import random
=======
from tda.avl import AVLTree 
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator 
>>>>>>> Stashed changes
import time
from visual.AVLVisualizer import AVLTreeVisualizer
from visual.AVLVisualizer import get_tree_traversals
from validaciones.validaciones import *
from visual.networkx_adapter import crear_visualizacion_red
from visual.AVLVisualizer import create_pie_chart, create_bar_chart
import io
import sys
<<<<<<< Updated upstream

# Remove the st.set_page_config() call from here since it's already in app.py

# Inicializar estado de sesión para persistencia de pestañas
=======
from api.shared_simulation_state import state_instance
from visual.map.map_builder import create_empty_map, add_nodes_to_map, add_edges_to_map, highlight_path_on_map, highlight_mst_on_map
from visual.map.flight_summary import display_route_details
from .report_generator import generate_pdf_report_content, get_report_filename

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
@st.cache_data
def ejecutar_simulacion(num_nodos, num_aristas, num_ordenes):
    """Ejecutar la simulación principal y retornar resultados"""
    g = Graph(directed=True)
    g.generate_random_graph(num_nodes=num_nodos, num_edges=num_aristas)
    
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    # Capturar salida de la simulación
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    simulator.process_orders(num_ordenes)
=======
def ejecutar_simulacion_completa(num_nodos, num_aristas, num_ordenes):
    """Ejecutar la simulación principal y retornar todos los resultados relevantes."""

    g = Graph(directed=False)
    g.generate_random_graph(num_nodes=num_nodos, num_edges_target=num_aristas, ensure_connectivity=True)

    route_manager = RouteManager(g)
    route_tracker = RouteTracker() # Fresh tracker for each simulation
    route_optimizer = RouteOptimizer(route_tracker, route_manager)
    order_simulator = OrderSimulator(route_manager, route_tracker)

    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    order_simulator.generate_clients(g) # Generates clients based on graph nodes
    order_simulator.process_orders(num_ordenes) # Simulates orders
>>>>>>> Stashed changes
    
    sys.stdout = old_stdout
    salida_simulacion = captured_output.getvalue()
    
<<<<<<< Updated upstream
    # Obtener estadísticas
    patrones_ruta = optimizer.analyze_route_patterns()
    reportes_optimizacion = optimizer.get_optimization_report()
    
    # Estadísticas del grafo
    estadisticas_nodos = {
        'almacen': len([v for v in g.vertices() if v.type() == 'warehouse']),
        'recarga': len([v for v in g.vertices() if v.type() == 'recharge']),
        'cliente': len([v for v in g.vertices() if v.type() == 'client'])
=======
    # 6. Create and populate AVL Tree for route analytics
    avl_tree_rutas = AVLTree()
    route_history = route_tracker.get_route_history()
    for route_record in route_history:
        avl_tree_rutas.insert(route_record['route']) # 'route' is the string like "N1->N2"


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
>>>>>>> Stashed changes
    }
    
    return g, patrones_ruta, reportes_optimizacion, salida_simulacion, tracker, estadisticas_nodos

<<<<<<< Updated upstream
def crear_avl_desde_rutas(tracker):
    """Crear un árbol AVL con las rutas más frecuentes"""   
    avl_root = None
    rutas_frecuentes = tracker.get_most_frequent_routes(15)  # Obtener más rutas para el AVL
    
    for ruta_hash, frecuencia in rutas_frecuentes:
        # Usar el hash de la ruta como clave para el AVL
        avl_root = avl_insert(avl_root, ruta_hash)
    
    return avl_root
=======
def crear_avl_desde_rutas(tracker: RouteTracker): # This function might be deprecated
    """Crear un árbol AVL con las rutas. (Potentially deprecated if AVL comes from session_state)"""
    avl_tree = AVLTree()

    # Populate AVL tree from individual route occurrences
    route_history = tracker.get_route_history() # list of dicts like {'route': "N1->N2", ...}

    for route_record in route_history:
        route_str = route_record['route']
        avl_tree.insert(route_str)

    return avl_tree # Return the AVLTree instance
>>>>>>> Stashed changes

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
            x_data=['Almacén', 'Recarga', 'Cliente'],
            y_data=list(estadisticas_nodos.values()),
            title="Cantidad de Nodos por Tipo",
            colors=['#8B4513', '#FFA500', '#32CD32'],
            xlabel="Tipo de Nodo",
            ylabel="Cantidad"
        )
        st.pyplot(fig_bar)

<<<<<<< Updated upstream
def renderizar_pestana_red(grafo):
    """Renderizar la pestaña de exploración de red"""
    st.header("🌐 Visualización de la Red")
    
    # Inicializar estado de cálculo de rutas
    if 'ruta_calculada' not in st.session_state:
        st.session_state.ruta_calculada = None
    if 'mensaje_ruta' not in st.session_state:
        st.session_state.mensaje_ruta = ""
    
    # Crear y mostrar visualización con Matplotlib
    ruta_resaltada = st.session_state.ruta_calculada.path if st.session_state.ruta_calculada else None
    fig = crear_visualizacion_red(grafo, ruta_destacada=ruta_resaltada)
    st.pyplot(fig)
    
    # Panel de cálculo de rutas
    st.subheader("🧭 Calcular Ruta")
    
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
=======

# Imports for Folium map tab
from streamlit_folium import st_folium
from visual.map.map_builder import create_empty_map, add_nodes_to_map, add_edges_to_map, highlight_path_on_map, highlight_mst_on_map

# Reemplaza la función completa en visual/dashboard.py

def renderizar_pestana_explorar_red(grafo: Graph, tracker: RouteTracker, avl_tree_obj: AVLTree):
    """Renderizar la pestaña de exploración de red con Folium y lógica de visualización mejorada."""
    st.header("🌐 Explorar Red Logística (Temuco)")

    if 'map_success_message' not in st.session_state:
        st.session_state.map_success_message = None

    if st.session_state.map_success_message:
        st.success(st.session_state.map_success_message)
        

    if not grafo or not list(grafo.vertices()):
        st.warning("⚠️ No hay datos del grafo para mostrar. Por favor, ejecute una simulación primero.")
        return
    
    if 'map_center' not in st.session_state:
        lats = [v.latitude() for v in grafo.vertices()]
        lons = [v.longitude() for v in grafo.vertices()]
        st.session_state.map_center = [sum(lats) / len(lats), sum(lons) / len(lons)] if lats and lons else [-38.7359, -72.5904]

    if 'selected_route_details' not in st.session_state: st.session_state.selected_route_details = None
    if 'show_mst_on_map' not in st.session_state: st.session_state.show_mst_on_map = False
    if 'folium_map_key' not in st.session_state: st.session_state.folium_map_key = 0

    # --- Layout de la página ---
    col_controls, col_map = st.columns([1, 2])

    with col_controls:
        st.subheader("⚙️ Controles de Red")

        almacen_nodes = [v.element() for v in grafo.vertices() if v.type() == 'warehouse']
        client_nodes = [v.element() for v in grafo.vertices() if v.type() == 'client']

        if not almacen_nodes or not client_nodes:
            st.warning("Debe haber al menos un nodo de Almacenamiento y uno de Cliente.")
            return

        selected_origin = st.selectbox("Punto de Origen (Almacén):", options=almacen_nodes, key="map_origin")
        selected_destination = st.selectbox("Punto de Destino (Cliente):", options=client_nodes, key="map_destination")

        # --- INICIO CAMBIO 3: Texto de algoritmo activo ---
        if st.session_state.show_mst_on_map:
            st.info("Visualizando: Árbol de Expansión Mínima.")
        elif st.session_state.selected_route_details:
            st.caption("✨ Algoritmo en uso: Dijkstra (Ruta Óptima con Recarga)")
        else:
            st.caption("✨ Algoritmo: Seleccione una acción (Calcular Ruta o Mostrar MST)")

        if st.button("🗺️ Calcular Ruta Óptima", key="calc_route_map"):
            st.session_state.map_success_message = None # <-- AÑADE ESTA LÍNEA
            st.session_state.show_mst_on_map = False
            manager = RouteManager(grafo)
            route_obj = manager.find_route_with_recharge(selected_origin, selected_destination)
            if route_obj:
                st.session_state.selected_route_details = {"path": route_obj.path, "cost": route_obj.total_cost, "recharges": route_obj.recharge_stops}
            else:
                st.session_state.selected_route_details = None
                st.error("No se pudo encontrar una ruta válida.")
            st.session_state.folium_map_key += 1
            st.rerun()

        # --- INICIO CAMBIO 2: Botón dinámico para activar/desactivar MST ---
        if st.session_state.show_mst_on_map:
            if st.button("🌳 Ocultar Árbol de Expansión Mínima", key="toggle_mst"):
                st.session_state.map_success_message = None
                st.session_state.show_mst_on_map = False
                st.session_state.folium_map_key += 1
                st.rerun()
        else:
            if st.button("🌳 Mostrar Árbol de Expansión Mínima (Kruskal)", key="toggle_mst"):
                st.session_state.selected_route_details = None
                st.session_state.show_mst_on_map = True
                st.session_state.folium_map_key += 1
                st.rerun()
        # --- FIN CAMBIO 2 ---

        # Mostrar detalles de la ruta calculada
        if st.session_state.selected_route_details and not st.session_state.show_mst_on_map:
            display_route_details(st.session_state.selected_route_details)
            # El botón de "Completar Entrega" puede ir justo después si quieres
            if st.button("🚚 Completar Entrega y Registrar Orden", ...):
                # Lógica para completar la entrega... (se mantiene tu lógica para crear 'client_obj' y 'order_id')
                route_info = st.session_state.selected_route_details
                client_obj = next((c for c in st.session_state.sim_clients if c.node_id == selected_destination), None)
                if client_obj:
                    order_id = f"ORD_MAP_{int(time.time())}"
                    st.session_state.map_success_message = f"✅ ¡Orden {order_id} creada exitosamente para el cliente {client_obj.id}!"
                st.rerun()

    with col_map:
        st.subheader("🗺️ Mapa Interactivo de la Red")
        m = create_empty_map(location=st.session_state.map_center)

        if not st.session_state.show_mst_on_map:
            add_edges_to_map(m, grafo, list(grafo.edges()))
        add_nodes_to_map(m, list(grafo.vertices()))
        if st.session_state.selected_route_details and not st.session_state.show_mst_on_map:
            highlight_path_on_map(m, grafo, st.session_state.selected_route_details["path"], color="red")
        if st.session_state.show_mst_on_map:
            mst_edges = grafo.kruskal_mst()
            highlight_mst_on_map(m, mst_edges, color="purple", dash_array="10, 10")
        st_folium(m, width=700, height=500, key=f"folium_map_{st.session_state.folium_map_key}")


def renderizar_pestana_clientes_ordenes(tracker):
>>>>>>> Stashed changes

# --- CÓDIGO A INSERTAR ---
    st.markdown("---")
    if st.button("🔄 Refrescar Datos", help="Actualiza la vista con los últimos cambios realizados a través de la API."):
        with st.spinner("Actualizando datos desde el estado compartido..."):
            # Obtener los datos más recientes desde la instancia compartida
            fresh_data = state_instance.get_data()
            
            st.session_state.sim_orders = fresh_data.get("orders", st.session_state.sim_orders)
            st.session_state.sim_tracker = fresh_data.get("route_tracker", st.session_state.sim_tracker)
            st.session_state.sim_clients = fresh_data.get("clients", st.session_state.sim_clients)
            # Actualizamos también los otros por consistencia
            st.session_state.sim_graph = fresh_data.get("graph", st.session_state.sim_graph)
            st.session_state.sim_avl_tree = fresh_data.get("avl_tree", st.session_state.sim_avl_tree)
            st.session_state.sim_summary = fresh_data.get("summary", st.session_state.sim_summary)
        st.success("¡Datos actualizados!")
        # Forzamos un re-run para que la UI se redibuje con los nuevos datos de session_state
        st.rerun() 
    
    st.markdown("---")
    # --- FIN DEL CÓDIGO A INSERTAR ---

    # El resto de la función sigue igual, ya que leerá los datos actualizados de st.session_state
    estadisticas_clientes = st.session_state.sim_tracker.get_client_stats()
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
    
    # Estadísticas de órdenes
    estadisticas_ordenes = tracker.get_order_stats()
    if estadisticas_ordenes:
        st.subheader("💰 Órdenes por Costo")
        datos_ordenes = [(oid, order.total_cost, order.status) for oid, order in estadisticas_ordenes[:10]]
        df_ordenes = pd.DataFrame(datos_ordenes, columns=['ID Orden', 'Costo Total', 'Estado'])
        st.dataframe(df_ordenes, use_container_width=True)
        
<<<<<<< Updated upstream
        # Gráfico de costo de órdenes
        if len(df_ordenes) > 0:
            fig_ordenes = create_bar_chart(
                x_data=df_ordenes['ID Orden'].astype(str),
                y_data=df_ordenes['Costo Total'],
                title='Top 10 Órdenes por Costo',
                colors=['#28a745' if estado == 'Delivered' else '#dc3545' 
                       for estado in df_ordenes['Estado']],
                xlabel='ID Orden',
                ylabel='Costo Total'
            )
            st.pyplot(fig_ordenes)

def renderizar_pestana_analisis_rutas(tracker):
=======
    st.markdown("---") # Separator

    # Lista de Órdenes (raw data from st.session_state.sim_orders)
    st.subheader("📋 Lista Completa de Órdenes")
    orders_list = st.session_state.get('sim_orders', []) # Get from session state
    if orders_list:
        # Displaying as JSON-like expandable sections
        for order_obj in orders_list:
            order_dict = {
                "order_id": order_obj.order_id,
                "client_id": order_obj.client.id,
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
>>>>>>> Stashed changes
    """Renderizar la pestaña de análisis de rutas con visualización AVL"""
    st.header("📊 Análisis de Rutas")
    
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
    avl_root = crear_avl_desde_rutas(tracker)
    
    if avl_root is not None:
        # Crear visualizador AVL
<<<<<<< Updated upstream
        visualizador = AVLTreeVisualizer()
        
        # Convertir las rutas frecuentes a claves para el árbol de demostración
        rutas_keys = [ruta_hash for ruta_hash, _ in rutas_frecuentes[:10]]  # Usar solo los primeros 10
        
        # Crear árbol de muestra con las claves de ruta
        if rutas_keys:
            arbol_muestra = visualizador.create_sample_tree(rutas_keys)
            
            # Crear la visualización del árbol
            fig_avl = visualizador.visualize_tree(arbol_muestra, title="Árbol AVL de Rutas Frecuentes")
=======
        visualizador = AVLTreeVisualizer() # Assuming AVLTreeVisualizer can take the root node
        actual_avl_root_for_viz = avl_tree_instance.get_root_for_visualizer()

        if actual_avl_root_for_viz:
            fig_avl = visualizador.visualize_tree(actual_avl_root_for_viz, title="Árbol AVL de Rutas (Real)")
>>>>>>> Stashed changes
            
            if fig_avl is not None:
                st.pyplot(fig_avl)
                
                # Información adicional sobre el AVL
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    altura_arbol = visualizador._get_height(arbol_muestra)
                    st.metric("Altura del Árbol", altura_arbol)
                
                with col2:
                    def count_nodes(node):
                        if not node:
                            return 0
                        return 1 + count_nodes(node.left) + count_nodes(node.right)
                    
                    total_nodos = count_nodes(arbol_muestra)
                    st.metric("Total de Nodos", total_nodos)
                
                with col3:
<<<<<<< Updated upstream
                    factor_balance = arbol_muestra.balance_factor if arbol_muestra else 0
=======
                    # Balance factor of the root of the actual tree
                    factor_balance = actual_avl_root_for_viz.balance_factor if hasattr(actual_avl_root_for_viz, 'balance_factor') else visualizador._get_height(actual_avl_root_for_viz.left) - visualizador._get_height(actual_avl_root_for_viz.right)                    # visualizer._get_balance might be safer if balance_factor is not always set on raw nodes by visualizer
>>>>>>> Stashed changes
                    st.metric("Factor de Balance (raíz)", factor_balance)
                
                # Mostrar información detallada del árbol
                with st.expander("🔍 Información Detallada del Árbol AVL"):
                    st.markdown("**Características del Árbol AVL:**")
<<<<<<< Updated upstream
                    st.markdown("- **Balanceado**: El árbol mantiene el balance automáticamente")
                    st.markdown("- **Clave**: Hash de ruta (identificador único)")
                    st.markdown("- **Valor**: Frecuencia de uso de la ruta")
                    st.markdown("- **Ordenamiento**: Por hash de ruta (orden lexicográfico)")
                    
                    # Mostrar recorridos del árbol
                    st.markdown("**Recorridos del Árbol:**")
                    
                    # Obtener recorridos usando el visualizador
                    traversals = get_tree_traversals(visualizador, arbol_muestra)
                    
                    # Recorrido inorden
                    st.text(f"Inorden: {traversals['inorder']}")
                    
                    # Recorrido preorden
=======
                    st.markdown("- **Balanceado**: El árbol mantiene el balance automáticamente.")
                    st.markdown("- **Clave**: String de Ruta (ej: 'N1->N2->N3').")
                    st.markdown("- **Valor**: Frecuencia de uso de la ruta.")
                    st.markdown("- **Ordenamiento**: Por string de ruta (orden lexicográfico).")
                    st.markdown("**Recorridos del Árbol (Primeros 50 Nodos):**")
                    traversals = get_tree_traversals(visualizador, actual_avl_root_for_viz)                    
                    st.text(f"Inorden (claves): {traversals['inorder']}")                    
>>>>>>> Stashed changes
                    st.text(f"Preorden: {traversals['preorder']}")
                    st.text(f"Postorden: {traversals['postorder']}")
            else:
                st.warning("No se pudo generar la visualización del árbol AVL")
        else:
            st.info("No hay rutas suficientes para visualizar")
    else:
        st.info("No hay suficientes datos de rutas para construir el árbol AVL")
    
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


    st.markdown("---")
    st.subheader("📄 Exportar Informe")

    if st.button("📥 Generar y Descargar Informe PDF"):
        with st.spinner("Generando reporte... por favor espere."):
            datos_para_reporte = {
                "graph": st.session_state.sim_graph,
                "clients": st.session_state.sim_clients,
                "orders": st.session_state.sim_orders,
                "route_tracker": st.session_state.sim_tracker,
                "summary": st.session_state.sim_summary
            }
            pdf_bytes = generate_pdf_report_content(datos_para_reporte)

            st.download_button(
                label="✅ ¡Descargar PDF Ahora!",
                data=pdf_bytes,
                file_name=get_report_filename(),
                mime="application/pdf"
            )


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
<<<<<<< Updated upstream
    
    # Inicializar estado de sesión para datos de simulación
    if 'datos_simulacion' not in st.session_state:
        st.session_state.datos_simulacion = None
=======

    if 'sim_graph' not in st.session_state: st.session_state.sim_graph = None
    if 'sim_tracker' not in st.session_state: st.session_state.sim_tracker = None
    if 'sim_avl_tree' not in st.session_state: st.session_state.sim_avl_tree = None
    if 'sim_log' not in st.session_state: st.session_state.sim_log = ""
    if 'sim_clients' not in st.session_state: st.session_state.sim_clients = []
    if 'sim_orders' not in st.session_state: st.session_state.sim_orders = []
    if 'sim_summary' not in st.session_state: st.session_state.sim_summary = ""
    if 'sim_node_counts' not in st.session_state: st.session_state.sim_node_counts = {}
    if 'sim_params' not in st.session_state: st.session_state.sim_params = {} # For num_nodos, etc.
>>>>>>> Stashed changes
    
    # Contenido principal
    if boton_ejecutar:
        with st.spinner("Inicializando simulación..."):
            # Ejecutar simulación y guardar en estado de sesión
            st.session_state.datos_simulacion = ejecutar_simulacion(num_nodos, num_aristas, num_ordenes)
            st.session_state.parametros_simulacion = {
                'num_nodos': num_nodos,
                'num_aristas': num_aristas,
                'num_ordenes': num_ordenes
            }
<<<<<<< Updated upstream
            # Add the following lines here:
            st.session_state.ruta_calculada = None
            st.session_state.mensaje_ruta = ""
    
    # Verificar si existen datos de simulación
    if st.session_state.datos_simulacion is not None:
        grafo, patrones_ruta, reportes_optimizacion, salida_simulacion, tracker, estadisticas_nodos = st.session_state.datos_simulacion
        parametros = st.session_state.parametros_simulacion
        
        # Navegación por pestañas con estado de sesión
        nombres_pestanas = ["🎯 Ejecutar Simulación", "🌐 Explorar Red", "👥 Clientes y Órdenes", "📊 Análisis de Rutas", "📈 Estadísticas"]
        
        # Crear pestañas pero manejar selección manualmente
=======

            # Update shared state for API
            state_instance.update_data(
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

    if st.session_state.sim_graph is not None:
        grafo = st.session_state.sim_graph
        tracker = st.session_state.sim_tracker
        salida_simulacion = st.session_state.sim_log
        estadisticas_nodos = st.session_state.sim_node_counts # Renamed from previous structure
        parametros = st.session_state.sim_params
        patrones_ruta = []
        reportes_optimizacion = []
        nombres_pestanas = ["🎯 Simulación Actual", "🌐 Explorar Red", "👥 Clientes y Órdenes", "📊 Analítica de Rutas", "📈 Estadísticas Generales"]
>>>>>>> Stashed changes
        pestana_seleccionada = st.selectbox("Seleccionar Pestaña:", nombres_pestanas, 
                                           index=st.session_state.active_tab,
                                           key="selector_pestana")
        
        # Actualizar pestaña activa en estado de sesión
        if pestana_seleccionada != nombres_pestanas[st.session_state.active_tab]:
            st.session_state.active_tab = nombres_pestanas.index(pestana_seleccionada)
        
        st.markdown("---")
        
        # Renderizar pestaña apropiada
        if st.session_state.active_tab == 0:  # Ejecutar Simulación
            renderizar_pestana_simulacion(parametros, estadisticas_nodos, salida_simulacion)
        elif st.session_state.active_tab == 1:  # Explorar Red
            renderizar_pestana_red(grafo)
        elif st.session_state.active_tab == 2:  # Clientes y Órdenes
<<<<<<< Updated upstream
            renderizar_pestana_clientes_ordenes(tracker)
        elif st.session_state.active_tab == 3:  # Análisis de Rutas
            renderizar_pestana_analisis_rutas(tracker)
        elif st.session_state.active_tab == 4:  # Estadísticas
            renderizar_pestana_estadisticas(grafo, patrones_ruta, reportes_optimizacion, salida_simulacion)
=======
            renderizar_pestana_clientes_ordenes(
                st.session_state.sim_tracker # This tab uses tracker for client/order stats
            )
        elif st.session_state.active_tab == 3:  # Analítica de Rutas
            renderizar_pestana_analisis_rutas(
                st.session_state.sim_tracker, # Passes tracker
                st.session_state.sim_avl_tree  # Passes AVL tree instance
            )
        elif st.session_state.active_tab == 4:  # Estadísticas Generales
            renderizar_pestana_estadisticas(
                st.session_state.sim_graph,
                patrones_ruta, # Placeholder, can be enhanced if RouteOptimizer is used more
                reportes_optimizacion, # Placeholder
                st.session_state.sim_log
            )
>>>>>>> Stashed changes
    
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