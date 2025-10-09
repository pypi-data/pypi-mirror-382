"""Demonstration of all shape classes in GeomKit."""

import math

from geomkit import Circle, Ellipse, Point2D, Polygon, Rectangle, RegularPolygon, Square, Triangle


def compare_circles():
    """Compare different circles."""
    print("=== Circle Comparison ===")

    circles = [Circle(Point2D(0, 0), 3), Circle(Point2D(0, 0), 5), Circle(Point2D(0, 0), 7)]

    print("Radius | Area      | Circumference")
    print("-------|-----------|-------------")
    for circle in circles:
        print(f"{circle.radius:6.1f} | {circle.area():9.2f} | {circle.circumference():13.2f}")
    print()


def ellipse_variations():
    """Demonstrate ellipse with different parameters."""
    print("=== Ellipse Variations ===")

    # Standard ellipse
    ellipse1 = Ellipse(Point2D(0, 0), 6, 4)
    print("Standard ellipse (a=6, b=4):")
    print(f"  Area: {ellipse1.area():.2f}")
    print(f"  Eccentricity: {ellipse1.eccentricity():.3f}")

    # Rotated ellipse
    ellipse2 = Ellipse(Point2D(0, 0), 6, 4, rotation=math.pi / 4)
    print("\nRotated ellipse (45°):")
    print(f"  Area: {ellipse2.area():.2f}")
    print(f"  Rotation: {math.degrees(ellipse2.rotation):.1f}°")

    # Nearly circular ellipse
    ellipse3 = Ellipse(Point2D(0, 0), 5, 4.8)
    print("\nNearly circular (a=5, b=4.8):")
    print(f"  Eccentricity: {ellipse3.eccentricity():.3f}")

    # Highly eccentric ellipse
    ellipse4 = Ellipse(Point2D(0, 0), 10, 2)
    print("\nHighly eccentric (a=10, b=2):")
    print(f"  Eccentricity: {ellipse4.eccentricity():.3f}")
    print()


def triangle_types():
    """Demonstrate different types of triangles."""
    print("=== Triangle Types ===")

    # Right triangle (3-4-5)
    right_triangle = Triangle(Point2D(0, 0), Point2D(3, 0), Point2D(0, 4))
    print("Right Triangle (3-4-5):")
    print(f"  Area: {right_triangle.area():.2f}")
    print(f"  Is right triangle: {right_triangle.is_right_triangle()}")
    sides = right_triangle.side_lengths()
    print(f"  Sides: {sides[0]:.2f}, {sides[1]:.2f}, {sides[2]:.2f}")

    # Equilateral triangle
    h = 4 * math.sqrt(3) / 2  # height of equilateral triangle with side 4
    equilateral = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, h))
    print("\nEquilateral Triangle:")
    print(f"  Area: {equilateral.area():.2f}")
    sides = equilateral.side_lengths()
    print(f"  Sides: {sides[0]:.2f}, {sides[1]:.2f}, {sides[2]:.2f}")
    angles = [math.degrees(a) for a in equilateral.angles()]
    print(f"  Angles: {angles[0]:.1f}°, {angles[1]:.1f}°, {angles[2]:.1f}°")

    # Isosceles triangle
    isosceles = Triangle(Point2D(0, 0), Point2D(6, 0), Point2D(3, 5))
    print("\nIsosceles Triangle:")
    print(f"  Area: {isosceles.area():.2f}")
    sides = isosceles.side_lengths()
    print(f"  Sides: {sides[0]:.2f}, {sides[1]:.2f}, {sides[2]:.2f}")
    print()


def quadrilateral_family():
    """Compare different quadrilaterals."""
    print("=== Quadrilateral Family ===")

    # Rectangle
    rect = Rectangle(Point2D(0, 0), width=6, height=4)
    print("Rectangle (6×4):")
    print(f"  Area: {rect.area():.2f}")
    print(f"  Perimeter: {rect.perimeter():.2f}")
    print(f"  Diagonal: {rect.diagonal_length():.2f}")

    # Square
    square = Square(Point2D(0, 0), side_length=5)
    print("\nSquare (5×5):")
    print(f"  Area: {square.area():.2f}")
    print(f"  Perimeter: {square.perimeter():.2f}")
    print(f"  Diagonal: {square.diagonal_length():.2f}")

    # General quadrilateral
    quad = Polygon([Point2D(0, 0), Point2D(5, 1), Point2D(6, 5), Point2D(1, 4)])
    print("\nGeneral Quadrilateral:")
    print(f"  Area: {quad.area():.2f}")
    print(f"  Perimeter: {quad.perimeter():.2f}")
    print(f"  Is convex: {quad.is_convex()}")
    print()


def regular_polygons():
    """Create and analyze regular polygons."""
    print("=== Regular Polygons ===")

    radius = 10
    polygons = [
        (3, "Triangle"),
        (4, "Square"),
        (5, "Pentagon"),
        (6, "Hexagon"),
        (8, "Octagon"),
        (12, "Dodecagon"),
    ]

    print(f"All inscribed in circle with radius {radius}")
    print("\nSides | Name       | Area    | Perimeter | Side Length | Interior Angle")
    print("------|------------|---------|-----------|-------------|---------------")

    for num_sides, name in polygons:
        poly = RegularPolygon(Point2D(0, 0), num_sides, radius)
        interior_angle = math.degrees(poly.interior_angle())
        print(
            f"{num_sides:5d} | {name:10s} | {poly.area():7.2f} | "
            f"{poly.perimeter():9.2f} | {poly.side_length():11.2f} | {interior_angle:14.2f}°"
        )
    print()


def shape_containment():
    """Test point containment in various shapes."""
    print("=== Point Containment Tests ===")

    test_points = [Point2D(2, 2), Point2D(5, 0), Point2D(0, 0), Point2D(-1, -1)]

    # Circle
    circle = Circle(Point2D(0, 0), 5)
    print("Circle (center=(0,0), radius=5):")
    for pt in test_points:
        inside = circle.contains_point(pt)
        print(f"  {pt}: {'INSIDE' if inside else 'OUTSIDE'}")

    # Square
    square = Square(Point2D(0, 0), 4)
    print("\nSquare (corner=(0,0), side=4):")
    for pt in test_points:
        inside = square.contains_point(pt)
        print(f"  {pt}: {'INSIDE' if inside else 'OUTSIDE'}")

    # Triangle
    triangle = Triangle(Point2D(0, 0), Point2D(6, 0), Point2D(3, 5))
    print("\nTriangle (vertices: (0,0), (6,0), (3,5)):")
    for pt in test_points:
        inside = triangle.contains_point(pt)
        print(f"  {pt}: {'INSIDE' if inside else 'OUTSIDE'}")
    print()


def shape_properties():
    """Compare properties of shapes with same area."""
    print("=== Shapes with Same Area (≈100) ===")

    # Calculate dimensions for area ≈ 100
    target_area = 100

    # Circle: A = πr²
    circle_radius = math.sqrt(target_area / math.pi)
    circle = Circle(Point2D(0, 0), circle_radius)

    # Square: A = s²
    square_side = math.sqrt(target_area)
    square = Square(Point2D(0, 0), square_side)

    # Rectangle: A = w*h (2:1 ratio)
    rect_width = math.sqrt(target_area * 2)
    rect_height = rect_width / 2
    rectangle = Rectangle(Point2D(0, 0), rect_width, rect_height)

    # Regular hexagon
    # A = (3√3/2) * s², solve for s
    hex_side = math.sqrt(target_area * 2 / (3 * math.sqrt(3)))
    # Then find radius: r = s
    hexagon = RegularPolygon(Point2D(0, 0), 6, hex_side)

    print("Shape      | Area    | Perimeter | Efficiency Ratio")
    print("-----------|---------|-----------|------------------")
    print(
        f"Circle     | {circle.area():7.2f} | {circle.circumference():9.2f} | "
        f"{circle.area() / circle.circumference():18.3f}"
    )
    print(
        f"Square     | {square.area():7.2f} | {square.perimeter():9.2f} | "
        f"{square.area() / square.perimeter():18.3f}"
    )
    print(
        f"Rectangle  | {rectangle.area():7.2f} | {rectangle.perimeter():9.2f} | "
        f"{rectangle.area() / rectangle.perimeter():18.3f}"
    )
    print(
        f"Hexagon    | {hexagon.area():7.2f} | {hexagon.perimeter():9.2f} | "
        f"{hexagon.area() / hexagon.perimeter():18.3f}"
    )

    print("\nNote: Higher ratio = more efficient (more area per unit perimeter)")
    print("Circle is the most efficient shape!")
    print()


if __name__ == "__main__":
    compare_circles()
    ellipse_variations()
    triangle_types()
    quadrilateral_family()
    regular_polygons()
    shape_containment()
    shape_properties()
    print("✓ All shape demonstrations completed!")
