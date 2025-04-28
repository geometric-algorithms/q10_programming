from __future__ import annotations
import os
from typing import List
from PIL import Image, ImageDraw
from tkinter import BOTH, LEFT, Button, Canvas, Event, Tk
from tkinter.filedialog import askopenfilename
from algorithms import *
from polygonal_area import *



class PolygonalAreaDrawer:
    def __init__(self, use_tkinter: bool = False, output_path: str = "output.png", canvas_size: tuple[int, int] = (800, 600)) -> None:
        """
        Initializes the PolygonalAreaDrawer.
        """
        self.use_tkinter = use_tkinter
        self.output_path = output_path
        self.canvas_size = canvas_size
        self.point_color = "brown"
        self.line_color = "grey"
        self.point_radius = 2
        self.polygons: List[Polygon] = []
        self.objects_ids_by_polygon: List[List[int]] = []  # For Tkinter
        self.triangles_ids: List[int] = []  # For Tkinter
        self.in_progress: bool = False  # For Tkinter
        self.image = None  # For PIL
        self.draw = None  # For PIL

        if self.use_tkinter:
            self.root = Tk()
            self.canvas = Canvas(self.root, bg="white")
            self.canvas.pack(fill=BOTH, expand=True)
            self.canvas.bind("<Button-1>", self._add_point_tkinter)
            self.canvas.bind("<Button-3>", self._close_polygon_tkinter)
            self.clear_button = Button(self.root, text="Clear", command=self._clear_tkinter, state="disabled")
            self.clear_button.pack(side=LEFT, padx=(20, 5), pady=10)
            self.load_button = Button(self.root, text="Load from File", command=self._load_from_file_tkinter)
            self.load_button.pack(side=LEFT, padx=(5, 5), pady=10)

    def run(self, polygons: List[Polygon] | None = None, input_file: str | None = None) -> None:
        """
        Runs the drawer in either Tkinter or PIL mode.
        """
        if self.use_tkinter:
            self.root.mainloop()
        else:
            if not (polygons or input_file):
                raise ValueError("Either polygons or input_file must be provided in PIL mode.")
            self.draw_polygons_pil(polygons, input_file)

    def draw_polygons_pil(self, polygons: List[Polygon] | None = None, input_file: str | None = None) -> None:
        """
        Draws polygons and their triangulation to a PNG file using PIL.
        """
        if input_file:
            try:
                self.polygons = self._load_from_file(input_file)
            except Exception as e:
                raise
        elif polygons:
            self.polygons = [poly for poly in polygons if len(poly) >= 3]
            if not self.polygons:
                raise ValueError("No valid polygons provided")

        self._normalize_coordinates_pil()

        try:
            self.image = Image.new("RGB", self.canvas_size, "white")
            self.draw = ImageDraw.Draw(self.image)
        except Exception as e:
            raise

        for i, polygon in enumerate(self.polygons):
            if len(polygon) < 3:
                continue
            self._draw_polygon_pil(polygon)

        self._triangulate()

        try:
            output_dir = os.path.dirname(self.output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.image.save(self.output_path, "PNG")
        except Exception as e:
            raise

    def _normalize_coordinates_pil(self) -> None:
        """
        Normalizes polygon coordinates to fit within the canvas with a margin (PIL mode).
        """
        if not self.polygons:
            return

        margin = 20
        all_vertices = [v for polygon in self.polygons for v in polygon]
        if not all_vertices:
            raise ValueError("No vertices to normalize")

        try:
            min_x = min(v.x for v in all_vertices)
            min_y = min(v.y for v in all_vertices)
            max_x = max(v.x for v in all_vertices)
            max_y = max(v.y for v in all_vertices)
        except Exception as e:
            raise

        for polygon in self.polygons:
            for vertex in polygon:
                vertex.x = vertex.x - min_x + margin
                vertex.y = vertex.y - min_y + margin

        content_width = max_x - min_x + 2 * margin
        content_height = max_y - min_y + 2 * margin
        self.canvas_size = (
            max(self.canvas_size[0], int(content_width)),
            max(self.canvas_size[1], int(content_height))
        )

    def _add_point_tkinter(self, event: Event) -> None:
        """
        Adds a vertex to the current polygon in Tkinter mode.
        """
        new_point = Vertex(event.x, event.y)

        if self._is_same_as_another_point(new_point) or self._draws_intersecting_lines(self.polygons[-1] if self.in_progress else None, new_point):
            return

        if not self.in_progress:
            self.polygons.append([])
            self.objects_ids_by_polygon.append([])
            self.in_progress = True
            self._update_buttons_tkinter()

        self.polygons[-1].append(new_point)
        self._draw_point_tkinter(new_point)

        if len(self.polygons[-1]) > 1:
            self._draw_line_tkinter(self.polygons[-1][-2], self.polygons[-1][-1])

    def _close_polygon_tkinter(self, _: Event) -> None:
        """
        Closes the current polygon in Tkinter mode.
        """
        if not self.in_progress or len(self.polygons[-1]) < 3 or self._draws_intersecting_lines(self.polygons[-1]):
            return

        self._draw_line_tkinter(self.polygons[-1][-1], self.polygons[-1][0])
        self.in_progress = False
        self._triangulate()

    def _clear_tkinter(self) -> None:
        """
        Clears all polygons and drawings in Tkinter mode.
        """
        self.canvas.delete("all")
        self.polygons = []
        self.objects_ids_by_polygon = []
        self.triangles_ids = []
        self.in_progress = False
        self._update_buttons_tkinter()

    def _update_buttons_tkinter(self) -> None:
        """
        Updates button states in Tkinter mode.
        """
        state = "normal" if self.polygons else "disabled"
        self.clear_button.config(state=state)

    def _load_from_file_tkinter(self) -> None:
        """
        Loads polygons from a file in Tkinter mode.
        """
        filepath = askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        self._clear_tkinter()
        polygons = self._load_from_file(filepath)

        margin = 20
        all_vertices = [v for polygon in polygons for v in polygon]
        min_x = min(v.x for v in all_vertices) if all_vertices else 0
        min_y = min(v.y for v in all_vertices) if all_vertices else 0

        for polygon in polygons:
            normalized = [Vertex(v.x - min_x + margin, v.y - min_y + margin) for v in polygon]
            self.polygons.append(normalized)
            self.objects_ids_by_polygon.append([])
            for pt in normalized:
                self._draw_point_tkinter(pt)
            for i in range(len(normalized)):
                self._draw_line_tkinter(normalized[i], normalized[(i + 1) % len(normalized)])

        self._triangulate()
        self._update_buttons_tkinter()

    def _load_from_file(self, filepath: str) -> List[Polygon]:
        """
        Loads polygons from a file (shared by both modes).

        Returns:
            List[Polygon]: List of loaded polygons.
        """
        polygons = []
        current_polygon: List[Vertex] = []

        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        if current_polygon and len(current_polygon) >= 3:
                            polygons.append(current_polygon)
                        current_polygon = []
                        continue
                    try:
                        x, y = map(float, line.split())
                        current_polygon.append(Vertex(x, y))
                    except ValueError as e:
                        continue
        except Exception as e:
            raise

        if current_polygon and len(current_polygon) >= 3:
            polygons.append(current_polygon)

        if not polygons:
            raise ValueError("No valid polygons found in file")

        return polygons

    def _draw_point_tkinter(self, point: Vertex) -> None:
        """
        Draws a vertex in Tkinter mode.
        """
        pt_id = self.canvas.create_oval(
            point.x - self.point_radius,
            point.y - self.point_radius,
            point.x + self.point_radius,
            point.y + self.point_radius,
            fill=self.point_color
        )
        self.objects_ids_by_polygon[-1].append(pt_id)

    def _draw_line_tkinter(self, pt_a: Vertex, pt_b: Vertex) -> None:
        """
        Draws a line in Tkinter mode.
        """
        line_id = self.canvas.create_line(
            pt_a.x, pt_a.y, pt_b.x, pt_b.y,
            fill=self.line_color
        )
        self.objects_ids_by_polygon[-1].append(line_id)

    def _draw_point_pil(self, point: Vertex) -> None:
        """
        Draws a vertex in PIL mode.
        """
        try:
            self.draw.ellipse(
                (
                    point.x - self.point_radius,
                    point.y - self.point_radius,
                    point.x + self.point_radius,
                    point.y + self.point_radius
                ),
                fill=self.point_color
            )
        except Exception as e:
            raise

    def _draw_line_pil(self, pt_a: Vertex, pt_b: Vertex) -> None:
        """
        Draws a line in PIL mode.
        """
        try:
            self.draw.line(
                (pt_a.x, pt_a.y, pt_b.x, pt_b.y),
                fill=self.line_color
            )
        except Exception as e:
            raise

    def _draw_polygon_pil(self, polygon: Polygon) -> None:
        """
        Draws a polygon in PIL mode.
        """
        for vertex in polygon:
            self._draw_point_pil(vertex)
        for i in range(len(polygon)):
            self._draw_line_pil(polygon[i], polygon[(i + 1) % len(polygon)])

    def _draw_triangle_tkinter(self, triangle: Triangle) -> None:
        """
        Draws a triangle in Tkinter mode.
        """
        pt1, pt2, pt3 = triangle.vertices
        color = triangle.color_str
        triangle_id = self.canvas.create_polygon(
            pt1.x, pt1.y, pt2.x, pt2.y, pt3.x, pt3.y,
            fill=color, outline=color, width=1
        )
        self.canvas.tag_lower(triangle_id)
        self.triangles_ids.append(triangle_id)

    def _draw_triangle_pil(self, triangle: Triangle) -> None:
        """
        Draws a triangle in PIL mode.
        """
        pt1, pt2, pt3 = triangle.vertices
        color = triangle.color_str
        # Validate color
        if not isinstance(color, str) or not (color.startswith("#") or color in ImageDraw.ImageDraw.fill.__dict__):
            color = "lightblue"
        try:
            self.draw.polygon(
                [(pt1.x, pt1.y), (pt2.x, pt2.y), (pt3.x, pt3.y)],
                fill=color, outline=color
            )
        except Exception as e:
            raise

    def _clear_triangulation_tkinter(self) -> None:
        """
        Clears triangulation in Tkinter mode.
        """
        for triangle_id in self.triangles_ids:
            self.canvas.delete(triangle_id)
        self.triangles_ids = []

    def _triangulate(self) -> None:
        """
        Performs triangulation and draws the resulting triangles.
        """
        try:
            polygonal_area = PolygonalArea(self.polygons)
            triangles = triangulate_polygonal_area(polygonal_area)
        except Exception as e:
            raise

        if self.use_tkinter:
            self._clear_triangulation_tkinter()

        for i, triangle in enumerate(triangles):
            if self.use_tkinter:
                self._draw_triangle_tkinter(triangle)
            else:
                self._draw_triangle_pil(triangle)

    def _is_same_as_another_point(self, new_point: Vertex) -> bool:
        """
        Checks if a point is the same as any existing point.
        """
        for polygon in self.polygons:
            for point in polygon:
                if math.isclose(new_point.x, point.x) and math.isclose(new_point.y, point.y):
                    return True
        return False

    def _draws_intersecting_lines(self, polygon: Polygon | None, new_pt: Vertex | None = None) -> bool:
        """
        Checks if adding a new point or closing a polygon results in intersecting lines.
        """
        if polygon is None:
            beg_new_line = None
        elif len(polygon) < 1:
            return False
        else:
            beg_new_line = polygon[-1]

        # If starting a new polygon (no previous points yet)
        if beg_new_line is None:
            return False  # Nothing to check

        closing = new_pt is None
        new_pt = polygon[0] if closing else new_pt

        for polygon_idx, other_polygon in enumerate(self.polygons):
            # Don't check against last polygon while it's still being drawn
            is_current_polygon = polygon in self.polygons and polygon_idx == len(self.polygons) - 1
            beg = 1 if is_current_polygon and closing else 0
            end_offset = 2 if is_current_polygon else 0

            for pt_index in range(beg, len(other_polygon) - end_offset):
                pt_a = other_polygon[pt_index]
                pt_b = other_polygon[(pt_index + 1) % len(other_polygon)]

                # Prevent checking adjacency (edge sharing point)
                if beg_new_line in (pt_a, pt_b) or new_pt in (pt_a, pt_b):
                    continue

                if segment_intersect(pt_a, pt_b, beg_new_line, new_pt):
                    return True

        return False
