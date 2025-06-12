import heapq
import random
import time
from collections import defaultdict, Counter
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from model.graph import Graph

class RouteManager:
    def __init__(self, graph):
        self.graph = graph
        self.route_cache = {}
        self.recharge_threshold = 50  

    def _get_vertex_by_id(self, vertex_id):
        for v in self.graph.vertices():
            if v.element() == vertex_id:
                return v
        return None

    def _dijkstra(self, start_id, end_id):
        start_vertex = self._get_vertex_by_id(start_id)
        end_vertex = self._get_vertex_by_id(end_id)

        if not start_vertex or not end_vertex:
            return None

        distances = {v.element(): float('infinity') for v in self.graph.vertices()}
        predecessors = {v.element(): None for v in self.graph.vertices()}
        distances[start_id] = 0
        priority_queue = [(0, start_id)]  # (cost, vertex_id)

        while priority_queue:
            current_cost, current_id = heapq.heappop(priority_queue)

            if current_cost > distances[current_id]:
                continue

            if current_id == end_id:
                path = []
                while current_id is not None:
                    path.insert(0, current_id)
                    current_id = predecessors[current_id]
                return {'path': path, 'cost': distances[end_id]}

            current_vertex = self._get_vertex_by_id(current_id)
            if current_vertex:
                for edge in self.graph.incident_edges(current_vertex):
                    neighbor_vertex = edge.opposite(current_vertex)
                    weight = edge.element()
                    new_cost = distances[current_id] + weight

                    if new_cost < distances[neighbor_vertex.element()]:
                        distances[neighbor_vertex.element()] = new_cost
                        predecessors[neighbor_vertex.element()] = current_id
                        heapq.heappush(priority_queue, (new_cost, neighbor_vertex.element()))
        return None

    def _route_feasible_with_battery(self, route_info, max_battery):
        return route_info['cost'] <= max_battery

    def _find_route_with_recharge_stops(self, origin, destination, max_battery):
        recharge_stations = [v.element() for v in self.graph.vertices() if v.type() == 'recharge']
        best_route = None
        min_total_cost = float('infinity')

        for recharge_stop in recharge_stations:
            path1_info = self._dijkstra(origin, recharge_stop)
            if not path1_info or not self._route_feasible_with_battery(path1_info, max_battery):
                continue

            path2_info = self._dijkstra(recharge_stop, destination)
            if not path2_info or not self._route_feasible_with_battery(path2_info, max_battery):
                continue

            total_cost = path1_info['cost'] + path2_info['cost']
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_route = Route(
                    path1_info['path'][:-1] + path2_info['path'],
                    total_cost,
                    [recharge_stop], # Una única parada de recarga
                    [path1_info['cost'], path2_info['cost']] # Costos de los segmentos
                )
        return best_route

    def find_route_with_recharge(self, origin, destination, max_battery=100):
        try:
            origin_vertex = self._get_vertex_by_id(origin)
            dest_vertex = self._get_vertex_by_id(destination)

            if not origin_vertex or not dest_vertex:
                print(f"DEBUG: No se encontraron vértices - Origin: {origin_vertex}, Dest: {dest_vertex}")
                return None

            # 1. Intentar ruta directa
            direct_route_info = self._dijkstra(origin, destination)
            if direct_route_info and self._route_feasible_with_battery(direct_route_info, max_battery):
                print(f"DEBUG: Ruta directa encontrada de {origin} a {destination}. Costo: {direct_route_info['cost']}")
                return Route(direct_route_info['path'], direct_route_info['cost'], [], [])

            print(f"DEBUG: Ruta directa no factible o no encontrada. Buscando con recarga para {origin} a {destination}")
            route_with_recharge = self._find_route_with_recharge_stops(origin, destination, max_battery)
            if route_with_recharge:
                print(f"DEBUG: Ruta encontrada con recarga. Costo total: {route_with_recharge.total_cost}")
                return route_with_recharge
            else:
                print(f"DEBUG: No se encontró ninguna ruta válida (directa o con recarga) para {origin} a {destination}")
                return None

        except Exception as e:
            print(f"Error en find_route_with_recharge: {e}")
            return None
    
    def _route_feasible_with_battery(self, route_info, max_battery):
        return route_info['cost'] <= max_battery * 0.95  
        
    def _find_route_with_recharge_stops(self, origin, destination, max_battery):
        try:
            recharge_stations = []
            for vertex in self.graph.vertices():
                node_id = vertex.element()
                if 'recharge' in str(node_id).lower() or self._is_recharge_station(vertex):
                    recharge_stations.append(node_id)
            
            if not recharge_stations:
                print("DEBUG: No se encontraron estaciones de recarga")
                return None
            
            best_route = None
            min_cost = float('inf')
            
            for station in recharge_stations:
                route1 = self._dijkstra(origin, station)
                route2 = self._dijkstra(station, destination)
                
                if route1 and route2:
                    if (self._route_feasible_with_battery(route1, max_battery) and 
                        self._route_feasible_with_battery(route2, max_battery)):
                        
                        total_cost = route1['cost'] + route2['cost']
                        if total_cost < min_cost:
                            min_cost = total_cost
                            # Combinar rutas
                            combined_path = route1['path'] + route2['path'][1:]  # Evitar duplicar estación
                            best_route = Route(combined_path, total_cost, [station], [])
            
            return best_route
            
        except Exception as e:
            print(f"Error en _find_route_with_recharge_stops: {e}")
            return None
    
    def _is_recharge_station(self, vertex):
        try:
            return hasattr(vertex, 'type') and vertex.type() == 'recharge'
        except:
            node_id = str(vertex.element())
            return 'recharge' in node_id.lower() or 'R' in node_id


class RouteTracker:
    def __init__(self):
        self.route_history = []
        self.route_frequency = Counter()
        self.node_visits = Counter()
        self.client_orders = defaultdict(int)
        self.order_records = []
        
    def track_route(self, route):
        if route:
            route_str = " -> ".join(route.path)
            self.route_history.append({
                'route': route_str,
                'path': route.path,
                'cost': route.total_cost,
                'timestamp': time.time(),
                'recharge_stops': route.recharge_stops if hasattr(route, 'recharge_stops') else []
            })
    
            self.route_frequency[route_str] += 1
            for node in route.path:
                self.node_visits[node] += 1
    
    def track_client_order(self, client_id):
        self.client_orders[client_id] += 1
    
    def track_order(self, order_id, order):
        self.order_records.append((order_id, order))
    
    def get_most_frequent_routes(self, limit=10):
        return self.route_frequency.most_common(limit)
    
    def get_node_visit_stats(self, limit=20):
        return self.node_visits.most_common(limit)
    
    def get_client_stats(self):
        return sorted([(client_id, orders) for client_id, orders in self.client_orders.items()], 
                     key=lambda x: x[1], reverse=True)
    
    def get_order_stats(self):
        return self.order_records
    
    def get_route_history(self):
        return self.route_history


class RouteOptimizer:
    
    def __init__(self, route_tracker, route_manager):
        self.tracker = route_tracker
        self.manager = route_manager
        self.optimization_reports = []
        
    def analyze_route_patterns(self):
        patterns = []
        
        # Analizar frecuencia de rutas
        frequent_routes = self.tracker.get_most_frequent_routes(5)
        if frequent_routes:
            patterns.append("=== ROUTE FREQUENCY ANALYSIS ===")
            for route, freq in frequent_routes:
                patterns.append(f"Route: {route} | Frequency: {freq}")
        
        # Analizar nodos más visitados
        node_stats = self.tracker.get_node_visit_stats(5)
        if node_stats:
            patterns.append("\n=== NODE VISIT ANALYSIS ===")
            for node, visits in node_stats:
                patterns.append(f"Node: {node} | Visits: {visits}")
        
        # Analizar eficiencia de rutas
        route_history = self.tracker.get_route_history()
        if route_history:
            patterns.append("\n=== ROUTE EFFICIENCY ANALYSIS ===")
            costs = [r['cost'] for r in route_history]
            avg_cost = sum(costs) / len(costs)
            patterns.append(f"Average route cost: {avg_cost:.2f}")
            patterns.append(f"Total routes analyzed: {len(route_history)}")
        
        return patterns
    
    def get_optimization_report(self):
        reports = []
        
        route_history = self.tracker.get_route_history()
        if route_history:
            reports.append("=== OPTIMIZATION REPORT ===")
            
            total_routes = len(route_history)
            total_cost = sum(r['cost'] for r in route_history)
            avg_cost = total_cost / total_routes if total_routes > 0 else 0
            
            routes_with_recharge = len([r for r in route_history if r['recharge_stops']])
            recharge_percentage = (routes_with_recharge / total_routes * 100) if total_routes > 0 else 0
            
            reports.append(f"Total routes processed: {total_routes}")
            reports.append(f"Average cost per route: {avg_cost:.2f}")
            reports.append(f"Routes requiring recharge: {routes_with_recharge} ({recharge_percentage:.1f}%)")
            
            high_cost_routes = [r for r in route_history if r['cost'] > avg_cost * 1.5]
            if high_cost_routes:
                reports.append(f"High-cost routes identified: {len(high_cost_routes)}")
                reports.append("Recommendation: Consider alternative routing strategies")
        
        return reports


class OrderSimulator:
    def __init__(self, route_manager, route_tracker):
        self.route_manager = route_manager
        self.tracker = route_tracker
        self.clients = []
        self.orders = []
        
    def generate_clients(self, graph):
        self.clients = []
        
        client_nodes = []
        for vertex in graph.vertices():
            node_id = vertex.element()
            if not self._is_warehouse_node(node_id) and not self._is_recharge_node(node_id):
                client_nodes.append(node_id)
        if not client_nodes:
            client_nodes = [v.element() for v in graph.vertices()]
        
        for i, node_id in enumerate(client_nodes):
            client = Client(
                id=f"C{i+1}",
                name=f"Cliente {i+1}",
                node_id=node_id
            )
            self.clients.append(client)
        
        return self.clients
    
    def _is_warehouse_node(self, node_id):
        node_str = str(node_id).lower()
        return 'warehouse' in node_str or 'w' in node_str
    
    def _is_recharge_node(self, node_id):
        node_str = str(node_id).lower()
        return 'recharge' in node_str or 'r' in node_str
    
    def process_orders(self, num_orders):
        graph = self.route_manager.graph
        
        if not self.clients:
            self.generate_clients(graph)
        
        warehouse_nodes = []
        for vertex in graph.vertices():
            node_id = vertex.element()
            if self._is_warehouse_node(node_id):
                warehouse_nodes.append(node_id)
        
        if not warehouse_nodes:
            all_nodes = [v.element() for v in graph.vertices()]
            warehouse_nodes = random.sample(all_nodes, min(3, len(all_nodes)))
            print(f"DEBUG: Usando nodos como warehouse: {warehouse_nodes}")
        
        if not warehouse_nodes or not self.clients:
            print("Error: No hay nodos warehouse o clientes disponibles")
            return
        
        print(f"Procesando {num_orders} órdenes...")
        print(f"DEBUG: Warehouse disponibles: {warehouse_nodes}")
        print(f"DEBUG: Clientes disponibles: {len(self.clients)}")
        
        for i in range(num_orders):
            origin = random.choice(warehouse_nodes)
            client = random.choice(self.clients)
            destination = client.node_id
            
            order = Order(
                order_id=f"ORD{i+1:03d}",
                client=client,
                origin=origin,
                destination=destination,
                weight=random.uniform(0.5, 5.0),
                priority=random.choice(['normal', 'urgent', 'express'])
            )
            
            self._process_single_order(order)
            
            self.tracker.track_client_order(client.id)
            self.tracker.track_order(order.order_id, order)
    
    def _process_single_order(self, order):
        print(f"\n--- Procesando Orden {order.order_id} ---")
        print(f"Cliente: {order.client.id}")
        print(f"Origen: {order.origin} -> Destino: {order.destination}")
        print(f"Peso: {order.weight:.2f}kg | Prioridad: {order.priority}")
        
        route = self.route_manager.find_route_with_recharge(order.origin, order.destination)
        
        if route:
            print(f"Ruta encontrada: {' -> '.join(route.path)}")
            print(f"Costo total: {route.total_cost:.2f}")
            
            if hasattr(route, 'recharge_stops') and route.recharge_stops:
                print(f"Paradas de recarga: {', '.join(route.recharge_stops)}")
            
         
            delivery_success = random.random() > 0.1 
            
            if delivery_success:
                order.status = "Entregado"
                order.total_cost = route.total_cost
                print("Estado: Entregado ✅")
            else:
                order.status = "Fallido"
                print("Estado: Fallido ❌")
            
            # Registrar ruta
            self.tracker.track_route(route)
            
        else:
            print("❌ No se pudo encontrar una ruta válida")
            order.status = "Sin ruta"
        
        self.orders.append(order)
    
    def get_simulation_summary(self):
        if not self.orders:
            return "No hay órdenes procesadas"
        
        total_orders = len(self.orders)
        delivered = len([o for o in self.orders if o.status == "Entregado"])
        failed = len([o for o in self.orders if o.status == "Fallido"])
        no_route = len([o for o in self.orders if o.status == "Sin ruta"])
        
        summary = f"""
=== RESUMEN DE SIMULACIÓN ===
Total de órdenes: {total_orders}
Entregadas: {delivered} ({delivered/total_orders*100:.1f}%)  
Fallidas: {failed} ({failed/total_orders*100:.1f}%)
Sin ruta: {no_route} ({no_route/total_orders*100:.1f}%)
        """
        
        return summary