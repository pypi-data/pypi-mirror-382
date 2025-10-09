"""Polygon classes for 2D geometric operations."""

import math
from typing import List, Tuple

from geomkit.primitives.point import Point2D


class Polygon:
    """Represents a polygon in 2D space.

    Examples:
        >>> p = Polygon([Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)])
        >>> p.area()
        12.0
        >>> p.perimeter()
        14.0
        >>> p.contains_point(Point2D(2, 1))
        True
    """

    def __init__(self, vertices: List[Point2D]) -> None:
        """
        Initialize a polygon from a list of vertices.

        Args:
            vertices: List of Point2D vertices in order

        Raises:
            ValueError: If fewer than 3 vertices provided

        Examples:
            >>> Polygon([Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)])
            Polygon(3 vertices)
            >>> Polygon([Point2D(0, 0), Point2D(1, 0)])
            Traceback (most recent call last):
                ...
            ValueError: A polygon must have at least 3 vertices
        """
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices")

        self.vertices = vertices

    def perimeter(self) -> float:
        """Calculate the perimeter of the polygon.

        Examples:
            >>> p = Polygon([Point2D(0, 0), Point2D(3, 0), Point2D(3, 4), Point2D(0, 4)])
            >>> p.perimeter()
            14.0
        """
        total = 0.0
        n = len(self.vertices)
        for i in range(n):
            total += self.vertices[i].distance_to(self.vertices[(i + 1) % n])
        return total

    def area(self) -> float:
        """
        Calculate the area of the polygon using the shoelace formula.

        Returns:
            Area of the polygon (always positive)

        Examples:
            >>> p = Polygon([Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)])
            >>> p.area()
            12.0
        """
        n = len(self.vertices)
        area = 0.0

        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y

        return abs(area) / 2.0

    def centroid(self) -> Point2D:
        """
        Calculate the centroid (center of mass) of the polygon.

        Returns:
            Point2D representing the centroid
        """
        n = len(self.vertices)
        cx = sum(v.x for v in self.vertices) / n
        cy = sum(v.y for v in self.vertices) / n
        return Point2D(cx, cy)

    def contains_point(self, point: Point2D) -> bool:
        """
        Check if a point is inside the polygon using ray casting algorithm.

        Args:
            point: Point to check

        Returns:
            True if point is inside the polygon
        """
        n = len(self.vertices)
        inside = False

        j = n - 1
        for i in range(n):
            xi, yi = self.vertices[i].x, self.vertices[i].y
            xj, yj = self.vertices[j].x, self.vertices[j].y

            if ((yi > point.y) != (yj > point.y)) and (
                point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi
            ):
                inside = not inside

            j = i

        return inside

    def is_convex(self) -> bool:
        """
        Check if the polygon is convex.

        Returns:
            True if polygon is convex
        """
        n = len(self.vertices)
        if n < 3:
            return False

        sign = None

        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            p3 = self.vertices[(i + 2) % n]

            # Cross product
            cross = (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)

            if not math.isclose(cross, 0):
                if sign is None:
                    sign = cross > 0
                elif (cross > 0) != sign:
                    return False

        return True

    def __repr__(self) -> str:
        return f"Polygon({len(self.vertices)} vertices)"

    def __str__(self) -> str:
        return f"Polygon with {len(self.vertices)} vertices"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polygon):
            return False
        if len(self.vertices) != len(other.vertices):
            return False
        return all(v1 == v2 for v1, v2 in zip(self.vertices, other.vertices))

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash(tuple(self.vertices))


class Triangle(Polygon):
    """Represents a triangle in 2D space.

    Examples:
        >>> t = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
        >>> t.area()
        6.0
        >>> t.perimeter()
        11.21110255092798
    """

    def __init__(self, p1: Point2D, p2: Point2D, p3: Point2D) -> None:
        """
        Initialize a triangle from three points.

        Args:
            p1: First vertex
            p2: Second vertex
            p3: Third vertex

        Examples:
            >>> t = Triangle(Point2D(0, 0), Point2D(1, 0), Point2D(0, 1))
            >>> t.area()
            0.5
        """
        super().__init__([p1, p2, p3])

    @property
    def a(self) -> Point2D:
        """First vertex."""
        return self.vertices[0]

    @property
    def b(self) -> Point2D:
        """Second vertex."""
        return self.vertices[1]

    @property
    def c(self) -> Point2D:
        """Third vertex."""
        return self.vertices[2]

    def side_lengths(self) -> Tuple[float, float, float]:
        """
        Calculate the lengths of all three sides.

        Returns:
            Tuple of (side_a, side_b, side_c) lengths
        """
        side_a = self.b.distance_to(self.c)
        side_b = self.c.distance_to(self.a)
        side_c = self.a.distance_to(self.b)
        return (side_a, side_b, side_c)

    def angles(self) -> Tuple[float, float, float]:
        """
        Calculate all three angles in radians.

        Returns:
            Tuple of angles at vertices (a, b, c)
        """
        side_a, side_b, side_c = self.side_lengths()

        # Law of cosines: cos(A) = (b² + c² - a²) / (2bc)
        angle_a = math.acos((side_b**2 + side_c**2 - side_a**2) / (2 * side_b * side_c))
        angle_b = math.acos((side_c**2 + side_a**2 - side_b**2) / (2 * side_c * side_a))
        angle_c = math.acos((side_a**2 + side_b**2 - side_c**2) / (2 * side_a * side_b))

        return (angle_a, angle_b, angle_c)

    def is_right_triangle(self, tolerance: float = 1e-9) -> bool:
        """
        Check if the triangle is a right triangle.

        Args:
            tolerance: Tolerance for floating point comparison

        Returns:
            True if triangle is right-angled
        """
        angles = self.angles()
        return any(math.isclose(angle, math.pi / 2, abs_tol=tolerance) for angle in angles)

    def __repr__(self) -> str:
        return f"Triangle({self.a}, {self.b}, {self.c})"

    def __str__(self) -> str:
        return f"Triangle[{self.a}, {self.b}, {self.c}]"


class Rectangle(Polygon):
    """Represents a rectangle in 2D space.

    Examples:
        >>> r = Rectangle(Point2D(0, 0), 4, 3)
        >>> r.area()
        12
        >>> r.diagonal_length()
        5.0
    """

    def __init__(self, bottom_left: Point2D, width: float, height: float) -> None:
        """
        Initialize a rectangle from bottom-left corner and dimensions.

        Args:
            bottom_left: Bottom-left corner point
            width: Width of the rectangle
            height: Height of the rectangle

        Raises:
            ValueError: If width or height is not positive

        Examples:
            >>> Rectangle(Point2D(0, 0), 4, 3)
            Rectangle(width=4, height=3)
            >>> Rectangle(Point2D(0, 0), -1, 3)
            Traceback (most recent call last):
                ...
            ValueError: Width and height must be positive
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")

        # Create vertices in counter-clockwise order
        vertices = [
            bottom_left,
            Point2D(bottom_left.x + width, bottom_left.y),
            Point2D(bottom_left.x + width, bottom_left.y + height),
            Point2D(bottom_left.x, bottom_left.y + height),
        ]
        super().__init__(vertices)

        self.width = width
        self.height = height

    def area(self) -> float:
        """Calculate the area of the rectangle."""
        return self.width * self.height

    def diagonal_length(self) -> float:
        """Calculate the length of the diagonal."""
        return math.sqrt(self.width**2 + self.height**2)

    def __repr__(self) -> str:
        return f"Rectangle(width={self.width}, height={self.height})"

    def __str__(self) -> str:
        return f"Rectangle {self.width}x{self.height}"


class Square(Rectangle):
    """Represents a square in 2D space.

    Examples:
        >>> s = Square(Point2D(0, 0), 5)
        >>> s.area()
        25
        >>> s.perimeter()
        20.0
    """

    def __init__(self, bottom_left: Point2D, side_length: float) -> None:
        """
        Initialize a square from bottom-left corner and side length.

        Args:
            bottom_left: Bottom-left corner point
            side_length: Length of each side

        Raises:
            ValueError: If side length is not positive

        Examples:
            >>> Square(Point2D(0, 0), 5)
            Square(side_length=5)
            >>> Square(Point2D(0, 0), 0)
            Traceback (most recent call last):
                ...
            ValueError: Width and height must be positive
        """
        super().__init__(bottom_left, side_length, side_length)
        self.side_length = side_length

    def __repr__(self) -> str:
        return f"Square(side_length={self.side_length})"

    def __str__(self) -> str:
        return f"Square {self.side_length}x{self.side_length}"


class RegularPolygon(Polygon):
    """Represents a regular polygon (all sides and angles equal) in 2D space.

    Examples:
        >>> hexagon = RegularPolygon(Point2D(0, 0), 6, 5)
        >>> round(hexagon.area(), 2)
        64.95
        >>> round(hexagon.interior_angle() * 180 / 3.14159, 1)
        120.0
    """

    def __init__(self, center: Point2D, num_sides: int, radius: float, rotation: float = 0) -> None:
        """
        Initialize a regular polygon.

        Args:
            center: Center point of the polygon
            num_sides: Number of sides (must be >= 3)
            radius: Distance from center to vertices (circumradius)
            rotation: Rotation angle in radians (default 0)

        Raises:
            ValueError: If num_sides < 3 or radius <= 0

        Examples:
            >>> RegularPolygon(Point2D(0, 0), 6, 5)
            RegularPolygon(6 sides, radius=5.0)
            >>> RegularPolygon(Point2D(0, 0), 2, 5)
            Traceback (most recent call last):
                ...
            ValueError: Regular polygon must have at least 3 sides
            >>> RegularPolygon(Point2D(0, 0), 6, -5)
            Traceback (most recent call last):
                ...
            ValueError: Radius must be positive
        """
        if num_sides < 3:
            raise ValueError("Regular polygon must have at least 3 sides")
        if radius <= 0:
            raise ValueError("Radius must be positive")

        self.center_point = center
        self.num_sides = num_sides
        self.radius = float(radius)
        self.rotation_angle = float(rotation)

        # Generate vertices
        vertices = []
        angle_step = 2 * math.pi / num_sides

        for i in range(num_sides):
            angle = rotation + i * angle_step
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            vertices.append(Point2D(x, y))

        super().__init__(vertices)

    def side_length(self) -> float:
        """
        Calculate the length of each side.

        Returns:
            Length of one side
        """
        return self.vertices[0].distance_to(self.vertices[1])

    def apothem(self) -> float:
        """
        Calculate the apothem (distance from center to midpoint of a side).

        Returns:
            Apothem length
        """
        return self.radius * math.cos(math.pi / self.num_sides)

    def interior_angle(self) -> float:
        """
        Calculate the interior angle in radians.

        Returns:
            Interior angle in radians
        """
        return (self.num_sides - 2) * math.pi / self.num_sides

    def exterior_angle(self) -> float:
        """
        Calculate the exterior angle in radians.

        Returns:
            Exterior angle in radians
        """
        return 2 * math.pi / self.num_sides

    def area(self) -> float:
        """
        Calculate the area of the regular polygon.

        Returns:
            Area
        """
        return (self.num_sides * self.radius**2 * math.sin(2 * math.pi / self.num_sides)) / 2

    def perimeter(self) -> float:
        """
        Calculate the perimeter of the regular polygon.

        Returns:
            Perimeter
        """
        return self.num_sides * self.side_length()

    def __repr__(self) -> str:
        return f"RegularPolygon({self.num_sides} sides, radius={self.radius})"

    def __str__(self) -> str:
        return f"Regular {self.num_sides}-gon with radius {self.radius}"
