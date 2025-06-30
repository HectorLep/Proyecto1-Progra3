# sim/rutas.py (Versión Original Optimizada y Corregida)

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
    """Gestiona el cálculo de rutas con una caché para optimizar el rendimiento."""
    def __init__(self, graph: Graph):
        self.graph = graph
        self.route_cache = {}  # Caché para almacenar rutas ya calculadas

    def _get_path_and_cost_from_cache(self, start_id, end_id):
        """Intenta obtener una ruta desde la caché."""
        return self.route_cache.get((start_id, end_id))

    def _store_path_in_cache(self, start_id, end_id, route_info):
        """Almacena una ruta calculada en la caché."""
        self.route_cache[(start_id, end_id)] = route_info

    def get_path_and_cost(self, start_id, end_id):
        """
        Obtiene la ruta y el costo, usando la caché primero.
        Si no está en caché, usa Dijkstra y la guarda.
        """
        cached_route = self._get_path_and_cost_from_cache(start_id, end_id)
        if cached_route:
            return cached_route

        # Si no está en caché, la calculamos con Dijkstra
        distances, predecessors = self.graph.dijkstra(start_id)
        path = self.graph.get_shortest_path(start_id, end_id, predecessors)
        cost = distances.get(end_id, float('inf'))

        if path and cost != float('inf'):
            route_info = {'path': path, 'cost': cost}
            self._store_path_in_cache(start_id, end_id, route_info)
            return route_info
            
        return None

    def find_route_with_recharge(self, origin, destination, max_battery=50) -> Route | None:
        """Encuentra la ruta óptima, usando paradas de recarga si es necesario."""
        # 1. Intentar ruta directa
        direct_route_info = self.get_path_and_cost(origin, destination)
        if direct_route_info and direct_route_info['cost'] <= max_battery:
            return Route(direct_route_info['path'], direct_route_info['cost'], [], [])

        # 2. Si la ruta directa no es factible, buscar la mejor ruta con UNA parada de recarga
        return self._find_best_route_with_one_recharge(origin, destination, max_battery)

    def _find_best_route_with_one_recharge(self, origin, destination, max_battery):
        """Encuentra la mejor ruta que pasa por una sola estación de recarga."""
        recharge_stations = [v.element() for v in self.graph.vertices() if v.type() == 'recharge']
        best_route_info = None
        min_total_cost = float('inf')

        for station in recharge_stations:
            # Tramo 1: Origen -> Estación de Recarga
            path1_info = self.get_path_and_cost(origin, station)
            if not path1_info or path1_info['cost'] > max_battery:
                continue

            # Tramo 2: Estación de Recarga -> Destino
            path2_info = self.get_path_and_cost(station, destination)
            if not path2_info or path2_info['cost'] > max_battery:
                continue
            
            # Comparamos si esta ruta con desvío es la mejor encontrada hasta ahora
            total_cost = path1_info['cost'] + path2_info['cost']
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_route_info = {
                    'path': path1_info['path'][:-1] + path2_info['path'], # Unir paths sin duplicar la estación
                    'cost': total_cost,
                    'recharge_stop': station
                }

        if best_route_info:
            return Route(
                path=best_route_info['path'],
                total_cost=best_route_info['cost'],
                recharge_stops=[best_route_info['recharge_stop']],
                segments=[]
            )
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
        self.route_manager = route_manager; self.tracker = route_tracker
        self.clients = []; self.orders = []
        
    def generate_clients(self, graph: Graph):
        self.clients = []
        # Lógica corregida para identificar nodos de cliente
        client_nodes = [v.element() for v in graph.vertices() if v.type() == 'client']
        for i, node_id in enumerate(client_nodes):
            client_type = random.choice(["Premium", "Normal"])
            client = Client(id=f"C{i+1:03d}", name=f"Cliente {i+1}", node_id=node_id, client_type=client_type)
            self.clients.append(client)
        return self.clients
    
    def process_orders(self, num_orders: int):
        graph = self.route_manager.graph
        if not self.clients: self.generate_clients(graph)
        
        # Lógica corregida para identificar almacenes
        warehouse_nodes = [v.element() for v in graph.vertices() if v.type() == 'warehouse']
        if not warehouse_nodes or not self.clients:
            print("ERROR: No hay suficientes nodos de almacén o clientes para procesar órdenes.")
            return

        print(f"Procesando {num_orders} órdenes...")
        for i in range(num_orders):
            origin = random.choice(warehouse_nodes)
            client = random.choice(self.clients)
            order = Order(
                order_id=f"ORD{i+1:03d}", client=client, origin=origin,
                destination=client.node_id, weight=random.uniform(0.5, 5.0),
                priority=random.choice(['normal', 'urgent']))
            
            self._process_single_order(order)
            self.tracker.track_client_order(client.id)
            client.total_orders += 1 # Re-integramos el conteo de órdenes
            self.tracker.track_order(order.order_id, order)
    
    def _process_single_order(self, order: Order):
        print(f"\n--- Procesando Orden {order.order_id} para Cliente {order.client.id} ---")
        print(f"Ruta: {order.origin} -> {order.destination}")
        route = self.route_manager.find_route_with_recharge(order.origin, order.destination)
        
        if route:
            print(f"Ruta encontrada: {' -> '.join(route.path)} (Costo: {route.total_cost:.2f})")
            if route.recharge_stops: print(f"Paradas de recarga: {', '.join(route.recharge_stops)}")
            
            order.status = "Entregado"
            order.delivery_date = datetime.now() # Re-integramos la fecha de entrega
            order.total_cost = route.total_cost
            print("Estado: Entregado ✅")
            self.tracker.track_route(route)
        else:
            print(f"Estado: Fallido - No se pudo encontrar una ruta válida ❌")
            order.status = "Fallido"        
        self.orders.append(order)
    
    def get_simulation_summary(self):
        if not self.orders: return "No hay órdenes procesadas para generar un resumen."
        total = len(self.orders); delivered = sum(1 for o in self.orders if o.status == "Entregado")
        failed = total - delivered
        return (f"Órdenes totales: {total},Entregadas: {delivered} ({delivered/total*100:.1f}%),Fallidas: {failed} ({failed/total*100:.1f}%)")