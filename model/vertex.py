import random

class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element', '_type', '_latitude', '_longitude'

    # Temuco bounding box: Lat (-38.9, -38.5), Lon (-72.8, -72.4)
    MIN_LAT, MAX_LAT = -38.75, -38.72  # Rango de Latitud súper acotado al centro
    MIN_LON, MAX_LON = -72.62, -72.57  # Rango de Longitud súper acotado al centro

    def __init__(self, element, type=None, latitude=None, longitude=None):
        """Initialize vertex with element, optional type, and geo-coordinates."""
        self._element = element
        self._type = type  # Node type: 'warehouse', 'recharge', or 'client'

        if latitude is None:
            self._latitude = random.uniform(Vertex.MIN_LAT, Vertex.MAX_LAT)
        else:
            self._latitude = latitude

        if longitude is None:
            self._longitude = random.uniform(Vertex.MIN_LON, Vertex.MAX_LON)
        else:
            self._longitude = longitude

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def type(self):
        """Return type of the vertex."""
        return self._type

    def latitude(self):
        """Return latitude of the vertex."""
        return self._latitude

    def longitude(self):
        """Return longitude of the vertex."""
        return self._longitude

    def __hash__(self):
        return hash(id(self)) # Keep using id for hash if vertices are mutable or element isn't unique for identity

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element}, type={self._type}, lat={self._latitude:.4f}, lon={self._longitude:.4f})"