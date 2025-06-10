from model.graph import Graph
from domain.cliente import Client
from domain.orden import Order
from domain.ruta import Route
from tda.avl import avl_insert
from tda.mapa_hash import HashMap
from sim.rutas import RouteManager, RouteTracker, RouteOptimizer, OrderSimulator

def main():
    # Crear un grafo de ejemplo
    g = Graph()
    
    # Insertar vértices
    vertices = {
        'A': g.insert_vertex('A'),
        'B': g.insert_vertex('B'),
        'C': g.insert_vertex('C'),
        'D': g.insert_vertex('D'),
        'R1': g.insert_vertex('R1')
    }
    
    # Insertar aristas con pesos (costos energéticos)
    g.insert_edge(vertices['A'], vertices['B'], 20)
    g.insert_edge(vertices['B'], vertices['A'], 20)
    g.insert_edge(vertices['B'], vertices['C'], 20)
    g.insert_edge(vertices['C'], vertices['B'], 20)
    g.insert_edge(vertices['A'], vertices['R1'], 15)
    g.insert_edge(vertices['R1'], vertices['A'], 15)
    g.insert_edge(vertices['R1'], vertices['D'], 15)
    g.insert_edge(vertices['D'], vertices['R1'], 15)
    g.insert_edge(vertices['A'], vertices['C'], 45)
    g.insert_edge(vertices['C'], vertices['A'], 45)
    
    # Inicializar los gestores y simuladores
    manager = RouteManager(g)
    tracker = RouteTracker()
    optimizer = RouteOptimizer(tracker, manager)
    simulator = OrderSimulator(manager, tracker)
    
    # Simular algunos pedidos
    print("=== SIMULACIÓN DE ÓRDENES ===")
    simulator.process_orders(5)
    
    # Mostrar estadísticas sobre los patrones de rutas
    print("\n=== ANÁLISIS DE PATRONES ===")
    for pattern in optimizer.analyze_route_patterns():
        print(pattern)
    
    # Mostrar el reporte de optimizaciones realizadas
    print("\n=== REPORTE DE OPTIMIZACIONES ===")
    for log in optimizer.get_optimization_report():
        print(log)

if __name__ == "__main__":
    main()