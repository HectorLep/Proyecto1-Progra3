from .simulation_initializer import SimulationInitializer
from domain.ruta import RouteManager, RouteTracker, RouteOptimizer  # Añadido para manejar rutas
from tda.avl import AVL  # Corregido import de AVL
from tda.mapa_hash import HashMap  # Corregido import de HashMap

class Simulation:
    def __init__(self):
        self.initializer = SimulationInitializer()
        self.route_manager = None
        self.route_tracker = None
        self.route_optimizer = None
        self.graph = None
        self.route_avl = AVL()  # AVL para gestionar las rutas
        self.is_initialized = False
        
    def initialize_simulation(self, n_nodes=15, m_edges=20):
        try:
            if n_nodes > 150:
                raise ValueError("Número máximo de nodos: 150")
            if m_edges < n_nodes - 1:
                raise ValueError(f"Mínimo {n_nodes - 1} aristas para garantizar conectividad")
                
            # Generar grafo conectado
            self.graph = self.initializer.generate_connected_graph(n_nodes, m_edges)
            role_distribution = self.initializer.assign_node_roles()
            
            # Inicializar gestores de rutas
            self.route_manager = RouteManager(self.graph)
            self.route_tracker = RouteTracker()  # Seguimiento de rutas
            self.route_optimizer = RouteOptimizer(self.route_tracker, self.route_manager)  # Optimización de rutas
            
            self.is_initialized = True
            
            return {"success": True, "graph": self.graph, "role_distribution": role_distribution}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_simulation(self):
        if not self.is_initialized:
            return {"success": False, "message": "Simulación no inicializada"}
            
        try:
            # Procesar rutas con el RouteManager
            self.route_optimizer.analyze_route_patterns()  # Analizar y optimizar las rutas
            self._store_routes_in_avl()  # Guardamos las rutas en AVL
            
            return {"success": True, "message": "Simulación completada"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _store_routes_in_avl(self):
        """Registra las rutas procesadas en el AVL para análisis posterior"""
        route_frequency = self.route_tracker.get_most_frequent_routes()
        for route_str, frequency in route_frequency:
            self.route_avl.insert(route_str, frequency)
    
    def get_simulation_stats(self):
        if not self.is_initialized:
            return {"error": "Simulación no inicializada"}
            
        try:
            route_frequency = self.route_tracker.get_most_frequent_routes()
            node_frequency = self.route_tracker.get_node_visit_stats()
            
            return {
                "route_frequency": route_frequency,
                "node_frequency": node_frequency,
                "avl_routes": self.route_avl.get_all_routes(),
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_graph(self):
        return self.graph
    
    def get_route_avl(self):
        return self.route_avl
