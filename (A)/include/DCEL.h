#pragma once

#include <set>
#include <utility>
#include <vector>

class HalfEdge;
class Edge;

class Vertex {
  public:
    int index;

    long double x;
    long double y;

    HalfEdge* half_edge;

    enum VertexType {
        START,
        END,
        SPLIT,
        MERGE,
        REGULAR
    } type;

    Vertex() : index(0), x(0.0), y(0.0), half_edge(nullptr), type(REGULAR) {}
    Vertex(const long double x, const long double y) : index(0), x(x), y(y), half_edge(nullptr), type(REGULAR) {}

    bool operator<(const Vertex& other) const {return y == other.y ? x < other.x : y < other.y;}

    bool is_below(const Vertex& other) const {return y == other.y ? x > other.x : y < other.y;}

    static bool height_comparator(const Vertex& a, const Vertex& b) {return a.y < b.y;}

    static bool triangulation_comparator(const Vertex& a, const Vertex& b) {return a.y == b.y ? a.x < b.x : a.y > b.y;}

    Vertex operator-(const Vertex& other) const {return {x - other.x, y - other.y};}

    static bool counter_clockwise(const Vertex& p1, const Vertex& p2, const Vertex& p3) {return (p2.x - p1.x) * (p3.y - p1.y) > (p3.x - p1.x) * (p2.y - p1.y);}

    long double get_angle() const {
        if (y > 0) return acos(x / sqrt(x * x + y * y));
        return 2 * M_PI - acos(x / sqrt(x * x + y * y));
    }

    void set_type(const Vertex& prev_vertex, const Vertex& next_vertex) {
        if (prev_vertex.is_below(*this) && next_vertex.is_below(*this)) {
            if (counter_clockwise(prev_vertex, *this, next_vertex)) type = START;
            else type = SPLIT;
        }
        if (this -> is_below(prev_vertex) && this -> is_below(next_vertex)) {
            if (counter_clockwise(prev_vertex, *this, next_vertex)) type = END;
            else type = MERGE;
        }
    }
};

class HalfEdge {
  public:
    int index;

    Edge* edge;
    Vertex* origin;

    HalfEdge* twin;
    HalfEdge* prev;
    HalfEdge* next;

    HalfEdge() : index(0), edge(nullptr), origin(nullptr), twin(nullptr), prev(nullptr), next(nullptr) {}
    HalfEdge(const int index, Edge* edge, Vertex* origin, HalfEdge* twin, HalfEdge* prev, HalfEdge* next) : index(index), edge(edge), origin(origin), twin(twin), prev(prev), next(next) {
        if (twin) twin -> twin = this;
        if (prev) prev -> next = this;
        if (next) next -> prev = this;
    }
};

class Edge {
  public:
    int index;

    Vertex* v1;
    Vertex* v2;

    HalfEdge *half_edge;

    Edge() : index(-1), v1(nullptr), v2(nullptr), half_edge(nullptr) {}
    Edge(const int index, Vertex* v1, Vertex* v2, HalfEdge* half_edge) : index(index), v1(v1), v2(v2), half_edge(half_edge) {}

    bool operator==(const Edge& other) const {
        return (v1 == other.v1 && v2 == other.v2) || (v1 == other.v2 && v2 == other.v1);
    }

    bool is_horizontal() const {
        return v1->y == v2->y;
    }

    bool operator<(const Edge& other) const {
        const bool this_horizontal = is_horizontal();

        const bool is_other_higher = v1 -> y < other.v1 -> y;
        const bool makes_cc_pair = Vertex::counter_clockwise(*v1, *v2, *other.v1);

        if (other.is_horizontal()) return this_horizontal ? is_other_higher : makes_cc_pair;
        if (this_horizontal || is_other_higher) return !Vertex::counter_clockwise(*v1, *other.v1, *other.v2);

        return makes_cc_pair;
    }
};

class DCEL {
  public:
    std::vector<Vertex> vertices;
    std::vector<HalfEdge*> faces;
    std::vector<HalfEdge> half_edges;
    std::vector<Edge> edges;

    std::set<Edge> binary_search_tree;

    explicit DCEL(std::vector<Vertex>& vertices);
    DCEL(std::vector<Vertex>& vertices, const std::vector<std::pair<int, int>>& edge_list);

    void add_search_edge(int index);
    void remove_search_edge(int index);
    int find_previous_index(const Vertex& v) const;
};

DCEL split_monotone(DCEL &dcel);
DCEL triangulate(DCEL& dcel);
