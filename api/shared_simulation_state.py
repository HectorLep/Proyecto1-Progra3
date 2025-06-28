# This module will hold the shared simulation data.
# Streamlit app will write to these variables after simulation runs.
# FastAPI will read from these variables.

# Placeholder for the main graph object
current_graph = None

# Placeholder for list of Client objects
current_clients_list = [] # List of domain.cliente.Client objects

# Placeholder for list of Order objects
current_orders_list = [] # List of domain.orden.Order objects

# Placeholder for the RouteTracker instance
current_route_tracker = None # Instance of sim.rutas.RouteTracker

# Placeholder for the AVLTree instance (for route frequencies)
current_avl_tree = None # Instance of tda.avl.AVLTree

# Placeholder for general simulation summary string
current_simulation_summary = "No simulation has been run yet."

# Placeholder for generated PDF report path or content
# For simplicity, we might store content directly if not too large, or a path.
# Let's assume PDF generation is on-the-fly for the API for now.
# current_pdf_report_content = None

def update_simulation_data(graph, clients, orders, tracker, avl, summary):
    """Called by the simulation runner (e.g., Streamlit app) to update shared data."""
    global current_graph, current_clients_list, current_orders_list
    global current_route_tracker, current_avl_tree, current_simulation_summary

    current_graph = graph
    current_clients_list = clients
    current_orders_list = orders
    current_route_tracker = tracker
    current_avl_tree = avl
    current_simulation_summary = summary
    print("DEBUG: Shared simulation state updated by API.")

def get_simulation_data():
    """Called by API controllers to access shared data."""
    return {
        "graph": current_graph,
        "clients": current_clients_list,
        "orders": current_orders_list,
        "route_tracker": current_route_tracker,
        "avl_tree": current_avl_tree,
        "summary": current_simulation_summary
    }
