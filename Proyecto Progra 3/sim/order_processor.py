from algorithms.pathfinding import PathFinder
from domain.ruta import Route
from datetime import datetime

class OrderProcessor:
    def __init__(self, graph, max_battery=50):
        self.graph = graph
        self.max_battery = max_battery
        self.pathfinder = PathFinder(graph)
        self.processed_routes = []
        
    def process_order(self, order):
        """
        Procesa una orden individual calculando la ruta óptima
        """
        try:
            # Obtener nodos origen y destino
            origin = self.graph.vertices.get(order.origin_id)
            destination = self.graph.vertices.get(order.destination_id)
            
            if not origin or not destination:
                order.status = "failed"
                order.failure_reason = "Nodos no encontrados"
                return None
                
            # Calcular ruta considerando batería
            path_info = self.pathfinder.find_path_with_battery(
                origin.id, 
                destination.id, 
                self.max_battery
            )
            
            if not path_info:
                order.status = "failed"
                order.failure_reason = "Ruta no encontrada"
                return None
                
            # Crear objeto Route
            route = Route(
                route_id=f"R_{order.order_id}",
                order_id=order.order_id,
                path=path_info['path'],
                total_cost=path_info['cost'],
                battery_stops=path_info.get('battery_stops', [])
            )
            
            # Actualizar orden
            order.route = route
            order.total_cost = path_info['cost']
            order.status = "completed"
            order.delivery_date = datetime.now()
            
            # Registrar ruta procesada
            self.processed_routes.append(route)
            
            return route
            
        except Exception as e:
            order.status = "failed"
            order.failure_reason = str(e)
            return None
    
    def process_orders_batch(self, orders):
        """
        Procesa un lote de órdenes
        """
        results = {
            "completed": [],
            "failed": [],
            "total_cost": 0,
            "total_battery_stops": 0
        }
        
        for order in orders:
            route = self.process_order(order)
            
            if route:
                results["completed"].append(order)
                results["total_cost"] += route.total_cost
                results["total_battery_stops"] += len(route.battery_stops)
            else:
                results["failed"].append(order)
                
        return results
    
    def get_route_frequency(self):
        """
        Calcula la frecuencia de uso de rutas
        """
        route_frequency = {}
        
        for route in self.processed_routes:
            path_str = " -> ".join(route.path)
            route_frequency[path_str] = route_frequency.get(path_str, 0) + 1
            
        return route_frequency
    
    def get_node_frequency(self):
        """
        Calcula la frecuencia de visitas por nodo
        """
        node_frequency = {
            "origins": {},
            "destinations": {},
            "intermediates": {}
        }
        
        for route in self.processed_routes:
            if route.path:
                # Contar origen
                origin = route.path[0]
                node_frequency["origins"][origin] = node_frequency["origins"].get(origin, 0) + 1
                
                # Contar destino
                destination = route.path[-1]
                node_frequency["destinations"][destination] = node_frequency["destinations"].get(destination, 0) + 1
                
                # Contar nodos intermedios
                for node in route.path[1:-1]:
                    node_frequency["intermediates"][node] = node_frequency["intermediates"].get(node, 0) + 1
                    
        return node_frequency
    
    def validate_route_battery(self, path):
        """
        Valida que una ruta respete el límite de batería
        """
        if not path or len(path) < 2:
            return True
            
        total_cost = 0
        
        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]
            
            # Buscar peso de la arista
            edge = self.graph.get_edge(current_node, next_node)
            if edge:
                total_cost += edge.weight
                
        return total_cost <= self.max_battery