import math
import random

class Vertex:
    """
    Represents a vertex in a 2D space with (x, y) coordinates and an associated color
    used to choose the color of neighboring triangles.
    """
    def __init__(self, x, y):
        """
        Initializes a vertex with given coordinates and a random pastel color.
        """
        self.x = x
        self.y = y
        self.color = [random.randint(100, 255) for _ in range(3)]

    def __gt__(self, other):
        """
        Compares two vertices based on their vertical (y) position,
        and their horizontal (x) position in case of a tie.
        """
        return self.y > other.y or (self.y == other.y and self.x > other.x)

def counter_clockwise(pt_a, pt_b, pt_c):
    """
    Determines if three vertices are arranged in a counter-clockwise order.
    """
    return (pt_c.y - pt_a.y) * (pt_b.x - pt_a.x) > (pt_b.y - pt_a.y) * (pt_c.x - pt_a.x)

def segment_intersect(pt_a, pt_b, pt_c, pt_d):
    """
    Checks if two segments, defined by four vertices, intersect.
    """
    return (counter_clockwise(pt_a, pt_b, pt_c) != counter_clockwise(pt_a, pt_b, pt_d)
            and counter_clockwise(pt_c, pt_d, pt_a) != counter_clockwise(pt_c, pt_d, pt_b))

def get_angle(vertex_1, vertex_2, vertex_3):
    """
    Calculates the angle in degrees between three vertices, measured at vertex_2.
    """
    def vector(pt_from, pt_to):
        return pt_to.x - pt_from.x, pt_to.y - pt_from.y

    def norm(vec):
        return math.sqrt(sum([component * component for component in vec]))

    vector_a = vector(vertex_2, vertex_1)
    vector_b = vector(vertex_2, vertex_3)

    dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
    cos_angle = dot_product / (norm(vector_a) * norm(vector_b))

    return math.degrees(math.acos(cos_angle))