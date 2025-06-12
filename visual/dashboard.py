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
from visual.networkx_adapter import crear_visualizacion_red
from visual.AVLVisualizer import create_pie_chart, create_bar_chart, create_horizontal_bar_chart
import numpy as np
import io
import sys

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
    
    sys.stdout = old_stdout
    salida_simulacion = captured_output.getvalue()
    
    # Obtener estadísticas
    patrones_ruta = optimizer.analyze_route_patterns()
    reportes_optimizacion = optimizer.get_optimization_report()
    
    # Estadísticas del grafo
    estadisticas_nodos = {
        'almacen': len([v for v in g.vertices() if v.type() == 'warehouse']),
        'recarga': len([v for v in g.vertices() if v.type() == 'recharge']),
        'cliente': len([v for v in g.vertices() if v.type() == 'client'])
    }
    
    return g, patrones_ruta, reportes_optimizacion, salida_simulacion, tracker, estadisticas_nodos

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
    
    # Estadísticas de órdenes
    estadisticas_ordenes = tracker.get_order_stats()
    if estadisticas_ordenes:
        st.subheader("💰 Órdenes por Costo")
        datos_ordenes = [(oid, order.total_cost, order.status) for oid, order in estadisticas_ordenes[:10]]
        df_ordenes = pd.DataFrame(datos_ordenes, columns=['ID Orden', 'Costo Total', 'Estado'])
        st.dataframe(df_ordenes, use_container_width=True)
        
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
    """Renderizar la pestaña de análisis de rutas"""
    st.header("📊 Análisis de Rutas")
    
    # Mostrar patrones de rutas
    st.subheader("🛣️ Frecuencia e Historial de Rutas")
    
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
        
        # Gráfico de frecuencia de rutas
        if len(rutas_frecuentes) > 0:
            etiquetas_rutas = [f"Ruta {i+1}" for i in range(len(rutas_frecuentes))]
            frecuencias_rutas = [freq for _, freq in rutas_frecuentes]
            
            fig_rutas = create_horizontal_bar_chart(
                x_data=frecuencias_rutas,
                y_data=etiquetas_rutas,
                title='Rutas Más Frecuentes',
                color='#ff6b6b'
            )
            st.pyplot(fig_rutas)
    
    # Estadísticas de visitas a nodos
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
    if 'datos_simulacion' not in st.session_state:
        st.session_state.datos_simulacion = None
    
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
            renderizar_pestana_clientes_ordenes(tracker)
        elif st.session_state.active_tab == 3:  # Análisis de Rutas
            renderizar_pestana_analisis_rutas(tracker)
        elif st.session_state.active_tab == 4:  # Estadísticas
            renderizar_pestana_estadisticas(grafo, patrones_ruta, reportes_optimizacion, salida_simulacion)
    
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