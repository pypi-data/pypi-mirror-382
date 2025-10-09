"""Examples of geometric transformations using GeomKit."""

import math

from geomkit import Point2D, RegularPolygon, Square, Triangle, Vector2D
from geomkit.operations.utils import lerp


def point_transformations():
    """Demonstrate point translation and rotation."""
    print("=== Point Transformations ===")

    original = Point2D(3, 4)
    print(f"Original point: {original}")

    # Translation
    translated = original.translate(2, -1)
    print(f"Translated by (2, -1): {translated}")

    # Rotation around origin
    rotated_90 = original.rotate(math.pi / 2)
    print(f"Rotated 90° around origin: ({rotated_90.x:.3f}, {rotated_90.y:.3f})")

    # Rotation around custom point
    pivot = Point2D(1, 1)
    rotated_custom = original.rotate(math.pi / 2, pivot)
    print(f"Rotated 90° around {pivot}: ({rotated_custom.x:.3f}, {rotated_custom.y:.3f})")

    # Multiple transformations
    result = original.translate(5, 0).rotate(math.pi / 4)
    print(f"Translate then rotate 45°: ({result.x:.3f}, {result.y:.3f})")
    print()


def vector_transformations():
    """Demonstrate vector operations and transformations."""
    print("=== Vector Transformations ===")

    v = Vector2D(3, 4)
    print(f"Original vector: {v}")
    print(f"Magnitude: {v.magnitude():.3f}")

    # Scaling
    scaled = v * 2
    print(f"\nScaled by 2: {scaled}")
    print(f"Magnitude: {scaled.magnitude():.3f}")

    # Normalization
    unit = v.normalize()
    print(f"\nNormalized: ({unit.x:.3f}, {unit.y:.3f})")
    print(f"Magnitude: {unit.magnitude():.3f}")

    # Rotation
    rotated = v.rotate(math.pi / 3)  # 60 degrees
    print(f"\nRotated 60°: ({rotated.x:.3f}, {rotated.y:.3f})")

    # Reflection (negate)
    reflected = -v
    print(f"Reflected through origin: {reflected}")
    print()


def triangle_rotation():
    """Rotate a triangle around its centroid."""
    print("=== Triangle Rotation ===")

    # Create triangle
    triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
    centroid = triangle.centroid()

    print("Original triangle:")
    print(f"  Vertices: {triangle.a}, {triangle.b}, {triangle.c}")
    print(f"  Centroid: {centroid}")

    # Rotate each vertex around centroid
    angle = math.pi / 4  # 45 degrees

    rotated_vertices = [
        triangle.a.rotate(angle, centroid),
        triangle.b.rotate(angle, centroid),
        triangle.c.rotate(angle, centroid),
    ]

    rotated_triangle = Triangle(*rotated_vertices)

    print("\nRotated triangle (45° around centroid):")
    for i, v in enumerate(rotated_vertices):
        print(f"  Vertex {i}: ({v.x:.3f}, {v.y:.3f})")

    # Check that area is preserved
    print(f"\nOriginal area: {triangle.area():.3f}")
    print(f"Rotated area: {rotated_triangle.area():.3f}")
    print(f"Area preserved: {abs(triangle.area() - rotated_triangle.area()) < 0.001}")
    print()


def shape_scaling():
    """Demonstrate scaling shapes from their center."""
    print("=== Shape Scaling ===")

    # Original square
    square = Square(Point2D(0, 0), 4)
    original_center = square.centroid()

    print("Original square:")
    print(f"  Side length: {square.side_length}")
    print(f"  Area: {square.area():.2f}")
    print(f"  Center: {original_center}")

    # Scale by 2 (double size)
    scale_factor = 2

    # Calculate new bottom-left corner to keep center same
    new_side = square.side_length * scale_factor
    offset = (new_side - square.side_length) / 2
    new_bottom_left = Point2D(square.vertices[0].x - offset, square.vertices[0].y - offset)

    scaled_square = Square(new_bottom_left, new_side)
    scaled_center = scaled_square.centroid()

    print("\nScaled square (2x):")
    print(f"  Side length: {scaled_square.side_length}")
    print(f"  Area: {scaled_square.area():.2f}")
    print(f"  Center: {scaled_center}")
    print(f"  Area ratio: {scaled_square.area() / square.area():.2f}")
    print()


def interpolation_demo():
    """Demonstrate linear interpolation between points."""
    print("=== Point Interpolation ===")

    p1 = Point2D(0, 0)
    p2 = Point2D(10, 5)

    print(f"Start point: {p1}")
    print(f"End point: {p2}")
    print("\nInterpolated points:")

    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        interpolated = lerp(p1, p2, t)
        print(f"  t={t:.2f}: {interpolated}")

    # Extrapolation
    extrapolated = lerp(p1, p2, 1.5)
    print(f"\nExtrapolation (t=1.5): {extrapolated}")
    print()


def polygon_morphing():
    """Morph between two polygons using interpolation."""
    print("=== Polygon Morphing ===")

    # Start: Triangle
    triangle_vertices = [Point2D(2, 0), Point2D(4, 0), Point2D(3, 2)]

    # End: Different triangle
    target_vertices = [Point2D(1, 1), Point2D(5, 1), Point2D(3, 4)]

    print("Morphing from triangle to another triangle:")
    print(f"Start: {triangle_vertices}")
    print(f"End: {target_vertices}")

    for t in [0.0, 0.5, 1.0]:
        morphed = [lerp(triangle_vertices[i], target_vertices[i], t) for i in range(3)]
        triangle = Triangle(*morphed)
        print(f"\nt={t:.1f}:")
        print(f"  Vertices: {[str(v) for v in morphed]}")
        print(f"  Area: {triangle.area():.3f}")
    print()


def regular_polygon_animation():
    """Demonstrate rotation animation of a regular polygon."""
    print("=== Regular Polygon Rotation Animation ===")

    # Hexagon
    hexagon = RegularPolygon(Point2D(5, 5), num_sides=6, radius=3)

    print(f"Original hexagon at {hexagon.center_point}:")
    print(f"  Rotation: {math.degrees(hexagon.rotation_angle):.1f}°")

    angles = [0, math.pi / 6, math.pi / 3, math.pi / 2]
    print("\nRotation frames:")

    for angle in angles:
        rotated_hex = RegularPolygon(hexagon.center_point, num_sides=6, radius=3, rotation=angle)
        print(f"\nRotation: {math.degrees(angle):.1f}°")
        print(f"  First vertex: ({rotated_hex.vertices[0].x:.3f}, {rotated_hex.vertices[0].y:.3f})")
    print()


def reflection_transformation():
    """Demonstrate reflection transformations."""
    print("=== Reflection Transformations ===")

    point = Point2D(3, 2)
    print(f"Original point: {point}")

    # Reflection over x-axis
    reflect_x = Point2D(point.x, -point.y)
    print(f"Reflected over x-axis: {reflect_x}")

    # Reflection over y-axis
    reflect_y = Point2D(-point.x, point.y)
    print(f"Reflected over y-axis: {reflect_y}")

    # Reflection over origin
    reflect_origin = Point2D(-point.x, -point.y)
    print(f"Reflected over origin: {reflect_origin}")

    # Reflection over line y=x (swap coordinates)
    reflect_diagonal = Point2D(point.y, point.x)
    print(f"Reflected over y=x: {reflect_diagonal}")
    print()


def composite_transformations():
    """Apply multiple transformations in sequence."""
    print("=== Composite Transformations ===")

    original = Point2D(2, 1)
    print(f"Original point: {original}")

    # Sequence: Translate → Rotate → Scale (via distance from origin)
    step1 = original.translate(3, 2)
    print(f"1. Translate by (3, 2): {step1}")

    step2 = step1.rotate(math.pi / 4)
    print(f"2. Rotate 45°: ({step2.x:.3f}, {step2.y:.3f})")

    # Scale by moving point further from origin
    distance = math.sqrt(step2.x**2 + step2.y**2)
    scale_factor = 1.5
    step3 = Point2D(step2.x * scale_factor, step2.y * scale_factor)
    print(f"3. Scale by 1.5: ({step3.x:.3f}, {step3.y:.3f})")

    new_distance = math.sqrt(step3.x**2 + step3.y**2)
    print(f"\nDistance from origin: {distance:.3f} → {new_distance:.3f}")
    print(f"Scale factor: {new_distance / distance:.3f}")
    print()


if __name__ == "__main__":
    point_transformations()
    vector_transformations()
    triangle_rotation()
    shape_scaling()
    interpolation_demo()
    polygon_morphing()
    regular_polygon_animation()
    reflection_transformation()
    composite_transformations()
    print("✓ All transformation examples completed!")
