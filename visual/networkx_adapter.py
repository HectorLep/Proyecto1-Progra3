import random
import time
from collections import defaultdict, Counter
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route

class RouteManager:
    """Gestor principal de rutas para el sistema de drones"""
    
    def __init__(self, graph):
        self.graph = graph
        self.route_cache = {}
        self.recharge_threshold = 80  # Umbral de batería para buscar recarga
        
    def find_route_with_recharge(self, origin, destination, max_battery=100):
        try:
            origin_vertex = self._get_vertex_by_id(origin)
            dest_vertex = self._get_vertex_by_id(destination)
            
            if not origin_vertex or not dest_vertex:
                print(f"DEBUG: No se encontraron vértices - Origin: {origin_vertex}, Dest: {dest_vertex}")
                return None
            
            direct_route = self._dijkstra(origin, destination)
            if direct_route and self._route_feasible_with_battery(direct_route, max_battery):
                return Route(direct_route['path'], direct_route['cost'], [], [])
            
            # Si la ruta directa no es factible, buscar con paradas de recarga
            return self._find_route_with_recharge_stops(origin, destination, max_battery)
            
        except Exception as e:
            print(f"Error en find_route_with_recharge: {e}")
            return None
    
    def _get_vertex_by_id(self, node_id):
        """Obtiene un vértice por su ID"""
        for vertex in self.graph.vertices():
            if vertex.element() == node_id:
                return vertex
        return None
    
    def _dijkstra(self, start, end):
        """Implementación del algoritmo de Dijkstra mejorada"""
        try:
            # Verificar que los nodos existen
            start_vertex = self._get_vertex_by_id(start)
            end_vertex = self._get_vertex_by_id(end)
            
            if not start_vertex or not end_vertex:
                return None
            
            distances = {}
            previous = {}
            
            # Inicializar distancias
            for vertex in self.graph.vertices():
                node_id = vertex.element()
                distances[node_id] = float('inf')
                previous[node_id] = None
            
            distances[start] = 0
            unvisited = set(vertex.element() for vertex in self.graph.vertices())
            
            while unvisited:
                # Encontrar el nodo no visitado con menor distancia
                current = min(unvisited, key=lambda x: distances[x])
                
                if distances[current] == float('inf'):
                    break
                
                unvisited.remove(current)
                
                if current == end:
                    # Reconstruir camino
                    path = []
                    cost = distances[end]
                    temp = current
                    while temp is not None:
                        path.append(temp)
                        temp = previous[temp]
                    path.reverse()
                    return {'path': path, 'cost': cost}
                
                # Examinar vecinos
                current_vertex = self._get_vertex_by_id(current)
                if current_vertex:
                    for edge in self.graph.incident_edges(current_vertex, outgoing=True):
                        neighbor_vertex = edge.opposite(current_vertex)
                        neighbor = neighbor_vertex.element()
                        
                        if neighbor in unvisited:
                            edge_weight = edge.element()
                            new_distance = distances[current] + edge_weight
                            
                            if new_distance < distances[neighbor]:
                                distances[neighbor] = new_distance
                                previous[neighbor] = current
            
            return None
            
        except Exception as e:
            print(f"Error en _dijkstra: {e}")
            return None
    
    def _route_feasible_with_battery(self, route_info, max_battery):
        """Verifica si una ruta es factible con la batería disponible"""
        return route_info['cost'] <= max_battery * 0.8  # Margen de seguridad del 20%
        
    def _find_route_with_recharge_stops(self, origin_id, destination_id, battery_capacity):
        # """Encuentra una ruta desde el origen hasta el destino, utilizando múltiples paradas de recarga si es necesario.""" # Docstring removed for subtask brevity
        
        full_path_nodes = []
        recharge_stops_made = []
        current_location_id = origin_id
        
        MAX_HOPS = len(self.graph.vertices()) * 2 
        hops = 0

        while current_location_id != destination_id and hops < MAX_HOPS:
            hops += 1

            path_to_dest_info = self._dijkstra(current_location_id, destination_id)

            if path_to_dest_info and self._route_feasible_with_battery(path_to_dest_info, battery_capacity):
                if not full_path_nodes:
                    full_path_nodes.extend(path_to_dest_info['path'])
                else:
                    full_path_nodes.extend(path_to_dest_info['path'][1:]) 
                current_location_id = destination_id 
                break 

            potential_next_recharge_stops = []
            
            all_recharge_nodes = [
                v.element() for v in self.graph.vertices() 
                if self._is_recharge_station(v) and v.element() != current_location_id
            ]

            if not all_recharge_nodes:
                return None 

            for station_id in all_recharge_nodes:
                if recharge_stops_made and recharge_stops_made[-1] == station_id:
                    continue

                path_to_station_info = self._dijkstra(current_location_id, station_id)
                
                if path_to_station_info and self._route_feasible_with_battery(path_to_station_info, battery_capacity):
                    potential_next_recharge_stops.append({
                        'station_id': station_id,
                        'path_info': path_to_station_info
                    })

            if not potential_next_recharge_stops:
                return None 

            best_next_station_trip = min(potential_next_recharge_stops, key=lambda x: x['path_info']['cost'])
            
            selected_station_id = best_next_station_trip['station_id']
            path_to_selected_station_nodes = best_next_station_trip['path_info']['path']

            if not full_path_nodes:
                full_path_nodes.extend(path_to_selected_station_nodes)
            else:
                full_path_nodes.extend(path_to_selected_station_nodes[1:])
            
            recharge_stops_made.append(selected_station_id) 
            current_location_id = selected_station_id
            
        if current_location_id == destination_id:
            return self._reconstruct_route_from_node_list(full_path_nodes, origin_id, destination_id, recharge_stops_made)
        else:
            if hops >= MAX_HOPS:
                print(f"Warning: Pathfinding exceeded MAX_HOPS for {origin_id} to {destination_id}.")
            return None

    def _reconstruct_route_from_node_list(self, node_list, origin_id, destination_id, recharge_stops_made):
        # """Creates a Route object from a list of node IDs and calculates its total cost by summing edge weights.""" # Docstring removed for subtask brevity
        if not node_list:
            return None
        
        if node_list[0] != origin_id or node_list[-1] != destination_id:
            pass

        total_cost = 0
        
        if len(node_list) < 2:
            if origin_id == destination_id and len(node_list) == 1 and node_list[0] == origin_id:
                 return Route([origin_id], 0, [], [])
            return None 

        try:
            for i in range(len(node_list) - 1):
                u_node_id = node_list[i]
                v_node_id = node_list[i+1]
                
                u_vertex = self._get_vertex_by_id(u_node_id)
                v_vertex = self._get_vertex_by_id(v_node_id)

                if not u_vertex or not v_vertex:
                    print(f"Error: Vertex not found during cost reconstruction: {u_node_id} or {v_node_id}")
                    return None 

                edge = self.graph.get_edge(u_vertex, v_vertex)
                if not edge and not self.graph.is_directed():
                    edge = self.graph.get_edge(v_vertex, u_vertex)

                if edge:
                    total_cost += edge.element() 
                else:
                    print(f"Error: No edge found between {u_node_id} and {v_node_id} in reconstructed path. Graph directed: {self.graph.is_directed()}.")
                    return None 
            
            return Route(node_list, total_cost, recharge_stops_made, segments=[])
        except Exception as e:
            print(f"Error during route reconstruction from node list: {e}")
            return None
    
    def _is_recharge_station(self, vertex):
        """Determina si un vértice es una estación de recarga.
        Prioritiza el atributo de tipo del vértice.
        Si el atributo de tipo no está disponible, recurre a la convención de nomenclatura del ID."""
        try:
            # Intenta obtener el tipo usando el método type()
            # Se asume que todos los objetos Vertex relevantes tienen este método.
            vertex_type = vertex.type()
            return vertex_type == 'recharge'
        except AttributeError:
            # Si el método type() no existe, se registra una advertencia y se recurre al ID.
            # Esto es para compatibilidad o manejo de objetos vértice inesperados.
            print(f"Advertencia: El vértice {str(vertex.element())} no tiene el método type(). "
                  "Recurriendo a la verificación basada en ID para la estación de recarga.")
            node_id = str(vertex.element())
            return 'recharge' in node_id.lower() or 'R' in node_id


class RouteTracker:
    """Seguimiento y análisis de rutas utilizadas"""
    
    def __init__(self):
        self.route_history = []
        self.route_frequency = Counter()
        self.node_visits = Counter()
        self.client_orders = defaultdict(int)
        self.order_records = []
        
    def track_route(self, route):
        """Registra una ruta utilizada"""
        if route:
            route_str = " -> ".join(route.path)
            self.route_history.append({
                'route': route_str,
                'path': route.path,
                'cost': route.total_cost,
                'timestamp': time.time(),
                'recharge_stops': route.recharge_stops if hasattr(route, 'recharge_stops') else []
            })
            
            # Actualizar frecuencias
            self.route_frequency[route_str] += 1
            for node in route.path:
                self.node_visits[node] += 1
    
    def track_client_order(self, client_id):
        """Registra un pedido de cliente"""
        self.client_orders[client_id] += 1
    
    def track_order(self, order_id, order):
        """Registra información de una orden"""
        self.order_records.append((order_id, order))
    
    def get_most_frequent_routes(self, limit=10):
        """Obtiene las rutas más frecuentes"""
        return self.route_frequency.most_common(limit)
    
    def get_node_visit_stats(self, limit=20):
        """Obtiene estadísticas de visitas a nodos"""
        return self.node_visits.most_common(limit)
    
    def get_client_stats(self):
        """Obtiene estadísticas de clientes"""
        return sorted([(client_id, orders) for client_id, orders in self.client_orders.items()], 
                     key=lambda x: x[1], reverse=True)
    
    def get_order_stats(self):
        """Obtiene estadísticas de órdenes"""
        return self.order_records
    
    def get_route_history(self):
        """Obtiene el historial completo de rutas"""
        return self.route_history


class RouteOptimizer:
    """Optimizador de rutas y análisis de patrones"""
    
    def __init__(self, route_tracker, route_manager):
        self.tracker = route_tracker
        self.manager = route_manager
        self.optimization_reports = []
        
    def analyze_route_patterns(self):
        """Analiza patrones en las rutas utilizadas"""
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
        """Genera reporte de optimización"""
        reports = []
        
        # Reporte de eficiencia
        route_history = self.tracker.get_route_history()
        if route_history:
            reports.append("=== OPTIMIZATION REPORT ===")
            
            # Calcular métricas
            total_routes = len(route_history)
            total_cost = sum(r['cost'] for r in route_history)
            avg_cost = total_cost / total_routes if total_routes > 0 else 0
            
            # Rutas con recarga
            routes_with_recharge = len([r for r in route_history if r['recharge_stops']])
            recharge_percentage = (routes_with_recharge / total_routes * 100) if total_routes > 0 else 0
            
            reports.append(f"Total routes processed: {total_routes}")
            reports.append(f"Average cost per route: {avg_cost:.2f}")
            reports.append(f"Routes requiring recharge: {routes_with_recharge} ({recharge_percentage:.1f}%)")
            
            # Identificar rutas ineficientes
            high_cost_routes = [r for r in route_history if r['cost'] > avg_cost * 1.5]
            if high_cost_routes:
                reports.append(f"High-cost routes identified: {len(high_cost_routes)}")
                reports.append("Recommendation: Consider alternative routing strategies")
        
        return reports


class OrderSimulator:
    """Simulador de órdenes y procesamiento"""
    
    def __init__(self, route_manager, route_tracker):
        self.route_manager = route_manager
        self.tracker = route_tracker
        self.clients = []
        self.orders = []
        
    def generate_clients(self, graph):
        """Genera clientes basados en los nodos del grafo"""
        self.clients = []
        
        # Buscar nodos que podrían ser clientes
        client_nodes = []
        for vertex in graph.vertices():
            node_id = vertex.element()
            # Buscar nodos que no sean warehouse ni recharge
            if not self._is_warehouse_node(node_id) and not self._is_recharge_node(node_id):
                client_nodes.append(node_id)
        
        # Si no hay nodos específicos de cliente, usar todos los nodos
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
        """Determina si un nodo es warehouse"""
        node_str = str(node_id).lower()
        return 'warehouse' in node_str or 'w' in node_str
    
    def _is_recharge_node(self, node_id):
        """Determina si un nodo es de recarga"""
        node_str = str(node_id).lower()
        return 'recharge' in node_str or 'r' in node_str
    
    def process_orders(self, num_orders):
        """Procesa un número determinado de órdenes"""
        graph = self.route_manager.graph
        
        # Generar clientes si no existen
        if not self.clients:
            self.generate_clients(graph)
        
        # Obtener nodos warehouse para orígenes
        warehouse_nodes = []
        for vertex in graph.vertices():
            node_id = vertex.element()
            if self._is_warehouse_node(node_id):
                warehouse_nodes.append(node_id)
        
        # Si no hay warehouse específicos, usar algunos nodos aleatorios como warehouse
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
            # Seleccionar origen y destino aleatorios
            origin = random.choice(warehouse_nodes)
            client = random.choice(self.clients)
            destination = client.node_id
            
            # Crear orden
            order = Order(
                order_id=f"ORD{i+1:03d}",
                client=client,
                origin=origin,
                destination=destination,
                weight=random.uniform(0.5, 5.0),
                priority=random.choice(['normal', 'urgent', 'express'])
            )
            
            # Procesar orden
            self._process_single_order(order)
            
            # Registrar estadísticas
            self.tracker.track_client_order(client.id)
            self.tracker.track_order(order.order_id, order)
    
    def _process_single_order(self, order):
        """Procesa una orden individual"""
        print(f"\n--- Procesando Orden {order.order_id} ---")
        print(f"Cliente: {order.client.id}")
        print(f"Origen: {order.origin} -> Destino: {order.destination}")
        print(f"Peso: {order.weight:.2f}kg | Prioridad: {order.priority}")
        
        # Buscar ruta
        route = self.route_manager.find_route_with_recharge(order.origin, order.destination)
        
        if route:
            print(f"Ruta encontrada: {' -> '.join(route.path)}")
            print(f"Costo total: {route.total_cost:.2f}")
            
            if hasattr(route, 'recharge_stops') and route.recharge_stops:
                print(f"Paradas de recarga: {', '.join(route.recharge_stops)}")
            
            # Simular entrega
            delivery_success = random.random() > 0.1  # 90% éxito
            
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
        """Obtiene resumen de la simulación"""
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