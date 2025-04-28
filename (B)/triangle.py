class Triangle:
    """
    Represents a triangle defined by three vertices in a 2D space.
    """
    def __init__(self, vertices):
        """
        Initializes a triangle with the given vertices.
        """
        self.vertices = vertices

        r, g, b = [int(sum([vertex.color[i] for vertex in self.vertices]) / 3) for i in range(3)]
        self.color_str = f"#{r:02x}{g:02x}{b:02x}"