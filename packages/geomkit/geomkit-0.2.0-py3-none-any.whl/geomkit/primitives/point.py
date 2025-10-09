"""Point classes for 2D and 3D geometric operations."""

import math
from typing import Optional, Tuple


class Point2D:
    """Represents a point in 2D space.

    Examples:
        >>> p1 = Point2D(0, 0)
        >>> p2 = Point2D(3, 4)
        >>> p1.distance_to(p2)
        5.0
        >>> p1.midpoint(p2)
        Point2D(1.5, 2.0)
        >>> p1 + p2
        Point2D(3.0, 4.0)
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialize a 2D point.

        Args:
            x: X coordinate
            y: Y coordinate

        Examples:
            >>> p = Point2D(3.5, 4.2)
            >>> p.x
            3.5
            >>> p.y
            4.2
        """
        self.x = float(x)
        self.y = float(y)

    def distance_to(self, other: "Point2D") -> float:
        """
        Calculate Euclidean distance to another point.

        Args:
            other: Another Point2D instance

        Returns:
            Distance between the two points

        Examples:
            >>> p1 = Point2D(0, 0)
            >>> p2 = Point2D(3, 4)
            >>> p1.distance_to(p2)
            5.0
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def midpoint(self, other: "Point2D") -> "Point2D":
        """
        Calculate the midpoint between this point and another.

        Args:
            other: Another Point2D instance

        Returns:
            A new Point2D representing the midpoint

        Examples:
            >>> p1 = Point2D(0, 0)
            >>> p2 = Point2D(4, 6)
            >>> p1.midpoint(p2)
            Point2D(2.0, 3.0)
        """
        return Point2D((self.x + other.x) / 2, (self.y + other.y) / 2)

    def translate(self, dx: float, dy: float) -> "Point2D":
        """
        Translate the point by given offsets.

        Args:
            dx: X offset
            dy: Y offset

        Returns:
            A new translated Point2D

        Examples:
            >>> p = Point2D(1, 2)
            >>> p.translate(3, 4)
            Point2D(4.0, 6.0)
        """
        return Point2D(self.x + dx, self.y + dy)

    def rotate(self, angle: float, origin: Optional["Point2D"] = None) -> "Point2D":
        """
        Rotate point around an origin by given angle (in radians).

        Args:
            angle: Rotation angle in radians
            origin: Point to rotate around (defaults to origin)

        Returns:
            A new rotated Point2D

        Examples:
            >>> import math
            >>> p = Point2D(1, 0)
            >>> rotated = p.rotate(math.pi / 2)  # 90 degrees
            >>> abs(rotated.x) < 1e-10 and abs(rotated.y - 1.0) < 1e-10
            True
        """
        if origin is None:
            origin = Point2D(0, 0)

        # Translate to origin
        temp_x = self.x - origin.x
        temp_y = self.y - origin.y

        # Rotate
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotated_x = temp_x * cos_a - temp_y * sin_a
        rotated_y = temp_x * sin_a + temp_y * cos_a

        # Translate back
        return Point2D(rotated_x + origin.x, rotated_y + origin.y)

    def to_tuple(self) -> Tuple[float, float]:
        """Convert point to tuple (x, y)."""
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Point2D({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point2D):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __hash__(self) -> int:
        """
        Return hash value for use in sets and as dict keys.

        Note: Since we use floating point comparison with tolerance in __eq__,
        this hash is based on rounded values to maintain hash consistency.
        """
        return hash((round(self.x, 9), round(self.y, 9)))

    def __add__(self, other: "Point2D") -> "Point2D":
        """Add two points (vector addition)."""
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point2D") -> "Point2D":
        """Subtract two points (vector subtraction)."""
        return Point2D(self.x - other.x, self.y - other.y)


class Point3D:
    """Represents a point in 3D space.

    Examples:
        >>> p1 = Point3D(0, 0, 0)
        >>> p2 = Point3D(1, 2, 2)
        >>> p1.distance_to(p2)
        3.0
        >>> p1.midpoint(p2)
        Point3D(0.5, 1.0, 1.0)
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        """
        Initialize a 3D point.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate

        Examples:
            >>> p = Point3D(1, 2, 3)
            >>> (p.x, p.y, p.z)
            (1.0, 2.0, 3.0)
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def distance_to(self, other: "Point3D") -> float:
        """
        Calculate Euclidean distance to another point.

        Args:
            other: Another Point3D instance

        Returns:
            Distance between the two points

        Examples:
            >>> p1 = Point3D(0, 0, 0)
            >>> p2 = Point3D(3, 4, 0)
            >>> p1.distance_to(p2)
            5.0
        """
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def midpoint(self, other: "Point3D") -> "Point3D":
        """
        Calculate the midpoint between this point and another.

        Args:
            other: Another Point3D instance

        Returns:
            A new Point3D representing the midpoint

        Examples:
            >>> p1 = Point3D(0, 0, 0)
            >>> p2 = Point3D(2, 4, 6)
            >>> p1.midpoint(p2)
            Point3D(1.0, 2.0, 3.0)
        """
        return Point3D((self.x + other.x) / 2, (self.y + other.y) / 2, (self.z + other.z) / 2)

    def translate(self, dx: float, dy: float, dz: float) -> "Point3D":
        """
        Translate the point by given offsets.

        Args:
            dx: X offset
            dy: Y offset
            dz: Z offset

        Returns:
            A new translated Point3D

        Examples:
            >>> p = Point3D(1, 2, 3)
            >>> p.translate(1, 1, 1)
            Point3D(2.0, 3.0, 4.0)
        """
        return Point3D(self.x + dx, self.y + dy, self.z + dz)

    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert point to tuple (x, y, z)."""
        return (self.x, self.y, self.z)

    def __repr__(self) -> str:
        return f"Point3D({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point3D):
            return False
        return (
            math.isclose(self.x, other.x)
            and math.isclose(self.y, other.y)
            and math.isclose(self.z, other.z)
        )

    def __hash__(self) -> int:
        """
        Return hash value for use in sets and as dict keys.

        Note: Since we use floating point comparison with tolerance in __eq__,
        this hash is based on rounded values to maintain hash consistency.
        """
        return hash((round(self.x, 9), round(self.y, 9), round(self.z, 9)))

    def __add__(self, other: "Point3D") -> "Point3D":
        """Add two points (vector addition)."""
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Point3D") -> "Point3D":
        """Subtract two points (vector subtraction)."""
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
