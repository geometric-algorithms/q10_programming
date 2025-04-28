from trapezoid import *
from vertex import Vertex

class Node:
    """
    Represents a node in the trapezoidal decomposition search structure.
    """
    def __init__(self, trapezoid, parent = None):
        """
        Initializes a new Node. A newly created node is always added at the bottom of the structure, and at the time of its creation, it is always a leaf node representing a trapezoid.
        """
        self.associated_obj = trapezoid
        self.left_child = None
        self.right_child = None
        self.parents = []
        
        trapezoid.associated_node = self

        if parent: self.parents.append(parent)

    def replace_by_another_node_in_tree(self, new_node):
        """
        Redirects all parent pointers that refer to this node (as left_child or right_child) to a new node.
        """
        if new_node == self: return

        for parent in self.parents:
            if parent.left_child == self: parent.left_child = new_node
            elif parent.right_child == self: parent.right_child = new_node

        new_node.parents.extend(self.parents)

    def insert_vertex(self, vertex):
        """
        Inserts a vertex into the trapezoidal decomposition structure.
        """
        self.__search_area_containing_vertex(vertex).__split_by_vertex(vertex)

    def insert_edge(self, edge, top_just_inserted, bottom_just_inserted):
        """
        Inserts an edge into the trapezoidal decomposition structure.
        """
        start_node = self.__search_area_containing_vertex(edge.mid_point)

        nodes_to_split_down_direction = start_node.__find_nodes_to_split_in_direction(edge, False)
        nodes_to_split_up_direction = start_node.__find_nodes_to_split_in_direction(edge, True)

        created_trap_couples = []

        for node_top_split in reversed(nodes_to_split_up_direction): node_top_split.__split_by_edge(edge, created_trap_couples)
        start_node.__split_by_edge(edge, created_trap_couples)
        for node_to_split in nodes_to_split_down_direction: node_to_split.__split_by_edge(edge, created_trap_couples)

        manage_adjacent_trapezoids_after_edge_split(edge, created_trap_couples, top_just_inserted, bottom_just_inserted)
        merge_redundant_trapezoids(created_trap_couples)

    def get_all_traps(self, trapezoids_acc = None):
        """
        Collects all trapezoids from the subtree rooted at this node.
        """
        if trapezoids_acc is None: trapezoids_acc = []

        if type(self.associated_obj) is Trapezoid: trapezoids_acc.append(self.associated_obj)

        else:
            self.left_child.get_all_traps(trapezoids_acc)
            self.right_child.get_all_traps(trapezoids_acc)

        return trapezoids_acc

    def __search_area_containing_vertex(self, vertex):
        """
        Finds the trapezoid node in the search structure that contains the given vertex.
        """
        obj_type = type(self.associated_obj)

        if obj_type is Trapezoid: return self

        relevant_child = self.left_child

        if (obj_type is Vertex and vertex > self.associated_obj) or (obj_type is Edge and self.associated_obj.is_vertex_at_the_right(vertex)): relevant_child = self.right_child

        return relevant_child.__search_area_containing_vertex(vertex)

    def __split_by_vertex(self, vertex):
        """
        Splits the trapezoid represented by this node into two trapezoids using a vertex.
        """
        bottom_trapezoid, top_trapezoid = self.associated_obj.split_by_vertex(vertex)

        self.associated_obj = vertex

        self.left_child = Node(bottom_trapezoid, self)
        self.right_child = Node(top_trapezoid, self)

    def __split_by_edge(self, edge, created_trap_couples):
        """
        Splits the trapezoid represented by this node into two trapezoids using an edge.
        """
        left_trapezoid, right_trapezoid = self.associated_obj.split_by_edge(edge)

        created_trap_couples.append((left_trapezoid, right_trapezoid))

        self.associated_obj = edge

        self.left_child = Node(left_trapezoid, self)
        self.right_child = Node(right_trapezoid, self)

    def __find_nodes_to_split_in_direction(self, edge, up_direction):
        """
        Finds the sequence of nodes to split along a given direction for an edge insertion.
        """
        nodes_to_split = []
        current_trap = self.associated_obj

        def is_the_end_of_edge(trap):
            if up_direction: return trap.top_vertex == edge.top_vertex
            else: return trap.bottom_vertex == edge.bottom_vertex

        while not is_the_end_of_edge(current_trap):
            next_traps_in_direction = current_trap.get_adjacent_traps(top=up_direction)

            sz = len(next_traps_in_direction)

            if sz == 1:
                current_trap = next_traps_in_direction[0]
            elif sz == 2:
                left_trap_in_direction = next_traps_in_direction[0]
                left_trap_relevant_rightmost_pt = left_trap_in_direction.get_extreme_point(not up_direction, True)
                trap_index = 0 if edge.is_vertex_at_the_right(left_trap_relevant_rightmost_pt) else 1
                current_trap = next_traps_in_direction[trap_index]

            nodes_to_split.append(current_trap.associated_node)

        return nodes_to_split