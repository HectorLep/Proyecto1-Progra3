import random
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
        tolerance = 0.05
        
        return (abs(warehouses - expected_warehouses) / total <= tolerance and
                abs(recharges - expected_recharges) / total <= tolerance and
                abs(clients - expected_clients) / total <= tolerance)
    def generate_random_graph(self, num_nodes, num_edges):
        self._outgoing.clear()
        if self._directed:
            self._incoming.clear()

        if num_nodes <= 0:
            return

        types_list = []
        if num_nodes > 0:
            target_warehouse = num_nodes * 0.2
            target_recharge = num_nodes * 0.2
            
            num_w = int(target_warehouse)
            num_r = int(target_recharge)
            
            if num_nodes >= 5:
                num_w = max(1, num_w)
                num_r = max(1, num_r)
            elif num_nodes == 4:
                num_w = 1
                num_r = 1
            elif num_nodes == 3:
                num_w = 1
                num_r = 1
            elif num_nodes == 2:
                num_w = 1
                num_r = 1
            elif num_nodes == 1:
                num_w = 1
                num_r = 0

            num_c = num_nodes - num_w - num_r

            if num_c < 0:
                if num_nodes == 1:
                    num_w = 1; num_r = 0; num_c = 0;
                elif num_nodes == 2:
                    num_w = 1; num_r = 1; num_c = 0;
                elif num_nodes == 3:
                    num_w = 1; num_r = 1; num_c = 1;
                elif num_nodes == 4:
                    num_c = num_nodes - num_w - num_r


            if num_nodes >= 2:
                if num_w == 0:
                    num_w = 1
                    num_c = num_nodes - num_w - num_r # re-calc client
                if num_r == 0:
                    num_r = 1
                    num_c = num_nodes - num_w - num_r # re-calc client
                
                while num_c < 0:
                    if num_w > 1 :
                        num_w -=1
                        num_c +=1
                    elif num_r > 1:
                        num_r -=1
                        num_c +=1
                    else:
                          break

            if num_nodes == 1: num_w=1; num_r=0; num_c=0;
            elif num_nodes == 2: num_w=1; num_r=1; num_c=0;
            elif num_nodes == 3: num_w=1; num_r=1; num_c=1;
            elif num_nodes == 4: num_w=1; num_r=1; num_c=2;


            types_list.extend(['warehouse'] * num_w)
            types_list.extend(['recharge'] * num_r)
            types_list.extend(['client'] * num_c)
            
            while len(types_list) < num_nodes:
                types_list.append('client')
            while len(types_list) > num_nodes:
                # Try to remove client first, then recharge, then warehouse
                if 'client' in types_list: types_list.remove('client')
                elif 'recharge' in types_list: types_list.remove('recharge')
                elif 'warehouse' in types_list: types_list.remove('warehouse')
                else: break

            random.shuffle(types_list)

        vertices = []
        for i in range(num_nodes):
            node_type = types_list[i] if i < len(types_list) else 'client'
            vertices.append(self.insert_vertex(f"N{i+1}", type=node_type))
        
        # Add Edges
        if num_nodes == 0:
            return

        all_vertices = list(self.vertices())
        if not all_vertices:
            return

        edges_added = 0
        possible_edges = []
        for i in range(len(all_vertices)):
            for j in range(i + 1, len(all_vertices)):
                possible_edges.append((all_vertices[i], all_vertices[j]))
        
        random.shuffle(possible_edges)

        for u, v in possible_edges:
            if edges_added >= num_edges:
                break
            if self.get_edge(u,v) is None:
                weight = random.randint(10, 50)
                self.insert_edge(u, v, weight)
                edges_added += 1
        
        if num_nodes > 1 and not self.is_connected():
            components = self._get_connected_components()
            while len(components) > 1:
                comp1 = random.choice(components)
                components.remove(comp1)
                if not components:
                    break 
                comp2 = random.choice(components)


                u = random.choice(list(comp1))
                v = random.choice(list(comp2))

                if self.get_edge(u,v) is None:
                    weight = random.randint(10, 50)
                    self.insert_edge(u, v, weight)
                    # After adding an edge, components need to be re-calculated
                    components = self._get_connected_components() 

        pass

    def _get_connected_components(self):
        """Helper method to find connected components using BFS."""
        if not self._outgoing:
            return []
        
        visited = set()
        components = []
        all_nodes = list(self.vertices())

        for node in all_nodes:
            if node not in visited:
                component = set()
                queue = deque([node])
                visited.add(node)
                component.add(node)
                while queue:
                    v = queue.popleft()
                    if v in self._outgoing:
                        for neighbor in self.neighbors(v):
                            if neighbor not in visited:
                                visited.add(neighbor)
                                component.add(neighbor)
                                queue.append(neighbor)
                components.append(component)
        return components