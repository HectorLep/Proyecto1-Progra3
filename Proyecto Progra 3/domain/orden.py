from datetime import datetime

class Order:
    def __init__(self, id, client, origin, destination, priority=1):
        self.id = id
        self.client = client
        self.client_id = client.id
        self.origin = origin
        self.destination = destination
        self.status = "pending"  # pending, delivered, failed
        self.creation_date = datetime.now()
        self.priority = priority  # 1 (low) to 5 (high)
        self.delivery_date = None
        self.total_cost = 0

    def mark_delivered(self, cost):
        self.status = "delivered"
        self.delivery_date = datetime.now()
        self.total_cost = cost
        self.client.increment_orders()

    def mark_failed(self):
        self.status = "failed"
        self.delivery_date = datetime.now()

    def __str__(self):
        return (f"Order(id={self.id}, client={self.client_id}, origin={self.origin}, "
                f"destination={self.destination}, status={self.status}, priority={self.priority})")

    def __repr__(self):
        return self.__str__()