"""Circle class for 2D geometric operations."""

import math
from typing import List, Tuple

from geomkit.primitives.point import Point2D


class Circle:
    """Represents a circle in 2D space.

    Examples:
        >>> c = Circle(Point2D(0, 0), 5)
        >>> c.area()
        78.53981633974483
        >>> c.circumference()
        31.41592653589793
        >>> c.contains_point(Point2D(3, 4))
        True
    """

    def __init__(self, center: Point2D, radius: float) -> None:
        """
        Initialize a circle.

        Args:
            center: Center point of the circle
            radius: Radius of the circle

        Raises:
            ValueError: If radius is negative or zero

        Examples:
            >>> c = Circle(Point2D(0, 0), 5)
            >>> c.radius
            5.0
            >>> Circle(Point2D(0, 0), -1)
            Traceback (most recent call last):
                ...
            ValueError: Radius must be positive
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        self.center = center
        self.radius = float(radius)

    def area(self) -> float:
        """Calculate the area of the circle.

        Examples:
            >>> c = Circle(Point2D(0, 0), 5)
            >>> round(c.area(), 2)
            78.54
        """
        return math.pi * self.radius**2

    def circumference(self) -> float:
        """Calculate the circumference of the circle.

        Examples:
            >>> c = Circle(Point2D(0, 0), 5)
            >>> round(c.circumference(), 2)
            31.42
        """
        return 2 * math.pi * self.radius

    def contains_point(self, point: Point2D) -> bool:
        """
        Check if a point is inside or on the circle.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the circle
        """
        return self.center.distance_to(point) <= self.radius

    def point_on_circle(self, angle: float) -> Point2D:
        """
        Get a point on the circle at a given angle.

        Args:
            angle: Angle in radians (0 is to the right, increases counter-clockwise)

        Returns:
            Point on the circle at the given angle
        """
        x = self.center.x + self.radius * math.cos(angle)
        y = self.center.y + self.radius * math.sin(angle)
        return Point2D(x, y)

    def intersects_circle(self, other: "Circle") -> bool:
        """
        Check if this circle intersects with another circle.

        Args:
            other: Another Circle instance

        Returns:
            True if circles intersect
        """
        distance = self.center.distance_to(other.center)
        return distance <= (self.radius + other.radius)

    def intersection_points(self, other: "Circle") -> List[Point2D]:
        """
        Find intersection points with another circle.

        Args:
            other: Another Circle instance

        Returns:
            List of intersection points (0, 1, or 2 points)
        """
        d = self.center.distance_to(other.center)

        # No intersection - circles too far apart or one inside the other
        if d > self.radius + other.radius or d < abs(self.radius - other.radius):
            return []

        # Circles are identical
        if d == 0 and self.radius == other.radius:
            return []

        # Calculate intersection points
        a = (self.radius**2 - other.radius**2 + d**2) / (2 * d)
        h = math.sqrt(self.radius**2 - a**2)

        # Point on line between centers
        px = self.center.x + a * (other.center.x - self.center.x) / d
        py = self.center.y + a * (other.center.y - self.center.y) / d

        # Circles touch at one point
        if math.isclose(h, 0):
            return [Point2D(px, py)]

        # Two intersection points
        offset_x = h * (other.center.y - self.center.y) / d
        offset_y = h * (other.center.x - self.center.x) / d

        return [Point2D(px + offset_x, py - offset_y), Point2D(px - offset_x, py + offset_y)]

    def tangent_points_from_point(self, point: Point2D) -> List[Point2D]:
        """
        Find points where tangent lines from an external point touch the circle.

        Args:
            point: External point

        Returns:
            List of tangent points (0 or 2 points)
        """
        distance = self.center.distance_to(point)

        # Point is inside or on the circle
        if distance <= self.radius:
            return []

        # Angle from center to external point
        angle_to_point = math.atan2(point.y - self.center.y, point.x - self.center.x)

        # Angle offset for tangent points
        angle_offset = math.asin(self.radius / distance)

        # Two tangent points
        return [
            self.point_on_circle(angle_to_point + angle_offset),
            self.point_on_circle(angle_to_point - angle_offset),
        ]

    def __repr__(self) -> str:
        return f"Circle(center={self.center}, radius={self.radius})"

    def __str__(self) -> str:
        return f"Circle at {self.center} with radius {self.radius}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return False
        return self.center == other.center and math.isclose(self.radius, other.radius)

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.center, round(self.radius, 9)))


class Ellipse:
    """Represents an ellipse in 2D space.

    Examples:
        >>> e = Ellipse(Point2D(0, 0), 5, 3)
        >>> round(e.area(), 2)
        47.12
        >>> round(e.eccentricity(), 2)
        0.8
    """

    def __init__(
        self, center: Point2D, semi_major_axis: float, semi_minor_axis: float, rotation: float = 0
    ) -> None:
        """
        Initialize an ellipse.

        Args:
            center: Center point of the ellipse
            semi_major_axis: Length of semi-major axis (a)
            semi_minor_axis: Length of semi-minor axis (b)
            rotation: Rotation angle in radians (default 0)

        Raises:
            ValueError: If semi-major or semi-minor axis is negative or zero

        Examples:
            >>> e = Ellipse(Point2D(0, 0), 5, 3)
            >>> (e.semi_major_axis, e.semi_minor_axis)
            (5.0, 3.0)
            >>> Ellipse(Point2D(0, 0), -5, 3)
            Traceback (most recent call last):
                ...
            ValueError: Semi-major and semi-minor axes must be positive
        """
        if semi_major_axis <= 0 or semi_minor_axis <= 0:
            raise ValueError("Semi-major and semi-minor axes must be positive")

        self.center = center
        self.semi_major_axis = float(semi_major_axis)
        self.semi_minor_axis = float(semi_minor_axis)
        self.rotation = float(rotation)

    def area(self) -> float:
        """Calculate the area of the ellipse.

        Examples:
            >>> e = Ellipse(Point2D(0, 0), 5, 3)
            >>> round(e.area(), 2)
            47.12
        """
        return math.pi * self.semi_major_axis * self.semi_minor_axis

    def perimeter(self) -> float:
        """
        Calculate the approximate perimeter of the ellipse using Ramanujan's formula.

        Returns:
            Approximate perimeter
        """
        a = self.semi_major_axis
        b = self.semi_minor_axis
        h = ((a - b) ** 2) / ((a + b) ** 2)
        return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

    def eccentricity(self) -> float:
        """
        Calculate the eccentricity of the ellipse.

        Returns:
            Eccentricity value (0 for circle, approaching 1 for elongated ellipse)
        """
        a = max(self.semi_major_axis, self.semi_minor_axis)
        b = min(self.semi_major_axis, self.semi_minor_axis)
        return math.sqrt(1 - (b**2) / (a**2))

    def contains_point(self, point: Point2D) -> bool:
        """
        Check if a point is inside or on the ellipse.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the ellipse
        """
        # Translate point to ellipse center
        dx = point.x - self.center.x
        dy = point.y - self.center.y

        # Rotate point by negative rotation angle
        cos_r = math.cos(-self.rotation)
        sin_r = math.sin(-self.rotation)
        x_rot = dx * cos_r - dy * sin_r
        y_rot = dx * sin_r + dy * cos_r

        # Check ellipse equation: (x/a)² + (y/b)² <= 1
        return ((x_rot / self.semi_major_axis) ** 2 + (y_rot / self.semi_minor_axis) ** 2) <= 1

    def point_on_ellipse(self, angle: float) -> Point2D:
        """
        Get a point on the ellipse at a given parametric angle.

        Args:
            angle: Parametric angle in radians

        Returns:
            Point on the ellipse at the given angle
        """
        # Parametric equations for ellipse
        x = self.semi_major_axis * math.cos(angle)
        y = self.semi_minor_axis * math.sin(angle)

        # Rotate point
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        x_rot = x * cos_r - y * sin_r
        y_rot = x * sin_r + y * cos_r

        # Translate to center
        return Point2D(self.center.x + x_rot, self.center.y + y_rot)

    def focal_points(self) -> Tuple[Point2D, Point2D]:
        """
        Get the two focal points of the ellipse.

        Returns:
            Tuple of two focal points
        """
        if self.semi_major_axis > self.semi_minor_axis:
            c = math.sqrt(self.semi_major_axis**2 - self.semi_minor_axis**2)
            # Foci along major axis
            f1_x = c * math.cos(self.rotation)
            f1_y = c * math.sin(self.rotation)
        else:
            c = math.sqrt(self.semi_minor_axis**2 - self.semi_major_axis**2)
            # Foci along minor axis (perpendicular)
            f1_x = c * math.cos(self.rotation + math.pi / 2)
            f1_y = c * math.sin(self.rotation + math.pi / 2)

        return (
            Point2D(self.center.x + f1_x, self.center.y + f1_y),
            Point2D(self.center.x - f1_x, self.center.y - f1_y),
        )

    def __repr__(self) -> str:
        return (
            f"Ellipse(center={self.center}, a={self.semi_major_axis}, "
            f"b={self.semi_minor_axis}, rotation={self.rotation})"
        )

    def __str__(self) -> str:
        return (
            f"Ellipse at {self.center} with axes ({self.semi_major_axis}, {self.semi_minor_axis})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ellipse):
            return False
        return (
            self.center == other.center
            and math.isclose(self.semi_major_axis, other.semi_major_axis)
            and math.isclose(self.semi_minor_axis, other.semi_minor_axis)
            and math.isclose(self.rotation, other.rotation)
        )

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash(
            (
                self.center,
                round(self.semi_major_axis, 9),
                round(self.semi_minor_axis, 9),
                round(self.rotation, 9),
            )
        )
