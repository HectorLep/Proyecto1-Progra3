class Route:
    def __init__(self, path, total_cost, recharge_stops, segments):
        self.path = path  # List of node IDs
        self.total_cost = total_cost
        self.recharge_stops = recharge_stops  # List of recharge node IDs
        self.segments = segments  # List of path segments between recharges

    def __str__(self):
        return (f"Route(path={'→'.join(self.path)}, cost={self.total_cost}, "
                f"recharge_stops={self.recharge_stops})")

    def __repr__(self):
        return self.__str__()
