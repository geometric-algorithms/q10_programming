#include "DCEL.h"

DCEL::DCEL(std::vector<Vertex>& vertices) {
    const int n = static_cast<int>(vertices.size());

    // If the top vertex is a split vertex according to the current ordering, reverse the order of the vertices
    const auto mx = std::max_element(vertices.begin(), vertices.end(), &Vertex::height_comparator);
    const auto mx_prev = mx == vertices.begin() ? vertices.end() - 1 : mx - 1;
    const auto mx_next = mx == vertices.end() - 1 ? vertices.begin() : mx + 1;

    mx -> set_type(*mx_prev, *mx_next);
    if (mx -> type == Vertex::SPLIT) reverse(vertices.begin(), vertices.end());

    // Set up vertices and their types
    this -> vertices = std::move(vertices);

    this -> vertices[0].set_type(this -> vertices[n - 1], this -> vertices[1]);
    for (int i = 1; i < n - 1; i++) this -> vertices[i].set_type(this -> vertices[i - 1], this -> vertices[i + 1]);
    this -> vertices[n - 1].set_type(this -> vertices[n - 2], this -> vertices[0]);

    // Link up half-edges and initialize edges
    edges.clear();
    edges.reserve(n);

    half_edges = std::vector<HalfEdge>(2 * n);

    for (int i = 0; i < n - 1; i++) {
        edges.emplace_back(i, &this -> vertices[i], &this -> vertices[i + 1], &half_edges[i]);

        half_edges[i] = HalfEdge(i, &edges[i], &this -> vertices[i], &half_edges[i + n], nullptr, &half_edges[i + 1]);
        half_edges[i + n] = HalfEdge(i + n, &edges[i], &this -> vertices[i + 1], &half_edges[i], &half_edges[i + 1 + n], nullptr);

        this -> vertices[i].index = i;
        this -> vertices[i].half_edge = &half_edges[i];
    }

    // Make an edge between the last vertex and the first vertex
    half_edges[n - 1] = HalfEdge(n - 1, &edges[n - 1], &this -> vertices[n - 1], &half_edges[2 * n - 1], nullptr, &half_edges[0]);
    half_edges[2 * n - 1] = HalfEdge(2 * n - 1, &edges[n - 1], &this -> vertices[0], &half_edges[n - 1], &half_edges[n], nullptr);

    edges[n - 1] = Edge(n - 1, &this -> vertices[n - 1], &this -> vertices[0], &half_edges[n - 1]);

    this -> vertices[n - 1].index = n - 1;
    this -> vertices[n - 1].half_edge = &half_edges[n - 1];
}

DCEL::DCEL(std::vector<Vertex>& vertices, const std::vector<std::pair<int, int>>& edge_list) {
    const int n = static_cast<int>(vertices.size());
    const int m = static_cast<int>(edge_list.size());

    this -> vertices = std::move(vertices);

    // Set up the new half-edges
    half_edges = std::vector<HalfEdge>(2 * m);

    for (int i = 0; i < m; i++) {
        half_edges[i].index = i;
        half_edges[i].twin = &half_edges[i + m];

        half_edges[i + m].index = i + m;
        half_edges[i + m].twin = &half_edges[i];
    }

    // Build an adjacency list of the edges based on the edge_list
    std::vector<std::vector<std::pair<int, int>>> vout(n);

    for (int i = 0; i < m; i++) {
        vout[edge_list[i].first].emplace_back(i, edge_list[i].second);
        vout[edge_list[i].second].emplace_back(i, edge_list[i].first);
    }

    for (int i = 0; i < n; i++) {
        this -> vertices[i].index = i;

        auto comparator = [&](const std::pair<int, int>& e1, const std::pair<int, int>& e2) {
            return (this -> vertices[e1.second] - this -> vertices[i]).get_angle() > (this -> vertices[e2.second] - this -> vertices[i]).get_angle();
        };

        std::sort(vout[i].begin(), vout[i].end(), comparator);

        const int sz = static_cast<int>(vout[i].size());

        for (int j = 0; j < sz - 1; j++) {
            const int from = vout[i][j].second;
            const int to = vout[i][j + 1].second;

            const int e1i = vout[i][j].first + (from < i ? m : 0);
            const int e2i = vout[i][j + 1].first + (i < to ? m : 0);

            half_edges[e1i].next = &half_edges[e2i];
            half_edges[e2i].prev = &half_edges[e1i];
            half_edges[e2i].origin = &this -> vertices[i];

            this -> vertices[i].half_edge = &half_edges[e1i];
        }

        const int from = vout[i][sz - 1].second;
        const int to = vout[i][0].second;

        const int e1i = vout[i][sz - 1].first + (from < i ? m : 0);
        const int e2i = vout[i][0].first + (i < to ? m : 0);

        half_edges[e1i].next = &half_edges[e2i];
        half_edges[e2i].prev = &half_edges[e1i];
        half_edges[e2i].origin = &this -> vertices[i];

        this -> vertices[i].half_edge = &half_edges[e1i];
    }

    std::vector<bool> done(2 * m, false);

    for (int i = 0; i < 2 * m; i++) {
        if (done[i]) continue;
        done[i] = true;

        const HalfEdge* head = &half_edges[i];
        const HalfEdge* curr = head -> next;

        while (curr != head) {
            done[curr->index] = true;
            curr = curr->next;
        }

        faces.emplace_back(&half_edges[i]);
    }

    edges.clear();
    edges.reserve(m);
    for (int i = 0; i < m; i++) edges.emplace_back(i, half_edges[i].origin, half_edges[i + m].origin, &half_edges[i]);
}

void DCEL::add_search_edge(const int index) {
    binary_search_tree.insert(edges[index]);
}

void DCEL::remove_search_edge(const int index) {
    binary_search_tree.erase(edges[index]);
}

int DCEL::find_previous_index(const Vertex& v) const {
    return (--binary_search_tree.lower_bound(Edge(-1, const_cast<Vertex*>(&v), const_cast<Vertex*>(&v), nullptr))) -> index;
}