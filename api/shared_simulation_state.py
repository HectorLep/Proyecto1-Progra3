import threading

class SimulationState:
    """
    Una clase Singleton y thread-safe para gestionar el estado de la simulación.
    Esta clase asegura que solo haya una instancia del estado y que el acceso
    a los datos esté sincronizado para evitar condiciones de carrera.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # El patrón Singleton asegura que solo se cree una instancia de esta clase.
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulationState, cls).__new__(cls)
                # Inicializar los atributos del estado aquí
                cls._instance._graph = None
                cls._instance._clients = []
                cls._instance._orders = []
                cls._instance._tracker = None
                cls._instance._avl_tree = None
                cls._instance._summary = "No simulation has been run yet."
        return cls._instance

    def update_data(self, graph, clients, orders, tracker, avl, summary):
        """Actualiza el estado de la simulación de forma segura."""
        with self._lock:
            self._graph = graph
            self._clients = clients
            self._orders = orders
            self._tracker = tracker
            self._avl_tree = avl
            self._summary = summary
            print("DEBUG: Shared simulation state updated safely.")

    def get_data(self):
        """Obtiene una copia del estado actual de forma segura."""
        with self._lock:
            return {
                "graph": self._graph,
                "clients": self._clients,
                "orders": self._orders,
                "route_tracker": self._tracker,
                "avl_tree": self._avl_tree,
                "summary": self._summary
            }

# --- Instancia Única (Singleton) ---
# Todo el programa importará y usará esta única instancia.
state_instance = SimulationState()