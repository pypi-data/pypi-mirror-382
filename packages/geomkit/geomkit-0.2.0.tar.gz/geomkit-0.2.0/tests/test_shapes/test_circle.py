"""Test cases for Circle and Ellipse classes using pytest."""

import math

import pytest

from geomkit import Circle, Ellipse, Point2D


class TestCircle:
    """Test cases for Circle class."""

    def test_initialization(self):
        """Test circle initialization."""
        center = Point2D(0, 0)
        circle = Circle(center, 5)
        assert circle.center == center
        assert circle.radius == 5.0

    def test_initialization_negative_radius_raises_error(self):
        """Test that negative radius raises error."""
        with pytest.raises(ValueError):
            Circle(Point2D(0, 0), -5)

    def test_initialization_zero_radius_raises_error(self):
        """Test that zero radius raises error."""
        with pytest.raises(ValueError):
            Circle(Point2D(0, 0), 0)

    def test_area(self):
        """Test area calculation."""
        circle = Circle(Point2D(0, 0), 5)
        expected_area = math.pi * 25
        assert math.isclose(circle.area(), expected_area)

    def test_circumference(self):
        """Test circumference calculation."""
        circle = Circle(Point2D(0, 0), 5)
        expected_circumference = 2 * math.pi * 5
        assert math.isclose(circle.circumference(), expected_circumference)

    def test_contains_point_inside(self):
        """Test point inside circle."""
        circle = Circle(Point2D(0, 0), 5)
        assert circle.contains_point(Point2D(3, 4)) is True

    def test_contains_point_on_edge(self):
        """Test point on circle edge."""
        circle = Circle(Point2D(0, 0), 5)
        assert circle.contains_point(Point2D(5, 0)) is True

    def test_contains_point_outside(self):
        """Test point outside circle."""
        circle = Circle(Point2D(0, 0), 5)
        assert circle.contains_point(Point2D(6, 0)) is False

    def test_point_on_circle(self):
        """Test getting point on circle at angle."""
        circle = Circle(Point2D(0, 0), 5)
        point = circle.point_on_circle(0)
        assert math.isclose(point.x, 5.0)
        assert math.isclose(point.y, 0.0)

    def test_point_on_circle_90_degrees(self):
        """Test point at 90 degrees."""
        circle = Circle(Point2D(0, 0), 5)
        point = circle.point_on_circle(math.pi / 2)
        assert math.isclose(point.x, 0.0, abs_tol=1e-10)
        assert math.isclose(point.y, 5.0)

    def test_intersects_circle_true(self):
        """Test circles that intersect."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(8, 0), 5)
        assert circle1.intersects_circle(circle2) is True

    def test_intersects_circle_false(self):
        """Test circles that don't intersect."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(20, 0), 5)
        assert circle1.intersects_circle(circle2) is False

    def test_intersects_circle_touching(self):
        """Test circles that touch at one point."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(10, 0), 5)
        assert circle1.intersects_circle(circle2) is True

    def test_intersection_points_two_points(self):
        """Test two intersection points."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(8, 0), 5)
        points = circle1.intersection_points(circle2)
        assert len(points) == 2

    def test_intersection_points_one_point(self):
        """Test one intersection point (touching)."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(10, 0), 5)
        points = circle1.intersection_points(circle2)
        assert len(points) == 1
        assert math.isclose(points[0].x, 5.0)
        assert math.isclose(points[0].y, 0.0)

    def test_intersection_points_no_intersection(self):
        """Test no intersection points."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(20, 0), 5)
        points = circle1.intersection_points(circle2)
        assert len(points) == 0

    def test_tangent_points_from_external_point(self):
        """Test tangent points from external point."""
        circle = Circle(Point2D(0, 0), 5)
        point = Point2D(10, 0)
        tangents = circle.tangent_points_from_point(point)
        assert len(tangents) == 2

    def test_tangent_points_from_internal_point(self):
        """Test no tangent points from internal point."""
        circle = Circle(Point2D(0, 0), 5)
        point = Point2D(2, 0)
        tangents = circle.tangent_points_from_point(point)
        assert len(tangents) == 0

    def test_equality(self):
        """Test circle equality."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(0, 0), 5)
        assert circle1 == circle2

    def test_inequality_different_center(self):
        """Test circles with different centers."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(1, 1), 5)
        assert circle1 != circle2

    def test_inequality_different_radius(self):
        """Test circles with different radii."""
        circle1 = Circle(Point2D(0, 0), 5)
        circle2 = Circle(Point2D(0, 0), 6)
        assert circle1 != circle2

    def test_repr(self):
        """Test string representation."""
        circle = Circle(Point2D(0, 0), 5)
        assert "Circle" in repr(circle)


class TestEllipse:
    """Test cases for Ellipse class."""

    def test_initialization(self):
        """Test ellipse initialization."""
        center = Point2D(0, 0)
        ellipse = Ellipse(center, 5, 3)
        assert ellipse.center == center
        assert ellipse.semi_major_axis == 5.0
        assert ellipse.semi_minor_axis == 3.0
        assert ellipse.rotation == 0.0

    def test_initialization_with_rotation(self):
        """Test ellipse initialization with rotation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3, math.pi / 4)
        assert math.isclose(ellipse.rotation, math.pi / 4)

    def test_initialization_negative_axis_raises_error(self):
        """Test that negative axis raises error."""
        with pytest.raises(ValueError):
            Ellipse(Point2D(0, 0), -5, 3)

    def test_area(self):
        """Test ellipse area calculation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        expected_area = math.pi * 5 * 3
        assert math.isclose(ellipse.area(), expected_area)

    def test_perimeter(self):
        """Test ellipse perimeter (approximate)."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        perimeter = ellipse.perimeter()
        assert perimeter > 0
        # Ramanujan's approximation should be close
        assert 20 < perimeter < 30

    def test_eccentricity(self):
        """Test eccentricity calculation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        ecc = ellipse.eccentricity()
        expected = math.sqrt(1 - (3**2) / (5**2))
        assert math.isclose(ecc, expected)

    def test_eccentricity_circle(self):
        """Test eccentricity of circle (should be 0)."""
        ellipse = Ellipse(Point2D(0, 0), 5, 5)
        assert math.isclose(ellipse.eccentricity(), 0.0)

    def test_contains_point_inside(self):
        """Test point inside ellipse."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        assert ellipse.contains_point(Point2D(2, 1)) is True

    def test_contains_point_outside(self):
        """Test point outside ellipse."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        assert ellipse.contains_point(Point2D(6, 0)) is False

    def test_contains_point_on_edge(self):
        """Test point on ellipse edge."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        assert ellipse.contains_point(Point2D(5, 0)) is True

    def test_point_on_ellipse(self):
        """Test getting point on ellipse."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        point = ellipse.point_on_ellipse(0)
        assert math.isclose(point.x, 5.0)
        assert math.isclose(point.y, 0.0)

    def test_point_on_ellipse_90_degrees(self):
        """Test point at 90 degrees."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        point = ellipse.point_on_ellipse(math.pi / 2)
        assert math.isclose(point.x, 0.0, abs_tol=1e-10)
        assert math.isclose(point.y, 3.0)

    def test_focal_points(self):
        """Test focal points calculation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        f1, f2 = ellipse.focal_points()
        # Distance from center to focus
        c = math.sqrt(5**2 - 3**2)
        assert math.isclose(f1.x, c)
        assert math.isclose(f1.y, 0.0)
        assert math.isclose(f2.x, -c)
        assert math.isclose(f2.y, 0.0)

    def test_focal_points_with_rotation(self):
        """Test focal points with rotation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3, math.pi / 2)
        f1, f2 = ellipse.focal_points()
        # Focal points should be rotated 90 degrees
        c = math.sqrt(5**2 - 3**2)
        assert math.isclose(f1.x, 0.0, abs_tol=1e-10)
        assert math.isclose(abs(f1.y), c)

    def test_equality(self):
        """Test ellipse equality."""
        ellipse1 = Ellipse(Point2D(0, 0), 5, 3)
        ellipse2 = Ellipse(Point2D(0, 0), 5, 3)
        assert ellipse1 == ellipse2

    def test_inequality(self):
        """Test ellipse inequality."""
        ellipse1 = Ellipse(Point2D(0, 0), 5, 3)
        ellipse2 = Ellipse(Point2D(0, 0), 6, 3)
        assert ellipse1 != ellipse2

    def test_repr(self):
        """Test string representation."""
        ellipse = Ellipse(Point2D(0, 0), 5, 3)
        assert "Ellipse" in repr(ellipse)
