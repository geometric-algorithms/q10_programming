import matplotlib.pyplot as plt
import os
import random
import sys

output_folder = sys.argv[1]

os.makedirs(output_folder, exist_ok=True)

# --- Read points ---
with open("./__vertices__.txt", "r") as f:
    n = int(f.readline())
    points = [list(map(float, f.readline().split())) for _ in range(n)]

# --- Plot 1: Vertices (Polygon) ---
plt.figure(figsize=(8,8))
for i in range(n):
    xvals = [points[i-1][0], points[i][0]]
    yvals = [points[i-1][1], points[i][1]]
    plt.plot(xvals, yvals, color="black")

plt.title("Original Polygon")
plt.axis("off")
plt.savefig(os.path.join(output_folder, "vertices.png"))
plt.close()

# --- Plot 2: Monotone Edges (Black lines) ---
plt.figure(figsize=(8,8))
with open("./__monotone_edges__.txt", "r") as f:
    m = int(f.readline())
    for _ in range(m):
        a, b = map(int, f.readline().split())
        xvals = [points[a][0], points[b][0]]
        yvals = [points[a][1], points[b][1]]
        plt.plot(xvals, yvals, color="black")

plt.title("Monotone Partition (Edges)")
plt.axis("off")
plt.savefig(os.path.join(output_folder, "monotone_edges.png"))
plt.close()

# --- Plot 3: Triangulated with colored faces ---
plt.figure(figsize=(8,8))
with open("./__triangulated_edges__.txt", "r") as f:
    m = int(f.readline())
    edges = []
    for _ in range(m):
        a, b = map(int, f.readline().split())
        edges.append((a, b))

from collections import defaultdict

adj = defaultdict(set)
for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)

visited_triangles = set()

def sorted_triangle(t1, t2, t3):
    return tuple(sorted([t1,t2,t3]))

for a in range(len(points)):
    for b in adj[a]:
        for c in adj[b]:
            if c in adj[a] and len({a,b,c}) == 3:
                triangle = sorted_triangle(a,b,c)
                if triangle not in visited_triangles:
                    visited_triangles.add(triangle)
                    # Random soft color
                    color = (random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0))
                    xvals = [points[triangle[0]][0], points[triangle[1]][0], points[triangle[2]][0]]
                    yvals = [points[triangle[0]][1], points[triangle[1]][1], points[triangle[2]][1]]
                    plt.fill(xvals, yvals, color=color, alpha=0.6)

# Plot black edges again
for (a, b) in edges:
    xvals = [points[a][0], points[b][0]]
    yvals = [points[a][1], points[b][1]]
    plt.plot(
        xvals, yvals,
        color="black",    # or color="#333333" for softer gray
        linewidth=0.5,    # thinner line
        alpha=0.5         # half-transparent
    )

plt.title("Triangulated Polygon")
plt.axis("off")
plt.savefig(os.path.join(output_folder, "triangulation.png"))
plt.close()
