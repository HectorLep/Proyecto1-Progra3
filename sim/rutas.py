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

    # _get_vertex_by_id is now in Graph class as get_vertex_by_element
    # _dijkstra is now in Graph class

    def _get_path_and_cost(self, start_element, end_element):
        """Helper to get path and cost using graph's Dijkstra."""
        if not self.graph: return None

        distances, predecessors = self.graph.dijkstra(start_element)

        path = self.graph.get_shortest_path(start_element, end_element, predecessors)
        cost = distances.get(end_element, float('infinity'))

        if path and cost != float('infinity'):
            return {'path': path, 'cost': cost}
        return None

    def _route_feasible_with_battery(self, route_info, max_battery):
        # Ensure route_info is not None and has 'cost'
        if route_info and 'cost' in route_info:
            return route_info['cost'] <= max_battery
        return False # Not feasible if route_info is invalid

    def _get_segment_cost(self, u_element, v_element):
        """Calculates the cost of a direct segment between two node elements."""
        # This helper uses Dijkstra for a single segment.
        # If edge weights are directly accessible and represent segment costs,
        # it could be simplified to a direct edge lookup, but Dijkstra is more general.
        path_info = self._get_path_and_cost(u_element, v_element)
        if path_info:
            # We are interested in the cost if these two nodes are *directly* connected in a proposed path.
            # However, _get_path_and_cost gives the shortest path, which might involve intermediate nodes.
            # For autonomy check, we need the cost of a single flight leg.
            # This requires a direct edge cost or a path of only two nodes.
            if len(path_info['path']) == 2: # Direct connection
                return path_info['cost']
            elif len(path_info['path']) > 2 :
                 # This means the "segment" u_element -> v_element is actually a path itself.
                 # This function is intended for checking segments of an ALREADY COMPUTED path.
                 # So, if path_info['path'] is not [u_element, v_element], it means there is no *direct* edge,
                 # or _get_path_and_cost is being misused here.
                 # For now, let's assume we want the shortest path cost between these two points as a "segment"
                 # This might need refinement based on how paths are constructed.
                 # Let's assume this function is to get cost of path u -> v
                 return path_info['cost']
        return float('infinity')


    def find_route_with_recharge(self, origin_element, destination_element, max_battery=50):
        MAX_ITERATIONS = 10 # To prevent infinite loops in path refinement

        origin_vertex = self.graph.get_vertex_by_element(origin_element)
        dest_vertex = self.graph.get_vertex_by_element(destination_element)

        if not origin_vertex or not dest_vertex:
            print(f"DEBUG: Origen o destino no encontrado - Origen: {origin_element}, Destino: {destination_element}")
            return None

        # Initial path calculation (shortest path ignoring segment autonomy for now)
        current_path_info = self._get_path_and_cost(origin_element, destination_element)
        if not current_path_info:
            print(f"DEBUG: No initial path found from {origin_element} to {destination_element}")
            return None

        current_path = current_path_info['path']
        recharge_stops_on_route = []

        # Iteratively refine path
        for iteration in range(MAX_ITERATIONS):
            found_long_segment = False
            new_path_candidate = []

            if not current_path or len(current_path) < 2: # Path is empty or just one node
                break

            # Check segments of the current_path
            for i in range(len(current_path) - 1):
                u_elem = current_path[i]
                v_elem = current_path[i+1]

                # Cost of the direct segment u_elem -> v_elem
                # This needs to be the cost of the specific segment as it appears in current_path,
                # not necessarily the shortest path between u_elem and v_elem generally.
                # We assume current_path is a sequence of nodes, and we need cost between adjacent ones.
                # For this, we need to sum edge weights along the "current_path" if it's not just Dijkstra output.
                # Let's refine _get_segment_cost or do it inline.

                # Re-calculating segment cost based on current path structure
                # This assumes that current_path is a list of node elements.
                # We need to get the actual vertex objects to find the edge.
                u_vertex_seg = self.graph.get_vertex_by_element(u_elem)
                v_vertex_seg = self.graph.get_vertex_by_element(v_elem)

                edge_uv = self.graph.get_edge(u_vertex_seg, v_vertex_seg) if u_vertex_seg and v_vertex_seg else None

                if edge_uv is None and not self.graph.is_directed(): # Try reverse if undirected
                    edge_uv = self.graph.get_edge(v_vertex_seg, u_vertex_seg)

                if edge_uv is None:
                    # This implies current_path is not a simple path of direct edges,
                    # or there's an issue. Fallback to Dijkstra for this segment.
                    # This can happen if a previous insertion of recharge stop made current_path complex.
                    segment_path_info = self._get_path_and_cost(u_elem, v_elem)
                    segment_cost = segment_path_info['cost'] if segment_path_info else float('infinity')
                    # If segment_path_info.path has intermediate nodes, this segment is already "multi-hop"
                    # This logic gets complicated quickly if current_path is not just a list of directly connected nodes.
                    # For now, let's assume _get_path_and_cost(u_elem, v_elem) gives the cost of traversing from u to v.
                    # And if current_path was from Dijkstra, its segments are single edges.
                    # After inserting recharge, current_path might become A -> R1 -> R2 -> B.
                    # Segments are then A->R1, R1->R2, R2->B. These should be checked.

                    # Let's simplify: assume current_path is a list of nodes, and we calculate shortest path cost between them.
                    # The issue is that the "current_path" might already contain multi-edge segments due to previous insertions.
                    # The robust way is to maintain current_path as a list of lists (segments), each segment being a direct path <= 50.
                    # Sticking to the iterative refinement of a single list of nodes for now:

                    # We need the cost of the segment *as it is intended to be flown*.
                    # If current_path = [A, B, C], segments are A-B, B-C.
                    # If A-B's shortest path is A-X-B, its cost is cost(A-X-B).
                    # If A-B is a direct edge in the graph, its cost is edge_weight(A,B).
                    # The Dijkstra output in self.graph.dijkstra gives shortest paths.
                    # Let's assume `_get_path_and_cost(u_elem, v_elem)` is the cost of the leg.
                    leg_cost_info = self._get_path_and_cost(u_elem, v_elem)
                    leg_cost = leg_cost_info['cost'] if leg_cost_info else float('infinity')


                else: # Direct edge exists
                    leg_cost = edge_uv.element()


                if leg_cost > max_battery:
                    found_long_segment = True
                    print(f"DEBUG: Long segment {u_elem}->{v_elem} cost {leg_cost} > {max_battery}. Iteration {iteration+1}")

                    # Try to insert a recharge station for u_elem -> v_elem
                    best_intermediate_recharge_stop = None
                    min_ detour_cost = float('infinity')

                    recharge_stations_elements = [v_obj.element() for v_obj in self.graph.vertices() if v_obj.type() == 'recharge']

                    for r_elem in recharge_stations_elements:
                        if r_elem == u_elem or r_elem == v_elem: continue

                        path_u_r_info = self._get_path_and_cost(u_elem, r_elem)
                        path_r_v_info = self._get_path_and_cost(r_elem, v_elem)

                        if path_u_r_info and path_r_v_info and \
                           path_u_r_info['cost'] <= max_battery and \
                           path_r_v_info['cost'] <= max_battery:

                            detour_cost = path_u_r_info['cost'] + path_r_v_info['cost']
                            if detour_cost < min_ detour_cost:
                                min_ detour_cost = detour_cost
                                best_intermediate_recharge_stop = r_elem
                                # Store the paths to reconstruct later
                                best_path_u_r = path_u_r_info['path']
                                best_path_r_v = path_r_v_info['path']

                    if best_intermediate_recharge_stop:
                        print(f"DEBUG: Found best recharge {best_intermediate_recharge_stop} for {u_elem}->{v_elem}")
                        # Reconstruct path: path_so_far + u_elem -> R_best -> v_elem + rest_of_path
                        # current_path is: ... path[i-1], u_elem, v_elem, path[i+2] ...
                        # new segment is: u_elem -> ... -> R_best -> ... -> v_elem
                        # new_path_candidate should be: current_path[0...i-1] + best_path_u_r (no end) + best_path_r_v
                        new_path_candidate.extend(best_path_u_r[:-1]) # Add path to R (excluding R itself)
                        new_path_candidate.extend(best_path_r_v)      # Add path from R to V (including R and V)

                        if best_intermediate_recharge_stop not in recharge_stops_on_route:
                            recharge_stops_on_route.append(best_intermediate_recharge_stop)

                        # Add rest of the original path from v_elem's original position
                        new_path_candidate.extend(current_path[i+2:])
                        current_path = new_path_candidate # Update current_path and restart segment checking
                        break # Restart checking segments from the beginning of the modified path
                    else:
                        # No single recharge station can fix this segment u_elem -> v_elem
                        print(f"DEBUG: No single recharge station found to fix segment {u_elem}->{v_elem}. Route might be impossible.")
                        return None # Or try more complex strategy (e.g. A->R1->R2->B) - out of scope for now.
                else:
                    # Segment is fine, add u_elem to new_path_candidate
                    # (v_elem will be added as u_elem in next iteration, or at the end)
                    if not new_path_candidate or new_path_candidate[-1] != u_elem :
                         new_path_candidate.append(u_elem)

            if not found_long_segment: # All segments are within autonomy
                if new_path_candidate : # If any changes were made that didn't break the loop
                     if current_path and current_path[-1] not in new_path_candidate:
                          if new_path_candidate[-1] != current_path[-1]: # Add last node if not added
                            new_path_candidate.append(current_path[-1]) # Ensure last node is included
                     current_path = new_path_candidate

                # Final check if the very last node was added if path was modified
                if current_path and current_path[-1] != destination_element and destination_element not in current_path:
                    # This case should ideally not happen if logic is correct.
                    # If new_path_candidate was being built, it should end with destination_element
                    # For safety, ensure destination is the last node if path exists
                    # This part is tricky, if path was fully rebuilt, it should be fine.
                    # Let's ensure the path ends at destination if it was being processed.
                    # The `new_path_candidate.extend(current_path[i+2:])` should handle this.
                    # If the loop completes without `found_long_segment`, current_path is the valid one.
                    pass


                final_cost = 0
                final_segments_costs = []
                for k in range(len(current_path) -1):
                    u, v = current_path[k], current_path[k+1]
                    cost_info = self._get_path_and_cost(u,v)
                    if not cost_info: return None # Should not happen if path was valid
                    final_cost += cost_info['cost']
                    final_segments_costs.append(cost_info['cost'])

                print(f"DEBUG: Path found respecting autonomy: {'->'.join(current_path)}, Cost: {final_cost}, Recharges: {recharge_stops_on_route}")
                return Route(path=current_path, total_cost=final_cost, recharge_stops=sorted(list(set(recharge_stops_on_route))), segments=final_segments_costs)

            if iteration == MAX_ITERATIONS - 1:
                print(f"DEBUG: Max iterations reached for path refinement. Route may not be optimal or fully compliant.")
                return None # Failed to find a compliant path

        return None # Should be covered by logic inside loop or initial checks

    def old_find_route_with_recharge_stops(self, origin_element, destination_element, max_battery):
        # This is the version that tries a single recharge stop between origin and destination
        # if the direct path is too long or non-existent.
        recharge_stations_elements = [v.element() for v in self.graph.vertices() if v.type() == 'recharge']
        best_route_obj = None
        min_total_cost = float('infinity')

        for r_elem in recharge_stations_elements:
            if r_elem == origin_element or r_elem == destination_element: continue

            path1_info = self._get_path_and_cost(origin_element, r_elem)
            if not path1_info or path1_info['cost'] > max_battery: continue

            path2_info = self._get_path_and_cost(r_elem, destination_element)
            if not path2_info or path2_info['cost'] > max_battery: continue

            current_total_cost = path1_info['cost'] + path2_info['cost']
            if current_total_cost < min_total_cost:
                min_total_cost = current_total_cost
                combined_path = path1_info['path'][:-1] + path2_info['path']
                best_route_obj = Route(
                    path=combined_path,
                    total_cost=current_total_cost,
                    recharge_stops=[r_elem],
                    segments=[path1_info['cost'], path2_info['cost']]
                )
        return best_route_obj


    def _is_recharge_station(self, vertex_obj): # Changed to take vertex object
        # This method is now redundant if we use vertex.type() directly.
        return vertex_obj.type() == 'recharge'


class RouteTracker:
                node_id = vertex.element()
                #
                # TYPE CHECKING FOR RECHARGE STATION NEEDS TO BE BASED ON vertex.type()
                #
                if vertex.type() == 'recharge': # Corrected
                    recharge_stations.append(node_id)

            if not recharge_stations:
                print("DEBUG: No se encontraron estaciones de recarga")
                return None

            best_route = None
            min_cost = float('inf')

            for station in recharge_stations:
                # OLD CALLS TO self._dijkstra need to be self._get_path_and_cost
                route1 = self._get_path_and_cost(origin, station)
                route2 = self._get_path_and_cost(station, destination)

                if route1 and route2:
                    if (self._route_feasible_with_battery(route1, max_battery) and
                        self._route_feasible_with_battery(route2, max_battery)):

                        total_cost = route1['cost'] + route2['cost']
                        if total_cost < min_cost:
                            min_cost = total_cost
                            combined_path = route1['path'] + route2['path'][1:]
                            best_route = Route(combined_path, total_cost, [station], []) # Pass path=

            return best_route

        except Exception as e:
            print(f"Error en _find_route_with_recharge_stops: {e}")
            return None

    def _is_recharge_station(self, vertex_obj): # Changed to take vertex object
        # This method is now redundant if we use vertex.type() directly.
        return vertex_obj.type() == 'recharge'


class RouteTracker:
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