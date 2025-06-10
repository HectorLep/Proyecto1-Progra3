class AVLNode:
    def __init__(self, route, frequency=1):
        self.route = route  # Route as string (e.g., "A→B→C")
        self.frequency = frequency  # Number of times route is used
        self.left = None
        self.right = None
        self.height = 0

def avl_height(node):
    """Return the height of the node or -1 if None."""
    return -1 if node is None else node.height

def avl_balance(node):
    """Return the balance factor of the node."""
    return 0 if node is None else avl_height(node.left) - avl_height(node.right)

def avl_right_rotate(y):
    """Perform a right rotation on node y."""
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1
    return x

def avl_left_rotate(x):
    """Perform a left rotation on node x."""
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1
    return y

def avl_insert(node, route):
    """Insert a route into the AVL tree or increment frequency if it exists."""
    if node is None:
        return AVLNode(route)
    
    if route < node.route:
        node.left = avl_insert(node.left, route)
    elif route > node.route:
        node.right = avl_insert(node.right, route)
    else:
        node.frequency += 1
        return node
    
    node.height = max(avl_height(node.left), avl_height(node.right)) + 1
    balance = avl_balance(node)
    
    # Left-Left Case
    if balance > 1 and route < node.left.route:
        return avl_right_rotate(node)
    # Right-Right Case
    if balance < -1 and route > node.right.route:
        return avl_left_rotate(node)
    # Left-Right Case
    if balance > 1 and route > node.left.route:
        node.left = avl_left_rotate(node.left)
        return avl_right_rotate(node)
    # Right-Left Case
    if balance < -1 and route < node.right.route:
        node.right = avl_right_rotate(node.right)
        return avl_left_rotate(node)
    
    return node

def avl_search(node, route):
    """Search for a route in the AVL tree."""
    if node is None or node.route == route:
        return node
    if route < node.route:
        return avl_search(node.left, route)
    return avl_search(node.right, route)

def avl_inorder(node, result):
    """Perform inorder traversal to collect routes and frequencies."""
    if node:
        avl_inorder(node.left, result)
        result.append((node.route, node.frequency))
        avl_inorder(node.right, result)

def avl_to_visualization_data(node):
    """Generate data for AVL visualization (node, frequency, children)."""
    if not node:
        return None
    return {
        'route': node.route,
        'frequency': node.frequency,
        'left': avl_to_visualization_data(node.left),
        'right': avl_to_visualization_data(node.right)
    }