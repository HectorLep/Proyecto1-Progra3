import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import FancyBboxPatch
import math

def create_pie_chart(values, labels, title, colors=None):
    """Create a pie chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(8, 6))
    if colors is None:
        colors = ['#8B4513', '#FFA500', '#32CD32']
    
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                      colors=colors, startangle=90)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text bold and white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    return fig

def create_bar_chart(x_data, y_data, title, colors=None, xlabel='', ylabel=''):
    """Create a bar chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(8, 6))
    if colors is None:
        colors = ['#8B4513', '#FFA500', '#32CD32']
    
    bars = ax.bar(x_data, y_data, color=colors)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Rotate x-axis labels if they're long
    if any(len(str(label)) > 8 for label in x_data):
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

def create_horizontal_bar_chart(x_data, y_data, title, color='#007bff'):
    """Create a horizontal bar chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(y_data, x_data, color=color)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Value', fontsize=12)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_line_chart(x_data, y_data, title, xlabel='', ylabel='', color='#007bff'):
    """Create a line chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x_data, y_data, color=color, linewidth=2, marker='o', markersize=6)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

class AVLNode:
    """Simplified AVL Node for visualization purposes"""
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1
        self.balance_factor = 0

class AVLTreeVisualizer:
    """Class for visualizing AVL Trees"""
    
    def __init__(self):
        self.node_radius = 0.3
        self.level_height = 1.0
        self.horizontal_spacing = 1.5
    
    def create_sample_tree(self, keys):
        """Create a sample AVL tree for visualization"""
        root = None
        for key in keys:
            root = self._insert(root, key)
        return root
    
    def _insert(self, node, key):
        """Insert a key into the AVL tree"""
        if not node:
            return AVLNode(key)
        
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node  # Duplicate keys not allowed
        
        # Update height and balance factor
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.balance_factor = self._get_height(node.left) - self._get_height(node.right)
        
        # Perform rotations if necessary
        return self._rebalance(node)
    
    def _get_height(self, node):
        """Get the height of a node"""
        if not node:
            return 0
        return node.height
    
    def _rebalance(self, node):
        """Rebalance the AVL tree"""
        # Left heavy
        if node.balance_factor > 1:
            if node.left.balance_factor < 0:
                node.left = self._rotate_left(node.left)
            node = self._rotate_right(node)
        
        # Right heavy
        elif node.balance_factor < -1:
            if node.right.balance_factor > 0:
                node.right = self._rotate_right(node.right)
            node = self._rotate_left(node)
        
        return node
    
    def _rotate_left(self, z):
        """Perform left rotation"""
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        z.balance_factor = self._get_height(z.left) - self._get_height(z.right)
        y.balance_factor = self._get_height(y.left) - self._get_height(y.right)
        
        return y
    
    def _rotate_right(self, z):
        """Perform right rotation"""
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        z.balance_factor = self._get_height(z.left) - self._get_height(z.right)
        y.balance_factor = self._get_height(y.left) - self._get_height(y.right)
        
        return y
    
    def visualize_tree(self, root, title="AVL Tree", figsize=(12, 8)):
        """Create a visual representation of the AVL tree"""
        if not root:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'Empty Tree', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.axis('off')
            return fig
        
        # Calculate positions
        positions = {}
        self._calculate_positions(root, 0, 0, 4, positions)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Draw edges first
        self._draw_edges(ax, root, positions)
        
        # Draw nodes
        self._draw_nodes(ax, root, positions)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.axis('equal')
        ax.axis('off')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Node', 
                      markerfacecolor='lightblue', markersize=10, markeredgecolor='black'),
            plt.Line2D([0], [0], color='black', label='Edge', linewidth=2)
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def _calculate_positions(self, node, x, y, spacing, positions):
        """Calculate positions for all nodes in the tree"""
        if not node:
            return
        
        positions[node] = (x, y)
        
        if node.left:
            self._calculate_positions(node.left, x - spacing, y - self.level_height, 
                                    spacing / 2, positions)
        
        if node.right:
            self._calculate_positions(node.right, x + spacing, y - self.level_height, 
                                    spacing / 2, positions)
    
    def _draw_edges(self, ax, node, positions):
        """Draw edges between nodes"""
        if not node:
            return
        
        x, y = positions[node]
        
        if node.left:
            left_x, left_y = positions[node.left]
            ax.plot([x, left_x], [y, left_y], 'k-', linewidth=2, alpha=0.7)
            self._draw_edges(ax, node.left, positions)
        
        if node.right:
            right_x, right_y = positions[node.right]
            ax.plot([x, right_x], [y, right_y], 'k-', linewidth=2, alpha=0.7)
            self._draw_edges(ax, node.right, positions)
    
    def _draw_nodes(self, ax, node, positions):
        """Draw nodes with their values and balance factors"""
        if not node:
            return
        
        x, y = positions[node]
        
        # Draw node circle
        circle = plt.Circle((x, y), self.node_radius, color='lightblue', 
                          ec='black', linewidth=2, zorder=3)
        ax.add_patch(circle)
        
        # Draw key (route_key or key) and frequency if available
        display_text = ""
        if hasattr(node, 'route_key'):
            display_text = str(node.route_key)
            if hasattr(node, 'frequency'):
                display_text += f"\n(f:{node.frequency})"
        elif hasattr(node, 'key'):
            display_text = str(node.key)

        ax.text(x, y, display_text, ha='center', va='center',
               fontsize=9, fontweight='bold', zorder=4) # Adjusted fontsize for potentially longer text

        # Draw balance factor if available (visualizer calculates it for its own nodes)
        # For external nodes, it might not be present.
        balance_factor_text = ""
        if hasattr(node, 'balance_factor'):
            balance_factor_text = f'BF:{node.balance_factor}'
        elif hasattr(node, '_balance_factor'): # If it's an AVLTree node and method exists
            # This won't work as _balance_factor needs the tree instance context
            pass

        ax.text(x + self.node_radius + 0.1, y + self.node_radius + 0.1, 
               balance_factor_text, ha='left', va='bottom',
               fontsize=8, color='red', fontweight='bold', zorder=4)
        
        # Draw height
        ax.text(x - self.node_radius - 0.1, y + self.node_radius + 0.1, 
               f'H:{node.height}', ha='right', va='bottom', 
               fontsize=8, color='blue', fontweight='bold', zorder=4)
        
        # Recursively draw children
        self._draw_nodes(ax, node.left, positions)
        self._draw_nodes(ax, node.right, positions)

def create_avl_operations_demo(operations_list):
    """Create a demo showing AVL tree operations"""
    visualizer = AVLTreeVisualizer()
    
    # Number of operations to show
    num_ops = len(operations_list)
    if num_ops == 0:
        return None
    
    # Calculate grid dimensions
    cols = min(3, num_ops)  # Maximum 3 columns
    rows = (num_ops + cols - 1) // cols  # Ceiling division
    
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 6 * rows))
    
    # Handle single subplot case
    if num_ops == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if hasattr(axes, '__len__') else [axes]
    else:
        axes = axes.flatten()
    
    root = None
    
    for i, op in enumerate(operations_list):
        if i >= len(axes):
            break
            
        if op['type'] == 'insert':
            root = visualizer._insert(root, op['key'])
            title = f"After inserting {op['key']}"
        elif op['type'] == 'delete':
            root = visualizer._delete(root, op['key'])
            title = f"After deleting {op['key']}"
        else:
            title = f"Operation {i+1}"
        
        # Create visualization for current state
        ax = axes[i]
        plt.sca(ax)
        
        if root:
            positions = {}
            visualizer._calculate_positions(root, 0, 0, 3, positions)
            visualizer._draw_edges(ax, root, positions)
            visualizer._draw_nodes(ax, root, positions)
        else:
            ax.text(0.5, 0.5, 'Empty Tree', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('equal')
        ax.axis('off')
    
    # Hide unused subplots
    for i in range(num_ops, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    return fig

# Additional methods to complete the AVLTreeVisualizer class
def _delete(self, node, key):
    """Delete a key from the AVL tree"""
    if not node:
        return node
    
    if key < node.key:
        node.left = self._delete(node.left, key)
    elif key > node.key:
        node.right = self._delete(node.right, key)
    else:
        # Node to be deleted found
        if not node.left:
            return node.right
        elif not node.right:
            return node.left
        else:
            # Node has two children
            temp = self._find_min(node.right)
            node.key = temp.key
            node.right = self._delete(node.right, temp.key)
    
    # Update height and balance factor
    node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
    node.balance_factor = self._get_height(node.left) - self._get_height(node.right)
    
    # Rebalance
    return self._rebalance(node)

def _find_min(self, node):
    """Find the minimum node in a subtree"""
    while node.left:
        node = node.left
    return node

def _search(self, node, key):
    """Search for a key in the AVL tree"""
    if not node or node.key == key:
        return node
    
    if key < node.key:
        return self._search(node.left, key)
    return self._search(node.right, key)

def _inorder_traversal(self, node, result):
    """Perform inorder traversal of the tree"""
    if node:
        self._inorder_traversal(node.left, result)
        result.append(node.route_key if hasattr(node, 'route_key') else node.key)
        self._inorder_traversal(node.right, result)

def _preorder_traversal(self, node, result):
    """Perform preorder traversal of the tree"""
    if node:
        result.append(node.route_key if hasattr(node, 'route_key') else node.key)
        self._preorder_traversal(node.left, result)
        self._preorder_traversal(node.right, result)

def _postorder_traversal(self, node, result):
    """Perform postorder traversal of the tree"""
    if node:
        self._postorder_traversal(node.left, result)
        self._postorder_traversal(node.right, result)
        result.append(node.route_key if hasattr(node, 'route_key') else node.key)

# Add these methods to the AVLTreeVisualizer class
AVLTreeVisualizer._delete = _delete
AVLTreeVisualizer._find_min = _find_min
AVLTreeVisualizer._search = _search
AVLTreeVisualizer._inorder_traversal = _inorder_traversal
AVLTreeVisualizer._preorder_traversal = _preorder_traversal
AVLTreeVisualizer._postorder_traversal = _postorder_traversal

def get_tree_traversals(visualizer, root):
    """Get all three traversals of the tree"""
    inorder = []
    preorder = []
    postorder = []
    
    visualizer._inorder_traversal(root, inorder)
    visualizer._preorder_traversal(root, preorder)
    visualizer._postorder_traversal(root, postorder)
    
    return {
        'inorder': inorder,
        'preorder': preorder,
        'postorder': postorder
    }

def create_tree_comparison(trees_data, titles=None):
    """Create a comparison visualization of multiple AVL trees"""
    visualizer = AVLTreeVisualizer()
    num_trees = len(trees_data)
    
    if num_trees == 0:
        return None
    
    # Calculate grid dimensions
    cols = min(2, num_trees)
    rows = (num_trees + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(8 * cols, 6 * rows))
    
    if num_trees == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if hasattr(axes, '__len__') else [axes]
    else:
        axes = axes.flatten()
    
    for i, tree_keys in enumerate(trees_data):
        if i >= len(axes):
            break
        
        # Create tree
        root = visualizer.create_sample_tree(tree_keys)
        
        ax = axes[i]
        plt.sca(ax)
        
        if root:
            positions = {}
            visualizer._calculate_positions(root, 0, 0, 3, positions)
            visualizer._draw_edges(ax, root, positions)
            visualizer._draw_nodes(ax, root, positions)
        else:
            ax.text(0.5, 0.5, 'Empty Tree', ha='center', va='center',
                   fontsize=16, transform=ax.transAxes)
        
        title = titles[i] if titles and i < len(titles) else f"Tree {i+1}"
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('equal')
        ax.axis('off')
    
    # Hide unused subplots
    for i in range(num_trees, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    return fig

def create_rotation_demo():
    """Create a demonstration of AVL rotations"""
    visualizer = AVLTreeVisualizer()
    
    # Create scenarios that trigger rotations
    scenarios = [
        {
            'keys': [10, 5, 15],
            'title': 'Balanced Tree',
            'description': 'Initial balanced state'
        },
        {
            'keys': [10, 5, 15, 3],
            'title': 'After adding 3',
            'description': 'Still balanced'
        },
        {
            'keys': [10, 5, 15, 3, 1],
            'title': 'Right Rotation Needed',
            'description': 'Left-heavy, triggers right rotation'
        },
        {
            'keys': [10, 5, 15, 20, 25],
            'title': 'Left Rotation Needed',
            'description': 'Right-heavy, triggers left rotation'
        }
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for i, scenario in enumerate(scenarios):
        root = visualizer.create_sample_tree(scenario['keys'])
        
        ax = axes[i]
        plt.sca(ax)
        
        if root:
            positions = {}
            visualizer._calculate_positions(root, 0, 0, 2.5, positions)
            visualizer._draw_edges(ax, root, positions)
            visualizer._draw_nodes(ax, root, positions)
        
        ax.set_title(f"{scenario['title']}\n{scenario['description']}", 
                    fontsize=10, fontweight='bold')
        ax.axis('equal')
        ax.axis('off')
    
    plt.suptitle('AVL Tree Rotation Examples', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

def create_tree_stats_visualization(root):
    """Create a visualization showing tree statistics"""
    if not root:
        return None
    
    visualizer = AVLTreeVisualizer()
    
    # Calculate statistics
    def count_nodes(node):
        if not node:
            return 0
        return 1 + count_nodes(node.left) + count_nodes(node.right)
    
    def count_leaves(node):
        if not node:
            return 0
        if not node.left and not node.right:
            return 1
        return count_leaves(node.left) + count_leaves(node.right)
    
    def get_max_depth(node):
        if not node:
            return 0
        return max(get_max_depth(node.left), get_max_depth(node.right)) + 1
    
    total_nodes = count_nodes(root)
    leaf_nodes = count_leaves(root)
    internal_nodes = total_nodes - leaf_nodes
    max_depth = get_max_depth(root)
    
    # Get traversals
    traversals = get_tree_traversals(visualizer, root)
    
    # Create visualization
    fig = plt.figure(figsize=(14, 10))
    
    # Tree visualization (top half)
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    positions = {}
    visualizer._calculate_positions(root, 0, 0, 4, positions)
    visualizer._draw_edges(ax1, root, positions)
    visualizer._draw_nodes(ax1, root, positions)
    ax1.set_title('AVL Tree Visualization', fontsize=14, fontweight='bold')
    ax1.axis('equal')
    ax1.axis('off')
    
    # Statistics (bottom left)
    ax2 = plt.subplot2grid((3, 2), (2, 0))
    stats = ['Total Nodes', 'Leaf Nodes', 'Internal Nodes', 'Max Depth']
    values = [total_nodes, leaf_nodes, internal_nodes, max_depth]
    bars = ax2.bar(stats, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    ax2.set_title('Tree Statistics', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Traversals (bottom right)
    ax3 = plt.subplot2grid((3, 2), (2, 1))
    ax3.text(0.05, 0.9, 'Tree Traversals:', fontsize=12, fontweight='bold', 
             transform=ax3.transAxes)
    ax3.text(0.05, 0.7, f"Inorder: {traversals['inorder']}", fontsize=10, 
             transform=ax3.transAxes)
    ax3.text(0.05, 0.5, f"Preorder: {traversals['preorder']}", fontsize=10, 
             transform=ax3.transAxes)
    ax3.text(0.05, 0.3, f"Postorder: {traversals['postorder']}", fontsize=10, 
             transform=ax3.transAxes)
    ax3.axis('off')
    
    plt.tight_layout()
    return fig