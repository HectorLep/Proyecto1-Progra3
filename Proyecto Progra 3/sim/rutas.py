from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.mapa_hash import HashMap
from tda.avl import AVLNode, avl_insert, avl_search, avl_inorder, avl_to_visualization_data
from collections import deque
import heapq
import random

# # Diccionario para mapear IDs de nodos a sus nombres descriptivos
# node_names = {
#     'A': 'Almacen_A',
#     'B': 'Estacion_B',
#     'C': 'Client_C',
#     'D': 'Client_D',
#     'R1': 'Recarga_R1'
# }
# 
# node_types = {
#     'A': 'warehouse',
#     'B': 'recharge',
#     'C': 'client',
#     'D': 'client',
#     'R1': 'recharge'
# }

class RouteManager:
    def __init__(self, graph):
        self.graph = graph
        self.vertex_types = {v.element(): v.type() for v in self.graph.vertices()}


    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        """BFS modificado que considera el costo acumulado usando heap."""
        heap = [(0, origin_id, [origin_id], battery_limit, [], [[origin_id]])]
        visited = {}
        vertex_map = {v.element(): v for v in self.graph.vertices()}

        while heap:
            total_cost, node_id, path, battery, recharge_stops, segments = heapq.heappop(heap)
            
            state = (node_id, battery)
            if state in visited and visited[state] <= total_cost:
                continue
            visited[state] = total_cost
            
            if node_id == destination_id:
                final_recharge_stops = [n for n in path if self.vertex_types.get(n) == 'recharge']
                return Route(path, total_cost, final_recharge_stops, segments)

            current_vertex = vertex_map[node_id]
            for edge in self.graph.incident_edges(current_vertex, outgoing=True):
                next_vertex = edge.opposite(current_vertex)
                next_node_id = next_vertex.element()
                weight = edge.element()
                new_battery = battery - weight

                if new_battery >= 0:
                    new_state = (next_node_id, new_battery)
                    new_cost = total_cost + weight
                    
                    if new_state not in visited or visited[new_state] > new_cost:
                        new_path = path + [next_node_id]
                        new_segments = [seg[:] for seg in segments]
                        new_segments[-1].append(next_node_id)
                        heapq.heappush(heap, (new_cost, next_node_id, new_path, new_battery, recharge_stops, new_segments))
                
                else:
                    recharge_node = self.find_nearest_recharge(node_id)
                    if recharge_node and recharge_node != node_id:
                        recharge_path, recharge_cost = self.get_path_to_recharge(node_id, recharge_node)
                        if recharge_path:
                            new_path = path + recharge_path[1:]
                            new_recharge_stops = recharge_stops + [recharge_node]
                            new_segments = [seg[:] for seg in segments] + [[recharge_node]]
                            new_total_cost = total_cost + recharge_cost
                            new_state = (recharge_node, battery_limit)
                            
                            if new_state not in visited or visited[new_state] > new_total_cost:
                                heapq.heappush(heap, (new_total_cost, recharge_node, new_path, battery_limit, new_recharge_stops, new_segments))
        
        return None

    def find_nearest_recharge(self, node_id):
        """Find the nearest recharge station using BFS."""
        if self.vertex_types.get(node_id) == 'recharge':
            return node_id
        
        vertex_map = {v.element(): v for v in self.graph.vertices()}
        queue = deque([(node_id, 0)])
        visited = set([node_id])
        
        while queue:
            curr, dist = queue.popleft()
            if self.vertex_types.get(curr) == 'recharge':
                return curr
            
            current_vertex = vertex_map[curr]
            for edge in self.graph.incident_edges(current_vertex, outgoing=True):
                next_vertex = edge.opposite(current_vertex)
                next_node_id = next_vertex.element()
                if next_node_id not in visited:
                    visited.add(next_node_id)
                    queue.append((next_node_id, dist + edge.element()))
        
        return None


    def get_path_to_recharge(self, start, recharge):
        """Find the shortest path to a recharge station."""
        vertex_map = {v.element(): v for v in self.graph.vertices()}
        start_vertex = vertex_map[start]  # Obtener el objeto Vertex
        recharge_vertex = vertex_map[recharge]  # Obtener el objeto Vertex
        queue = deque([(start_vertex, [start], 0)])
        visited = set([start])
        
        while queue:
            node, path, cost = queue.popleft()
            if node.element() == recharge_vertex.element():
                return path, cost
                
            for edge in self.graph.incident_edges(node, outgoing=True):
                next_vertex = edge.opposite(node)
                next_node_id = next_vertex.element()
                if next_node_id not in visited:
                    visited.add(next_node_id)
                    queue.append((next_vertex, path + [next_node_id], cost + edge.element()))
        return None, 0
    
class RouteTracker:
    def __init__(self):
        self.route_frequency_avl = None
        self.node_visits = HashMap()
        self.clients = HashMap()
        self.orders = HashMap()

    def register_route(self, route, order):
        """Register a route using AVL and update clients/orders."""
        route_str = "→".join(str(node_id) for node_id in route.path)
        
        # actualiza AVL por ruta de frecuencia
        self.route_frequency_avl = avl_insert(self.route_frequency_avl, route_str)
        
        # actualiza la visita de nodos
        for node_id in route.path:
            count = self.node_visits.get(node_id) or 0
            self.node_visits.put(node_id, count + 1)
        
        # registra cliente y orden
        self.clients.put(order.client_id, order.client)
        self.orders.put(order.id, order)

    def register_route_frequency(self, route_str):
        """Register route frequency in AVL."""
        self.route_frequency_avl = avl_insert(self.route_frequency_avl, route_str)

    def get_most_frequent_routes(self, top_n=5):
        """Get the most frequent routes from the AVL."""
        if self.route_frequency_avl is None:
            return []
        
        routes = []
        avl_inorder(self.route_frequency_avl, routes)
        return sorted(routes, key=lambda x: x[1], reverse=True)[:top_n]

    def get_node_visit_stats(self):
        """Get node visit statistics."""
        stats = []
        for bucket in self.node_visits.buckets:
            for key, value in bucket:
                stats.append((key, value))
        return sorted(stats, key=lambda x: x[1], reverse=True)

    def get_client_stats(self):
        """Get client statistics based on total orders."""
        stats = []
        for bucket in self.clients.buckets:
            for key, client in bucket:
                stats.append((key, client.total_orders))
        return sorted(stats, key=lambda x: x[1], reverse=True)

    def get_order_stats(self):
        """Get order statistics based on total cost."""
        stats = []
        for bucket in self.orders.buckets:
            for key, order in bucket:
                stats.append((key, order))
        return sorted(stats, key=lambda x: x[1].total_cost, reverse=True)

class RouteOptimizer:
    def __init__(self, route_tracker, route_manager):
        self.route_tracker = route_tracker
        self.route_manager = route_manager
        self.optimization_log = []

    def analyze_route_patterns(self):
        """Analyze route patterns for future optimization."""
        patterns = []
        
        # Frequent routes
        patterns.append("=== ANÁLISIS DE PATRONES DE RUTAS ===")
        for route, freq in self.route_tracker.get_most_frequent_routes():
            patterns.append(f"Ruta frecuente: {route} | Usos: {freq}")
        
        # Most visited nodes
        patterns.append("\n=== NODOS MÁS VISITADOS ===")
        for node, visits in self.route_tracker.get_node_visit_stats()[:5]:

            patterns.append(f"Nodo: {node} | Visitas: {visits}")
        
        # Client statistics
        patterns.append("\n=== ESTADÍSTICAS DE CLIENTES ===")
        for client_id, orders in self.route_tracker.get_client_stats()[:5]:

            patterns.append(f"Cliente: {client_id} | Órdenes: {orders}")
        
        return patterns

    def get_optimization_report(self):
        """Generate a report of optimizations performed."""
        return self.optimization_log

class OrderSimulator:
    def __init__(self, route_manager, route_tracker):
        self.route_manager = route_manager
        self.route_tracker = route_tracker

    def process_orders(self, num_orders=10):
        """Process orders with required output format."""
        warehouses = [v.element() for v in self.route_manager.graph.vertices() 
                     if self.route_manager.vertex_types.get(v.element()) == 'warehouse']
        clients = [v.element() for v in self.route_manager.graph.vertices() 
                  if self.route_manager.vertex_types.get(v.element()) == 'client']
        
        for i in range(num_orders):
            if not warehouses or not clients:
                print(f"Orden #{i+1}: No hay almacenes o clientes disponibles")
                continue
                
            origin = random.choice(warehouses)
            destination = random.choice(clients)
            client_obj = self.route_tracker.clients.get(destination)
            if not client_obj:
                client_obj = Client(destination, destination) # Use ID as name
                self.route_tracker.clients.put(destination, client_obj)
            
            order = Order(i+1, client_obj, origin, destination)
            
            route = self.route_manager.find_route_with_recharge(origin, destination)
            
            if route:
                order.mark_delivered(route.total_cost)
                self.route_tracker.register_route(route, order)
                
                origin_name = origin 
                dest_name = destination
                route_names = [node_id for node_id in route.path]
                recharge_names = [node_id for node_id in route.recharge_stops]
                
                print(f"Orden #{i+1}: {origin_name} → {dest_name}")
                print(f"Ruta: {' → '.join(route_names)}")
                print(f"Costo: {route.total_cost} | Paradas de recarga: {recharge_names} | Estado: Entregado")
            else:
                order.mark_failed()
                origin_name = origin
                dest_name = destination
                print(f"Orden #{i+1}: {origin_name} → {dest_name}")
                print(f"Estado: No se encontró ruta válida")