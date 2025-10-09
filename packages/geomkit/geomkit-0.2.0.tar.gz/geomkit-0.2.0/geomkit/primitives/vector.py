"""Vector classes for 2D and 3D geometric operations."""

import math


class Vector2D:
    """Represents a 2D vector.

    Examples:
        >>> v1 = Vector2D(3, 4)
        >>> v1.magnitude()
        5.0
        >>> v1.normalize()
        Vector2D(0.6, 0.8)
        >>> v2 = Vector2D(1, 0)
        >>> v1.dot(v2)
        3.0
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialize a 2D vector.

        Args:
            x: X component
            y: Y component

        Examples:
            >>> v = Vector2D(3, 4)
            >>> (v.x, v.y)
            (3.0, 4.0)
        """
        self.x = float(x)
        self.y = float(y)

    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the vector.

        Examples:
            >>> Vector2D(3, 4).magnitude()
            5.0
            >>> Vector2D(0, 0).magnitude()
            0.0
        """
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2D":
        """
        Return a normalized (unit) vector.

        Returns:
            A new Vector2D with magnitude 1

        Raises:
            ValueError: If vector has zero magnitude

        Examples:
            >>> v = Vector2D(3, 4)
            >>> n = v.normalize()
            >>> abs(n.magnitude() - 1.0) < 1e-10
            True
            >>> Vector2D(0, 0).normalize()
            Traceback (most recent call last):
                ...
            ValueError: Cannot normalize a zero vector
        """
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector")
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: "Vector2D") -> float:
        """
        Calculate dot product with another vector.

        Args:
            other: Another Vector2D instance

        Returns:
            Dot product value

        Examples:
            >>> Vector2D(1, 0).dot(Vector2D(0, 1))
            0.0
            >>> Vector2D(3, 4).dot(Vector2D(1, 0))
            3.0
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vector2D") -> float:
        """
        Calculate cross product magnitude with another vector.

        Args:
            other: Another Vector2D instance

        Returns:
            Magnitude of cross product (scalar for 2D)
        """
        return self.x * other.y - self.y * other.x

    def angle_to(self, other: "Vector2D") -> float:
        """
        Calculate angle to another vector in radians.

        Args:
            other: Another Vector2D instance

        Returns:
            Angle in radians
        """
        dot_product = self.dot(other)
        magnitudes = self.magnitude() * other.magnitude()
        if magnitudes == 0:
            return 0.0
        return math.acos(max(-1, min(1, dot_product / magnitudes)))

    def rotate(self, angle: float) -> "Vector2D":
        """
        Rotate vector by given angle (in radians).

        Args:
            angle: Rotation angle in radians

        Returns:
            A new rotated Vector2D
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(self.x * cos_a - self.y * sin_a, self.x * sin_a + self.y * cos_a)

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"<{self.x}, {self.y}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __hash__(self) -> int:
        """
        Return hash value for use in sets and as dict keys.

        Note: Since we use floating point comparison with tolerance in __eq__,
        this hash is based on rounded values to maintain hash consistency.
        """
        return hash((round(self.x, 9), round(self.y, 9)))

    def __add__(self, other: "Vector2D") -> "Vector2D":
        """Add two vectors."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        """Subtract two vectors."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        """Multiply vector by scalar."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2D":
        """Multiply vector by scalar (reverse)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector2D":
        """Divide vector by scalar."""
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vector2D":
        """Negate vector."""
        return Vector2D(-self.x, -self.y)


class Vector3D:
    """Represents a 3D vector.

    Examples:
        >>> v = Vector3D(1, 2, 2)
        >>> v.magnitude()
        3.0
        >>> v1 = Vector3D(1, 0, 0)
        >>> v2 = Vector3D(0, 1, 0)
        >>> v1.cross(v2)
        Vector3D(0.0, 0.0, 1.0)
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        """
        Initialize a 3D vector.

        Args:
            x: X component
            y: Y component
            z: Z component

        Examples:
            >>> v = Vector3D(1, 2, 3)
            >>> (v.x, v.y, v.z)
            (1.0, 2.0, 3.0)
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def magnitude(self) -> float:
        """Calculate the magnitude (length) of the vector.

        Examples:
            >>> Vector3D(1, 2, 2).magnitude()
            3.0
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        """
        Return a normalized (unit) vector.

        Returns:
            A new Vector3D with magnitude 1

        Raises:
            ValueError: If vector has zero magnitude

        Examples:
            >>> v = Vector3D(3, 4, 0)
            >>> n = v.normalize()
            >>> abs(n.magnitude() - 1.0) < 1e-10
            True
        """
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector")
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: "Vector3D") -> float:
        """
        Calculate dot product with another vector.

        Args:
            other: Another Vector3D instance

        Returns:
            Dot product value
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3D") -> "Vector3D":
        """
        Calculate cross product with another vector.

        Args:
            other: Another Vector3D instance

        Returns:
            A new Vector3D representing the cross product
        """
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def angle_to(self, other: "Vector3D") -> float:
        """
        Calculate angle to another vector in radians.

        Args:
            other: Another Vector3D instance

        Returns:
            Angle in radians
        """
        dot_product = self.dot(other)
        magnitudes = self.magnitude() * other.magnitude()
        if magnitudes == 0:
            return 0.0
        return math.acos(max(-1, min(1, dot_product / magnitudes)))

    def __repr__(self) -> str:
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"<{self.x}, {self.y}, {self.z}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3D):
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

    def __add__(self, other: "Vector3D") -> "Vector3D":
        """Add two vectors."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        """Subtract two vectors."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        """Multiply vector by scalar."""
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vector3D":
        """Multiply vector by scalar (reverse)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector3D":
        """Divide vector by scalar."""
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> "Vector3D":
        """Negate vector."""
        return Vector3D(-self.x, -self.y, -self.z)
