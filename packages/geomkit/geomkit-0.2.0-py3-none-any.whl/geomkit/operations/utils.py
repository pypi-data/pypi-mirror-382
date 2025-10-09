"""Utility functions for geometric calculations."""

import math
from typing import List, Optional, Union

from geomkit.primitives.line import LineSegment2D
from geomkit.primitives.point import Point2D, Point3D
from geomkit.primitives.vector import Vector2D, Vector3D


def distance(obj1: Union[Point2D, Point3D], obj2: Union[Point2D, Point3D]) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        obj1: First point (2D or 3D)
        obj2: Second point (2D or 3D)

    Returns:
        Distance between the points

    Raises:
        TypeError: If points are not of compatible types
    """
    if isinstance(obj1, Point2D) and isinstance(obj2, Point2D):
        return obj1.distance_to(obj2)
    elif isinstance(obj1, Point3D) and isinstance(obj2, Point3D):
        return obj1.distance_to(obj2)
    else:
        raise TypeError("Both points must be of the same type (2D or 3D)")


def angle_between(
    vec1: Union[Vector2D, Vector3D], vec2: Union[Vector2D, Vector3D], degrees: bool = False
) -> float:
    """
    Calculate angle between two vectors.

    Args:
        vec1: First vector (2D or 3D)
        vec2: Second vector (2D or 3D)
        degrees: If True, return angle in degrees; otherwise radians

    Returns:
        Angle between the vectors

    Raises:
        TypeError: If vectors are not of compatible types
    """
    if isinstance(vec1, Vector2D) and isinstance(vec2, Vector2D):
        angle = vec1.angle_to(vec2)
    elif isinstance(vec1, Vector3D) and isinstance(vec2, Vector3D):
        angle = vec1.angle_to(vec2)
    else:
        raise TypeError("Both vectors must be of the same type (2D or 3D)")

    return math.degrees(angle) if degrees else angle


def collinear(p1: Point2D, p2: Point2D, p3: Point2D, tolerance: float = 1e-9) -> bool:
    """
    Check if three 2D points are collinear.

    Args:
        p1: First point
        p2: Second point
        p3: Third point
        tolerance: Tolerance for floating point comparison

    Returns:
        True if points are collinear
    """
    # Calculate cross product
    cross = (p2.y - p1.y) * (p3.x - p2.x) - (p2.x - p1.x) * (p3.y - p2.y)
    return math.isclose(cross, 0, abs_tol=tolerance)


def triangle_area(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
    """
    Calculate area of a triangle from three points.

    Args:
        p1: First vertex
        p2: Second vertex
        p3: Third vertex

    Returns:
        Area of the triangle
    """
    return abs((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)) / 2.0


def lerp(p1: Point2D, p2: Point2D, t: float) -> Point2D:
    """
    Linear interpolation between two 2D points.

    Args:
        p1: Start point
        p2: End point
        t: Interpolation parameter (0 returns p1, 1 returns p2)

    Returns:
        Interpolated point
    """
    return Point2D(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return math.radians(degrees)


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(radians)


def convex_hull(points: List[Point2D]) -> List[Point2D]:
    """
    Compute the convex hull of a set of 2D points using Graham's scan algorithm.

    Args:
        points: List of Point2D objects

    Returns:
        List of Point2D objects forming the convex hull in counter-clockwise order

    Raises:
        ValueError: If fewer than 3 points provided

    Examples:
        >>> from geomkit.primitives.point import Point2D
        >>> pts = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4), Point2D(2, 2)]
        >>> hull = convex_hull(pts)
        >>> len(hull)
        4
    """
    if len(points) < 3:
        raise ValueError("Convex hull requires at least 3 points")

    # Create a copy to avoid modifying input
    points = list(points)

    # Find the point with lowest y-coordinate (and leftmost if tie)
    start = min(points, key=lambda p: (p.y, p.x))

    def polar_angle_key(point: Point2D) -> tuple:
        """Key function for sorting by polar angle."""
        if point == start:
            return (-math.inf, 0)
        dx = point.x - start.x
        dy = point.y - start.y
        angle = math.atan2(dy, dx)
        distance = dx * dx + dy * dy
        return (angle, distance)

    # Sort points by polar angle with respect to start point
    sorted_points = sorted(points, key=polar_angle_key)

    def cross_product(o: Point2D, a: Point2D, b: Point2D) -> float:
        """Calculate cross product of vectors OA and OB."""
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

    # Build convex hull
    hull: List[Point2D] = []

    for point in sorted_points:
        # Remove points that make clockwise turn
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)

    return hull


def line_segments_intersect(seg1: LineSegment2D, seg2: LineSegment2D) -> bool:
    """
    Check if two line segments intersect.

    Args:
        seg1: First line segment
        seg2: Second line segment

    Returns:
        True if segments intersect

    Examples:
        >>> from geomkit.primitives.point import Point2D
        >>> from geomkit.primitives.line import LineSegment2D
        >>> s1 = LineSegment2D(Point2D(0, 0), Point2D(2, 2))
        >>> s2 = LineSegment2D(Point2D(0, 2), Point2D(2, 0))
        >>> line_segments_intersect(s1, s2)
        True
    """
    return seg1.intersects(seg2)


def line_segment_intersection_point(seg1: LineSegment2D, seg2: LineSegment2D) -> Optional[Point2D]:
    """
    Find the intersection point of two line segments.

    Args:
        seg1: First line segment
        seg2: Second line segment

    Returns:
        Point2D of intersection, or None if segments don't intersect

    Examples:
        >>> from geomkit.primitives.point import Point2D
        >>> from geomkit.primitives.line import LineSegment2D
        >>> s1 = LineSegment2D(Point2D(0, 0), Point2D(2, 2))
        >>> s2 = LineSegment2D(Point2D(0, 2), Point2D(2, 0))
        >>> pt = line_segment_intersection_point(s1, s2)
        >>> pt
        Point2D(1.0, 1.0)
    """
    return seg1.intersection_point(seg2)
