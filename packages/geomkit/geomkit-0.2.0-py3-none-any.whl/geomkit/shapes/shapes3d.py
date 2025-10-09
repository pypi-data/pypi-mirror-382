"""3D shape classes for geometric operations."""

import math
from typing import List

from geomkit.primitives.point import Point3D


class Sphere:
    """Represents a sphere in 3D space.

    Examples:
        >>> s = Sphere(Point3D(0, 0, 0), 5)
        >>> s.volume()
        523.5987755982989
        >>> s.surface_area()
        314.1592653589793
        >>> s.contains_point(Point3D(3, 0, 0))
        True
    """

    def __init__(self, center: Point3D, radius: float) -> None:
        """
        Initialize a sphere.

        Args:
            center: Center point of the sphere
            radius: Radius of the sphere

        Raises:
            ValueError: If radius is negative or zero

        Examples:
            >>> s = Sphere(Point3D(0, 0, 0), 5)
            >>> s.radius
            5.0
            >>> Sphere(Point3D(0, 0, 0), -1)
            Traceback (most recent call last):
                ...
            ValueError: Radius must be positive
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        self.center = center
        self.radius = float(radius)

    def volume(self) -> float:
        """Calculate the volume of the sphere.

        Examples:
            >>> s = Sphere(Point3D(0, 0, 0), 3)
            >>> round(s.volume(), 2)
            113.1
        """
        return (4 / 3) * math.pi * self.radius**3

    def surface_area(self) -> float:
        """Calculate the surface area of the sphere.

        Examples:
            >>> s = Sphere(Point3D(0, 0, 0), 3)
            >>> round(s.surface_area(), 2)
            113.1
        """
        return 4 * math.pi * self.radius**2

    def contains_point(self, point: Point3D) -> bool:
        """
        Check if a point is inside or on the sphere.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the sphere

        Examples:
            >>> s = Sphere(Point3D(0, 0, 0), 5)
            >>> s.contains_point(Point3D(3, 0, 0))
            True
            >>> s.contains_point(Point3D(10, 0, 0))
            False
        """
        return self.center.distance_to(point) <= self.radius

    def point_on_sphere(self, theta: float, phi: float) -> Point3D:
        """
        Get a point on the sphere using spherical coordinates.

        Args:
            theta: Azimuthal angle in radians (0 to 2π)
            phi: Polar angle in radians (0 to π)

        Returns:
            Point on the sphere surface

        Examples:
            >>> s = Sphere(Point3D(0, 0, 0), 5)
            >>> p = s.point_on_sphere(0, math.pi/2)
            >>> abs(p.z) < 1e-10
            True
        """
        x = self.center.x + self.radius * math.sin(phi) * math.cos(theta)
        y = self.center.y + self.radius * math.sin(phi) * math.sin(theta)
        z = self.center.z + self.radius * math.cos(phi)
        return Point3D(x, y, z)

    def intersects_sphere(self, other: "Sphere") -> bool:
        """
        Check if this sphere intersects with another sphere.

        Args:
            other: Another Sphere instance

        Returns:
            True if spheres intersect

        Examples:
            >>> s1 = Sphere(Point3D(0, 0, 0), 5)
            >>> s2 = Sphere(Point3D(5, 0, 0), 5)
            >>> s1.intersects_sphere(s2)
            True
        """
        distance = self.center.distance_to(other.center)
        return distance <= (self.radius + other.radius)

    def __repr__(self) -> str:
        return f"Sphere(center={self.center}, radius={self.radius})"

    def __str__(self) -> str:
        return f"Sphere at {self.center} with radius {self.radius}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sphere):
            return False
        return self.center == other.center and math.isclose(self.radius, other.radius)

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.center, round(self.radius, 9)))


class Cube:
    """Represents a cube in 3D space.

    Examples:
        >>> c = Cube(Point3D(0, 0, 0), 4)
        >>> c.volume()
        64.0
        >>> c.surface_area()
        96.0
    """

    def __init__(self, origin: Point3D, side_length: float) -> None:
        """
        Initialize a cube from origin point and side length.

        Args:
            origin: Origin corner point (minimum x, y, z)
            side_length: Length of each side

        Raises:
            ValueError: If side length is not positive

        Examples:
            >>> c = Cube(Point3D(0, 0, 0), 4)
            >>> c.side_length
            4.0
            >>> Cube(Point3D(0, 0, 0), -1)
            Traceback (most recent call last):
                ...
            ValueError: Side length must be positive
        """
        if side_length <= 0:
            raise ValueError("Side length must be positive")

        self.origin = origin
        self.side_length = float(side_length)

    def volume(self) -> float:
        """Calculate the volume of the cube.

        Examples:
            >>> Cube(Point3D(0, 0, 0), 3).volume()
            27.0
        """
        return self.side_length**3

    def surface_area(self) -> float:
        """Calculate the surface area of the cube.

        Examples:
            >>> Cube(Point3D(0, 0, 0), 3).surface_area()
            54.0
        """
        return 6 * self.side_length**2

    def diagonal_length(self) -> float:
        """Calculate the length of the space diagonal.

        Examples:
            >>> c = Cube(Point3D(0, 0, 0), 1)
            >>> round(c.diagonal_length(), 4)
            1.7321
        """
        return self.side_length * math.sqrt(3)

    def center(self) -> Point3D:
        """Calculate the center point of the cube.

        Examples:
            >>> c = Cube(Point3D(0, 0, 0), 4)
            >>> c.center()
            Point3D(2.0, 2.0, 2.0)
        """
        offset = self.side_length / 2
        return Point3D(self.origin.x + offset, self.origin.y + offset, self.origin.z + offset)

    def vertices(self) -> List[Point3D]:
        """Get all 8 vertices of the cube.

        Returns:
            List of 8 Point3D vertices
        """
        o = self.origin
        s = self.side_length
        return [
            o,
            Point3D(o.x + s, o.y, o.z),
            Point3D(o.x + s, o.y + s, o.z),
            Point3D(o.x, o.y + s, o.z),
            Point3D(o.x, o.y, o.z + s),
            Point3D(o.x + s, o.y, o.z + s),
            Point3D(o.x + s, o.y + s, o.z + s),
            Point3D(o.x, o.y + s, o.z + s),
        ]

    def contains_point(self, point: Point3D) -> bool:
        """
        Check if a point is inside or on the cube.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the cube

        Examples:
            >>> c = Cube(Point3D(0, 0, 0), 4)
            >>> c.contains_point(Point3D(2, 2, 2))
            True
            >>> c.contains_point(Point3D(5, 0, 0))
            False
        """
        return (
            self.origin.x <= point.x <= self.origin.x + self.side_length
            and self.origin.y <= point.y <= self.origin.y + self.side_length
            and self.origin.z <= point.z <= self.origin.z + self.side_length
        )

    def __repr__(self) -> str:
        return f"Cube(origin={self.origin}, side_length={self.side_length})"

    def __str__(self) -> str:
        return f"Cube at {self.origin} with side length {self.side_length}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cube):
            return False
        return self.origin == other.origin and math.isclose(self.side_length, other.side_length)

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.origin, round(self.side_length, 9)))


class RectangularPrism:
    """Represents a rectangular prism (box) in 3D space.

    Examples:
        >>> rp = RectangularPrism(Point3D(0, 0, 0), 4, 3, 2)
        >>> rp.volume()
        24.0
        >>> rp.surface_area()
        52.0
    """

    def __init__(self, origin: Point3D, width: float, height: float, depth: float) -> None:
        """
        Initialize a rectangular prism.

        Args:
            origin: Origin corner point (minimum x, y, z)
            width: Width (x dimension)
            height: Height (y dimension)
            depth: Depth (z dimension)

        Raises:
            ValueError: If any dimension is not positive

        Examples:
            >>> rp = RectangularPrism(Point3D(0, 0, 0), 4, 3, 2)
            >>> (rp.width, rp.height, rp.depth)
            (4.0, 3.0, 2.0)
            >>> RectangularPrism(Point3D(0, 0, 0), -1, 3, 2)
            Traceback (most recent call last):
                ...
            ValueError: Width, height, and depth must be positive
        """
        if width <= 0 or height <= 0 or depth <= 0:
            raise ValueError("Width, height, and depth must be positive")

        self.origin = origin
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)

    def volume(self) -> float:
        """Calculate the volume of the rectangular prism.

        Examples:
            >>> RectangularPrism(Point3D(0, 0, 0), 4, 3, 2).volume()
            24.0
        """
        return self.width * self.height * self.depth

    def surface_area(self) -> float:
        """Calculate the surface area of the rectangular prism.

        Examples:
            >>> RectangularPrism(Point3D(0, 0, 0), 4, 3, 2).surface_area()
            52.0
        """
        return 2 * (self.width * self.height + self.height * self.depth + self.depth * self.width)

    def diagonal_length(self) -> float:
        """Calculate the length of the space diagonal.

        Examples:
            >>> rp = RectangularPrism(Point3D(0, 0, 0), 2, 3, 6)
            >>> rp.diagonal_length()
            7.0
        """
        return math.sqrt(self.width**2 + self.height**2 + self.depth**2)

    def center(self) -> Point3D:
        """Calculate the center point of the rectangular prism.

        Examples:
            >>> rp = RectangularPrism(Point3D(0, 0, 0), 4, 6, 8)
            >>> rp.center()
            Point3D(2.0, 3.0, 4.0)
        """
        return Point3D(
            self.origin.x + self.width / 2,
            self.origin.y + self.height / 2,
            self.origin.z + self.depth / 2,
        )

    def vertices(self) -> List[Point3D]:
        """Get all 8 vertices of the rectangular prism.

        Returns:
            List of 8 Point3D vertices
        """
        o = self.origin
        w, h, d = self.width, self.height, self.depth
        return [
            o,
            Point3D(o.x + w, o.y, o.z),
            Point3D(o.x + w, o.y + h, o.z),
            Point3D(o.x, o.y + h, o.z),
            Point3D(o.x, o.y, o.z + d),
            Point3D(o.x + w, o.y, o.z + d),
            Point3D(o.x + w, o.y + h, o.z + d),
            Point3D(o.x, o.y + h, o.z + d),
        ]

    def contains_point(self, point: Point3D) -> bool:
        """
        Check if a point is inside or on the rectangular prism.

        Args:
            point: Point to check

        Returns:
            True if point is inside or on the prism

        Examples:
            >>> rp = RectangularPrism(Point3D(0, 0, 0), 4, 3, 2)
            >>> rp.contains_point(Point3D(2, 1, 1))
            True
            >>> rp.contains_point(Point3D(5, 0, 0))
            False
        """
        return (
            self.origin.x <= point.x <= self.origin.x + self.width
            and self.origin.y <= point.y <= self.origin.y + self.height
            and self.origin.z <= point.z <= self.origin.z + self.depth
        )

    def __repr__(self) -> str:
        return (
            f"RectangularPrism(origin={self.origin}, width={self.width}, "
            f"height={self.height}, depth={self.depth})"
        )

    def __str__(self) -> str:
        return f"RectangularPrism {self.width}x{self.height}x{self.depth} at {self.origin}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RectangularPrism):
            return False
        return (
            self.origin == other.origin
            and math.isclose(self.width, other.width)
            and math.isclose(self.height, other.height)
            and math.isclose(self.depth, other.depth)
        )

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash(
            (self.origin, round(self.width, 9), round(self.height, 9), round(self.depth, 9))
        )
