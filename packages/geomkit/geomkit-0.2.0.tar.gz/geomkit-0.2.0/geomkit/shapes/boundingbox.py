"""Bounding box classes for collision detection and spatial queries."""

from typing import List

from geomkit.primitives.point import Point2D, Point3D


class AABB2D:
    """Axis-Aligned Bounding Box in 2D space.

    Examples:
        >>> box = AABB2D(Point2D(0, 0), Point2D(4, 3))
        >>> box.width()
        4.0
        >>> box.height()
        3.0
        >>> box.contains_point(Point2D(2, 1))
        True
    """

    def __init__(self, min_point: Point2D, max_point: Point2D) -> None:
        """
        Initialize a 2D axis-aligned bounding box.

        Args:
            min_point: Minimum corner (bottom-left)
            max_point: Maximum corner (top-right)

        Raises:
            ValueError: If min_point is not less than max_point in all dimensions

        Examples:
            >>> box = AABB2D(Point2D(0, 0), Point2D(4, 3))
            >>> box.width()
            4.0
            >>> AABB2D(Point2D(4, 0), Point2D(0, 3))
            Traceback (most recent call last):
                ...
            ValueError: min_point must be less than max_point in all dimensions
        """
        if min_point.x >= max_point.x or min_point.y >= max_point.y:
            raise ValueError("min_point must be less than max_point in all dimensions")

        self.min = min_point
        self.max = max_point

    @staticmethod
    def from_points(points: List[Point2D]) -> "AABB2D":
        """
        Create an AABB that contains all given points.

        Args:
            points: List of Point2D objects

        Returns:
            AABB2D containing all points

        Raises:
            ValueError: If points list is empty

        Examples:
            >>> pts = [Point2D(1, 2), Point2D(5, 1), Point2D(3, 6)]
            >>> box = AABB2D.from_points(pts)
            >>> (box.min.x, box.min.y, box.max.x, box.max.y)
            (1.0, 1.0, 5.0, 6.0)
        """
        if not points:
            raise ValueError("Cannot create AABB from empty list of points")

        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)

        return AABB2D(Point2D(min_x, min_y), Point2D(max_x, max_y))

    @staticmethod
    def from_center_and_size(center: Point2D, width: float, height: float) -> "AABB2D":
        """
        Create an AABB from center point and dimensions.

        Args:
            center: Center point
            width: Width of the box
            height: Height of the box

        Returns:
            AABB2D with specified center and dimensions

        Examples:
            >>> box = AABB2D.from_center_and_size(Point2D(2, 2), 4, 6)
            >>> (box.min.x, box.min.y, box.max.x, box.max.y)
            (0.0, -1.0, 4.0, 5.0)
        """
        half_w = width / 2
        half_h = height / 2
        return AABB2D(
            Point2D(center.x - half_w, center.y - half_h),
            Point2D(center.x + half_w, center.y + half_h),
        )

    def width(self) -> float:
        """Calculate the width of the bounding box.

        Examples:
            >>> AABB2D(Point2D(0, 0), Point2D(4, 3)).width()
            4.0
        """
        return self.max.x - self.min.x

    def height(self) -> float:
        """Calculate the height of the bounding box.

        Examples:
            >>> AABB2D(Point2D(0, 0), Point2D(4, 3)).height()
            3.0
        """
        return self.max.y - self.min.y

    def area(self) -> float:
        """Calculate the area of the bounding box.

        Examples:
            >>> AABB2D(Point2D(0, 0), Point2D(4, 3)).area()
            12.0
        """
        return self.width() * self.height()

    def center(self) -> Point2D:
        """Calculate the center point of the bounding box.

        Examples:
            >>> AABB2D(Point2D(0, 0), Point2D(4, 6)).center()
            Point2D(2.0, 3.0)
        """
        return Point2D((self.min.x + self.max.x) / 2, (self.min.y + self.max.y) / 2)

    def contains_point(self, point: Point2D) -> bool:
        """
        Check if a point is inside the bounding box.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the boundary

        Examples:
            >>> box = AABB2D(Point2D(0, 0), Point2D(4, 3))
            >>> box.contains_point(Point2D(2, 1))
            True
            >>> box.contains_point(Point2D(5, 1))
            False
        """
        return self.min.x <= point.x <= self.max.x and self.min.y <= point.y <= self.max.y

    def intersects(self, other: "AABB2D") -> bool:
        """
        Check if this bounding box intersects with another.

        Args:
            other: Another AABB2D

        Returns:
            True if boxes intersect

        Examples:
            >>> box1 = AABB2D(Point2D(0, 0), Point2D(4, 3))
            >>> box2 = AABB2D(Point2D(2, 1), Point2D(6, 5))
            >>> box1.intersects(box2)
            True
            >>> box3 = AABB2D(Point2D(5, 0), Point2D(9, 3))
            >>> box1.intersects(box3)
            False
        """
        return not (
            self.max.x < other.min.x
            or self.min.x > other.max.x
            or self.max.y < other.min.y
            or self.min.y > other.max.y
        )

    def union(self, other: "AABB2D") -> "AABB2D":
        """
        Create a bounding box that contains both this and another box.

        Args:
            other: Another AABB2D

        Returns:
            AABB2D containing both boxes

        Examples:
            >>> box1 = AABB2D(Point2D(0, 0), Point2D(4, 3))
            >>> box2 = AABB2D(Point2D(2, 1), Point2D(6, 5))
            >>> union = box1.union(box2)
            >>> (union.min.x, union.min.y, union.max.x, union.max.y)
            (0.0, 0.0, 6.0, 5.0)
        """
        return AABB2D(
            Point2D(min(self.min.x, other.min.x), min(self.min.y, other.min.y)),
            Point2D(max(self.max.x, other.max.x), max(self.max.y, other.max.y)),
        )

    def intersection(self, other: "AABB2D") -> "AABB2D":
        """
        Create a bounding box from the intersection of this and another box.

        Args:
            other: Another AABB2D

        Returns:
            AABB2D representing the intersection

        Raises:
            ValueError: If boxes don't intersect

        Examples:
            >>> box1 = AABB2D(Point2D(0, 0), Point2D(4, 3))
            >>> box2 = AABB2D(Point2D(2, 1), Point2D(6, 5))
            >>> inter = box1.intersection(box2)
            >>> (inter.min.x, inter.min.y, inter.max.x, inter.max.y)
            (2.0, 1.0, 4.0, 3.0)
        """
        if not self.intersects(other):
            raise ValueError("Boxes do not intersect")

        return AABB2D(
            Point2D(max(self.min.x, other.min.x), max(self.min.y, other.min.y)),
            Point2D(min(self.max.x, other.max.x), min(self.max.y, other.max.y)),
        )

    def expand(self, amount: float) -> "AABB2D":
        """
        Create a new AABB expanded by the given amount in all directions.

        Args:
            amount: Amount to expand (positive) or contract (negative)

        Returns:
            Expanded AABB2D

        Examples:
            >>> box = AABB2D(Point2D(1, 1), Point2D(3, 3))
            >>> expanded = box.expand(1)
            >>> (expanded.min.x, expanded.min.y, expanded.max.x, expanded.max.y)
            (0.0, 0.0, 4.0, 4.0)
        """
        return AABB2D(
            Point2D(self.min.x - amount, self.min.y - amount),
            Point2D(self.max.x + amount, self.max.y + amount),
        )

    def __repr__(self) -> str:
        return f"AABB2D(min={self.min}, max={self.max})"

    def __str__(self) -> str:
        return f"AABB2D[{self.min} to {self.max}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AABB2D):
            return False
        return self.min == other.min and self.max == other.max

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.min, self.max))


class AABB3D:
    """Axis-Aligned Bounding Box in 3D space.

    Examples:
        >>> box = AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2))
        >>> box.volume()
        24.0
        >>> box.contains_point(Point3D(2, 1, 1))
        True
    """

    def __init__(self, min_point: Point3D, max_point: Point3D) -> None:
        """
        Initialize a 3D axis-aligned bounding box.

        Args:
            min_point: Minimum corner
            max_point: Maximum corner

        Raises:
            ValueError: If min_point is not less than max_point in all dimensions

        Examples:
            >>> box = AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2))
            >>> box.volume()
            24.0
        """
        if min_point.x >= max_point.x or min_point.y >= max_point.y or min_point.z >= max_point.z:
            raise ValueError("min_point must be less than max_point in all dimensions")

        self.min = min_point
        self.max = max_point

    @staticmethod
    def from_points(points: List[Point3D]) -> "AABB3D":
        """
        Create an AABB that contains all given points.

        Args:
            points: List of Point3D objects

        Returns:
            AABB3D containing all points

        Raises:
            ValueError: If points list is empty

        Examples:
            >>> pts = [Point3D(1, 2, 3), Point3D(5, 1, 2), Point3D(3, 6, 4)]
            >>> box = AABB3D.from_points(pts)
            >>> (box.min.x, box.max.z)
            (1.0, 4.0)
        """
        if not points:
            raise ValueError("Cannot create AABB from empty list of points")

        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        min_z = min(p.z for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        max_z = max(p.z for p in points)

        return AABB3D(Point3D(min_x, min_y, min_z), Point3D(max_x, max_y, max_z))

    def width(self) -> float:
        """Calculate the width (x dimension) of the bounding box."""
        return self.max.x - self.min.x

    def height(self) -> float:
        """Calculate the height (y dimension) of the bounding box."""
        return self.max.y - self.min.y

    def depth(self) -> float:
        """Calculate the depth (z dimension) of the bounding box."""
        return self.max.z - self.min.z

    def volume(self) -> float:
        """Calculate the volume of the bounding box.

        Examples:
            >>> AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2)).volume()
            24.0
        """
        return self.width() * self.height() * self.depth()

    def surface_area(self) -> float:
        """Calculate the surface area of the bounding box.

        Examples:
            >>> AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2)).surface_area()
            52.0
        """
        w, h, d = self.width(), self.height(), self.depth()
        return 2 * (w * h + h * d + d * w)

    def center(self) -> Point3D:
        """Calculate the center point of the bounding box.

        Examples:
            >>> AABB3D(Point3D(0, 0, 0), Point3D(4, 6, 8)).center()
            Point3D(2.0, 3.0, 4.0)
        """
        return Point3D(
            (self.min.x + self.max.x) / 2,
            (self.min.y + self.max.y) / 2,
            (self.min.z + self.max.z) / 2,
        )

    def contains_point(self, point: Point3D) -> bool:
        """
        Check if a point is inside the bounding box.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the boundary

        Examples:
            >>> box = AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2))
            >>> box.contains_point(Point3D(2, 1, 1))
            True
            >>> box.contains_point(Point3D(5, 1, 1))
            False
        """
        return (
            self.min.x <= point.x <= self.max.x
            and self.min.y <= point.y <= self.max.y
            and self.min.z <= point.z <= self.max.z
        )

    def intersects(self, other: "AABB3D") -> bool:
        """
        Check if this bounding box intersects with another.

        Args:
            other: Another AABB3D

        Returns:
            True if boxes intersect

        Examples:
            >>> box1 = AABB3D(Point3D(0, 0, 0), Point3D(4, 3, 2))
            >>> box2 = AABB3D(Point3D(2, 1, 1), Point3D(6, 5, 3))
            >>> box1.intersects(box2)
            True
        """
        return not (
            self.max.x < other.min.x
            or self.min.x > other.max.x
            or self.max.y < other.min.y
            or self.min.y > other.max.y
            or self.max.z < other.min.z
            or self.min.z > other.max.z
        )

    def __repr__(self) -> str:
        return f"AABB3D(min={self.min}, max={self.max})"

    def __str__(self) -> str:
        return f"AABB3D[{self.min} to {self.max}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AABB3D):
            return False
        return self.min == other.min and self.max == other.max

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.min, self.max))
