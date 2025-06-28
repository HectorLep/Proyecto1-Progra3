# from .simulation_initializer import SimulationInitializer # Removed
from domain.ruta import RouteManager, RouteTracker, RouteOptimizer
from tda.avl import AVLTree # Changed
from tda.mapa_hash import HashMap
from model.graph import Graph # Added for graph initialization placeholder

class Simulation:
    def __init__(self):
        # self.initializer = SimulationInitializer() # Removed
        self.route_manager = None
        self.route_tracker = RouteTracker() # Initialize here
        self.route_optimizer = None
        self.graph = None
        self.route_avl = AVLTree() # Changed
        self.is_initialized = False
        
    def initialize_simulation(self, n_nodes=15, m_edges=20, num_orders=10): # Added num_orders for consistency
        try:
            if n_nodes > 150:
                raise ValueError("Número máximo de nodos: 150")
            # Graph generation will be moved here or called from here (from model.graph)
            # For now, creating a graph instance but random generation will be done in Step 2
            self.graph = Graph(directed=False) # Assuming undirected for now, adjust as needed
            # TODO: Call self.graph.generate_random_graph(n_nodes, m_edges) in Step 2
            # TODO: Assign roles in Step 2

            # This part depends on actual graph initialization in Step 2.
            # For now, we focus on AVL tree integration.
            
            # Simulate graph initialization for now for RouteManager
            if not list(self.graph.vertices()): # If graph is empty (no generate_random_graph yet)
                 # Add a dummy vertex if empty, so RouteManager can be initialized.
                 # This is a temporary workaround.
                if n_nodes > 0:
                    self.graph.insert_vertex("temp_N0")


            self.route_manager = RouteManager(self.graph)
            # self.route_tracker = RouteTracker() # Moved to __init__
            self.route_optimizer = RouteOptimizer(self.route_tracker, self.manager) # manager should be self.route_manager
            
            self.is_initialized = True # This might be premature if graph is not fully ready
            
            # role_distribution will be properly set in Step 2
            return {"success": True, "graph": self.graph, "role_distribution": {}}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_simulation(self, num_orders=10): # Added num_orders, assuming it's passed from dashboard
        if not self.is_initialized:
            return {"success": False, "message": "Simulación no inicializada"}
            
        try:
            # Simulate order processing which populates route_tracker
            # This is a placeholder for actual order simulation logic that uses OrderSimulator
            # order_simulator = OrderSimulator(self.route_manager, self.route_tracker)
            # order_simulator.process_orders(num_orders) # This would populate tracker

            # For testing _store_routes_in_avl, manually add some history if tracker is empty
            if not self.route_tracker.get_route_history() and self.graph and list(self.graph.vertices()):
                # Create some dummy routes if graph has nodes
                nodes = list(v.element() for v in self.graph.vertices())
                if len(nodes) >= 2:
                    dummy_route1 = Route([nodes[0], nodes[1]], 10, [], [])
                    self.route_tracker.track_route(dummy_route1)
                    if len(nodes) >= 3:
                         dummy_route2 = Route([nodes[0], nodes[1], nodes[2]], 20, [], [])
                         self.route_tracker.track_route(dummy_route2)
                         self.route_tracker.track_route(dummy_route1) # Track route1 again for frequency


            if self.route_optimizer: # Ensure optimizer is initialized
                 self.route_optimizer.analyze_route_patterns()
            self._store_routes_in_avl()
            
            return {"success": True, "message": "Simulación completada"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _store_routes_in_avl(self):
        """Registra las rutas procesadas en el AVL para análisis posterior."""
        if not self.route_tracker:
            print("Error: RouteTracker no inicializado en _store_routes_in_avl.")
            return

        # Iterate through individual route occurrences from history
        for route_record in self.route_tracker.get_route_history():
            route_str = route_record['route']
            self.route_avl.insert(route_str)
    
    def get_simulation_stats(self):
        if not self.is_initialized: # Or check if graph has been generated
            return {"error": "Simulación no inicializada o grafo no generado"}
            
        try:
            route_frequency_from_tracker = self.route_tracker.get_most_frequent_routes()
            node_frequency = self.route_tracker.get_node_visit_stats()
            
            avl_routes_with_freq = self.route_avl.inorder_traversal()

            return {
                "route_frequency_tracker": route_frequency_from_tracker,
                "node_frequency": node_frequency,
                "avl_routes_sorted_by_freq": self.route_avl.get_frequent_routes(count=len(avl_routes_with_freq)),
                "avl_raw_inorder": avl_routes_with_freq
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_graph(self):
        return self.graph
    
    def get_route_avl(self): # This method returns the AVLTree instance
        return self.route_avl
