from .simulation_initializer import SimulationInitializer
from .order_simulator import OrderSimulator
from .order_processor import OrderProcessor
from tda.avl import AVL
from tda.map import Map

class Simulation:
    def __init__(self):
        self.initializer = SimulationInitializer()
        self.order_simulator = None
        self.order_processor = None
        self.graph = None
        self.route_avl = AVL()
        self.client_map = Map()
        self.order_map = Map()
        self.is_initialized = False
        
    def initialize_simulation(self, n_nodes=15, m_edges=20, n_orders=10):
        """
        Inicializa la simulación completa
        """
        try:
            # Validaciones
            if n_nodes > 150:
                raise ValueError("Número máximo de nodos: 150")
            if m_edges < n_nodes - 1:
                raise ValueError(f"Mínimo {n_nodes - 1} aristas para garantizar conectividad")
                
            # Generar grafo conectado
            self.graph = self.initializer.generate_connected_graph(n_nodes, m_edges)
            
            # Asignar roles
            role_distribution = self.initializer.assign_node_roles()
            
            # Inicializar simuladores
            self.order_simulator = OrderSimulator(self.graph)
            self.order_processor = OrderProcessor(self.graph)
            
            # Generar clientes y órdenes
            clients = self.order_simulator.generate_clients()
            orders = self.order_simulator.generate_orders(n_orders)
            
            # Almacenar en estructuras de datos
            self._store_clients_in_map(clients)
            self._store_orders_in_map(orders)
            
            self.is_initialized = True
            
            return {
                "success": True,
                "graph": self.graph,
                "role_distribution": role_distribution,
                "clients": clients,
                "orders": orders,
                "message": f"Simulación inicializada: {n_nodes} nodos, {m_edges} aristas, {n_orders} órdenes"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al inicializar simulación: {str(e)}"
            }
    
    def run_simulation(self):
        """
        Ejecuta la simulación procesando todas las órdenes
        """
        if not self.is_initialized:
            return {"success": False, "message": "Simulación no inicializada"}
            
        try:
            # Obtener todas las órdenes
            orders = list(self.order_map.values())
            
            # Procesar órdenes
            results = self.order_processor.process_orders_batch(orders)
            
            # Almacenar rutas en AVL
            self._store_routes_in_avl()
            
            # Actualizar contadores de órdenes por cliente
            self.order_simulator.update_client_order_count()
            
            return {
                "success": True,
                "results": results,
                "message": f"Simulación completada: {len(results['completed'])} órdenes exitosas, {len(results['failed'])} fallidas"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error durante la simulación: {str(e)}"
            }
    
    def _store_clients_in_map(self, clients):
        """
        Almacena clientes en el mapa hash
        """
        for client in clients:
            self.client_map.put(client.client_id, client)
    
    def _store_orders_in_map(self, orders):
        """
        Almacena órdenes en el mapa hash
        """
        for order in orders:
            self.order_map.put(order.order_id, order)
    
    def _store_routes_in_avl(self):
        """
        Almacena rutas procesadas en el AVL
        """
        route_frequency = self.order_processor.get_route_frequency()
        
        for route_path, frequency in route_frequency.items():
            self.route_avl.insert(route_path, frequency)
    
    def get_simulation_stats(self):
        """
        Obtiene estadísticas completas de la simulación
        """
        if not self.is_initialized:
            return {"error": "Simulación no inicializada"}
            
        try:
            # Estadísticas de órdenes
            order_stats = self.order_simulator.get_order_statistics()
            
            # Estadísticas de rutas
            route_frequency = self.order_processor.get_route_frequency()
            node_frequency = self.order_processor.get_node_frequency()
            
            # Estadísticas de nodos por rol
            role_stats = self._get_role_statistics()
            
            return {
                "order_statistics": order_stats,
                "route_frequency": route_frequency,
                "node_frequency": node_frequency,
                "role_statistics": role_stats,
                "avl_routes": self.route_avl.get_all_routes(),
                "total_clients": len(self.client_map),
                "total_orders": len(self.order_map)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_role_statistics(self):
        """
        Obtiene estadísticas por rol de nodo
        """
        role_counts = {"storage": 0, "charge": 0, "client": 0}
        
        for vertex in self.graph.vertices.values():
            if hasattr(vertex, 'role'):
                role_counts[vertex.role] = role_counts.get(vertex.role, 0) + 1
                
        return role_counts
    
    def get_clients(self):
        """Obtiene todos los clientes"""
        return list(self.client_map.values())
    
    def get_orders(self):
        """Obtiene todas las órdenes"""
        return list(self.order_map.values())
    
    def get_graph(self):
        """Obtiene el grafo de la simulación"""
        return self.graph
    
    def get_route_avl(self):
        """Obtiene el AVL de rutas"""
        return self.route_avl