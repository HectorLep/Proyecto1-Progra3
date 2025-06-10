class Client:
    def __init__(self, id, name, type="client"):
        self.id = id
        self.name = name
        self.type = type  # 'client', 'warehouse', or 'recharge'
        self.total_orders = 0

    def increment_orders(self):
        self.total_orders += 1

    def __str__(self):
        return f"Client(id={self.id}, name={self.name}, type={self.type}, orders={self.total_orders})"

    def __repr__(self):
        return self.__str__()