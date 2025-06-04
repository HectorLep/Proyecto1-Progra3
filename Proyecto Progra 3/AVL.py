class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0  # nodo singular tiene altura 0

def height(N):
    return -1 if N is None else N.height

def get_balance(N):
    return 0 if N is None else height(N.left) - height(N.right)

def right_rotate(y):
    x = y.left
    T2 = x.right

    # Rotación
    x.right = y
    y.left = T2

    # Actualizar alturas
    y.height = max(height(y.left), height(y.right)) + 1
    x.height = max(height(x.left), height(x.right)) + 1

    return x

def left_rotate(x):
    y = x.right
    T2 = y.left

    # Rotación
    y.left = x
    x.right = T2

    # Actualizar alturas
    x.height = max(height(x.left), height(x.right)) + 1
    y.height = max(height(y.left), height(y.right)) + 1

    return y

def insert(node, key):
    if node is None:
        return Node(key)

    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    else:
        return node  # no se permiten duplicados

    node.height = max(height(node.left), height(node.right)) + 1
    balance = get_balance(node)

    # Casos de desbalanceo
    if balance > 1 and key < node.left.key:
        return right_rotate(node)
    if balance < -1 and key > node.right.key:
        return left_rotate(node)
    if balance > 1 and key > node.left.key:
        node.left = left_rotate(node.left)
        return right_rotate(node)
    if balance < -1 and key < node.right.key:
        node.right = right_rotate(node.right)
        return left_rotate(node)

    return node

def min_value_node(node):
    current = node
    while current.left:
        current = current.left
    return current

def delete_node(root, key):
    if root is None:
        return root

    if key < root.key:
        root.left = delete_node(root.left, key)
    elif key > root.key:
        root.right = delete_node(root.right, key)
    else:
        if root.left is None or root.right is None:
            root = root.left or root.right
        else:
            temp = min_value_node(root.right)
            root.key = temp.key
            root.right = delete_node(root.right, temp.key)

    if root is None:
        return root

    root.height = max(height(root.left), height(root.right)) + 1
    balance = get_balance(root)

    if balance > 1 and get_balance(root.left) >= 0:
        return right_rotate(root)
    if balance > 1 and get_balance(root.left) < 0:
        root.left = left_rotate(root.left)
        return right_rotate(root)
    if balance < -1 and get_balance(root.right) <= 0:
        return left_rotate(root)
    if balance < -1 and get_balance(root.right) > 0:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root

def pre_order(root):
    if root:
        print(f"{root.key} ", end="")
        pre_order(root.left)
        pre_order(root.right)

# Prueba
if __name__ == "__main__":
    root = None
    for key in [9, 5, 10, 0, 6, 11, -1, 1, 2]:
        root = insert(root, key)

    print("Preorden del AVL construido:")
    pre_order(root)

    root = delete_node(root, 10)
    print("\nPreorden luego de eliminar 10:")
    pre_order(root)
