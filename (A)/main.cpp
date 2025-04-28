#include "DCEL.h"

#include <iostream>
#include <fstream>

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file> <output_folder>" << std::endl;
        return 1;
    }

    std::ifstream input(argv[1]);
    std::string output_folder(argv[2]);

    if (!input.is_open()) {
        std::cerr << "Error opening file: " << argv[1] << std::endl;
        return 1;
    }

    std::ofstream original_vertices("./__vertices__.txt");
    std::ofstream monotone_edges("./__monotone_edges__.txt");
    std::ofstream triangulated_edges("./__triangulated_edges__.txt");

    std::vector<Vertex> vertices;

    while (!input.eof()) {
        long double x, y;
        input >> x >> y;
        vertices.emplace_back(x, y);
    }

    DCEL dcel(vertices);

    original_vertices << dcel.vertices.size() << "\n";
    for (const auto& it : dcel.vertices) {
        original_vertices << it.x << " " << it.y << "\n";
    }

    DCEL monotone_dcel = split_monotone(dcel);

    monotone_edges << monotone_dcel.edges.size() << "\n";
    for (const auto& it : monotone_dcel.edges) {
        monotone_edges << it.v1 -> index << " " << it.v2 -> index << "\n";
    }

    DCEL triangulate_dcel = triangulate(monotone_dcel);

    triangulated_edges << triangulate_dcel.edges.size() << "\n";
    for (const auto& it : triangulate_dcel.edges) {
        triangulated_edges << it.v1 -> index << " " << it.v2 -> index << "\n";
    }

    original_vertices.close();
    monotone_edges.close();
    triangulated_edges.close();

    system(std::string("python3 plot.py " + output_folder).c_str());
    system("rm __vertices__.txt");
    system("rm __monotone_edges__.txt");
    system("rm __triangulated_edges__.txt");
}