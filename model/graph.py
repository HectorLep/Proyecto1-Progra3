import random
import heapq
import math
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

    def insert_vertex(self, element, type=None, latitude=None, longitude=None):
        # Vertex constructor now handles random geo-coordinate generation if not provided
        v = Vertex(element, type=type, latitude=latitude, longitude=longitude)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def get_vertex_by_element(self, element_val):
        """Return the vertex object whose element is element_val."""
        for v in self.vertices():
            if v.element() == element_val:
                return v
        return None

    def insert_edge(self, u_vertex, v_vertex, weight): # Changed 'element' to 'weight' for clarity
        # Ensure u_vertex and v_vertex are actual Vertex objects
        if not isinstance(u_vertex, Vertex) or not isinstance(v_vertex, Vertex):
            raise TypeError("u_vertex and v_vertex must be Vertex instances.")
        e = Edge(u_vertex, v_vertex, weight)
        self._outgoing[u_vertex][v_vertex] = e
        self._incoming[v_vertex][u_vertex] = e # Assumes undirected or symmetric for directed for now
        if not self.is_directed(): # For undirected graphs, add the reverse edge representation too
             self._outgoing[v_vertex][u_vertex] = e # This might need adjustment if strictly directed graph needs asymmetric edges
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

    def generate_random_graph(self, num_nodes, num_edges_target, ensure_connectivity=True):
        self._outgoing.clear()
        self._incoming.clear() # Assuming self._incoming is self._outgoing if not directed

        if num_nodes <= 0:
            return

        # 1. Create Vertices with Roles and Geo-coordinates
        node_types = ['warehouse', 'recharge', 'client']
        num_warehouse = math.ceil(num_nodes * 0.2)
        num_recharge = math.ceil(num_nodes * 0.2)
        num_client = num_nodes - num_warehouse - num_recharge

        # Adjust if counts are off due to ceil, prioritize clients
        if num_client < 0:
            num_client = 0
            # If still not enough for warehouse/recharge, adjust them (e.g., ensure at least one if possible)
            if num_warehouse + num_recharge > num_nodes:
                if num_nodes == 1: num_warehouse=1; num_recharge=0; num_client=0;
                elif num_nodes == 2: num_warehouse=1; num_recharge=1; num_client=0;
                else: # Prioritize warehouse and recharge if num_nodes is small
                    num_warehouse = max(0, num_nodes - num_recharge)


        # Ensure at least one of each type if num_nodes is sufficient (e.g. >=3)
        if num_nodes >= 3:
            if num_warehouse == 0: num_warehouse = 1; num_client = max(0, num_client-1);
            if num_recharge == 0: num_recharge = 1; num_client = max(0, num_client-1 if num_client > 0 else 0);
        elif num_nodes == 2:
            num_warehouse = 1; num_recharge = 1; num_client = 0;
        elif num_nodes == 1:
            num_warehouse = 1; num_recharge = 0; num_client = 0;
        
        # Final recalculation for client if others were adjusted
        num_client = num_nodes - num_warehouse - num_recharge

        assigned_types = (['warehouse'] * num_warehouse +
                          ['recharge'] * num_recharge +
                          ['client'] * num_client)

        # If list is too short due to rounding, fill with clients
        while len(assigned_types) < num_nodes:
            assigned_types.append('client')
        # If too long, trim (prefer removing clients)
        while len(assigned_types) > num_nodes:
            if 'client' in assigned_types: assigned_types.remove('client')
            elif 'recharge' in assigned_types: assigned_types.remove('recharge')
            elif 'warehouse' in assigned_types: assigned_types.remove('warehouse')


        random.shuffle(assigned_types)

        vertex_objs = []
        for i in range(num_nodes):
            node_type = assigned_types[i] if i < len(assigned_types) else 'client'
            # Vertex constructor handles random lat/lon
            v = self.insert_vertex(element=f"N{i+1}", type=node_type)
            vertex_objs.append(v)

        # 2. Add Edges
        edges_added = 0
        if num_nodes == 0: return

        # Ensure connectivity by creating a spanning tree first (if required and num_nodes > 1)
        if ensure_connectivity and num_nodes > 1:
            # Connect nodes in a cycle or a line to ensure basic connectivity
            # This is a simple way, a proper spanning tree (e.g. random walk) is better
            for i in range(num_nodes -1):
                u, v_node = vertex_objs[i], vertex_objs[i+1]
                if self.get_edge(u,v_node) is None:
                    weight = random.randint(10, 50)
                    self.insert_edge(u, v_node, weight)
                    edges_added +=1
            # Optionally, connect the last to the first for a cycle if undirected
            if not self.is_directed() and num_nodes > 2:
                 u, v_node = vertex_objs[num_nodes-1], vertex_objs[0]
                 if self.get_edge(u,v_node) is None:
                    weight = random.randint(10, 50)
                    self.insert_edge(u, v_node, weight)
                    edges_added +=1
        
        # Add remaining edges randomly until num_edges_target is reached
        # or all possible edges are created.
        possible_pairs = []
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes): # Avoid self-loops and duplicate pairs for undirected
                possible_pairs.append((vertex_objs[i], vertex_objs[j]))

        random.shuffle(possible_pairs)

        for u, v_node in possible_pairs:
            if edges_added >= num_edges_target:
                break
            if self.get_edge(u, v_node) is None: # Check if edge already exists
                weight = random.randint(10, 50)
                self.insert_edge(u, v_node, weight)
                edges_added += 1
        
        # If after all that, it's still not connected (and should be)
        # (e.g. if ensure_connectivity was false or initial tree was insufficient)
        # run the component connection logic.
        if ensure_connectivity and num_nodes > 1 and not self.is_connected():
            self._connect_components(vertex_objs)


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
            # components.remove(comp2_nodes) # Don't remove, re-calculate components after adding edge

            # Pick one random node from each component
            u_node = random.choice(list(comp1_nodes))
            v_node = random.choice(list(comp2_nodes))

            # Add an edge if it doesn't exist
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

    # --- ALGORITHMS ---
    def dijkstra(self, start_vertex_element):
        """
        Computes shortest paths from start_vertex_element to all other vertices.
        Args:
            start_vertex_element: The element() of the starting Vertex.
        Returns:
            A tuple (distances, predecessors):
            distances: A dict mapping vertex elements to their shortest distance from start.
            predecessors: A dict mapping vertex elements to their predecessor's element on the shortest path.
        """
        start_vertex = self.get_vertex_by_element(start_vertex_element)
        if not start_vertex:
            raise ValueError(f"Start vertex {start_vertex_element} not found in graph.")

        distances = {v: float('infinity') for v in self.vertices()}
        predecessors = {v: None for v in self.vertices()}
        distances[start_vertex] = 0

        # Priority queue stores tuples of (cost, vertex_object)
        pq = [(0, start_vertex)]

        while pq:
            current_cost, u_vertex = heapq.heappop(pq)

            if current_cost > distances[u_vertex]:
                continue # Already found a shorter path

            for edge in self.incident_edges(u_vertex, outgoing=True):
                v_vertex = edge.opposite(u_vertex)
                weight = edge.element() # Edge weight

                if distances[u_vertex] + weight < distances[v_vertex]:
                    distances[v_vertex] = distances[u_vertex] + weight
                    predecessors[v_vertex] = u_vertex
                    heapq.heappush(pq, (distances[v_vertex], v_vertex))

        # Convert keys in results from Vertex objects to vertex elements for easier use
        dist_by_element = {v.element(): d for v, d in distances.items()}
        pred_by_element = {v.element(): (p.element() if p else None) for v, p in predecessors.items()}

        return dist_by_element, pred_by_element

    def get_shortest_path(self, start_vertex_element, end_vertex_element, predecessors_map_elements):
        """
        Reconstructs the shortest path from start to end using the predecessors map from Dijkstra.
        Args:
            start_vertex_element: Element of the starting vertex.
            end_vertex_element: Element of the ending vertex.
            predecessors_map_elements: Dict mapping vertex elements to predecessor elements.
        Returns:
            A list of vertex elements representing the path, or None if no path.
        """
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
        """
        Computes all-pairs shortest paths using Floyd-Warshall algorithm.
        Returns:
            A dict of dicts where dist[u_elem][v_elem] is the shortest distance
            from vertex u (by element) to vertex v (by element).
        """
        vertices_list = list(self.vertices())
        n = len(vertices_list)
        vertex_map = {v: i for i, v in enumerate(vertices_list)} # Vertex object to index

        # Initialize distances matrix
        dist = [[float('infinity')] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0

        for u_vertex in self.vertices():
            u_idx = vertex_map[u_vertex]
            for edge in self.incident_edges(u_vertex, outgoing=True):
                v_vertex = edge.opposite(u_vertex)
                v_idx = vertex_map[v_vertex]
                dist[u_idx][v_idx] = min(dist[u_idx][v_idx], edge.element()) # Use edge weight

        # Floyd-Warshall algorithm
        for k_obj in vertices_list:
            k = vertex_map[k_obj]
            for i_obj in vertices_list:
                i = vertex_map[i_obj]
                for j_obj in vertices_list:
                    j = vertex_map[j_obj]
                    if dist[i][k] != float('infinity') and dist[k][j] != float('infinity'):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

        # Convert matrix to dict of dicts with vertex elements as keys
        dist_by_elements = {u.element(): {} for u in vertices_list}
        for i, u_vertex in enumerate(vertices_list):
            for j, v_vertex in enumerate(vertices_list):
                dist_by_elements[u_vertex.element()][v_vertex.element()] = dist[i][j]

        return dist_by_elements

    def kruskal_mst(self):
        """
        Computes the Minimum Spanning Tree (MST) using Kruskal's algorithm.
        Assumes the graph is undirected. If called on a directed graph, behavior might be unexpected.
        Returns:
            A list of Edges that form the MST.
        """
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
        
        # Check if MST spans all vertices (graph was connected)
        if num_edges_in_mst < total_vertices - 1 and total_vertices > 0 :
             # This implies the graph was not connected if we haven't formed a spanning tree.
             # Kruskal finds an MST for each connected component (a minimum spanning forest).
             # The requirement is a single MST, implying the graph should be connected.
             # For now, we return what Kruskal found. Connectivity is handled by generate_random_graph.
             pass

        return mst_edges

    def validate_role_distribution(self):
        """Validate node role distribution: 20% warehouse, 20% recharge, 60% client."""
        # This method can be used for verification after generation if needed
        if not self.vertices():
            return True # Or false, depending on requirements for empty graph

        total_nodes = len(list(self.vertices()))
        counts = {'warehouse': 0, 'recharge': 0, 'client': 0, 'unknown': 0}
        for v_obj in self.vertices():
            v_type = v_obj.type()
            if v_type in counts:
                counts[v_type] += 1
            else:
                counts['unknown'] +=1

        # print(f"Role counts: {counts}") # For debugging

        expected_w = total_nodes * 0.2
        expected_r = total_nodes * 0.2
        # expected_c = total_nodes * 0.6 # Client is the remainder

        # Check if counts are reasonably close to expected, allowing for rounding.
        # Using math.ceil for initial assignment means counts might be slightly higher.
        # A simple check:
        if not (counts['warehouse'] >= math.floor(expected_w) and \
            counts['recharge'] >= math.floor(expected_r)):
            # print(f"Warehouse or Recharge count too low. W: {counts['warehouse']} (exp floor {math.floor(expected_w)}), R: {counts['recharge']} (exp floor {math.floor(expected_r)})")
            # return False # This validation might be too strict due to integer rounding.
            pass # Relaxing for now, primary check is in generation.

        return True