import os
import random
import math
import sys

def generate_random_polygon(n_sides, xy_range=(0, 100)):
    vertices = []
    for _ in range(n_sides):
        x = random.uniform(*xy_range)
        y = random.uniform(*xy_range)
        vertices.append((x, y))

    centroid_x = sum(x for x, _ in vertices) / n_sides
    centroid_y = sum(y for _, y in vertices) / n_sides
    vertices.sort(key=lambda point: math.atan2(point[1] - centroid_y, point[0] - centroid_x))

    return vertices

def write_vertices_to_file(vertices, filename):
    with open(os.path.join("./tests", filename) , 'w') as f:
        for x, y in vertices[:-1]:
            f.write(f"{x:.6f} {y:.6f}\n")
        f.write(f"{vertices[-1][0]:.6f} {vertices[-1][1]:.6f}")

if __name__ == "__main__":
    os.makedirs("tests", exist_ok=True)
    n = int(input("Enter number of sides: "))
    filename = sys.argv[1] if len(sys.argv) > 1 else "new.txt"
    polygon_vertices = generate_random_polygon(n)
    write_vertices_to_file(polygon_vertices, filename)
    print(f"Generated {n} vertices and wrote them to tests/{filename}")
