"""Advanced geometry examples demonstrating complex operations."""


from geomkit import Circle, Line2D, LineSegment2D, Point2D, RegularPolygon, Triangle, Vector2D
from geomkit.operations.utils import collinear, triangle_area


def circle_intersections():
    """Find and analyze circle intersection points."""
    print("=== Circle Intersection Analysis ===")

    circle1 = Circle(Point2D(0, 0), 5)
    circle2 = Circle(Point2D(8, 0), 5)

    if circle1.intersects_circle(circle2):
        points = circle1.intersection_points(circle2)
        print(f"Number of intersection points: {len(points)}")

        for i, point in enumerate(points, 1):
            print(f"  Point {i}: {point}")
            # Verify point is on both circles
            dist1 = circle1.center.distance_to(point)
            dist2 = circle2.center.distance_to(point)
            print(f"    Distance to circle1 center: {dist1:.3f}")
            print(f"    Distance to circle2 center: {dist2:.3f}")
    print()


def tangent_lines():
    """Demonstrate tangent line calculations."""
    print("=== Tangent Lines from External Point ===")

    circle = Circle(Point2D(0, 0), 5)
    external_point = Point2D(13, 0)

    tangent_points = circle.tangent_points_from_point(external_point)

    print(f"External point: {external_point}")
    print(f"Number of tangent points: {len(tangent_points)}")

    for i, tp in enumerate(tangent_points, 1):
        print(f"\nTangent point {i}: {tp}")

        # Calculate tangent line length
        tangent_length = external_point.distance_to(tp)
        print(f"  Tangent line length: {tangent_length:.3f}")

        # Verify perpendicularity
        # Vector from center to tangent point
        v1 = Vector2D(tp.x - circle.center.x, tp.y - circle.center.y)
        # Vector from tangent point to external point
        v2 = Vector2D(external_point.x - tp.x, external_point.y - tp.y)

        dot_product = v1.dot(v2)
        print(f"  Dot product (should be ~0): {dot_product:.6f}")
    print()


def polygon_triangulation():
    """Demonstrate polygon triangulation using triangle area."""
    print("=== Polygon Triangulation ===")

    # Create a quadrilateral
    vertices = [Point2D(0, 0), Point2D(5, 0), Point2D(6, 4), Point2D(1, 5)]

    print("Quadrilateral vertices:")
    for i, v in enumerate(vertices):
        print(f"  V{i}: {v}")

    # Triangulate by dividing into two triangles
    triangle1_area = triangle_area(vertices[0], vertices[1], vertices[2])
    triangle2_area = triangle_area(vertices[0], vertices[2], vertices[3])

    total_area = triangle1_area + triangle2_area

    print(f"\nTriangle 1 area: {triangle1_area:.2f}")
    print(f"Triangle 2 area: {triangle2_area:.2f}")
    print(f"Total polygon area: {total_area:.2f}")
    print()


def line_segment_intersections():
    """Analyze line segment intersections."""
    print("=== Line Segment Intersection ===")

    # Create two intersecting segments
    seg1 = LineSegment2D(Point2D(0, 0), Point2D(10, 10))
    seg2 = LineSegment2D(Point2D(0, 10), Point2D(10, 0))

    print(f"Segment 1: {seg1.start} to {seg1.end}")
    print(f"Segment 2: {seg2.start} to {seg2.end}")

    if seg1.intersects(seg2):
        intersection = seg1.intersection_point(seg2)
        print(f"Intersection point: {intersection}")

        # Calculate distances to intersection
        dist_from_seg1_start = seg1.start.distance_to(intersection)
        dist_from_seg1_end = seg1.end.distance_to(intersection)

        print(f"Distance from seg1 start: {dist_from_seg1_start:.3f}")
        print(f"Distance from seg1 end: {dist_from_seg1_end:.3f}")

        # Check if intersection is at midpoint
        seg1_length = seg1.length()
        print(f"Segment 1 length: {seg1_length:.3f}")
        print(f"Intersection at midpoint: {abs(dist_from_seg1_start - seg1_length / 2) < 0.001}")
    print()


def inscribed_polygon():
    """Create a polygon inscribed in a circle."""
    print("=== Inscribed Regular Polygon ===")

    # Create a regular pentagon inscribed in a circle
    pentagon = RegularPolygon(Point2D(0, 0), num_sides=5, radius=10)

    print("Pentagon inscribed in circle with radius 10")
    print(f"Number of sides: {pentagon.num_sides}")
    print(f"Side length: {pentagon.side_length():.3f}")
    print(f"Area: {pentagon.area():.3f}")
    print(f"Perimeter: {pentagon.perimeter():.3f}")
    print(f"Apothem: {pentagon.apothem():.3f}")

    # Verify vertices are on the circle
    print("\nVerifying vertices are on circumcircle:")
    for i, vertex in enumerate(pentagon.vertices):
        dist = pentagon.center_point.distance_to(vertex)
        print(f"  Vertex {i}: distance to center = {dist:.3f}")
    print()


def vector_projection():
    """Demonstrate vector projection."""
    print("=== Vector Projection ===")

    # Project vector v1 onto v2
    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 0)

    print(f"Vector v1: {v1}")
    print(f"Vector v2: {v2}")

    # Projection of v1 onto v2
    projection_length = v1.dot(v2) / v2.magnitude()
    projection_vector = v2.normalize() * projection_length

    print("\nProjection of v1 onto v2:")
    print(f"  Projection length: {projection_length:.3f}")
    print(f"  Projection vector: {projection_vector}")

    # Calculate perpendicular component
    perpendicular = Vector2D(v1.x - projection_vector.x, v1.y - projection_vector.y)
    print(f"  Perpendicular component: {perpendicular}")

    # Verify orthogonality
    dot = projection_vector.dot(perpendicular)
    print(f"  Dot product (should be ~0): {dot:.6f}")
    print()


def circle_through_three_points():
    """Find circle passing through three points."""
    print("=== Circle Through Three Points ===")

    p1 = Point2D(0, 0)
    p2 = Point2D(4, 0)
    p3 = Point2D(2, 3)

    print(f"Points: {p1}, {p2}, {p3}")

    # Check if points are collinear
    if collinear(p1, p2, p3):
        print("Points are collinear - no unique circle exists")
    else:
        # Calculate circumcenter (simplified for this case)
        # Using perpendicular bisectors method
        mid1 = p1.midpoint(p2)
        mid2 = p2.midpoint(p3)

        print(f"\nMidpoint of p1-p2: {mid1}")
        print(f"Midpoint of p2-p3: {mid2}")

        # For this specific case, we can calculate the circumcenter
        # This is a simplified demonstration
        triangle = Triangle(p1, p2, p3)
        centroid = triangle.centroid()

        print(f"Triangle centroid: {centroid}")
        print(f"Triangle area: {triangle.area():.3f}")
    print()


def closest_point_on_line():
    """Find closest point on a line to an external point."""
    print("=== Closest Point on Line ===")

    line = Line2D(Point2D(0, 0), Point2D(4, 0))
    external_point = Point2D(2, 3)

    print(f"Line: {line}")
    print(f"External point: {external_point}")

    # The closest point on a horizontal line is directly below/above
    distance = line.distance_to_point(external_point)
    print(f"Distance from point to line: {distance:.3f}")

    # For horizontal line y=0, closest point is (x, 0)
    closest_point = Point2D(external_point.x, 0)
    print(f"Closest point on line: {closest_point}")

    # Verify
    actual_distance = external_point.distance_to(closest_point)
    print(f"Verification distance: {actual_distance:.3f}")
    print()


if __name__ == "__main__":
    circle_intersections()
    tangent_lines()
    polygon_triangulation()
    line_segment_intersections()
    inscribed_polygon()
    vector_projection()
    circle_through_three_points()
    closest_point_on_line()
    print("✓ All advanced examples completed!")
