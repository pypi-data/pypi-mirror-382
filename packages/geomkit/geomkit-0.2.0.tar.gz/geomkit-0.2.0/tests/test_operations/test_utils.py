"""Test cases for utility functions using pytest."""

import math

import pytest

from geomkit import Point2D, Point3D, Vector2D, Vector3D
from geomkit.operations.utils import (
    angle_between,
    collinear,
    degrees_to_radians,
    distance,
    lerp,
    radians_to_degrees,
    triangle_area,
)


class TestDistance:
    """Test cases for distance function."""

    def test_distance_2d_points(self):
        """Test distance between 2D points."""
        p1 = Point2D(0, 0)
        p2 = Point2D(3, 4)
        assert distance(p1, p2) == 5.0

    def test_distance_3d_points(self):
        """Test distance between 3D points."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(1, 2, 2)
        assert distance(p1, p2) == 3.0

    def test_distance_same_point(self):
        """Test distance to same point."""
        p = Point2D(5, 5)
        assert distance(p, p) == 0.0

    def test_distance_mixed_dimensions_raises_error(self):
        """Test that mixing 2D and 3D raises error."""
        p1 = Point2D(0, 0)
        p2 = Point3D(0, 0, 0)
        with pytest.raises(TypeError):
            distance(p1, p2)


class TestAngleBetween:
    """Test cases for angle_between function."""

    def test_angle_between_2d_vectors_radians(self):
        """Test angle between 2D vectors in radians."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        angle = angle_between(v1, v2)
        assert math.isclose(angle, math.pi / 2)

    def test_angle_between_2d_vectors_degrees(self):
        """Test angle between 2D vectors in degrees."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        angle = angle_between(v1, v2, degrees=True)
        assert math.isclose(angle, 90.0)

    def test_angle_between_3d_vectors(self):
        """Test angle between 3D vectors."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        angle = angle_between(v1, v2)
        assert math.isclose(angle, math.pi / 2)

    def test_angle_between_parallel_vectors(self):
        """Test angle between parallel vectors."""
        v1 = Vector2D(1, 1)
        v2 = Vector2D(2, 2)
        angle = angle_between(v1, v2)
        assert math.isclose(angle, 0.0, abs_tol=1e-7)

    def test_angle_between_opposite_vectors(self):
        """Test angle between opposite vectors."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(-1, 0)
        angle = angle_between(v1, v2)
        assert math.isclose(angle, math.pi)

    def test_angle_between_mixed_dimensions_raises_error(self):
        """Test that mixing 2D and 3D raises error."""
        v1 = Vector2D(1, 0)
        v2 = Vector3D(1, 0, 0)
        with pytest.raises(TypeError):
            angle_between(v1, v2)


class TestCollinear:
    """Test cases for collinear function."""

    def test_collinear_points_true(self):
        """Test collinear points on line."""
        p1 = Point2D(0, 0)
        p2 = Point2D(1, 1)
        p3 = Point2D(2, 2)
        assert collinear(p1, p2, p3) is True

    def test_collinear_points_false(self):
        """Test non-collinear points."""
        p1 = Point2D(0, 0)
        p2 = Point2D(1, 1)
        p3 = Point2D(1, 2)
        assert collinear(p1, p2, p3) is False

    def test_collinear_horizontal_line(self):
        """Test collinear points on horizontal line."""
        p1 = Point2D(0, 5)
        p2 = Point2D(3, 5)
        p3 = Point2D(7, 5)
        assert collinear(p1, p2, p3) is True

    def test_collinear_vertical_line(self):
        """Test collinear points on vertical line."""
        p1 = Point2D(3, 0)
        p2 = Point2D(3, 5)
        p3 = Point2D(3, 10)
        assert collinear(p1, p2, p3) is True


class TestTriangleArea:
    """Test cases for triangle_area function."""

    def test_triangle_area_right_triangle(self):
        """Test area of right triangle."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 0)
        p3 = Point2D(0, 3)
        assert triangle_area(p1, p2, p3) == 6.0

    def test_triangle_area_general_triangle(self):
        """Test area of general triangle."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 0)
        p3 = Point2D(2, 3)
        assert triangle_area(p1, p2, p3) == 6.0

    def test_triangle_area_zero_for_collinear(self):
        """Test area is zero for collinear points."""
        p1 = Point2D(0, 0)
        p2 = Point2D(1, 1)
        p3 = Point2D(2, 2)
        assert math.isclose(triangle_area(p1, p2, p3), 0.0)

    def test_triangle_area_negative_coordinates(self):
        """Test area with negative coordinates."""
        p1 = Point2D(-2, -1)
        p2 = Point2D(2, -1)
        p3 = Point2D(0, 2)
        assert triangle_area(p1, p2, p3) == 6.0


class TestLerp:
    """Test cases for lerp (linear interpolation) function."""

    def test_lerp_at_start(self):
        """Test interpolation at t=0."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 6)
        result = lerp(p1, p2, 0)
        assert result == p1

    def test_lerp_at_end(self):
        """Test interpolation at t=1."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 6)
        result = lerp(p1, p2, 1)
        assert result == p2

    def test_lerp_at_midpoint(self):
        """Test interpolation at t=0.5 (midpoint)."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 6)
        result = lerp(p1, p2, 0.5)
        assert result.x == 2.0
        assert result.y == 3.0

    def test_lerp_quarter_point(self):
        """Test interpolation at t=0.25."""
        p1 = Point2D(0, 0)
        p2 = Point2D(8, 4)
        result = lerp(p1, p2, 0.25)
        assert result.x == 2.0
        assert result.y == 1.0

    def test_lerp_beyond_range(self):
        """Test interpolation with t > 1 (extrapolation)."""
        p1 = Point2D(0, 0)
        p2 = Point2D(2, 2)
        result = lerp(p1, p2, 2.0)
        assert result.x == 4.0
        assert result.y == 4.0


class TestAngleConversions:
    """Test cases for angle conversion functions."""

    def test_degrees_to_radians(self):
        """Test degrees to radians conversion."""
        assert math.isclose(degrees_to_radians(0), 0.0)
        assert math.isclose(degrees_to_radians(90), math.pi / 2)
        assert math.isclose(degrees_to_radians(180), math.pi)
        assert math.isclose(degrees_to_radians(360), 2 * math.pi)

    def test_radians_to_degrees(self):
        """Test radians to degrees conversion."""
        assert math.isclose(radians_to_degrees(0), 0.0)
        assert math.isclose(radians_to_degrees(math.pi / 2), 90.0)
        assert math.isclose(radians_to_degrees(math.pi), 180.0)
        assert math.isclose(radians_to_degrees(2 * math.pi), 360.0)

    def test_round_trip_conversion(self):
        """Test round-trip conversion."""
        original = 45.0
        radians = degrees_to_radians(original)
        back_to_degrees = radians_to_degrees(radians)
        assert math.isclose(original, back_to_degrees)

    def test_negative_angles(self):
        """Test conversion with negative angles."""
        assert math.isclose(degrees_to_radians(-90), -math.pi / 2)
        assert math.isclose(radians_to_degrees(-math.pi), -180.0)
