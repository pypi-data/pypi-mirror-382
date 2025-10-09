"""
Advanced features demonstration for GeomKit.

This example showcases:
- 3D shapes (Sphere, Cube, Rectangular Prism)
- Transformation matrices (Matrix2D, Matrix3D)
- Bézier curves (Quadratic and Cubic)
- Convex hull algorithm
- Bounding boxes (AABB)
- Line segment intersection
"""

import math

from geomkit import (
    AABB2D,
    AABB3D,
    Cube,
    CubicBezier,
    LineSegment2D,
    Matrix2D,
    Matrix3D,
    Point2D,
    Point3D,
    QuadraticBezier,
    RectangularPrism,
    Sphere,
    convex_hull,
    line_segment_intersection_point,
)


def print_section(title):
    """Print a section header."""
    print(f"\n=== {title} ===")


def main():
    print("GeomKit Advanced Features Demonstration")
    print("=" * 50)

    # 3D Shapes
    print_section("3D Shapes")

    # Sphere
    sphere = Sphere(Point3D(0, 0, 0), 5)
    print(f"Sphere: {sphere}")
    print(f"Volume: {sphere.volume():.2f}")
    print(f"Surface Area: {sphere.surface_area():.2f}")
    print(f"Contains Point3D(3, 0, 0): {sphere.contains_point(Point3D(3, 0, 0))}")

    # Cube
    cube = Cube(Point3D(0, 0, 0), 4)
    print(f"\nCube: {cube}")
    print(f"Volume: {cube.volume():.2f}")
    print(f"Surface Area: {cube.surface_area():.2f}")
    print(f"Diagonal: {cube.diagonal_length():.2f}")
    print(f"Center: {cube.center()}")

    # Rectangular Prism
    prism = RectangularPrism(Point3D(0, 0, 0), 4, 3, 2)
    print(f"\nRectangular Prism: {prism}")
    print(f"Volume: {prism.volume():.2f}")
    print(f"Surface Area: {prism.surface_area():.2f}")

    # Transformation Matrices
    print_section("2D Transformation Matrices")

    # Translation
    m_translate = Matrix2D.translation(5, 10)
    p1 = Point2D(1, 2)
    p1_translated = m_translate.transform_point(p1)
    print(f"Point {p1} translated by (5, 10): {p1_translated}")

    # Rotation
    m_rotate = Matrix2D.rotation(math.pi / 4)  # 45 degrees
    p2 = Point2D(1, 0)
    p2_rotated = m_rotate.transform_point(p2)
    print(f"Point {p2} rotated 45°: ({p2_rotated.x:.3f}, {p2_rotated.y:.3f})")

    # Scaling
    m_scale = Matrix2D.scaling(2, 3)
    p3 = Point2D(1, 1)
    p3_scaled = m_scale.transform_point(p3)
    print(f"Point {p3} scaled by (2, 3): {p3_scaled}")

    # Combined transformation
    m_combined = m_translate.multiply(m_rotate).multiply(m_scale)
    p4 = Point2D(1, 0)
    p4_transformed = m_combined.transform_point(p4)
    print(f"Point {p4} with combined transform: ({p4_transformed.x:.2f}, {p4_transformed.y:.2f})")

    print_section("3D Transformation Matrices")

    # 3D Rotation around Z axis
    m_rotate_z = Matrix3D.rotation_z(math.pi / 2)  # 90 degrees
    p3d = Point3D(1, 0, 0)
    p3d_rotated = m_rotate_z.transform_point(p3d)
    print(
        f"Point {p3d} rotated 90° around Z: "
        f"({p3d_rotated.x:.3f}, {p3d_rotated.y:.3f}, {p3d_rotated.z:.3f})"
    )

    # 3D Scaling
    m_scale_3d = Matrix3D.scaling(2, 3, 4)
    p3d2 = Point3D(1, 1, 1)
    p3d2_scaled = m_scale_3d.transform_point(p3d2)
    print(f"Point {p3d2} scaled by (2, 3, 4): {p3d2_scaled}")

    # Bézier Curves
    print_section("Bézier Curves")

    # Quadratic Bézier
    quad_curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
    print(f"Quadratic Bézier: {quad_curve}")
    print(f"Point at t=0.5: {quad_curve.point_at(0.5)}")
    print(f"Approximate length: {quad_curve.approximate_length():.2f}")

    # Cubic Bézier
    cubic_curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
    print(f"\nCubic Bézier: {cubic_curve}")
    print(f"Point at t=0.5: {cubic_curve.point_at(0.5)}")
    print(f"Approximate length: {cubic_curve.approximate_length():.2f}")

    # Split curve
    left, right = cubic_curve.split(0.5)
    print("Split at t=0.5:")
    print(f"  Left curve ends at: {left.p3}")
    print(f"  Right curve starts at: {right.p0}")

    # Bounding Boxes
    print_section("Axis-Aligned Bounding Boxes (AABB)")

    # 2D AABB
    box1 = AABB2D(Point2D(0, 0), Point2D(4, 3))
    box2 = AABB2D(Point2D(2, 1), Point2D(6, 5))
    print(f"Box 1: {box1}")
    print(f"Box 1 area: {box1.area():.2f}")
    print(f"Box 1 center: {box1.center()}")
    print(f"\nBox 2: {box2}")
    print(f"Boxes intersect: {box1.intersects(box2)}")

    union_box = box1.union(box2)
    print(f"Union: {union_box}")

    inter_box = box1.intersection(box2)
    print(f"Intersection: {inter_box}")

    # Create AABB from points
    points_2d = [Point2D(1, 2), Point2D(5, 1), Point2D(3, 6), Point2D(2, 3)]
    box_from_points = AABB2D.from_points(points_2d)
    print(f"\nAABB from points: {box_from_points}")

    # 3D AABB
    box3d = AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2))
    print(f"\n3D Box: {box3d}")
    print(f"Volume: {box3d.volume():.2f}")
    print(f"Surface Area: {box3d.surface_area():.2f}")

    # Convex Hull
    print_section("Convex Hull Algorithm")

    # Random-looking points
    points = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(4, 4),
        Point2D(0, 4),
        Point2D(2, 2),  # Interior point
        Point2D(1, 1),  # Interior point
        Point2D(3, 3),  # Interior point
    ]

    print(f"Input points: {len(points)}")
    hull = convex_hull(points)
    print(f"Convex hull vertices: {len(hull)}")
    print("Hull points:")
    for i, p in enumerate(hull):
        print(f"  {i + 1}. {p}")

    # Line Segment Intersection
    print_section("Line Segment Intersection")

    seg1 = LineSegment2D(Point2D(0, 0), Point2D(4, 4))
    seg2 = LineSegment2D(Point2D(0, 4), Point2D(4, 0))

    print(f"Segment 1: {seg1}")
    print(f"Segment 2: {seg2}")

    intersection = line_segment_intersection_point(seg1, seg2)
    if intersection:
        print(f"Intersection point: {intersection}")
    else:
        print("Segments do not intersect")

    # Parallel segments
    seg3 = LineSegment2D(Point2D(0, 0), Point2D(2, 2))
    seg4 = LineSegment2D(Point2D(0, 1), Point2D(2, 3))

    print(f"\nSegment 3: {seg3}")
    print(f"Segment 4: {seg4}")

    intersection2 = line_segment_intersection_point(seg3, seg4)
    if intersection2:
        print(f"Intersection point: {intersection2}")
    else:
        print("Segments do not intersect (parallel)")

    print("\n" + "=" * 50)
    print("✓ All advanced features demonstrated successfully!")


if __name__ == "__main__":
    main()
