from collections import defaultdict

from edge import *
from vertex import Vertex

def replace(list_to_modify, to_replace, replace_by):
    for index in range(len(list_to_modify)):
        if list_to_modify[index] == to_replace: list_to_modify[index] = replace_by

class Trapezoid:
    traps_by_right_edge = defaultdict(set)

    def __init__(self, top_vertex = None, bottom_vertex = None, trapezoids_above = None, trapezoids_below = None, left_edge = None, right_edge = None):
        """
        Initializes a new Trapezoid object.
        """
        self.top_vertex = top_vertex
        self.bottom_vertex = bottom_vertex
        self.trapezoids_above = [] if trapezoids_above is None else trapezoids_above
        self.trapezoids_below = [] if trapezoids_below is None else trapezoids_below
        self.left_edge = left_edge
        self.__right_edge = None
        self.set_right_edge(right_edge)
        self.associated_node = None

        self.is_cached = False
        self.cache_result = None

    def get_right_edge(self):
        return self.__right_edge

    def set_right_edge(self, new_right_edge):
        self.remove_from_edge_registry()
        self.__right_edge = new_right_edge
        self.__register_in_edge_registry()

    def is_inside(self) -> bool:
        """
        Determines whether the trapezoid lies inside the polygonal area.
        """
        if self.is_cached: return self.cache_result
        self.is_cached = True

        if self.get_right_edge() is None or self.left_edge is None:
            self.cache_result = False
        else:
            left_traps = Trapezoid.traps_by_right_edge[self.left_edge]
            left_trap = next(iter(left_traps))
            self.cache_result = not left_trap.is_inside()

        return self.cache_result

    def get_adjacent_traps(self, top):
        """
        Retrieves the trapezoids adjacent to this one in the specified direction.
        """
        return self.trapezoids_above if top else self.trapezoids_below

    def set_adjacent_traps(self, new_traps, top):
        """
        Updates the trapezoids adjacent to this one in the specified direction.
        """
        if top: self.trapezoids_above = new_traps
        else: self.trapezoids_below = new_traps

    def remove_from_edge_registry(self):
        """
        Removes this trapezoid from the global registry of trapezoids mapped by their right edge.
        """
        if self.__right_edge is not None: Trapezoid.traps_by_right_edge[self.__right_edge].remove(self)

    def split_by_vertex(self, vertex):
        """
        Splits the trapezoid horizontally into two trapezoids using a given vertex as the dividing point.
        """
        top_trapezoid = self
        bottom_trapezoid = self.__duplicate()

        top_trapezoid.bottom_vertex = vertex
        bottom_trapezoid.top_vertex = vertex

        bottom_trapezoid.trapezoids_above = [top_trapezoid]
        bottom_trapezoid.trapezoids_below = self.trapezoids_below
        for trap in self.trapezoids_below: replace(trap.trapezoids_above, self, bottom_trapezoid)
        top_trapezoid.trapezoids_below = [bottom_trapezoid]

        return bottom_trapezoid, top_trapezoid

    def split_by_edge(self, edge):
        """
        Splits the trapezoid obliquely into two trapezoids using a given edge as the dividing boundary.
        """
        right_trapezoid = self
        left_trapezoid = self.__duplicate()

        left_trapezoid.set_right_edge(edge)
        right_trapezoid.left_edge = edge

        return left_trapezoid, right_trapezoid

    def get_extreme_point(self, top, right):
        """
        Calculates one of the four extreme points of the trapezoid.
        """
        relevant_vertex = self.top_vertex if top else self.bottom_vertex
        relevant_edge = self.get_right_edge() if right else self.left_edge

        extreme_y = relevant_vertex.y
        extreme_x = relevant_edge.get_x_by_y(extreme_y)

        return Vertex(extreme_x, extreme_y)

    def __register_in_edge_registry(self):
        """
        Adds this trapezoid to the global registry of trapezoids mapped by their right edge.
        """
        if self.__right_edge is not None: Trapezoid.traps_by_right_edge[self.__right_edge].add(self)

    def __duplicate(self):
        """
        Creates a duplicate of the current trapezoid with the same vertices and edges.
        """
        return Trapezoid(self.top_vertex, self.bottom_vertex, None, None, self.left_edge, self.get_right_edge())

def manage_adjacent_trapezoids_after_edge_split(edge, created_trap_couples, top_just_inserted, bottom_just_inserted):
    """
    Updates the adjacency relationships of trapezoids after an edge insertion.
    """
    manage_adjacent_trapezoid_at_inserted_edge_end(edge, created_trap_couples[0][0], created_trap_couples[0][1], top_just_inserted, True)
    manage_adjacent_trapezoid_at_inserted_edge_end(edge, created_trap_couples[-1][0], created_trap_couples[-1][1], bottom_just_inserted, False)

    for trap_couple_index in range(len(created_trap_couples) - 1):
        top_left_trap, top_right_trap = created_trap_couples[trap_couple_index]
        bottom_left_trap, bottom_right_trap = created_trap_couples[trap_couple_index + 1]

        if len(top_right_trap.trapezoids_below) == 2:
            manage_adjacent_trapezoids_on_branch(edge, bottom_left_trap, bottom_right_trap, top_left_trap, top_right_trap, False)

        elif len(bottom_right_trap.trapezoids_above) == 2:
            manage_adjacent_trapezoids_on_branch(edge, top_left_trap, top_right_trap, bottom_left_trap, bottom_right_trap, True,)

        else:
            top_left_trap.trapezoids_below = [bottom_left_trap]
            bottom_left_trap.trapezoids_above = [top_left_trap]

def merge_redundant_trapezoids(created_trap_couples):
    """
    Merges redundant stacked trapezoids created during edge insertion.
    """
    for left_or_right in [0, 1]:
        stack_to_merge = [created_trap_couples[0][left_or_right]]

        for trap_couple in created_trap_couples[1:]:
            trap = trap_couple[left_or_right]

            if stack_to_merge[-1].left_edge != trap.left_edge or stack_to_merge[-1].get_right_edge() != trap.get_right_edge():
                merge_trapezoids_stack(stack_to_merge)
                stack_to_merge = []

            stack_to_merge.append(trap)

        merge_trapezoids_stack(stack_to_merge)

def manage_adjacent_trapezoid_at_inserted_edge_end(edge, end_trap_left, end_trap_right, end_just_inserted, top_end):
    """
    Adjusts the adjacency relationships of trapezoids at one endpoint of an inserted edge.
    """
    exterior_adjacent_traps = end_trap_right.get_adjacent_traps(top_end)

    if end_just_inserted:
        end_trap_left.set_adjacent_traps(exterior_adjacent_traps.copy(), top_end)
        adjacent_trap = exterior_adjacent_traps[0]
        adjacent_trap.set_adjacent_traps([end_trap_left, end_trap_right], not top_end)
        return

    edge_relevant_end = get_edge_vertex(edge, top_end)

    if get_edge_vertex(end_trap_left.left_edge, top_end) == edge_relevant_end:
        pass
    elif get_edge_vertex(end_trap_right.get_right_edge(), top_end) == edge_relevant_end:
        end_trap_left.set_adjacent_traps(exterior_adjacent_traps, top_end)
        end_trap_right.set_adjacent_traps([], top_end)
        replace(exterior_adjacent_traps[0].get_adjacent_traps(not top_end), end_trap_right, end_trap_left)

    else:
        left_adjacent, right_adjacent = exterior_adjacent_traps
        end_trap_left.set_adjacent_traps([left_adjacent], top_end)
        end_trap_right.set_adjacent_traps([right_adjacent], top_end)
        replace(left_adjacent.get_adjacent_traps(not top_end), end_trap_right, end_trap_left)

def manage_adjacent_trapezoids_on_branch(edge, left_trap_A, right_trap_A, left_trap_B, right_trap_B, upward_branch):
    """
    Adjusts the adjacency relationships of trapezoids on a horizontal border with a "branch."
    """
    left_trap_A.set_adjacent_traps([left_trap_B], not upward_branch)

    branch_point = right_trap_B.get_adjacent_traps(upward_branch)[0].get_extreme_point(not upward_branch, True)

    if edge.is_vertex_at_the_right(branch_point):
        left_trap_B.set_adjacent_traps([left_trap_A], upward_branch)
        return

    additional_left_trap_A = right_trap_B.get_adjacent_traps(upward_branch)[0]

    right_trap_A.set_adjacent_traps([right_trap_B], not upward_branch)
    right_trap_B.set_adjacent_traps([right_trap_A], upward_branch)

    left_trap_B.set_adjacent_traps([additional_left_trap_A, left_trap_A], upward_branch)
    additional_left_trap_A.set_adjacent_traps([left_trap_B], not upward_branch)

def merge_trapezoids_stack(trapezoids_stack):
    """
    Merges a vertical stack of trapezoids into a single trapezoid.
    """
    if len(trapezoids_stack) < 2:
        return

    top_trap = trapezoids_stack[0]
    bottom_trap = trapezoids_stack[-1]

    top_trap.bottom_vertex = bottom_trap.bottom_vertex
    top_trap.trapezoids_below = bottom_trap.trapezoids_below

    for trap in bottom_trap.trapezoids_below: replace(trap.trapezoids_above, bottom_trap, top_trap)

    for trap in trapezoids_stack[1:]:
        trap.associated_node.replace_by_another_node_in_tree(top_trap.associated_node)
        trap.remove_from_edge_registry()