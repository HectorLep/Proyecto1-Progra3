from graph import Graph
from collections import deque
import heapq
import random

# Implementación de AVL Tree modificada para manejar strings y contadores
class AVLNode:
    def __init__(self, route, frequency=1):
        self.route = route
        self.frequency = frequency
        self.left = None
        self.right = None
        self.height = 0

def avl_height(node):
    return -1 if node is None else node.height

def avl_balance(node):
    return 0 if node is None else avl_height(node.left) - avl_height(node.right)

def avl_right_rotate(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1
    return x

def avl_left_rotate(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1
    return y

def avl_insert(node, route):
    if node is None:
        return AVLNode(route)
    
    if route < node.route:
        node.left = avl_insert(node.left, route)
    elif route > node.route:
        node.right = avl_insert(node.right, route)
    else:
        node.frequency += 1
        return node
    
    node.height = max(avl_height(node.left), avl_height(node.right)) + 1
    balance = avl_balance(node)
    
    if balance > 1 and route < node.left.route:
        return avl_right_rotate(node)
    if balance < -1 and route > node.right.route:
        return avl_left_rotate(node)
    if balance > 1 and route > node.left.route:
        node.left = avl_left_rotate(node.left)
        return avl_right_rotate(node)
    if balance < -1 and route < node.right.route:
        node.right = avl_right_rotate(node.right)
        return avl_left_rotate(node)
    
    return node

def avl_search(node, route):
    if node is None or node.route == route:
        return node
    if route < node.route:
        return avl_search(node.left, route)
    return avl_search(node.right, route)

def avl_inorder(node, result):
    if node:
        avl_inorder(node.left, result)
        result.append((node.route, node.frequency))
        avl_inorder(node.right, result)

# Diccionario para mapear IDs de nodos a sus nombres descriptivos
node_names = {
    'A': 'Almacen_A',
    'B': 'Estacion_B', 
    'C': 'Client_C',
    'D': 'Client_D',
    'R1': 'Recarga_R1'
}

node_types = {
    'A': 'warehouse',
    'B': 'recharge',
    'C': 'client',
    'D': 'client',
    'R1': 'recharge'
}

class RouteManager:
    def __init__(self, graph):
        self.graph = graph
        self.node_types = node_types

    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        """BFS modificado que considera el costo acumulado usando heap"""
        heap = [(0, origin_id, [origin_id], battery_limit, [], [[origin_id]])]
        visited = {}
        vertex_map = {v.element(): v for v in self.graph.vertices()}

        while heap:
            total_cost, node, path, battery, recharge_stops, segments = heapq.heappop(heap)
            
            state = (node, battery)
            if state in visited and visited[state] <= total_cost:
                continue
            visited[state] = total_cost
            
            if node == destination_id:
                final_recharge_stops = [n for n in path if self.node_types.get(n) == 'recharge']
                return {
                    'path': path,
                    'total_cost': total_cost,
                    'recharge_stops': final_recharge_stops,
                    'segments': segments
                }

            current_vertex = vertex_map[node]
            for edge in self.graph.incident_edges(current_vertex, outgoing=True):
                next_vertex = edge.opposite(current_vertex)
                next_node = next_vertex.element()
                weight = edge.element()
                new_battery = battery - weight

                if new_battery >= 0:
                    new_state = (next_node, new_battery)
                    new_cost = total_cost + weight
                    
                    if new_state not in visited or visited[new_state] > new_cost:
                        new_path = path + [next_node]
                        new_segments = [seg[:] for seg in segments]
                        new_segments[-1].append(next_node)
                        heapq.heappush(heap, (new_cost, next_node, new_path, new_battery, recharge_stops, new_segments))
                
                else:
                    recharge_node = self.find_nearest_recharge(node)
                    if recharge_node and recharge_node != node:
                        recharge_path, recharge_cost = self.get_path_to_recharge(node, recharge_node)
                        if recharge_path:
                            new_path = path + recharge_path[1:]
                            new_recharge_stops = recharge_stops + [recharge_node]
                            new_segments = [seg[:] for seg in segments] + [[recharge_node]]
                            new_total_cost = total_cost + recharge_cost
                            new_state = (recharge_node, battery_limit)
                            
                            if new_state not in visited or visited[new_state] > new_total_cost:
                                heapq.heappush(heap, (new_total_cost, recharge_node, new_path, battery_limit, new_recharge_stops, new_segments))
        
        return None

    def find_nearest_recharge(self, node):
        """Encontrar estación de recarga más cercana usando BFS"""
        if self.node_types.get(node) == 'recharge':
            return node
            
        vertex_map = {v.element(): v for v in self.graph.vertices()}
        queue = deque([(node, 0)])
        visited = set([node])
        
        while queue:
            curr, dist = queue.popleft()
            if self.node_types.get(curr) == 'recharge':
                return curr
                
            current_vertex = vertex_map[curr]
            for edge in self.graph.incident_edges(current_vertex, outgoing=True):
                next_vertex = edge.opposite(current_vertex)
                next_node = next_vertex.element()
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, dist + edge.element()))
        return None

    def get_path_to_recharge(self, start, recharge):
        """Obtener el camino más corto a una estación de recarga"""
        vertex_map = {v.element(): v for v in self.graph.vertices()}
        queue = deque([(vertex_map[start], [start], 0)])
        visited = set([start])
        
        while queue:
            node, path, cost = queue.popleft()
            if node.element() == recharge:
                return path, cost
                
            for edge in self.graph.incident_edges(node, outgoing=True):
                next_vertex = edge.opposite(node)
                next_node = next_vertex.element()
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_vertex, path + [next_node], cost + edge.element()))
        return None, 0

class RouteTracker:
    def __init__(self):
        self.route_frequency_avl = None  # AVL tree para frecuencias de rutas
        self.node_visits = {}
        self.hashmap = self.create_custom_hashmap()

    def create_custom_hashmap(self, initial_size=17):
        """Crear HashMap básico con tamaño primo para mejor distribución"""
        return [[] for _ in range(initial_size)]

    def hash_function(self, key):
        """Función hash mejorada para mejor distribución"""
        if isinstance(key, str):
            return sum(ord(c) * (i + 1) for i, c in enumerate(str(key))) % len(self.hashmap)
        return hash(key) % len(self.hashmap)

    def register_route(self, route_path, cost):
        """Registrar ruta usando AVL para frecuencias y HashMap para visitas de nodos"""
        route_str = "→".join(str(node) for node in route_path)
        
        # Usar AVL para frecuencias de rutas
        self.route_frequency_avl = avl_insert(self.route_frequency_avl, route_str)
        
        # HashMap para contar visitas por nodo
        for node in route_path:
            self.node_visits[node] = self.node_visits.get(node, 0) + 1
            hash_index = self.hash_function(node)
            
            # Buscar si el nodo ya existe en la cadena de colisiones
            found = False
            for i, (key, value) in enumerate(self.hashmap[hash_index]):
                if key == node:
                    self.hashmap[hash_index][i] = (key, value + 1)
                    found = True
                    break
            
            if not found:
                self.hashmap[hash_index].append((node, 1))

    def get_most_frequent_routes(self, top_n=5):
        """Obtener las rutas más frecuentes del AVL"""
        if self.route_frequency_avl is None:
            return []
        
        routes = []
        avl_inorder(self.route_frequency_avl, routes)
        return sorted(routes, key=lambda x: x[1], reverse=True)[:top_n]

    def get_node_visit_stats(self):
        """Obtener estadísticas de visitas por nodo"""
        return sorted(self.node_visits.items(), key=lambda x: x[1], reverse=True)

    def get_hashmap_stats(self):
        """Obtener estadísticas del HashMap implementado"""
        stats = []
        for i, chain in enumerate(self.hashmap):
            if chain:
                stats.extend(chain)
        return sorted(stats, key=lambda x: x[1], reverse=True)

class RouteOptimizer:
    def __init__(self, route_tracker, route_manager):
        self.route_tracker = route_tracker
        self.route_manager = route_manager
        self.optimization_log = []

    def suggest_optimized_route(self, origin_id, destination_id):
        """Sugerir ruta optimizada basada en historial"""
        # Buscar ruta exacta en el historial
        for route, freq in self.route_tracker.get_most_frequent_routes(10):
            nodes = route.split("→")
            if nodes[0] == str(origin_id) and nodes[-1] == str(destination_id):
                self.optimization_log.append(f"Ruta exacta encontrada en historial: {route} (usado {freq} veces)")
                return {'path': nodes, 'total_cost': 0, 'recharge_stops': [], 'segments': [nodes]}

        # Buscar segmentos parciales útiles
        segments = []
        for route, freq in self.route_tracker.get_most_frequent_routes(10):
            nodes = route.split("→")
            if str(origin_id) in nodes and str(destination_id) in nodes:
                idx_start = nodes.index(str(origin_id))
                idx_end = nodes.index(str(destination_id))
                if idx_start < idx_end:
                    segments.append((nodes[idx_start:idx_end+1], freq))
        
        if segments:
            # Priorizar segmento con mayor frecuencia de uso
            best_segment = max(segments, key=lambda x: x[1])
            self.optimization_log.append(f"Segmento parcial optimizado usado: {best_segment[0]} (frecuencia: {best_segment[1]})")
            return {'path': best_segment[0], 'total_cost': 0, 'recharge_stops': [], 'segments': [best_segment[0]]}

        # Calcular nueva ruta si no hay historial útil
        result = self.route_manager.find_route_with_recharge(origin_id, destination_id)
        if result:
            self.route_tracker.register_route(result['path'], result['total_cost'])
            self.optimization_log.append(f"Nueva ruta calculada y registrada: {result['path']}")
            return result
        
        return None

    def analyze_route_patterns(self):
        """Analizar patrones de rutas para optimización futura"""
        patterns = []
        
        # Patrones de rutas frecuentes
        patterns.append("=== ANÁLISIS DE PATRONES DE RUTAS ===")
        for route, freq in self.route_tracker.get_most_frequent_routes():
            patterns.append(f"Ruta frecuente: {route} | Usos: {freq}")
        
        # Nodos más visitados
        patterns.append("\n=== NODOS MÁS VISITADOS ===")
        for node, visits in self.route_tracker.get_node_visit_stats()[:5]:
            node_name = node_names.get(node, node)
            patterns.append(f"Nodo: {node_name} ({node}) | Visitas: {visits}")
        
        # Estadísticas del HashMap
        patterns.append("\n=== ESTADÍSTICAS HASHMAP ===")
        for node, visits in self.route_tracker.get_hashmap_stats()[:5]:
            node_name = node_names.get(node, node)
            patterns.append(f"HashMap - {node_name}: {visits} visitas")
        
        return patterns

    def get_optimization_report(self):
        """Generar reporte de optimizaciones realizadas"""
        return self.optimization_log

class OrderSimulator:
    def __init__(self, route_manager, route_tracker):
        self.route_manager = route_manager
        self.route_tracker = route_tracker

    def process_orders(self, num_orders=10):
        """Procesar órdenes con formato de salida requerido"""
        warehouses = [v.element() for v in self.route_manager.graph.vertices() 
                     if self.route_manager.node_types.get(v.element()) == 'warehouse']
        clients = [v.element() for v in self.route_manager.graph.vertices() 
                  if self.route_manager.node_types.get(v.element()) == 'client']
        
        for i in range(num_orders):
            if not warehouses or not clients:
                print(f"Orden #{i+1}: No hay almacenes o clientes disponibles")
                continue
                
            origin = random.choice(warehouses)
            destination = random.choice(clients)
            
            route_info = self.route_manager.find_route_with_recharge(origin, destination)
            
            if route_info:
                self.route_tracker.register_route(route_info['path'], route_info['total_cost'])
                
                # Formato de salida exacto según requerimientos
                origin_name = node_names.get(origin, f"Nodo_{origin}")
                dest_name = node_names.get(destination, f"Nodo_{destination}")
                route_names = [node_names.get(node, f"Nodo_{node}") for node in route_info['path']]
                recharge_names = [node_names.get(node, f"Nodo_{node}") for node in route_info['recharge_stops']]
                
                print(f"Orden #{i+1}: {origin_name} → {dest_name}")
                print(f"Ruta: {' → '.join(route_names)}")
                print(f"Costo: {route_info['total_cost']} | Paradas de recarga: {recharge_names} | Estado: Entregado")
            else:
                origin_name = node_names.get(origin, f"Nodo_{origin}")
                dest_name = node_names.get(destination, f"Nodo_{destination}")
                print(f"Orden #{i+1}: {origin_name} → {dest_name}")
                print(f"Estado: No se encontró ruta válida")

if __name__ == "__main__":
    # Crear grafo de ejemplo
    g = Graph()
    
    # Insertar vértices
    vertices = {
        'A': g.insert_vertex('A'),
        'B': g.insert_vertex('B'),
        'C': g.insert_vertex('C'),
        'D': g.insert_vertex('D'),
        'R1': g.insert_vertex('R1')
    }
    
    # Insertar aristas con pesos (costo energético)
    g.insert_edge(vertices['A'], vertices['B'], 20)
    g.insert_edge(vertices['B'], vertices['A'], 20)
    g.insert_edge(vertices['B'], vertices['C'], 20)
    g.insert_edge(vertices['C'], vertices['B'], 20)
    g.insert_edge(vertices['A'], vertices['R1'], 15)
    g.insert_edge(vertices['R1'], vertices['A'], 15)
    g.insert_edge(vertices['R1'], vertices['D'], 15)
    g.insert_edge(vertices['D'], vertices['R1'], 15)
    g.insert_edge(vertices['A'], vertices['C'], 45)  # Ruta directa costosa
    g.insert_edge(vertices['C'], vertices['A'], 45)
    
    # Inicializar sistema
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    # Procesar órdenes de prueba
    print("=== SIMULACIÓN DE ÓRDENES ===")
    simulator.process_orders(5)
    
    # Mostrar estadísticas
    print("\n=== ANÁLISIS DE PATRONES ===")
    for pattern in optimizer.analyze_route_patterns():
        print(pattern)
    
    # Mostrar log de optimizaciones
    print("\n=== REPORTE DE OPTIMIZACIONES ===")
    for log in optimizer.get_optimization_report():
        print(log)