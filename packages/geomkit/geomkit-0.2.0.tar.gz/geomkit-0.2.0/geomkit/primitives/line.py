"""Line and line segment classes for 2D geometric operations."""

import math
from typing import Optional

from geomkit.primitives.point import Point2D


class Line2D:
    """Represents an infinite line in 2D space using slope-intercept form.

    Examples:
        >>> p1 = Point2D(0, 0)
        >>> p2 = Point2D(1, 1)
        >>> line = Line2D(p1, p2)
        >>> line.contains_point(Point2D(2, 2))
        True
        >>> round(line.distance_to_point(Point2D(0, 1)), 10)
        0.7071067812
    """

    slope: Optional[float]
    y_intercept: Optional[float]
    x_intercept: Optional[float]

    def __init__(self, point1: Point2D, point2: Point2D) -> None:
        """
        Initialize a line from two points.

        Args:
            point1: First point on the line
            point2: Second point on the line

        Raises:
            ValueError: If both points are the same

        Examples:
            >>> Line2D(Point2D(0, 0), Point2D(1, 1))
            Line2D(y = 1.0x + 0.0)
            >>> Line2D(Point2D(0, 0), Point2D(0, 0))
            Traceback (most recent call last):
                ...
            ValueError: Two distinct points are required to define a line
        """
        if point1 == point2:
            raise ValueError("Two distinct points are required to define a line")

        self.point1 = point1
        self.point2 = point2

        # Calculate slope and y-intercept
        if math.isclose(point2.x, point1.x):
            # Vertical line
            self.is_vertical = True
            self.slope = None
            self.y_intercept = None
            self.x_intercept = point1.x
        else:
            self.is_vertical = False
            self.slope = (point2.y - point1.y) / (point2.x - point1.x)
            self.y_intercept = point1.y - self.slope * point1.x
            if self.slope != 0:
                self.x_intercept = -self.y_intercept / self.slope
            else:
                self.x_intercept = None

    def contains_point(self, point: Point2D, tolerance: float = 1e-9) -> bool:
        """
        Check if a point lies on the line.

        Args:
            point: Point to check
            tolerance: Tolerance for floating point comparison

        Returns:
            True if point is on the line

        Examples:
            >>> line = Line2D(Point2D(0, 0), Point2D(1, 1))
            >>> line.contains_point(Point2D(2, 2))
            True
            >>> line.contains_point(Point2D(1, 0))
            False
        """
        if self.is_vertical:
            assert self.x_intercept is not None
            return math.isclose(point.x, self.x_intercept, abs_tol=tolerance)
        else:
            assert self.slope is not None and self.y_intercept is not None
            expected_y = self.slope * point.x + self.y_intercept
            return math.isclose(point.y, expected_y, abs_tol=tolerance)

    def is_parallel(self, other: "Line2D") -> bool:
        """
        Check if this line is parallel to another.

        Args:
            other: Another Line2D instance

        Returns:
            True if lines are parallel
        """
        if self.is_vertical and other.is_vertical:
            return True
        if self.is_vertical or other.is_vertical:
            return False
        assert self.slope is not None and other.slope is not None
        return math.isclose(self.slope, other.slope)

    def is_perpendicular(self, other: "Line2D") -> bool:
        """
        Check if this line is perpendicular to another.

        Args:
            other: Another Line2D instance

        Returns:
            True if lines are perpendicular
        """
        if self.is_vertical:
            return other.slope == 0 if other.slope is not None else False
        if other.is_vertical:
            return self.slope == 0 if self.slope is not None else False
        assert self.slope is not None and other.slope is not None
        return math.isclose(self.slope * other.slope, -1)

    def intersection(self, other: "Line2D") -> Optional[Point2D]:
        """
        Find intersection point with another line.

        Args:
            other: Another Line2D instance

        Returns:
            Point2D of intersection, or None if lines are parallel
        """
        if self.is_parallel(other):
            return None

        if self.is_vertical:
            assert self.x_intercept is not None
            assert other.slope is not None and other.y_intercept is not None
            x = self.x_intercept
            y = other.slope * x + other.y_intercept
            return Point2D(x, y)

        if other.is_vertical:
            assert other.x_intercept is not None
            assert self.slope is not None and self.y_intercept is not None
            x = other.x_intercept
            y = self.slope * x + self.y_intercept
            return Point2D(x, y)

        # Solve: y = m1*x + b1 and y = m2*x + b2
        assert self.slope is not None and self.y_intercept is not None
        assert other.slope is not None and other.y_intercept is not None
        x = (other.y_intercept - self.y_intercept) / (self.slope - other.slope)
        y = self.slope * x + self.y_intercept
        return Point2D(x, y)

    def distance_to_point(self, point: Point2D) -> float:
        """
        Calculate perpendicular distance from point to line.

        Args:
            point: Point to measure distance to

        Returns:
            Perpendicular distance
        """
        if self.is_vertical:
            assert self.x_intercept is not None
            return abs(point.x - self.x_intercept)

        # Use formula: |ax + by + c| / sqrt(a^2 + b^2)
        # where line is ax + by + c = 0
        # From y = mx + b: mx - y + b = 0
        assert self.slope is not None and self.y_intercept is not None
        a = self.slope
        b = -1
        c = self.y_intercept

        return abs(a * point.x + b * point.y + c) / math.sqrt(a**2 + b**2)

    def __repr__(self) -> str:
        if self.is_vertical:
            return f"Line2D(x = {self.x_intercept})"
        return f"Line2D(y = {self.slope}x + {self.y_intercept})"

    def __str__(self) -> str:
        if self.is_vertical:
            return f"x = {self.x_intercept}"
        return f"y = {self.slope}x + {self.y_intercept}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Line2D):
            return False
        if self.is_vertical and other.is_vertical:
            assert self.x_intercept is not None and other.x_intercept is not None
            return math.isclose(self.x_intercept, other.x_intercept)
        if self.is_vertical or other.is_vertical:
            return False
        assert self.slope is not None and self.y_intercept is not None
        assert other.slope is not None and other.y_intercept is not None
        return math.isclose(self.slope, other.slope) and math.isclose(
            self.y_intercept, other.y_intercept
        )

    def __hash__(self) -> int:
        """
        Return hash value for use in sets and as dict keys.

        Note: Since we use floating point comparison with tolerance in __eq__,
        this hash is based on rounded values to maintain hash consistency.
        """
        if self.is_vertical:
            assert self.x_intercept is not None
            return hash(("vertical", round(self.x_intercept, 9)))
        assert self.slope is not None and self.y_intercept is not None
        return hash((round(self.slope, 9), round(self.y_intercept, 9)))


class LineSegment2D:
    """Represents a line segment in 2D space.

    Examples:
        >>> seg = LineSegment2D(Point2D(0, 0), Point2D(3, 4))
        >>> seg.length()
        5.0
        >>> seg.midpoint()
        Point2D(1.5, 2.0)
    """

    def __init__(self, start: Point2D, end: Point2D) -> None:
        """
        Initialize a line segment.

        Args:
            start: Start point
            end: End point

        Raises:
            ValueError: If start and end points are the same

        Examples:
            >>> seg = LineSegment2D(Point2D(0, 0), Point2D(1, 1))
            >>> seg.length()
            1.4142135623730951
            >>> LineSegment2D(Point2D(0, 0), Point2D(0, 0))
            Traceback (most recent call last):
                ...
            ValueError: Start and end points must be different
        """
        if start == end:
            raise ValueError("Start and end points must be different")

        self.start = start
        self.end = end

    def length(self) -> float:
        """Calculate the length of the line segment.

        Examples:
            >>> seg = LineSegment2D(Point2D(0, 0), Point2D(3, 4))
            >>> seg.length()
            5.0
        """
        return self.start.distance_to(self.end)

    def midpoint(self) -> Point2D:
        """Calculate the midpoint of the line segment.

        Examples:
            >>> seg = LineSegment2D(Point2D(0, 0), Point2D(4, 6))
            >>> seg.midpoint()
            Point2D(2.0, 3.0)
        """
        return self.start.midpoint(self.end)

    def contains_point(self, point: Point2D, tolerance: float = 1e-9) -> bool:
        """
        Check if a point lies on the line segment.

        Args:
            point: Point to check
            tolerance: Tolerance for floating point comparison

        Returns:
            True if point is on the segment
        """
        # Check if point is collinear with segment
        cross_product = (point.y - self.start.y) * (self.end.x - self.start.x) - (
            point.x - self.start.x
        ) * (self.end.y - self.start.y)

        if not math.isclose(cross_product, 0, abs_tol=tolerance):
            return False

        # Check if point is within bounding box
        min_x = min(self.start.x, self.end.x)
        max_x = max(self.start.x, self.end.x)
        min_y = min(self.start.y, self.end.y)
        max_y = max(self.start.y, self.end.y)

        return (
            min_x - tolerance <= point.x <= max_x + tolerance
            and min_y - tolerance <= point.y <= max_y + tolerance
        )

    def intersects(self, other: "LineSegment2D") -> bool:
        """
        Check if this segment intersects with another.

        Args:
            other: Another LineSegment2D instance

        Returns:
            True if segments intersect
        """

        def ccw(a: Point2D, b: Point2D, c: Point2D) -> bool:
            """Check if three points are in counter-clockwise order."""
            return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)

        return ccw(self.start, other.start, other.end) != ccw(
            self.end, other.start, other.end
        ) and ccw(self.start, self.end, other.start) != ccw(self.start, self.end, other.end)

    def intersection_point(self, other: "LineSegment2D") -> Optional[Point2D]:
        """
        Find intersection point with another line segment.

        Args:
            other: Another LineSegment2D instance

        Returns:
            Point2D of intersection, or None if segments don't intersect
        """
        if not self.intersects(other):
            return None

        # Line segment 1: P1 + t * (P2 - P1)
        # Line segment 2: P3 + u * (P4 - P3)
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        x3, y3 = other.start.x, other.start.y
        x4, y4 = other.end.x, other.end.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if math.isclose(denom, 0):
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom

        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        return Point2D(x, y)

    def __repr__(self) -> str:
        return f"LineSegment2D({self.start}, {self.end})"

    def __str__(self) -> str:
        return f"[{self.start} -> {self.end}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LineSegment2D):
            return False
        return self.start == other.start and self.end == other.end

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.start, self.end))
