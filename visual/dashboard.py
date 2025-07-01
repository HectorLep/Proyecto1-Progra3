import streamlit as st
import pandas as pd
from model.graph import Graph
from tda.avl import AVLTree 
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator 
import time
from visual.AVLVisualizer import AVLTreeVisualizer
from visual.AVLVisualizer import get_tree_traversals
from validaciones.validaciones import *
from visual.networkx_adapter import crear_visualizacion_red
from visual.AVLVisualizer import create_pie_chart, create_bar_chart
import io
import sys
from api.shared_simulation_state import state_instance
from visual.map.map_builder import create_empty_map, add_nodes_to_map, add_edges_to_map, highlight_path_on_map, highlight_mst_on_map
from visual.map.flight_summary import display_route_details
from .report_generator import generate_pdf_report_content, get_report_filename

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
    
    # 5. Restore stdout and get simulation log
    sys.stdout = old_stdout
    salida_simulacion_log = captured_output.getvalue()
    
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
    }

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
                    factor_balance = actual_avl_root_for_viz.balance_factor if hasattr(actual_avl_root_for_viz, 'balance_factor') else visualizador._get_height(actual_avl_root_for_viz.left) - visualizador._get_height(actual_avl_root_for_viz.right)                    # visualizer._get_balance might be safer if balance_factor is not always set on raw nodes by visualizer
                    st.metric("Factor de Balance (raíz)", factor_balance)
                
                # Mostrar información detallada del árbol
                with st.expander("🔍 Información Detallada del Árbol AVL"):
                    st.markdown("**Características del Árbol AVL:**")
                    st.markdown("- **Balanceado**: El árbol mantiene el balance automáticamente.")
                    st.markdown("- **Clave**: String de Ruta (ej: 'N1->N2->N3').")
                    st.markdown("- **Valor**: Frecuencia de uso de la ruta.")
                    st.markdown("- **Ordenamiento**: Por string de ruta (orden lexicográfico).")
                    st.markdown("**Recorridos del Árbol (Primeros 50 Nodos):**")
                    traversals = get_tree_traversals(visualizador, actual_avl_root_for_viz)                    
                    st.text(f"Inorden (claves): {traversals['inorder']}")                    
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