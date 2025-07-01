import folium
from branca.element import Figure

# Default map center (e.g., Temuco)
DEFAULT_LOCATION = [-38.7359, -72.5904] 
DEFAULT_ZOOM = 12

def create_empty_map(location=None, zoom_start=None):
    """Creates a new Folium map."""
    if location is None:
        location = DEFAULT_LOCATION
    if zoom_start is None:
        zoom_start = DEFAULT_ZOOM

    fig = Figure() # Use branca Figure to avoid issues with Streamlit width
    m = folium.Map(location=location, zoom_start=zoom_start, control_scale=True)
    fig.add_child(m)
    return m

def add_nodes_to_map(folium_map, graph_nodes):
    """
    Adds graph nodes to the Folium map.
    Args:
        folium_map: The Folium map object.
        graph_nodes: A list of Vertex objects from model.vertex.Vertex.
    """
    if not graph_nodes:
        return

    for node in graph_nodes:
        node_id = node.element()
        node_type = node.type()
        lat = node.latitude()
        lon = node.longitude()

        color = "blue" # Default
        icon_type = "info-sign"
        popup_text = f"<b>ID:</b> {node_id}<br><b>Type:</b> {node_type}<br><b>Coords:</b> ({lat:.4f}, {lon:.4f})"

        if node_type == 'warehouse':
            color = "darkred"
            icon_type = "home"
        elif node_type == 'recharge':
            color = "orange"
            icon_type = "flash"
        elif node_type == 'client':
            color = "green"
            icon_type = "user"

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{node_id} ({node_type})",
            icon=folium.Icon(color=color, icon=icon_type, prefix="glyphicon")
        ).add_to(folium_map)

def add_edges_to_map(folium_map, graph, graph_edges):
    """
    Adds graph edges to the Folium map.
    Args:
        folium_map: The Folium map object.
        graph: The Graph object (to get vertex objects if needed).
        graph_edges: A list of Edge objects from model.edge.Edge.
    """
    if not graph_edges:
        return

    for edge in graph_edges:
        u_vertex, v_vertex = edge.endpoints()
        weight = edge.element()

        u_lat, u_lon = u_vertex.latitude(), u_vertex.longitude()
        v_lat, v_lon = v_vertex.latitude(), v_vertex.longitude()

        folium.PolyLine(
            locations=[(u_lat, u_lon), (v_lat, v_lon)],
            tooltip=f"Edge: {u_vertex.element()} - {v_vertex.element()}<br>Cost: {weight}",
            color="gray",
            weight=2,
            opacity=0.7
        ).add_to(folium_map)

def highlight_path_on_map(folium_map, graph, path_elements, color="red", line_weight=5, line_opacity=0.8, dash_array=None):
    """
    Highlights a specific path on the Folium map.
    Args:
        folium_map: The Folium map object.
        graph: The Graph object (to get vertex coordinates by element).
        path_elements: A list of node elements (strings) representing the path.
        color: Color of the highlighted path.
        line_weight: Weight of the path line.
        line_opacity: Opacity of the path line.
        dash_array: String for dash pattern (e.g., '5, 5') or None for solid.
    """
    if not path_elements or len(path_elements) < 2:
        return

    path_coords = []
    for node_elem in path_elements:
        vertex = graph.get_vertex_by_element(node_elem)
        if vertex:
            path_coords.append((vertex.latitude(), vertex.longitude()))
        else:
            print(f"Warning: Vertex element {node_elem} not found in graph for path highlighting.")
            return # Or handle error appropriately

    folium.PolyLine(
        locations=path_coords,
        color=color,
        weight=line_weight,
        opacity=line_opacity,
        tooltip=f"Route: {' -> '.join(path_elements)}",
        dash_array=dash_array
    ).add_to(folium_map)

def highlight_mst_on_map(folium_map, mst_edges, color="blue", line_weight=3, dash_array='10, 10'):
    """
    Highlights the Minimum Spanning Tree (MST) edges on the map.
    Args:
        folium_map: The Folium map object.
        mst_edges: A list of Edge objects forming the MST.
    """
    if not mst_edges:
        return

    for edge in mst_edges:
        u_vertex, v_vertex = edge.endpoints()
        weight = edge.element()

        u_lat, u_lon = u_vertex.latitude(), u_vertex.longitude()
        v_lat, v_lon = v_vertex.latitude(), v_vertex.longitude()

        folium.PolyLine(
            locations=[(u_lat, u_lon), (v_lat, v_lon)],
            tooltip=f"MST Edge: {u_vertex.element()} - {v_vertex.element()}<br>Cost: {weight}",
            color=color,
            weight=line_weight,
            opacity=0.7,
            dash_array=dash_array
        ).add_to(folium_map)
