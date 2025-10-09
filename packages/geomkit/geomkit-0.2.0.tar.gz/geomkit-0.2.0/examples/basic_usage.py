"""Basic usage examples for GeomKit."""

import math

from geomkit import (
    Circle,
    Ellipse,
    Line2D,
    Point2D,
    Rectangle,
    RegularPolygon,
    Square,
    Triangle,
    Vector2D,
)
from geomkit.operations.utils import angle_between, collinear, distance


def point_examples():
    """Examples using Point2D."""
    print("=== Point Examples ===")

    # Create points
    p1 = Point2D(0, 0)
    p2 = Point2D(3, 4)

    # Distance
    distance = p1.distance_to(p2)
    print(f"Distance from {p1} to {p2}: {distance}")

    # Midpoint
    mid = p1.midpoint(p2)
    print(f"Midpoint: {mid}")

    # Rotation
    rotated = p2.rotate(math.pi / 2)  # 90 degrees
    print(f"Point {p2} rotated 90°: {rotated}")
    print()


def vector_examples():
    """Examples using Vector2D."""
    print("=== Vector Examples ===")

    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 0)

    # Magnitude
    print(f"Magnitude of {v1}: {v1.magnitude()}")

    # Normalize
    unit = v1.normalize()
    print(f"Unit vector of {v1}: {unit}")

    # Dot product
    dot = v1.dot(v2)
    print(f"Dot product: {dot}")

    # Angle between vectors
    angle = v1.angle_to(v2)
    print(f"Angle between vectors: {math.degrees(angle)}°")

    # Vector operations
    v3 = v1 + v2
    print(f"{v1} + {v2} = {v3}")
    print()


def circle_examples():
    """Examples using Circle."""
    print("=== Circle Examples ===")

    circle1 = Circle(Point2D(0, 0), 5)
    circle2 = Circle(Point2D(8, 0), 5)

    print(f"Circle 1: {circle1}")
    print(f"Area: {circle1.area():.2f}")
    print(f"Circumference: {circle1.circumference():.2f}")

    # Check if point is inside
    test_point = Point2D(3, 4)
    print(f"Point {test_point} inside circle: {circle1.contains_point(test_point)}")

    # Circle intersection
    if circle1.intersects_circle(circle2):
        points = circle1.intersection_points(circle2)
        print(f"Circles intersect at: {points}")
    print()


def triangle_examples():
    """Examples using Triangle."""
    print("=== Triangle Examples ===")

    triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

    print(f"Triangle: {triangle}")
    print(f"Area: {triangle.area()}")
    print(f"Perimeter: {triangle.perimeter():.2f}")

    # Side lengths
    sides = triangle.side_lengths()
    print(f"Side lengths: {[f'{s:.2f}' for s in sides]}")

    # Angles in degrees
    angles = triangle.angles()
    angles_deg = [math.degrees(a) for a in angles]
    print(f"Angles (degrees): {[f'{a:.2f}' for a in angles_deg]}")

    # Check if point is inside
    test_point = Point2D(2, 1)
    print(f"Point {test_point} inside triangle: {triangle.contains_point(test_point)}")
    print()


def line_examples():
    """Examples using Line2D."""
    print("=== Line Examples ===")

    line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
    line2 = Line2D(Point2D(0, 1), Point2D(1, 0))

    print(f"Line 1: {line1}")
    print(f"Line 2: {line2}")

    # Check if lines are parallel
    print(f"Lines parallel: {line1.is_parallel(line2)}")

    # Check if perpendicular
    print(f"Lines perpendicular: {line1.is_perpendicular(line2)}")

    # Find intersection
    intersection = line1.intersection(line2)
    print(f"Intersection point: {intersection}")

    # Distance from point to line
    point = Point2D(1, 0)
    distance = line1.distance_to_point(point)
    print(f"Distance from {point} to line: {distance:.2f}")
    print()


def ellipse_examples():
    """Examples using Ellipse."""
    print("=== Ellipse Examples ===")

    ellipse = Ellipse(Point2D(0, 0), semi_major_axis=5, semi_minor_axis=3)

    print(f"Ellipse: {ellipse}")
    print(f"Area: {ellipse.area():.2f}")
    print(f"Perimeter (approx): {ellipse.perimeter():.2f}")
    print(f"Eccentricity: {ellipse.eccentricity():.3f}")

    # Focal points
    f1, f2 = ellipse.focal_points()
    print(f"Focal points: {f1}, {f2}")

    # Point on ellipse
    point = ellipse.point_on_ellipse(math.pi / 4)
    print(f"Point at 45°: {point}")
    print()


def polygon_examples():
    """Examples using polygon shapes."""
    print("=== Polygon Examples ===")

    # Rectangle
    rect = Rectangle(Point2D(0, 0), width=4, height=3)
    print(f"Rectangle area: {rect.area()}")
    print(f"Rectangle diagonal: {rect.diagonal_length():.2f}")

    # Square
    square = Square(Point2D(0, 0), side_length=5)
    print(f"Square area: {square.area()}")
    print(f"Square perimeter: {square.perimeter()}")

    # Regular Hexagon
    hexagon = RegularPolygon(Point2D(0, 0), num_sides=6, radius=5)
    print(f"Hexagon area: {hexagon.area():.2f}")
    print(f"Hexagon side length: {hexagon.side_length():.2f}")
    print(f"Hexagon interior angle: {math.degrees(hexagon.interior_angle()):.2f}°")
    print()


def utility_examples():
    """Examples using utility functions."""
    print("=== Utility Functions ===")

    p1 = Point2D(0, 0)
    p2 = Point2D(3, 4)
    p3 = Point2D(6, 8)

    # Distance
    dist = distance(p1, p2)
    print(f"Distance between {p1} and {p2}: {dist}")

    # Collinearity
    print(f"Points collinear: {collinear(p1, p2, p3)}")

    # Vector angle
    v1 = Vector2D(1, 0)
    v2 = Vector2D(1, 1)
    angle_deg = angle_between(v1, v2, degrees=True)
    print(f"Angle between vectors: {angle_deg:.2f}°")
    print()


if __name__ == "__main__":
    point_examples()
    vector_examples()
    circle_examples()
    ellipse_examples()
    triangle_examples()
    polygon_examples()
    line_examples()
    utility_examples()
    print("\n✓ All examples completed successfully!")
