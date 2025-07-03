import heapq
from datetime import datetime
import random
import time
from collections import defaultdict, Counter
from domain.ruta import Route
from domain.orden import Order
from domain.cliente import Client
from model.graph import Graph

class RouteManager:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.route_cache = {}

    def get_path_and_cost(self, start_id, end_id):
        if (start_id, end_id) in self.route_cache:
            return self.route_cache[(start_id, end_id)]
        distances, predecessors = self.graph.dijkstra(start_id)
        path = self.graph.get_shortest_path(start_id, end_id, predecessors)
        cost = distances.get(end_id, float('inf'))
        if path and cost != float('inf'):
            route_info = {'path': path, 'cost': cost}
            self.route_cache[(start_id, end_id)] = route_info
            return route_info
        return None

    def find_route_with_recharge(self, origin, destination, max_battery: int) -> Route | None:
        """
        Encuentra la ruta óptima... (el resto de la función se mantiene igual)
        """
        pq = [(0, origin, [origin], [])]
        visited = {origin: 0}
        recharge_stations = {v.element() for v in self.graph.vertices() if v.type() == 'recharge'}

        while pq:
            total_cost, current_node, path, recharges = heapq.heappop(pq)
            if current_node == destination:
                return Route(path=path, total_cost=total_cost, recharge_stops=recharges, segments=[])
            if total_cost > visited[current_node]:
                continue
            
            possible_next_stops = recharge_stations.union({destination})
            for next_stop in possible_next_stops:
                if next_stop == current_node:
                    continue
                segment_info = self.get_path_and_cost(current_node, next_stop)
                if segment_info and segment_info['cost'] <= max_battery:
                    new_cost = total_cost + segment_info['cost']
                    if new_cost < visited.get(next_stop, float('inf')):
                        visited[next_stop] = new_cost
                        new_path = path[:-1] + segment_info['path']
                        new_recharges = recharges + [current_node] if current_node in recharge_stations else recharges
                        heapq.heappush(pq, (new_cost, next_stop, new_path, new_recharges))
        return None

class RouteTracker:
    """Rastrea el historial de rutas, frecuencia y otras estadísticas. (Sin cambios)"""
    def __init__(self):
        self.route_history = []; self.route_frequency = Counter()
        self.node_visits = Counter(); self.client_orders = defaultdict(int)
        self.order_records = []
    def track_route(self, route: Route):
        if route:
            route_str = " -> ".join(route.path)
            self.route_history.append({'route': route_str, 'path': route.path, 'cost': route.total_cost, 'timestamp': time.time(), 'recharge_stops': route.recharge_stops})
            self.route_frequency[route_str] += 1
            for node in route.path: self.node_visits[node] += 1
    def track_client_order(self, client_id: str): self.client_orders[client_id] += 1
    def track_order(self, order_id: str, order: Order): self.order_records.append((order_id, order))
    def get_most_frequent_routes(self, limit=10): return self.route_frequency.most_common(limit)
    def get_node_visit_stats(self, limit=20): return self.node_visits.most_common(limit)
    def get_client_stats(self): return sorted(self.client_orders.items(), key=lambda x: x[1], reverse=True)
    def get_order_stats(self): return self.order_records
    def get_route_history(self): return self.route_history


class RouteOptimizer:
    """Analiza los datos de rutas. (Sin cambios)"""
    def __init__(self, route_tracker: RouteTracker, route_manager: RouteManager):
        self.tracker = route_tracker; self.manager = route_manager
    def analyze_route_patterns(self): return [] # Placeholder
    def get_optimization_report(self): return [] # Placeholder



class OrderSimulator:
    """Simula la generación y procesamiento de órdenes."""
    def __init__(self, route_manager: RouteManager, route_tracker: RouteTracker):
        self.route_manager = route_manager
        self.tracker = route_tracker
        self.clients = []
        self.orders = []
        
    def generate_clients(self, graph: Graph):
        self.clients = []
        client_nodes = [v.element() for v in graph.vertices() if v.type() == 'client']
        for i, node_id in enumerate(client_nodes):
            client_type = random.choice(["Premium", "Normal"])
            client = Client(id=f"C{i+1:03d}", name=f"Cliente {i+1}", node_id=node_id, client_type=client_type)
            self.clients.append(client)
        return self.clients
    
    # <-- INICIO DE LA LÓGICA MODIFICADA ---
    def process_orders(self, num_orders_to_create: int, num_orders_to_process: int, max_battery: int):
        graph = self.route_manager.graph
        if not self.clients: self.generate_clients(graph)
        
        warehouse_nodes = [v.element() for v in graph.vertices() if v.type() == 'warehouse']
        if not warehouse_nodes or not self.clients:
            print("ERROR: No hay suficientes nodos de almacén o clientes.")
            return

        # 1. Primero, CREAMOS todas las órdenes y las dejamos en estado 'pending'.
        print(f"Creando {num_orders_to_create} órdenes...")
        for i in range(num_orders_to_create):
            origin = random.choice(warehouse_nodes)
            client = random.choice(self.clients)
            order = Order(
                order_id=f"ORD{i+1:03d}", client=client, origin=origin,
                destination=client.node_id, weight=random.uniform(0.5, 5.0),
                priority=random.choice(['normal', 'urgent']))
            self.orders.append(order) # La añadimos a la lista principal

        # 2. Luego, PROCESAMOS solo una parte de ellas.
        # Asegurarnos de no procesar más órdenes de las que existen
        orders_to_process_list = self.orders[:min(num_orders_to_process, len(self.orders))]
        
        print(f"Procesando {len(orders_to_process_list)} de {len(self.orders)} órdenes totales...")
        for order in orders_to_process_list:
            self._process_single_order(order, max_battery)
            self.tracker.track_client_order(order.client.id)
            self.tracker.track_order(order.order_id, order) # Rastreamos la orden procesada
    
    def _process_single_order(self, order: Order, max_battery: int):
        # Esta función ahora solo actualiza el estado, ya no añade la orden a la lista.
        print(f"\n--- Intentando procesar Orden {order.order_id} para Cliente {order.client.id} ---")
        
        route = self.route_manager.find_route_with_recharge(order.origin, order.destination, max_battery)
        
        if route:
            # Lógica para marcar como entregada
            order.status = "Entregado"
            order.delivery_date = datetime.now()
            order.total_cost = route.total_cost
            print(f"Estado: Entregado ✅ (Ruta: {' -> '.join(route.path)})")
            self.tracker.track_route(route)
        else:
            # Lógica para marcar como fallida
            order.status = "Fallido"
            print(f"Estado: Fallido - No se pudo encontrar una ruta válida ❌")
    # <-- FIN DE LA LÓGICA MODIFICADA ---
            
    def get_simulation_summary(self):
        if not self.orders: return "No hay órdenes para generar un resumen."
        total = len(self.orders)
        processed = sum(1 for o in self.orders if o.status in ["Entregado", "Fallido"])
        pending = total - processed
        delivered = sum(1 for o in self.orders if o.status == "Entregado")
        return (f"Órdenes totales: {total}, Pendientes: {pending}, Procesadas: {processed}, Entregadas con éxito: {delivered}")