#include <queue>

#include "DCEL.h"

namespace VertexHandling {
    int n;
    DCEL* dcel;
    std::vector<int>* helper;
    std::vector<std::pair<int, int>>* diagonals;

    void handleMerging(const Vertex& event_point) {
        const int prev_index = (event_point.index - 1 + n) % n;
        const int endIndex = helper -> at(prev_index);
        if (endIndex > -1 && dcel -> vertices[endIndex].type == Vertex::MERGE) diagonals -> emplace_back(event_point.index, endIndex);
        dcel -> remove_search_edge(prev_index);
    }

    void handleSplitting(const Vertex& event_point, const bool handleMerge) {
        const int ejp = dcel -> find_previous_index(event_point);

        if (handleMerge) {if (dcel -> vertices[helper -> at(ejp)].type == Vertex::MERGE) diagonals -> emplace_back(event_point.index, helper -> at(ejp));}
        else diagonals -> emplace_back(helper -> at(ejp), event_point.index);

        helper -> at(ejp) = event_point.index;
    }

    void handleStartVertex(const Vertex& event_point) {
        dcel -> add_search_edge(event_point.index);
        helper -> at(event_point.index) = event_point.index;
    }

    void handleEndVertex(const Vertex& event_point) {
        handleMerging(event_point);
    }

    void handleSplitVertex(const Vertex& event_point) {
        handleSplitting(event_point, false);
        handleStartVertex(event_point);
    }

    void handleMergeVertex(const Vertex& event_point) {
        handleMerging(event_point);
        handleSplitting(event_point, true);
    }

    void handleRegularVertex(const Vertex& event_point) {
        const int n = static_cast<int>(dcel -> vertices.size());

        if (event_point.is_below(dcel -> vertices[(event_point.index - 1 + n) % n]) && dcel -> vertices[(event_point.index + 1) % n].is_below(event_point)) {
            handleMerging(event_point);
            handleStartVertex(event_point);
        }
        else handleSplitting(event_point, true);
    }

    void handleVertex(const Vertex& event_point) {
        switch (event_point.type) {
            case Vertex::START: handleStartVertex(event_point); break;
            case Vertex::END: handleEndVertex(event_point); break;
            case Vertex::SPLIT: handleSplitVertex(event_point); break;
            case Vertex::MERGE: handleMergeVertex(event_point); break;
            case Vertex::REGULAR: handleRegularVertex(event_point);
        }
    }
}

DCEL split_monotone(DCEL &dcel) {
    const int sz = static_cast<int>(dcel.vertices.size());

    VertexHandling::n = sz;
    VertexHandling::dcel = &dcel;
    VertexHandling::helper = new std::vector<int>(sz, -1);
    VertexHandling::diagonals = new std::vector<std::pair<int, int>>();

    std::priority_queue<Vertex> event_points;
    for (int i = 0; i < sz; i++) event_points.emplace(dcel.vertices[i]);

    while (!event_points.empty()) {
        Vertex event_point = event_points.top();
        event_points.pop();
        VertexHandling::handleVertex(event_point);
    }

    std::vector<std::pair<int, int>> edges;
    edges.reserve(sz + VertexHandling::diagonals -> size());

    for (int i = 0; i < sz; i++) edges.emplace_back(i, (i + 1) % sz);
    for (std::pair<int, int> p : *VertexHandling::diagonals) edges.emplace_back(p);

    return {dcel.vertices, edges};
}
