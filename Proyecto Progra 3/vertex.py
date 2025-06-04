class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element'

    def __init__(self, element):
        """Do not call constructor directly. Use Graph's insert_vertex(element)."""
        self._element = element

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element})"
