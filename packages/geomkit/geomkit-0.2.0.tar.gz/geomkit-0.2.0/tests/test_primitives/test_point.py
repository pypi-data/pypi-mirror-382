"""Test cases for Point2D and Point3D classes using pytest."""

import math

from geomkit import Point2D, Point3D


class TestPoint2D:
    """Test cases for Point2D class."""

    def test_initialization(self):
        """Test point initialization."""
        p = Point2D(3, 4)
        assert p.x == 3.0
        assert p.y == 4.0

    def test_distance_to(self):
        """Test distance calculation between points."""
        p1 = Point2D(0, 0)
        p2 = Point2D(3, 4)
        assert p1.distance_to(p2) == 5.0

    def test_distance_to_same_point(self):
        """Test distance to same point is zero."""
        p = Point2D(5, 5)
        assert p.distance_to(p) == 0.0

    def test_midpoint(self):
        """Test midpoint calculation."""
        p1 = Point2D(0, 0)
        p2 = Point2D(4, 6)
        mid = p1.midpoint(p2)
        assert mid.x == 2.0
        assert mid.y == 3.0

    def test_translate(self):
        """Test point translation."""
        p = Point2D(1, 2)
        translated = p.translate(3, 4)
        assert translated.x == 4.0
        assert translated.y == 6.0

    def test_rotate_90_degrees(self):
        """Test point rotation by 90 degrees."""
        p = Point2D(1, 0)
        rotated = p.rotate(math.pi / 2)
        assert math.isclose(rotated.x, 0.0, abs_tol=1e-10)
        assert math.isclose(rotated.y, 1.0, abs_tol=1e-10)

    def test_rotate_around_custom_origin(self):
        """Test rotation around custom origin."""
        p = Point2D(2, 1)
        origin = Point2D(1, 1)
        rotated = p.rotate(math.pi / 2, origin)
        assert math.isclose(rotated.x, 1.0, abs_tol=1e-10)
        assert math.isclose(rotated.y, 2.0, abs_tol=1e-10)

    def test_to_tuple(self):
        """Test conversion to tuple."""
        p = Point2D(3, 4)
        assert p.to_tuple() == (3.0, 4.0)

    def test_equality(self):
        """Test point equality."""
        p1 = Point2D(3, 4)
        p2 = Point2D(3, 4)
        p3 = Point2D(3.0, 4.0)
        assert p1 == p2
        assert p1 == p3

    def test_inequality(self):
        """Test point inequality."""
        p1 = Point2D(3, 4)
        p2 = Point2D(4, 3)
        assert p1 != p2

    def test_addition(self):
        """Test point addition."""
        p1 = Point2D(1, 2)
        p2 = Point2D(3, 4)
        result = p1 + p2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_subtraction(self):
        """Test point subtraction."""
        p1 = Point2D(5, 7)
        p2 = Point2D(2, 3)
        result = p1 - p2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_repr(self):
        """Test string representation."""
        p = Point2D(3, 4)
        assert repr(p) == "Point2D(3.0, 4.0)"


class TestPoint3D:
    """Test cases for Point3D class."""

    def test_initialization(self):
        """Test 3D point initialization."""
        p = Point3D(1, 2, 3)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_distance_to(self):
        """Test 3D distance calculation."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(1, 2, 2)
        assert p1.distance_to(p2) == 3.0

    def test_midpoint(self):
        """Test 3D midpoint calculation."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(4, 6, 8)
        mid = p1.midpoint(p2)
        assert mid.x == 2.0
        assert mid.y == 3.0
        assert mid.z == 4.0

    def test_translate(self):
        """Test 3D point translation."""
        p = Point3D(1, 2, 3)
        translated = p.translate(1, 1, 1)
        assert translated.x == 2.0
        assert translated.y == 3.0
        assert translated.z == 4.0

    def test_to_tuple(self):
        """Test 3D conversion to tuple."""
        p = Point3D(1, 2, 3)
        assert p.to_tuple() == (1.0, 2.0, 3.0)

    def test_equality(self):
        """Test 3D point equality."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(1, 2, 3)
        assert p1 == p2

    def test_addition(self):
        """Test 3D point addition."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(4, 5, 6)
        result = p1 + p2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

    def test_subtraction(self):
        """Test 3D point subtraction."""
        p1 = Point3D(5, 7, 9)
        p2 = Point3D(2, 3, 4)
        result = p1 - p2
        assert result.x == 3.0
        assert result.y == 4.0
        assert result.z == 5.0

    def test_repr(self):
        """Test 3D string representation."""
        p = Point3D(1, 2, 3)
        assert repr(p) == "Point3D(1.0, 2.0, 3.0)"
