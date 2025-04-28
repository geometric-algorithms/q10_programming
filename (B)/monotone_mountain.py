class MonotoneMountain:
    """
    Represents a monotone mountain polygon.
    """
    def __init__(self, bottom_vertex, base):
        """
        Initializes a monotone mountain with its bottom vertex and base edge.
        """
        self.base = base
        self.bottom_vertex = bottom_vertex

    def is_degenerated(self):
        """
        Checks if the monotone mountain is degenerated.
        """
        if (above := self.bottom_vertex.above) is None: return True
        if above.above is None: return True
        return False
