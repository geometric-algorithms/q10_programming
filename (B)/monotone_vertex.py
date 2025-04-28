class MonotoneVertex:
    """
    Represents a vertex in a monotone mountain polygon.
    """

    def __init__(self, vertex, above = None, below = None):
        """
        Initializes a MonotoneVertex with its geometric vertex and optionally its adjacent vertices in the monotone mountain structure.
        """
        self.vertex = vertex
        self.above = above
        self.below = below
        self.is_cached = False
        self.cache_result = None

    def is_base_vertex(self) -> bool:
        """
        Determines if this vertex is a base vertex in the monotone mountain, i.e. if the vertex is one of the ends of the chain.
        """
        if self.is_cached: return self.cache_result
        self.is_cached = True
        self.cache_result = self.above is None or self.below is None
        return self.cache_result
