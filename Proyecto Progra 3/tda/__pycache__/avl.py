class AVLNode:
    def __init__(self, route_key, frequency=1): # Changed 'route' to 'route_key' for clarity
        self.route_key = route_key  # Route as string key (e.g., "A->B->C")
        self.frequency = frequency  # Number of times route is used
        self.left = None
        self.right = None
        self.height = 0  # Height of the node in the tree

class AVLTree:
    def __init__(self):
        self.root = None

    def _height(self, node):
        return -1 if node is None else node.height

    def _balance_factor(self, node):
        return 0 if node is None else self._height(node.left) - self._height(node.right)

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = max(self._height(y.left), self._height(y.right)) + 1
        x.height = max(self._height(x.left), self._height(x.right)) + 1
        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self._height(x.left), self._height(x.right)) + 1
        y.height = max(self._height(y.left), self._height(y.right)) + 1
        return y

    def insert(self, route_key): # route_key is the string like "N1->N2"
        self.root = self._insert_recursive(self.root, route_key)

    def _insert_recursive(self, node, route_key):
        if node is None:
            return AVLNode(route_key)

        if route_key < node.route_key:
            node.left = self._insert_recursive(node.left, route_key)
        elif route_key > node.route_key:
            node.right = self._insert_recursive(node.right, route_key)
        else:
            node.frequency += 1
            return node # No need to rebalance if only frequency changes

        node.height = max(self._height(node.left), self._height(node.right)) + 1
        balance = self._balance_factor(node)

        # Left-Left Case
        if balance > 1 and route_key < node.left.route_key:
            return self._right_rotate(node)
        # Right-Right Case
        if balance < -1 and route_key > node.right.route_key:
            return self._left_rotate(node)
        # Left-Right Case
        if balance > 1 and route_key > node.left.route_key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        # Right-Left Case
        if balance < -1 and route_key < node.right.route_key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, route_key):
        return self._search_recursive(self.root, route_key)

    def _search_recursive(self, node, route_key):
        if node is None or node.route_key == route_key:
            return node
        if route_key < node.route_key:
            return self._search_recursive(node.left, route_key)
        return self._search_recursive(node.right, route_key)

    def inorder_traversal(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result # Returns list of (route_key, frequency) tuples

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append((node.route_key, node.frequency))
            self._inorder_recursive(node.right, result)

    def get_frequent_routes(self, count=10): # Default count to 10
        all_routes = self.inorder_traversal()
        # Sort by frequency (descending), then by route_key (ascending) as a tie-breaker
        all_routes.sort(key=lambda x: (-x[1], x[0]))
        return all_routes[:count]

    def get_visualization_data(self): # For potential future use with an updated visualizer
        return self._get_visualization_data_recursive(self.root)

    def _get_visualization_data_recursive(self, node):
        if not node:
            return None
        return {
            'route_key': node.route_key, # Changed from 'route' to 'route_key'
            'frequency': node.frequency,
            'left': self._get_visualization_data_recursive(node.left),
            'right': self._get_visualization_data_recursive(node.right),
            'height': node.height,
            'balance_factor': self._balance_factor(node)
        }

    def get_root_for_visualizer(self):
        # This method is specifically for the existing AVLVisualizer,
        # which expects a raw AVLNode-like structure.
        # The visualizer expects node.route, node.left, node.right, node.height, node.balance_factor
        # Our AVLNode has route_key. We will need to adapt AVLVisualizer.py to use 'route_key'
        # or provide a translation here. For now, returning self.root and will adapt visualizer later.
        return self.root