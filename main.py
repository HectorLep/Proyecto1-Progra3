from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import avl_insert
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator

def main():
    # Crear un grafo aleatorio
    g = Graph(directed=True)
    g.generate_random_graph(num_nodes=150, num_edges=300) #valores maximos
    
    #gestores y simuladores
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    print("=== SIMULACIÓN DE ÓRDENES ===")
    simulator.process_orders(500) # Test with max orders
    
    print("\n=== ANÁLISIS DE PATRONES ===")
    for pattern in optimizer.analyze_route_patterns():
        print(pattern)
    
    print("\n=== REPORTE DE OPTIMIZACIONES ===")
    for log in optimizer.get_optimization_report():
        print(log)

if __name__ == "__main__":
    main()