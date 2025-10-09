"""Bézier curve classes for 2D geometric operations."""

from typing import Tuple

from geomkit.primitives.point import Point2D


class QuadraticBezier:
    """Represents a quadratic Bézier curve in 2D space.

    A quadratic Bézier curve is defined by 3 control points.

    Examples:
        >>> p0 = Point2D(0, 0)
        >>> p1 = Point2D(1, 2)
        >>> p2 = Point2D(2, 0)
        >>> curve = QuadraticBezier(p0, p1, p2)
        >>> curve.point_at(0.5)
        Point2D(1.0, 1.0)
    """

    def __init__(self, p0: Point2D, p1: Point2D, p2: Point2D) -> None:
        """
        Initialize a quadratic Bézier curve.

        Args:
            p0: Start point
            p1: Control point
            p2: End point

        Examples:
            >>> curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
            >>> curve.p0
            Point2D(0.0, 0.0)
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

    def point_at(self, t: float) -> Point2D:
        """
        Calculate a point on the curve at parameter t.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Point on the curve

        Examples:
            >>> curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
            >>> curve.point_at(0)
            Point2D(0.0, 0.0)
            >>> curve.point_at(1)
            Point2D(2.0, 0.0)
            >>> curve.point_at(0.5)
            Point2D(1.0, 1.0)
        """
        # Quadratic Bézier formula: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
        t2 = t * t
        mt = 1 - t
        mt2 = mt * mt

        x = mt2 * self.p0.x + 2 * mt * t * self.p1.x + t2 * self.p2.x
        y = mt2 * self.p0.y + 2 * mt * t * self.p1.y + t2 * self.p2.y

        return Point2D(x, y)

    def tangent_at(self, t: float) -> Point2D:
        """
        Calculate the tangent vector at parameter t.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Tangent vector at t

        Examples:
            >>> curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
            >>> tangent = curve.tangent_at(0)
            >>> (tangent.x, tangent.y)
            (2.0, 4.0)
        """
        # Derivative: B'(t) = 2(1-t)(P1-P0) + 2t(P2-P1)
        mt = 1 - t

        x = 2 * mt * (self.p1.x - self.p0.x) + 2 * t * (self.p2.x - self.p1.x)
        y = 2 * mt * (self.p1.y - self.p0.y) + 2 * t * (self.p2.y - self.p1.y)

        return Point2D(x, y)

    def split(self, t: float) -> Tuple["QuadraticBezier", "QuadraticBezier"]:
        """
        Split the curve at parameter t into two curves.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Tuple of two QuadraticBezier curves

        Examples:
            >>> curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
            >>> left, right = curve.split(0.5)
            >>> left.p2
            Point2D(1.0, 1.0)
        """
        # Using de Casteljau's algorithm
        q0 = Point2D((1 - t) * self.p0.x + t * self.p1.x, (1 - t) * self.p0.y + t * self.p1.y)
        q1 = Point2D((1 - t) * self.p1.x + t * self.p2.x, (1 - t) * self.p1.y + t * self.p2.y)
        r = Point2D((1 - t) * q0.x + t * q1.x, (1 - t) * q0.y + t * q1.y)

        left = QuadraticBezier(self.p0, q0, r)
        right = QuadraticBezier(r, q1, self.p2)

        return left, right

    def approximate_length(self, num_samples: int = 100) -> float:
        """
        Approximate the length of the curve using linear segments.

        Args:
            num_samples: Number of samples to use

        Returns:
            Approximate curve length

        Examples:
            >>> curve = QuadraticBezier(Point2D(0, 0), Point2D(1, 2), Point2D(2, 0))
            >>> length = curve.approximate_length()
            >>> 2.8 < length < 3.0
            True
        """
        length = 0.0
        prev_point = self.p0

        for i in range(1, num_samples + 1):
            t = i / num_samples
            current_point = self.point_at(t)
            length += prev_point.distance_to(current_point)
            prev_point = current_point

        return length

    def __repr__(self) -> str:
        return f"QuadraticBezier({self.p0}, {self.p1}, {self.p2})"

    def __str__(self) -> str:
        return f"Quadratic Bézier: {self.p0} -> {self.p1} -> {self.p2}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuadraticBezier):
            return False
        return self.p0 == other.p0 and self.p1 == other.p1 and self.p2 == other.p2

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.p0, self.p1, self.p2))


class CubicBezier:
    """Represents a cubic Bézier curve in 2D space.

    A cubic Bézier curve is defined by 4 control points.

    Examples:
        >>> p0 = Point2D(0, 0)
        >>> p1 = Point2D(0, 2)
        >>> p2 = Point2D(2, 2)
        >>> p3 = Point2D(2, 0)
        >>> curve = CubicBezier(p0, p1, p2, p3)
        >>> curve.point_at(0.5)
        Point2D(1.0, 1.5)
    """

    def __init__(self, p0: Point2D, p1: Point2D, p2: Point2D, p3: Point2D) -> None:
        """
        Initialize a cubic Bézier curve.

        Args:
            p0: Start point
            p1: First control point
            p2: Second control point
            p3: End point

        Examples:
            >>> curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
            >>> curve.p0
            Point2D(0.0, 0.0)
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def point_at(self, t: float) -> Point2D:
        """
        Calculate a point on the curve at parameter t.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Point on the curve

        Examples:
            >>> curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
            >>> curve.point_at(0)
            Point2D(0.0, 0.0)
            >>> curve.point_at(1)
            Point2D(2.0, 0.0)
        """
        # Cubic Bézier formula: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt

        x = mt3 * self.p0.x + 3 * mt2 * t * self.p1.x + 3 * mt * t2 * self.p2.x + t3 * self.p3.x

        y = mt3 * self.p0.y + 3 * mt2 * t * self.p1.y + 3 * mt * t2 * self.p2.y + t3 * self.p3.y

        return Point2D(x, y)

    def tangent_at(self, t: float) -> Point2D:
        """
        Calculate the tangent vector at parameter t.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Tangent vector at t

        Examples:
            >>> curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
            >>> tangent = curve.tangent_at(0)
            >>> (tangent.x, tangent.y)
            (0.0, 6.0)
        """
        # Derivative: B'(t) = 3(1-t)²(P1-P0) + 6(1-t)t(P2-P1) + 3t²(P3-P2)
        t2 = t * t
        mt = 1 - t
        mt2 = mt * mt

        x = (
            3 * mt2 * (self.p1.x - self.p0.x)
            + 6 * mt * t * (self.p2.x - self.p1.x)
            + 3 * t2 * (self.p3.x - self.p2.x)
        )

        y = (
            3 * mt2 * (self.p1.y - self.p0.y)
            + 6 * mt * t * (self.p2.y - self.p1.y)
            + 3 * t2 * (self.p3.y - self.p2.y)
        )

        return Point2D(x, y)

    def split(self, t: float) -> Tuple["CubicBezier", "CubicBezier"]:
        """
        Split the curve at parameter t into two curves.

        Args:
            t: Parameter value between 0 and 1

        Returns:
            Tuple of two CubicBezier curves

        Examples:
            >>> curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
            >>> left, right = curve.split(0.5)
            >>> left.p3
            Point2D(1.0, 1.5)
        """
        # Using de Casteljau's algorithm
        q0 = Point2D((1 - t) * self.p0.x + t * self.p1.x, (1 - t) * self.p0.y + t * self.p1.y)
        q1 = Point2D((1 - t) * self.p1.x + t * self.p2.x, (1 - t) * self.p1.y + t * self.p2.y)
        q2 = Point2D((1 - t) * self.p2.x + t * self.p3.x, (1 - t) * self.p2.y + t * self.p3.y)

        r0 = Point2D((1 - t) * q0.x + t * q1.x, (1 - t) * q0.y + t * q1.y)
        r1 = Point2D((1 - t) * q1.x + t * q2.x, (1 - t) * q1.y + t * q2.y)

        s = Point2D((1 - t) * r0.x + t * r1.x, (1 - t) * r0.y + t * r1.y)

        left = CubicBezier(self.p0, q0, r0, s)
        right = CubicBezier(s, r1, q2, self.p3)

        return left, right

    def approximate_length(self, num_samples: int = 100) -> float:
        """
        Approximate the length of the curve using linear segments.

        Args:
            num_samples: Number of samples to use

        Returns:
            Approximate curve length

        Examples:
            >>> curve = CubicBezier(Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0))
            >>> length = curve.approximate_length()
            >>> 3.5 < length < 4.5
            True
        """
        length = 0.0
        prev_point = self.p0

        for i in range(1, num_samples + 1):
            t = i / num_samples
            current_point = self.point_at(t)
            length += prev_point.distance_to(current_point)
            prev_point = current_point

        return length

    def __repr__(self) -> str:
        return f"CubicBezier({self.p0}, {self.p1}, {self.p2}, {self.p3})"

    def __str__(self) -> str:
        return f"Cubic Bézier: {self.p0} -> {self.p1} -> {self.p2} -> {self.p3}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CubicBezier):
            return False
        return (
            self.p0 == other.p0
            and self.p1 == other.p1
            and self.p2 == other.p2
            and self.p3 == other.p3
        )

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash((self.p0, self.p1, self.p2, self.p3))
