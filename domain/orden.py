from datetime import datetime

class Order:
    def __init__(self, order_id, client, origin, destination, weight, priority):
        self.order_id = order_id 
        self.client = client
        self.client_id = client.id
        self.origin = origin
        self.destination = destination
        self.weight = weight  
        self.priority = priority 
        self.status = "pending"  
        self.creation_date = datetime.now()
        self.delivery_date = None
        self.total_cost = 0

    def mark_delivered(self, cost):
        self.status = "Entregado" 
        self.delivery_date = datetime.now()
        self.total_cost = cost
        self.client.increment_orders()

    def mark_failed(self):
        self.status = "failed"
        self.delivery_date = datetime.now()

    def __str__(self):
        return (f"Order(id={self.order_id}, client={self.client_id}, origin={self.origin}, "
                f"destination={self.destination}, status={self.status}, priority={self.priority})")

    def __repr__(self):
        return self.__str__()