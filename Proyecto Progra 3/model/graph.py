from .vertex import Vertex
from .edge import Edge
from collections import deque

class Graph:
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def is_directed(self):
        return self._directed

    def insert_vertex(self, element, type=None):
        v = Vertex(element, type)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, element):
        e = Edge(u, v, element)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
        return e

    def remove_edge(self, u, v):
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        return self._outgoing.keys()

    def edges(self):
        seen = set()
        for map in self._outgoing.values():
            seen.update(map.values())
        return seen

    def neighbors(self, v):
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()

    def is_connected(self):
        """Check if the graph is connected using BFS."""
        if not self._outgoing:
            return True
        start = next(iter(self._outgoing))
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            v = queue.popleft()
            for u in self.neighbors(v):
                if u not in visited:
                    visited.add(u)
                    queue.append(u)
        
        return len(visited) == len(self._outgoing)

    def validate_role_distribution(self):
        """Validate node role distribution: 20% warehouse, 20% recharge, 60% client."""
        if not self._outgoing:
            return True
        total = len(self._outgoing)
        warehouses = sum(1 for v in self._outgoing if v.type() == 'warehouse')
        recharges = sum(1 for v in self._outgoing if v.type() == 'recharge')
        clients = sum(1 for v in self._outgoing if v.type() == 'client')
        
        expected_warehouses = total * 0.2
        expected_recharges = total * 0.2
        expected_clients = total * 0.6
        tolerance = 0.05  # Allow 5% deviation
        
        return (abs(warehouses - expected_warehouses) / total <= tolerance and
                abs(recharges - expected_recharges) / total <= tolerance and
                abs(clients - expected_clients) / total <= tolerance)