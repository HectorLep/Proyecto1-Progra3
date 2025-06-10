class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element', '_type'

    def __init__(self, element, type=None):
        """Initialize vertex with element and optional type (warehouse, recharge, client)."""
        self._element = element
        self._type = type  # Node type: 'warehouse', 'recharge', or 'client'

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def type(self):
        """Return type of the vertex."""
        return self._type

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element}, type={self._type})"