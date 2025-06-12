import random
from model.graph import Graph
from model.vertex import Vertex
from model.edge import Edge

class SimulationInitializer:
    def __init__(self):
        self.graph = None
        
    def generate_connected_graph(self, n_nodes, m_edges):
        if m_edges < n_nodes - 1:
            raise ValueError("Número de aristas insuficiente para garantizar conectividad")
            
        self.graph = Graph()
        nodes = [Vertex(f"N{i}") for i in range(n_nodes)]
        for node in nodes:
            self.graph.add_vertex(node)
        
        self._create_spanning_tree(nodes)
        self._add_additional_edges(nodes, m_edges)
        
        return self.graph
    
    def _create_spanning_tree(self, nodes):
        connected = [nodes[0]]
        unconnected = nodes[1:]
        
        while unconnected:
            from_node = random.choice(connected)
            to_node = random.choice(unconnected)
            weight = random.randint(1, 15)
            edge1 = Edge(from_node, to_node, weight)
            edge2 = Edge(to_node, from_node, weight)
            self.graph.add_edge(edge1)
            self.graph.add_edge(edge2)
            connected.append(to_node)
            unconnected.remove(to_node)
    
    def _add_additional_edges(self, nodes, target_edges):
        current_edges = len(self.graph.edges) // 2
        while current_edges < target_edges:
            from_node = random.choice(nodes)
            to_node = random.choice(nodes)
            if from_node != to_node and not self.graph.has_edge(from_node.id, to_node.id):
                weight = random.randint(1, 15)
                edge1 = Edge(from_node, to_node, weight)
                edge2 = Edge(to_node, from_node, weight)
                self.graph.add_edge(edge1)
                self.graph.add_edge(edge2)
                current_edges += 1
    
    def assign_node_roles(self):
        if not self.graph:
            raise ValueError("Grafo no inicializado")
            
        vertices = list(self.graph.vertices.values())
        random.shuffle(vertices)
        
        for i, vertex in enumerate(vertices):
            if i < len(vertices) * 0.20:
                vertex.set_role("storage")
            elif i < len(vertices) * 0.40:
                vertex.set_role("charge")
            else:
                vertex.set_role("client")
        
        return {"storage": int(len(vertices) * 0.20), "charge": int(len(vertices) * 0.20), "client": int(len(vertices) * 0.60)}
