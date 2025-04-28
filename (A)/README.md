## Simple Polygon Triangulator

This is a simple CPP polygon triangulator based on Monotone Partitioning.

## Project Setup

From the root directory of the project, run the following commands:

```bash
mkdir build
cd build
cmake ..
cmake --build .
```
This will create a `triangulate` executable in the `build` directory.

Copy the executable to the root directory of the project:

```bash
cp triangulate ..
```
Ensure that the executable and the `plot.py` script are in the same directory.

## Usage

The program expects inputs in a file with the following format:

```
Vertex1.x Vertex1.y
Vertex2.x Vertex2.y
...
```

Where each line represents a vertex of the polygon in order. There should be no empty lines in the file.

An output folder must also be provided where the original polygon, monotone partitioned form and the final triangulated polygon will be saved. The output will be saved in the form of a `.png` file.

```bash
./triangulate input.txt output
```

## Random Testcases

A python script `gen.py` is provided to generate random test cases. The script generates a random polygon with a specified number of vertices. A filename can also be provided, the program defaults to new.txt. All files generated via this script are saved in `tests/` directory.

