import matplotlib.pyplot as plt
import networkx as nx
from model.graph import Graph

def grafo_a_networkx(grafo):
    """Convertir Grafo personalizado a NetworkX DiGraph"""
    G = nx.DiGraph()
    
    # Agregar nodos con sus tipos
    for vertice in grafo.vertices():
        id_nodo = vertice.element()
        tipo_nodo = vertice.type()
        G.add_node(id_nodo, type=tipo_nodo)
    
    # Agregar aristas
    for arista in grafo.edges():
        u, v = arista.endpoints()
        peso = arista.element()
        G.add_edge(u.element(), v.element(), weight=peso)
    
    return G

def crear_visualizacion_red(grafo, ruta_destacada=None, figsize=(12, 10)):
    """Crear una visualización completa de la red con características mejoradas"""
    G = grafo_a_networkx(grafo)
    
    # Usar diferentes algoritmos de diseño basados en el tamaño del grafo
    num_nodos = len(G.nodes())
    if num_nodos < 20:
        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    elif num_nodos < 50:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)
    
    # Crear la figura con tamaño más grande
    plt.figure(figsize=figsize)
    
    # Colorear nodos según su tipo con colores mejorados
    colores_nodos = []
    tamaños_nodos = []
    for nodo in G.nodes():
        tipo_nodo = G.nodes[nodo].get('type', 'client')
        if tipo_nodo == 'warehouse':
            colores_nodos.append('#8B4513')  # Marrón
            tamaños_nodos.append(800)  # Más grande para almacenes
        elif tipo_nodo == 'recharge':
            colores_nodos.append('#FFA500')  # Naranja
            tamaños_nodos.append(600)  # Mediano para estaciones de recarga
        else:  # client
            colores_nodos.append('#32CD32')  # Verde
            tamaños_nodos.append(400)  # Más pequeño para clientes
    
    # Dibujar los nodos con estilo mejorado
    nx.draw_networkx_nodes(G, pos, 
                          node_color=colores_nodos, 
                          node_size=tamaños_nodos,
                          alpha=0.8,
                          edgecolors='black',
                          linewidths=1.5)
    
    # Preparar colores y anchos de aristas
    colores_aristas = []
    anchos_aristas = []
    
    for arista in G.edges():
        colores_aristas.append('#888888')  # Gris por defecto
        anchos_aristas.append(1.0)  # Ancho por defecto
    
    # Destacar la ruta en rojo si se proporciona
    if ruta_destacada:
        aristas_ruta = [(ruta_destacada[i], ruta_destacada[i+1]) 
                       for i in range(len(ruta_destacada)-1)]
        
        for i, arista in enumerate(G.edges()):
            if arista in aristas_ruta or (arista[1], arista[0]) in aristas_ruta:
                colores_aristas[i] = '#FF0000'  # Rojo para ruta destacada
                anchos_aristas[i] = 3.0  # Más grueso para ruta destacada
    
    # Dibujar aristas con estilo mejorado
    nx.draw_networkx_edges(G, pos, 
                          edge_color=colores_aristas, 
                          width=anchos_aristas,
                          arrows=True, 
                          arrowsize=20,
                          arrowstyle='->', 
                          alpha=0.7,
                          connectionstyle="arc3,rad=0.1")
    
    # Dibujar etiquetas de nodos con mejor formato
    nx.draw_networkx_labels(G, pos, 
                           font_size=9, 
                           font_weight='bold',
                           font_color='white',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='black', 
                                   alpha=0.7))
    
    # Dibujar etiquetas de aristas (pesos) con posicionamiento mejorado
    etiquetas_aristas = nx.get_edge_attributes(G, 'weight')
    # Formatear etiquetas de aristas para mostrar solo 2 decimales
    etiquetas_formateadas = {k: f"{v:.1f}" for k, v in etiquetas_aristas.items()}
    
    nx.draw_networkx_edge_labels(G, pos, 
                                edge_labels=etiquetas_formateadas, 
                                font_size=7,
                                font_color='darkblue',
                                bbox=dict(boxstyle="round,pad=0.2", 
                                        facecolor='white', 
                                        alpha=0.8))
    
    # Título mejorado
    titulo = "Red de Entrega por Drones"
    if ruta_destacada:
        titulo += f" - Ruta: {' → '.join(ruta_destacada)}"
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    # Remover ejes
    plt.axis('off')
    
    # Crear leyenda mejorada
    from matplotlib.lines import Line2D
    elementos_leyenda = [
        Line2D([0], [0], marker='o', color='w', label='Almacén', 
               markerfacecolor='#8B4513', markersize=12, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Estación de Recarga', 
               markerfacecolor='#FFA500', markersize=10, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Cliente', 
               markerfacecolor='#32CD32', markersize=8, markeredgecolor='black'),
        Line2D([0], [0], color='#888888', label='Ruta Regular', linewidth=2),
    ]
    
    if ruta_destacada:
        elementos_leyenda.append(
            Line2D([0], [0], color='#FF0000', label='Ruta Destacada', linewidth=3)
        )
    
    plt.legend(handles=elementos_leyenda, 
              loc='upper left', 
              bbox_to_anchor=(0.02, 0.98),
              fontsize=10,
              frameon=True,
              fancybox=True,
              shadow=True)
    
    # Agregar estadísticas de la red como texto
    texto_estadisticas = f"Nodos: {len(G.nodes())} | Aristas: {len(G.edges())}"
    if ruta_destacada:
        costo_ruta = sum(G[ruta_destacada[i]][ruta_destacada[i+1]]['weight'] 
                        for i in range(len(ruta_destacada)-1))
        texto_estadisticas += f" | Costo de Ruta: {costo_ruta:.2f}"
    
    plt.figtext(0.02, 0.02, texto_estadisticas, fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return plt.gcf()

def crear_visualizacion_comparacion_rutas(grafo, lista_rutas, etiquetas_rutas=None):
    """Crear una visualización comparando múltiples rutas"""
    G = grafo_a_networkx(grafo)
    pos = nx.spring_layout(G, k=1.0, iterations=100, seed=42)
    
    # Crear subgráficos para cada ruta
    num_rutas = len(lista_rutas)
    fig, axes = plt.subplots(1, num_rutas, figsize=(6*num_rutas, 6))
    
    if num_rutas == 1:
        axes = [axes]
    
    colores = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFFF00']
    
    for idx, (ruta, ax) in enumerate(zip(lista_rutas, axes)):
        # Colorear nodos según su tipo
        colores_nodos = []
        tamaños_nodos = []
        for nodo in G.nodes():
            tipo_nodo = G.nodes[nodo].get('type', 'client')
            if tipo_nodo == 'warehouse':
                colores_nodos.append('#8B4513')
                tamaños_nodos.append(600)
            elif tipo_nodo == 'recharge':
                colores_nodos.append('#FFA500')
                tamaños_nodos.append(450)
            else:
                colores_nodos.append('#32CD32')
                tamaños_nodos.append(300)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(G, pos, 
                              node_color=colores_nodos, 
                              node_size=tamaños_nodos,
                              alpha=0.8,
                              ax=ax)
        
        # Dibujar todas las aristas en gris
        nx.draw_networkx_edges(G, pos, 
                              edge_color='#CCCCCC', 
                              arrows=True, 
                              arrowsize=15,
                              alpha=0.5,
                              ax=ax)
        
        # Destacar ruta actual
        if ruta:
            aristas_ruta = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
            nx.draw_networkx_edges(G, pos,
                                  edgelist=aristas_ruta,
                                  edge_color=colores[idx % len(colores)],
                                  width=3.0,
                                  arrows=True,
                                  arrowsize=20,
                                  ax=ax)
        
        # Dibujar etiquetas
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
        
        # Establecer título
        titulo = etiquetas_rutas[idx] if etiquetas_rutas else f"Ruta {idx+1}"
        if ruta:
            costo_ruta = sum(G[ruta[i]][ruta[i+1]]['weight'] 
                           for i in range(len(ruta)-1))
            titulo += f" (Costo: {costo_ruta:.2f})"
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    return fig

def analizar_propiedades_red(grafo):
    """Analizar y devolver propiedades de la red"""
    G = grafo_a_networkx(grafo)
    
    propiedades = {
        'num_nodos': len(G.nodes()),
        'num_aristas': len(G.edges()),
        'densidad': nx.density(G),
        'esta_conectado': nx.is_weakly_connected(G),
        'num_componentes': nx.number_weakly_connected_components(G),
        'grado_promedio': sum(dict(G.degree()).values()) / len(G.nodes()) if len(G.nodes()) > 0 else 0,
        'coeficiente_clustering': nx.average_clustering(G.to_undirected()),
        'diametro': nx.diameter(G.to_undirected()) if nx.is_connected(G.to_undirected()) else 'N/A (desconectado)',
        'tipos_nodos': {
            'warehouse': len([n for n, d in G.nodes(data=True) if d.get('type') == 'warehouse']),
            'recharge': len([n for n, d in G.nodes(data=True) if d.get('type') == 'recharge']),
            'client': len([n for n, d in G.nodes(data=True) if d.get('type') == 'client'])
        }
    }
    
    return propiedades

def crear_reporte_analisis_red(grafo):
    """Generar un reporte completo de análisis de la red"""
    propiedades = analizar_propiedades_red(grafo)
    
    reporte = f"""
    📊 REPORTE DE ANÁLISIS DE RED
    ============================
    
    🔢 Estadísticas Básicas:
    - Total de Nodos: {propiedades['num_nodos']}
    - Total de Aristas: {propiedades['num_aristas']}
    - Densidad del Grafo: {propiedades['densidad']:.3f}
    - Grado Promedio: {propiedades['grado_promedio']:.2f}
    
    🔗 Conectividad:
    - Está Conectado: {propiedades['esta_conectado']}
    - Número de Componentes: {propiedades['num_componentes']}
    - Coeficiente de Clustering: {propiedades['coeficiente_clustering']:.3f}
    - Diámetro: {propiedades['diametro']}
    
    🏢 Distribución de Nodos:
    - Nodos Almacén: {propiedades['tipos_nodos']['warehouse']}
    - Estaciones de Recarga: {propiedades['tipos_nodos']['recharge']}
    - Nodos Cliente: {propiedades['tipos_nodos']['client']}
    
    📈 Proporciones:
    - Almacenes: {propiedades['tipos_nodos']['warehouse']/propiedades['num_nodos']*100:.1f}%
    - Estaciones de Recarga: {propiedades['tipos_nodos']['recharge']/propiedades['num_nodos']*100:.1f}%
    - Clientes: {propiedades['tipos_nodos']['client']/propiedades['num_nodos']*100:.1f}%
    """
    
    return reporte

def obtener_analisis_rutas_mas_cortas(grafo, nodos_origen=None):
    """Analizar rutas más cortas desde nodos origen hacia todos los otros nodos"""
    G = grafo_a_networkx(grafo)
    
    if nodos_origen is None:
        # Usar todos los nodos almacén como orígenes
        nodos_origen = [n for n, d in G.nodes(data=True) if d.get('type') == 'warehouse']
    
    analisis = {}
    
    for origen in nodos_origen:
        try:
            # Calcular rutas más cortas desde origen hacia todos los otros nodos
            longitudes = nx.single_source_dijkstra_path_length(G, origen, weight='weight')
            rutas = nx.single_source_dijkstra_path(G, origen, weight='weight')
            
            analisis[origen] = {
                'nodos_alcanzables': len(longitudes),
                'total_nodos': len(G.nodes()),
                'longitud_promedio_ruta': sum(longitudes.values()) / len(longitudes) if longitudes else 0,
                'longitud_maxima_ruta': max(longitudes.values()) if longitudes else 0,
                'rutas_a_clientes': {nodo: {'longitud': longitud, 'ruta': rutas[nodo]} 
                                   for nodo, longitud in longitudes.items() 
                                   if G.nodes[nodo].get('type') == 'client'}
            }
        except nx.NetworkXNoPath:
            analisis[origen] = {
                'nodos_alcanzables': 0,
                'total_nodos': len(G.nodes()),
                'longitud_promedio_ruta': float('inf'),
                'longitud_maxima_ruta': float('inf'),
                'rutas_a_clientes': {}
            }
    
    return analisis

def crear_grafico_distribucion_grados(grafo):
    """Crear un gráfico de distribución de grados"""
    G = grafo_a_networkx(grafo)
    
    # Calcular distribución de grados
    grados = [G.degree(n) for n in G.nodes()]
    
    plt.figure(figsize=(10, 6))
    plt.hist(grados, bins=max(1, len(set(grados))), color='#45b7d1', alpha=0.7, edgecolor='black')
    plt.title('Distribución de Grados de Nodos', fontsize=14, fontweight='bold')
    plt.xlabel('Grado', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Agregar texto de estadísticas
    grado_promedio = sum(grados) / len(grados) if grados else 0
    grado_maximo = max(grados) if grados else 0
    grado_minimo = min(grados) if grados else 0
    
    texto_estadisticas = f'Promedio: {grado_promedio:.2f}, Máx: {grado_maximo}, Mín: {grado_minimo}'
    plt.text(0.7, 0.9, texto_estadisticas, transform=plt.gca().transAxes, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return plt.gcf()

def crear_grafico_distribucion_tipos_nodos(grafo):
    """Crear un gráfico mostrando la distribución de tipos de nodos"""
    G = grafo_a_networkx(grafo)
    
    # Contar tipos de nodos
    conteos_tipos = {'warehouse': 0, 'recharge': 0, 'client': 0}
    for nodo, datos in G.nodes(data=True):
        tipo_nodo = datos.get('type', 'client')
        conteos_tipos[tipo_nodo] += 1
    
    # Crear gráfico de pastel
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Gráfico de pastel
    colores = ['#8B4513', '#FFA500', '#32CD32']
    etiquetas = ['Almacén', 'Recarga', 'Cliente']
    tamaños = [conteos_tipos['warehouse'], conteos_tipos['recharge'], conteos_tipos['client']]
    
    ax1.pie(tamaños, labels=etiquetas, colors=colores, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Distribución de Tipos de Nodos', fontsize=14, fontweight='bold')
    
    # Gráfico de barras
    ax2.bar(etiquetas, tamaños, color=colores, alpha=0.7, edgecolor='black')
    ax2.set_title('Conteo de Tipos de Nodos', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Cantidad')
    
    # Agregar etiquetas de valor en las barras
    for i, v in enumerate(tamaños):
        ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig