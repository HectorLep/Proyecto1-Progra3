import random
from model.graph import Graph
from model.vertex import Vertex
from model.edge import Edge

class SimulationInitializer:
    def __init__(self):
        self.graph = None
        
    def generate_connected_graph(self, n_nodes, m_edges):
        """
        Genera un grafo aleatorio conectado garantizando conectividad
        """
        if m_edges < n_nodes - 1:
            raise ValueError("Número de aristas insuficiente para garantizar conectividad")
            
        # Crear grafo vacío
        self.graph = Graph()
        
        # Crear todos los nodos
        nodes = []
        for i in range(n_nodes):
            node_id = f"N{i}"
            vertex = Vertex(node_id)
            self.graph.add_vertex(vertex)
            nodes.append(vertex)
            
        # Garantizar conectividad: crear árbol generador mínimo
        self._create_spanning_tree(nodes)
        
        # Agregar aristas adicionales para completar m_edges
        self._add_additional_edges(nodes, m_edges)
        
        return self.graph
    
    def _create_spanning_tree(self, nodes):
        """
        Crea un árbol generador para garantizar conectividad
        """
        connected = [nodes[0]]  # Comenzar con el primer nodo
        unconnected = nodes[1:]  # Resto de nodos
        
        while unconnected:
            # Seleccionar nodo conectado y no conectado aleatoriamente
            from_node = random.choice(connected)
            to_node = random.choice(unconnected)
            
            # Crear arista bidireccional con peso aleatorio
            weight = random.randint(1, 15)
            
            edge1 = Edge(from_node, to_node, weight)
            edge2 = Edge(to_node, from_node, weight)
            
            self.graph.add_edge(edge1)
            self.graph.add_edge(edge2)
            
            # Mover nodo a la lista de conectados
            connected.append(to_node)
            unconnected.remove(to_node)
    
    def _add_additional_edges(self, nodes, target_edges):
        """
        Agrega aristas adicionales sin crear duplicados
        """
        current_edges = len(self.graph.edges) // 2  # Dividir por 2 porque son bidireccionales
        
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
        """
        Asigna roles a los nodos: 20% almacén, 20% recarga, 60% cliente
        """
        if not self.graph:
            raise ValueError("Grafo no inicializado")
            
        vertices = list(self.graph.vertices.values())
        n_nodes = len(vertices)
        
        # Calcular cantidades por rol
        n_storage = max(1, int(n_nodes * 0.20))  # Mínimo 1 almacén
        n_charge = max(1, int(n_nodes * 0.20))   # Mínimo 1 recarga
        n_client = n_nodes - n_storage - n_charge
        
        # Mezclar nodos aleatoriamente
        random.shuffle(vertices)
        
        # Asignar roles
        for i, vertex in enumerate(vertices):
            if i < n_storage:
                vertex.set_role("storage")
                vertex.name = f"📦 Storage_{i}"
            elif i < n_storage + n_charge:
                vertex.set_role("charge")
                vertex.name = f"🔋 Charge_{i - n_storage}"
            else:
                vertex.set_role("client")
                vertex.name = f"👤 Client_{i - n_storage - n_charge}"
        
        return {
            "storage": n_storage,
            "charge": n_charge, 
            "client": n_client
        }
    
    def get_nodes_by_role(self, role):
        """
        Obtiene nodos por su rol específico
        """
        if not self.graph:
            return []
            
        return [vertex for vertex in self.graph.vertices.values() 
                if hasattr(vertex, 'role') and vertex.role == role]