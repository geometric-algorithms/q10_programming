#include <stack>

#include "DCEL.h"

DCEL triangulate(DCEL &dcel) {
    const int n = static_cast<int>(dcel.faces.size());

    std::vector<std::pair<int, int>> diagonals;

    for (int i = 1; i < n; i++) {
        std::vector<std::pair<Vertex*, int>> ordered_vertices;

        const auto head = dcel.faces[i];
        auto curr = head -> next;

        ordered_vertices.emplace_back(head -> origin, -1);

        while (curr != head) {
            ordered_vertices.emplace_back(curr -> origin, -1);
            curr = curr -> next;
        }

        const int sz = static_cast<int>(ordered_vertices.size());

        std::vector<int> index_in_dcel(sz);

        for (int j = 0; j < sz; j++) {
            ordered_vertices[j].second = j;
            index_in_dcel[j] = ordered_vertices[j].first -> index;
        }

        std::sort(ordered_vertices.begin(), ordered_vertices.end(), [](const auto& v1, const auto& v2) {return Vertex::triangulation_comparator(*v1.first, *v2.first);});

        std::stack<std::pair<Vertex*, int>> st({ordered_vertices[0], ordered_vertices[1]});

        for (int j = 2; j < sz - 1; j++) {
            const int stopi = index_in_dcel[st.top().second];
            const int stoppi = index_in_dcel[(st.top().second - 1 + sz) % sz];

            const int ji = index_in_dcel[ordered_vertices[j].second];
            const int jpi = index_in_dcel[(ordered_vertices[j].second - 1 + sz) % sz];

            if (dcel.vertices[ji].is_below(dcel.vertices[jpi]) != dcel.vertices[stopi].is_below(dcel.vertices[stoppi])) {
                while (!st.empty()) {
                    const int top_index = st.top().second;
                    st.pop();
                    if (st.empty()) break;
                    diagonals.emplace_back(ji, index_in_dcel[top_index]);
                }
                st.push(ordered_vertices[j - 1]);
                st.push(ordered_vertices[j]);
            }
            else {
                auto lpop = st.top();
                st.pop();
                while (!st.empty()) {
                    if (dcel.vertices[ji].is_below(dcel.vertices[jpi]) ^ Vertex::counter_clockwise(*ordered_vertices[j].first, *lpop.first, *st.top().first)){
                        diagonals.emplace_back(ji, index_in_dcel[st.top().second]);
                        lpop = st.top();
                        st.pop();
                    }
                    else break;
                }
                st.push(lpop);
                st.push(ordered_vertices[j]);
            }
        }

        while (!st.empty()) {
            diagonals.emplace_back(ordered_vertices.back().first -> index, st.top().first -> index);
            st.pop();
        }
    }

    std::vector<std::pair<int, int>> new_edges;
    new_edges.reserve(dcel.edges.size() + diagonals.size());

    for (const auto& it : dcel.edges) new_edges.emplace_back(it.v1 -> index, it.v2 -> index);
    for (const auto& it : diagonals) new_edges.emplace_back(it);

    return {dcel.vertices, new_edges};
}