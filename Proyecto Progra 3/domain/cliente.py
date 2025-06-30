class Client:
    def __init__(self, id, name, node_id, client_type: str):
        self.id = id
        self.name = name
        self.node_id = node_id
        self.type = client_type 
        self.total_orders = 0

    def increment_orders(self):
        self.total_orders += 1

    def __str__(self):
        return f"Client(id={self.id}, name={self.name}, type={self.type}, orders={self.total_orders})"

    def __repr__(self):
        return self.__str__()