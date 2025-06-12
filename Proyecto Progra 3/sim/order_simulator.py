import random
from datetime import datetime, timedelta
from domain.orden import Order
from domain.cliente import Client

class OrderSimulator:
    def __init__(self, graph):
        self.graph = graph
        self.clients = []
        self.orders = []
        self.order_counter = 0
        
    def generate_clients(self):
        """
        Genera clientes basados en nodos con rol 'client'
        """
        client_nodes = [vertex for vertex in self.graph.vertices.values() 
                       if hasattr(vertex, 'role') and vertex.role == 'client']
        
        self.clients = []
        for i, node in enumerate(client_nodes):
            client = Client(
                client_id=f"C{i:03d}",
                name=f"Cliente_{i}",
                node_id=node.id,
                priority=random.randint(1, 5)  # Prioridad 1-5
            )
            self.clients.append(client)
            
        return self.clients
    
    def generate_orders(self, n_orders):
        """
        Genera órdenes aleatorias para la simulación
        """
        if not self.clients:
            self.generate_clients()
            
        storage_nodes = [vertex for vertex in self.graph.vertices.values() 
                        if hasattr(vertex, 'role') and vertex.role == 'storage']
        
        if not storage_nodes:
            raise ValueError("No hay nodos de almacenamiento disponibles")
            
        self.orders = []
        base_date = datetime.now()
        
        for i in range(n_orders):
            # Seleccionar cliente y origen aleatorios
            client = random.choice(self.clients)
            origin = random.choice(storage_nodes)
            destination_node = self.graph.vertices[client.node_id]
            
            # Crear orden
            order = Order(
                order_id=f"ORD{self.order_counter:04d}",
                client_id=client.client_id,
                origin_id=origin.id,
                destination_id=destination_node.id,
                priority=client.priority,
                creation_date=base_date + timedelta(minutes=random.randint(0, 1440))
            )
            
            self.orders.append(order)
            self.order_counter += 1
            
        return self.orders
    
    def get_order_statistics(self):
        """
        Obtiene estadísticas de las órdenes generadas
        """
        if not self.orders:
            return {}
            
        priority_counts = {}
        status_counts = {}
        
        for order in self.orders:
            # Contar por prioridad
            priority_counts[order.priority] = priority_counts.get(order.priority, 0) + 1
            
            # Contar por estado
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
            
        return {
            "total_orders": len(self.orders),
            "priority_distribution": priority_counts,
            "status_distribution": status_counts,
            "total_clients": len(self.clients)
        }
    
    def get_client_orders(self, client_id):
        """
        Obtiene todas las órdenes de un cliente específico
        """
        return [order for order in self.orders if order.client_id == client_id]
    
    def update_client_order_count(self):
        """
        Actualiza el contador de órdenes por cliente
        """
        for client in self.clients:
            client.total_orders = len(self.get_client_orders(client.client_id))