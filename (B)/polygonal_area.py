from edge import Edge
from vertex import Vertex

Polygon = list[Vertex]

class PolygonalArea:
    """
    Represents a polygonal area in 2D space, which may include holes or disjoint regions.
    """
    def __init__(self, polygons):
        """
        Initializes a PolygonalArea with a list of non-intersecting polygons.
        """
        self.__polygons = polygons

    def get_edges(self):
        """
        Extracts all edges from the polygons in the polygonal area.
        """
        return [Edge(poly[ind], poly[(ind + 1) % len(poly)]) for poly in self.__polygons for ind in range(len(poly))]