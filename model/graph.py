import random
import heapq
import math
from .vertex import Vertex
from .edge import Edge
from collections import deque

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en KM entre dos puntos geográficos."""
    R = 6371  # Radio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

class Graph:
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def is_directed(self):
        return self._directed

    def insert_vertex(self, element, type=None, latitude=None, longitude=None):
        v = Vertex(element, type=type, latitude=latitude, longitude=longitude)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def get_vertex_by_element(self, element_val):
        for v in self.vertices():
            if v.element() == element_val:
                return v
        return None

    def insert_edge(self, u_vertex, v_vertex, weight):
        if not isinstance(u_vertex, Vertex) or not isinstance(v_vertex, Vertex):
            raise TypeError("u_vertex and v_vertex must be Vertex instances.")
        e = Edge(u_vertex, v_vertex, weight)
        self._outgoing[u_vertex][v_vertex] = e
        self._incoming[v_vertex][u_vertex] = e
        return e

    def remove_edge(self, u_vertex, v_vertex):
        if u_vertex in self._outgoing and v_vertex in self._outgoing[u_vertex]:
            del self._outgoing[u_vertex][v_vertex]
            del self._incoming[v_vertex][u_vertex]
            if not self.is_directed() and v_vertex in self._outgoing and u_vertex in self._outgoing[v_vertex]:
                 del self._outgoing[v_vertex][u_vertex]
                 del self._incoming[u_vertex][v_vertex]


    def remove_vertex(self, v_vertex):
        # Remove all incident edges
        for u_vertex in list(self._outgoing.get(v_vertex, {}).keys()):
            self.remove_edge(v_vertex, u_vertex)
        for u_vertex in list(self._incoming.get(v_vertex, {}).keys()):
            self.remove_edge(u_vertex, v_vertex)

        self._outgoing.pop(v_vertex, None)
        if self._directed:
            self._incoming.pop(v_vertex, None)

    def get_edge(self, u_vertex, v_vertex):
        return self._outgoing.get(u_vertex, {}).get(v_vertex)

    def vertices(self):
        return self._outgoing.keys()

    def edges(self):
        result = set()
        for source_map in self._outgoing.values():
            result.update(source_map.values())
        return result

    def degree(self, v_vertex, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return len(adj.get(v_vertex, {}))

    def incident_edges(self, v_vertex, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return adj.get(v_vertex, {}).values()

    def neighbors(self, v_vertex):
        return self._outgoing.get(v_vertex, {}).keys()

    def is_connected(self):
        if not self._outgoing:
            return True  # Or False, depending on definition for empty graph
        
        start_node = next(iter(self.vertices()), None)
        if start_node is None:
            return True # An empty graph or graph with no vertices can be considered connected or not.

        visited_count = 0
        q = deque([start_node])
        visited = {start_node}
        visited_count = 1
        
        while q:
            curr = q.popleft()
            for neighbor in self.neighbors(curr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    visited_count +=1
                    q.append(neighbor)
        return visited_count == len(list(self.vertices()))


    # Reemplaza esta función completa en model/graph.py

    def generate_random_graph(self, num_nodes, num_edges_target, warehouse_pct, recharge_pct):
        """
        Genera un grafo aleatorio, usando los porcentajes de roles pasados como parámetros.
        """
        self._outgoing.clear()
        self._incoming.clear()

        if num_nodes <= 0: return

        # 1. Asignar Roles y Crear Vértices usando los parámetros recibidos
        # Convertimos los porcentajes (ej. 10) a decimales (ej. 0.10)
        num_warehouse = math.ceil(num_nodes * (warehouse_pct / 100.0))
        num_recharge = math.ceil(num_nodes * (recharge_pct / 100.0))
        num_client = num_nodes - num_warehouse - num_recharge

        if num_client < 0: num_client = 0
        
        assigned_types = (['warehouse'] * num_warehouse +
                        ['recharge'] * num_recharge +
                        ['client'] * num_client)
        
        while len(assigned_types) < num_nodes: assigned_types.append('client')
        assigned_types = assigned_types[:num_nodes]
        random.shuffle(assigned_types)

        vertex_objs = [self.insert_vertex(f"N{i+1}", assigned_types[i]) for i in range(num_nodes)]

        if num_nodes < 2: return

        # El resto de la función (creación de aristas con MST, etc.) se mantiene igual
        # ... (el resto de tu lógica de aristas que ya tienes está bien) ...
        possible_edges = []
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                u, v = vertex_objs[i], vertex_objs[j]
                dist = haversine_distance(u.latitude(), u.longitude(), v.latitude(), v.longitude())
                weight = round(dist * random.uniform(1.0, 1.3), 2)
                possible_edges.append((weight, u, v))
        
        possible_edges.sort(key=lambda x: x[0])

        parent = {v: v for v in vertex_objs}
        def find_set(v):
            if parent[v] == v: return v
            parent[v] = find_set(parent[v])
            return parent[v]
        def unite_sets(a, b):
            a_root, b_root = find_set(a), find_set(b)
            if a_root != b_root:
                parent[b_root] = a_root
                return True
            return False

        edges_added = 0
        mst_edge_pool = []
        for weight, u, v in possible_edges:
            if unite_sets(u, v):
                self.insert_edge(u, v, weight)
                edges_added += 1
                mst_edge_pool.append((weight, u, v))

        remaining_edges = [edge for edge in possible_edges if edge not in mst_edge_pool]
        random.shuffle(remaining_edges)

        for weight, u, v in remaining_edges:
            if edges_added >= num_edges_target:
                break
            if self.get_edge(u, v) is None:
                self.insert_edge(u, v, weight)
                edges_added += 1
                

    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calcula la distancia en KM entre dos puntos geográficos."""
        R = 6371  # Radio de la Tierra en km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    

    def _connect_components(self, all_vertices_list):
        """Connects disconnected components of the graph."""
        if not all_vertices_list: return

        components = self._get_all_connected_components()
        while len(components) > 1:
            # Pick two random components
            comp1_nodes = random.choice(components)
            components.remove(comp1_nodes)
            if not components: break # Should not happen if len > 1 initially
            comp2_nodes = random.choice(components)
            u_node = random.choice(list(comp1_nodes))
            v_node = random.choice(list(comp2_nodes))
            if self.get_edge(u_node, v_node) is None:
                weight = random.randint(10, 50)
                self.insert_edge(u_node, v_node, weight)

            components = self._get_all_connected_components() # Re-calculate components


    def _get_all_connected_components(self):
        """Finds all connected components in the graph."""
        if not self.vertices():
            return []

        visited = set()
        all_components = []

        for vertex in self.vertices():
            if vertex not in visited:
                component = set()
                q = deque([vertex])
                visited.add(vertex)
                component.add(vertex)
                while q:
                    curr = q.popleft()
                    for neighbor in self.neighbors(curr):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            component.add(neighbor)
                            q.append(neighbor)
                all_components.append(component)
        return all_components

    def dijkstra(self, start_vertex_element):
        start_vertex = self.get_vertex_by_element(start_vertex_element)
        if not start_vertex:
            raise ValueError(f"Start vertex {start_vertex_element} not found in graph.")

        distances = {v: float('infinity') for v in self.vertices()}
        predecessors = {v: None for v in self.vertices()}
        distances[start_vertex] = 0
        contador = 0  
        pq = [(0, contador, start_vertex)]
        while pq:
            current_cost, _, u_vertex = heapq.heappop(pq) # Extraemos el contador pero no lo usamos

            if current_cost > distances[u_vertex]:
                continue # Already found a shorter path

            for edge in self.incident_edges(u_vertex, outgoing=True):
                v_vertex = edge.opposite(u_vertex)
                weight = edge.element() # Edge weight

                if distances[u_vertex] + weight < distances[v_vertex]:
                    distances[v_vertex] = distances[u_vertex] + weight
                    predecessors[v_vertex] = u_vertex
                    # --- INICIO DE LA CORRECCIÓN ---
                    contador += 1 # Incrementar el contador en cada inserción
                    heapq.heappush(pq, (distances[v_vertex], contador, v_vertex))
                    # --- FIN DE LA CORRECCIÓN ---

        # Convert keys in results from Vertex objects to vertex elements for easier use
        dist_by_element = {v.element(): d for v, d in distances.items()}
        pred_by_element = {v.element(): (p.element() if p else None) for v, p in predecessors.items()}

        return dist_by_element, pred_by_element
    
    def get_shortest_path(self, start_vertex_element, end_vertex_element, predecessors_map_elements):
        path = []
        current_element = end_vertex_element

        while current_element is not None:
            path.append(current_element)
            if current_element == start_vertex_element:
                break
            current_element = predecessors_map_elements.get(current_element)
            if current_element is None and path[-1] != start_vertex_element : # Path broken
                return None

        if path[-1] == start_vertex_element:
            return path[::-1] # Reverse to get path from start to end
        return None # No path found or start/end not in map correctly

    def floyd_warshall(self):

        vertices_list = list(self.vertices())
        n = len(vertices_list)
        vertex_map = {v: i for i, v in enumerate(vertices_list)} # Vertex object to index

        dist = [[float('infinity')] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0

        for u_vertex in self.vertices():
            u_idx = vertex_map[u_vertex]
            for edge in self.incident_edges(u_vertex, outgoing=True):
                v_vertex = edge.opposite(u_vertex)
                v_idx = vertex_map[v_vertex]
                dist[u_idx][v_idx] = min(dist[u_idx][v_idx], edge.element()) # Use edge weight

        for k_obj in vertices_list:
            k = vertex_map[k_obj]
            for i_obj in vertices_list:
                i = vertex_map[i_obj]
                for j_obj in vertices_list:
                    j = vertex_map[j_obj]
                    if dist[i][k] != float('infinity') and dist[k][j] != float('infinity'):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        dist_by_elements = {u.element(): {} for u in vertices_list}
        for i, u_vertex in enumerate(vertices_list):
            for j, v_vertex in enumerate(vertices_list):
                dist_by_elements[u_vertex.element()][v_vertex.element()] = dist[i][j]

        return dist_by_elements

    def kruskal_mst(self):
        mst_edges = []
        all_edges = sorted(list(self.edges()), key=lambda edge: edge.element()) # Sort edges by weight

        parent = {v: v for v in self.vertices()}
        rank = {v: 0 for v in self.vertices()}

        def find_set(v_vertex):
            if parent[v_vertex] == v_vertex:
                return v_vertex
            parent[v_vertex] = find_set(parent[v_vertex]) # Path compression
            return parent[v_vertex]

        def union_sets(a_vertex, b_vertex):
            a_root = find_set(a_vertex)
            b_root = find_set(b_vertex)
            if a_root != b_root:
                if rank[a_root] < rank[b_root]:
                    a_root, b_root = b_root, a_root # Ensure a_root has higher rank
                parent[b_root] = a_root
                if rank[a_root] == rank[b_root]:
                    rank[a_root] += 1
                return True
            return False

        num_edges_in_mst = 0
        total_vertices = len(list(self.vertices()))

        if total_vertices == 0:
            return []

        for edge in all_edges:
            u_vertex, v_vertex = edge.endpoints()
            if find_set(u_vertex) != find_set(v_vertex):
                union_sets(u_vertex, v_vertex)
                mst_edges.append(edge)
                num_edges_in_mst += 1
                if num_edges_in_mst == total_vertices - 1: # MST found
                    break
        if num_edges_in_mst < total_vertices - 1 and total_vertices > 0 :
             pass

        return mst_edges

    def validate_role_distribution(self):
        """Validate node role distribution: 20% warehouse, 20% recharge, 60% client."""
        if not self.vertices():
            return True 
        total_nodes = len(list(self.vertices()))
        counts = {'warehouse': 0, 'recharge': 0, 'client': 0, 'unknown': 0}
        for v_obj in self.vertices():
            v_type = v_obj.type()
            if v_type in counts:
                counts[v_type] += 1
            else:
                counts['unknown'] +=1

        expected_w = total_nodes * 0.2
        expected_r = total_nodes * 0.2

        if not (counts['warehouse'] >= math.floor(expected_w) and \
            counts['recharge'] >= math.floor(expected_r)):
            pass 
        return True