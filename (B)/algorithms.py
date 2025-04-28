from __future__ import annotations

from typing import TYPE_CHECKING, cast
from random import shuffle

from vertex import *
from triangle import *
from node import *
from trapezoid import *
from monotone_mountain import *
from monotone_vertex import *


if TYPE_CHECKING:
    from polygonal_area import PolygonalArea


def triangulate_polygonal_area(polygonal_area: PolygonalArea) -> list[Triangle]:
    """
    Triangulates a polygonal area.

    This function first decomposes the polygonal area into trapezoids, then selects the
    trapezoids that are inside, generates monotone mountains from the inside trapezoids
    and then triangulate each monotone mountain to produce a list of triangles that cover
    the polygonal area.

    Args:
        polygonal_area (PolygonalArea): The polygonal area to be triangulated.

    Returns:
        list[Triangle]: A list of triangles resulting from the triangulation of the polygonal area.
    """
    trapezoids = trapezoidation(polygonal_area)

    inside_trapezoids = select_inside_trapezoids(trapezoids)

    monotone_mountains = make_monotone_mountains(inside_trapezoids)

    triangles = make_triangles(monotone_mountains)

    return triangles


def trapezoidation(polygonal_area: PolygonalArea) -> list[Trapezoid]:
    """
    Divides the 2D space into trapezoids according to the polygonal area.

    The decomposition is a tree structure where all edges of the polygonal area are inserted
    one after the other in a randomized order (for performances purpose).
    For each edge, both vertices are first inserted (if not already inserted), then the
    edge itself is inserted.

    Args:
        polygonal_area (PolygonalArea): The polygonal area to use for trapezoid decomposition of the 2D space.

    Returns:
        list[Trapezoid]: All the trapezoids resulting from the decomposition of the 2D space.
    """
    edges: list[Edge] = polygonal_area.get_edges()
    shuffle(edges)

    search_tree = Node(trapezoid=Trapezoid())
    already_inserted: set[Vertex] = set()

    def insert_vertex_if_necessary(vertex: Vertex) -> bool:
        if vertex in already_inserted:
            return False

        search_tree.insert_vertex(vertex)
        already_inserted.add(vertex)
        return True

    for edge in edges:
        top_just_inserted = insert_vertex_if_necessary(edge.top_vertex)
        bottom_just_inserted = insert_vertex_if_necessary(edge.bottom_vertex)

        search_tree.insert_edge(edge, top_just_inserted, bottom_just_inserted)

    return search_tree.get_all_traps()


def select_inside_trapezoids(all_trapezoids: list[Trapezoid]) -> list[Trapezoid]:
    """
    Filters the trapezoids to select only those that are inside the polygonal area.
    """
    return [trap for trap in all_trapezoids if trap.is_inside()]


def make_monotone_mountains(
    trapezoids: list[Trapezoid],
) -> list[MonotoneMountain]:
    """
    Transforms a trapezoids partition of the polygonal area into a monotone mountains partition of the same area.
    """
    above_vertex_by_base_edge: dict[Edge, dict[Vertex, Vertex]] = (
        group_vertices_by_mountain(trapezoids)
    )

    monotone_mountains: list[MonotoneMountain] = []

    for base, above_vertex_mapping in above_vertex_by_base_edge.items():
        below_monotone_vertex: MonotoneVertex | None = None
        current_vertex = base.bottom_vertex
        monotone_mountain_created = False

        while current_vertex is not None:
            current_monotone_vertex = MonotoneVertex(
                vertex=current_vertex, below=below_monotone_vertex
            )
            if below_monotone_vertex:
                below_monotone_vertex.above = current_monotone_vertex

            above_vertex = above_vertex_mapping.get(current_vertex, None)
            current_vertex = above_vertex
            below_monotone_vertex = current_monotone_vertex

            if not monotone_mountain_created:
                monotone_mountains.append(
                    MonotoneMountain(current_monotone_vertex, base)
                )
                monotone_mountain_created = True

    return monotone_mountains


def group_vertices_by_mountain(
    trapezoids: list[Trapezoid],
) -> dict[Edge, dict[Vertex, Vertex]]:
    """
    Performs the first part of the transformation of a trapezoids partition into
    a monotone mountains partition.
    """
    above_vertex_by_base_edge: dict[Edge, dict[Vertex, Vertex]] = defaultdict(dict)

    for trap in trapezoids:
        mountain_bases: list[Edge] = []

        for edge in [trap.left_edge, trap.get_right_edge()]:
            edge = cast(Edge, edge)
            if (
                trap.bottom_vertex != edge.bottom_vertex
                or trap.top_vertex != edge.top_vertex
            ):
                mountain_bases.append(edge)

        for mountain_base in mountain_bases:
            above_vertex_by_base_edge[mountain_base][
                cast(Vertex, trap.bottom_vertex)
            ] = cast(Vertex, trap.top_vertex)

    return above_vertex_by_base_edge


def make_triangles(monotone_mountains: list[MonotoneMountain]) -> list[Triangle]:
    """
    Generates triangles from a list of monotone mountains.
    """
    triangles: list[Triangle] = []

    for monotone_mountain in monotone_mountains:
        triangulate_monotone_mountain(monotone_mountain, triangles)

    return triangles


def triangulate_monotone_mountain(mountain, triangles):
    """
    Decomposes a monotone mountain into triangles, append the resulting triangles in the ⁠ triangles ⁠ list provided as argument.
    """
    if mountain.is_degenerated(): return

    first_non_base_vertex = cast(MonotoneVertex, mountain.bottom_vertex.above)

    convex_order = counter_clockwise(mountain.base.top_vertex, mountain.base.bottom_vertex, first_non_base_vertex.vertex,)

    current_vertex = first_non_base_vertex

    while not current_vertex.is_base_vertex():
        below = cast(MonotoneVertex, current_vertex.below)
        above = cast(MonotoneVertex, current_vertex.above)
        current_vertex_convex = counter_clockwise(below.vertex, current_vertex.vertex, above.vertex) == convex_order

        if not current_vertex_convex:
            current_vertex = above
            continue

        vertices_counter_clockwise = (below.vertex, current_vertex.vertex, above.vertex) if convex_order else (below.vertex, above.vertex, current_vertex.vertex)

        triangles.append(Triangle(vertices_counter_clockwise))
        below.above = above
        above.below = below
        current_vertex = above if below.is_base_vertex() else below