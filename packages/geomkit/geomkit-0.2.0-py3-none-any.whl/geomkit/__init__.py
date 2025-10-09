"""
GeomKit - A Python library for mathematical geometrical functionalities.

This library provides comprehensive geometric primitives and operations including:
- 2D and 3D points, vectors, and lines
- 2D shapes: circles, ellipses, polygons
- 3D shapes: spheres, cubes, rectangular prisms
- Transformation matrices (2D and 3D)
- Bézier curves (quadratic and cubic)
- Bounding boxes (AABB)
- Geometric algorithms: convex hull, intersections
- Distance calculations and transformations
"""

__version__ = "0.2.0"
__author__ = "Mohamed Sajith"
__email__ = "mmssajith@gmail.com"

# Import from submodules
from geomkit.curves import CubicBezier, QuadraticBezier
from geomkit.operations import (
    angle_between,
    convex_hull,
    distance,
    line_segment_intersection_point,
    line_segments_intersect,
)
from geomkit.primitives import Line2D, LineSegment2D, Point2D, Point3D, Vector2D, Vector3D
from geomkit.primitives.matrix import Matrix2D, Matrix3D
from geomkit.shapes import Circle, Ellipse, Polygon, Rectangle, RegularPolygon, Square, Triangle
from geomkit.shapes.boundingbox import AABB2D, AABB3D
from geomkit.shapes.shapes3d import Cube, RectangularPrism, Sphere

__all__ = [
    # Primitives
    "Point2D",
    "Point3D",
    "Vector2D",
    "Vector3D",
    "Line2D",
    "LineSegment2D",
    "Matrix2D",
    "Matrix3D",
    # 2D Shapes
    "Circle",
    "Ellipse",
    "Polygon",
    "Triangle",
    "Rectangle",
    "Square",
    "RegularPolygon",
    # 3D Shapes
    "Sphere",
    "Cube",
    "RectangularPrism",
    # Bounding Boxes
    "AABB2D",
    "AABB3D",
    # Curves
    "QuadraticBezier",
    "CubicBezier",
    # Operations
    "distance",
    "angle_between",
    "convex_hull",
    "line_segments_intersect",
    "line_segment_intersection_point",
]
