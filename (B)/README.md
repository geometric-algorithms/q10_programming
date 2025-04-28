### Advanced Triangulator for Polygons with Holes

This program supports triangulating polygons with holes inside them.
The algorithm is based upon Raimund Siedel's 1991 paper - [A simple and fast incremental randomized algorithm for computing trapezoidal decompositions and for triangulating polygons](https://www.sciencedirect.com/science/article/pii/0925772191900124)

## Setup

Install python requirements by running the following
```bash
pip install -r requirements.txt
```

## Usage

The program can be used in two modes: interactive and static.

The static mode loads the polygon from a file with the following format
```
Polygon1Vertex1.x Polygon1Vertex1.y
...

Polygon1Vertex2.x Polygon1Vertex2.y
...
...
```

The file should list all vertices of a polygon on contiguous lines. A new polygon is specified by inserting an empty line.

The interactive mode allows for drawing polygons. Click to add a new vertex at the mouse position, and right click to close a polygon. The triangulation is generated immediately.

Interactive mode:
```bash
./test.sh yes
```

Static mode:
```bash
./test.sh no <filename>
```
