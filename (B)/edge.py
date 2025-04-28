from vertex import Vertex

class Edge:
    """
    Represents an edge in 2D space, defined by two vertices.
    """
    def __init__(self, start, end):
        """
        Initializes an edge by determining its bottom and top vertices.
        """
        if start > end:
            self.bottom_vertex = end
            self.top_vertex = start
        else:
            self.bottom_vertex = start
            self.top_vertex = end

        self.mid_point = Vertex((self.bottom_vertex.x + self.top_vertex.x) / 2, (self.bottom_vertex.y + self.top_vertex.y) / 2)


    def get_vertex(self, top):
        """
        Retrieves either the top or bottom vertex of the edge.
        """
        return self.top_vertex if top else self.bottom_vertex

    def is_vertex_at_the_right(self, vertex):
        """
        Determines if a given vertex is to the right of the edge at the vertex's y-coordinate.
        """
        return vertex.x > self.get_x_by_y(vertex.y)

    def get_x_by_y(self, y):
        """
        Calculates the x-coordinate on the edge corresponding to a given y-coordinate.

        If the edge is horizontal (both vertices have the same y-coordinate), the
        average of the x-coordinates of the two vertices is returned.
        """
        if self.bottom_vertex.y == self.top_vertex.y:
            return (self.bottom_vertex.x + self.top_vertex.x) / 2

        t = (y - self.bottom_vertex.y) / (self.top_vertex.y - self.bottom_vertex.y)
        return self.bottom_vertex.x + t * (self.top_vertex.x - self.bottom_vertex.x)

def get_edge_vertex(edge, top):
    """
    Retrieves the top or bottom vertex of a given edge, or None if the edge is None.
    """
    return None if edge is None else edge.get_vertex(top)
