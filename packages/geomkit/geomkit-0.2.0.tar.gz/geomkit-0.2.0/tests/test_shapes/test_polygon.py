"""Test cases for Polygon, Triangle, Rectangle, Square, and RegularPolygon classes using pytest."""

import math

import pytest

from geomkit import Point2D, Polygon, Rectangle, RegularPolygon, Square, Triangle


class TestPolygon:
    """Test cases for Polygon class."""

    def test_initialization(self):
        """Test polygon initialization."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert len(polygon.vertices) == 4

    def test_initialization_too_few_vertices_raises_error(self):
        """Test that fewer than 3 vertices raises error."""
        with pytest.raises(ValueError):
            Polygon([Point2D(0, 0), Point2D(1, 1)])

    def test_perimeter(self):
        """Test perimeter calculation."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.perimeter() == 14.0

    def test_area_rectangle(self):
        """Test area calculation for rectangle."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.area() == 12.0

    def test_area_triangle(self):
        """Test area calculation for triangle."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)]
        polygon = Polygon(vertices)
        assert polygon.area() == 6.0

    def test_centroid(self):
        """Test centroid calculation."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
        polygon = Polygon(vertices)
        centroid = polygon.centroid()
        assert centroid.x == 2.0
        assert centroid.y == 2.0

    def test_contains_point_inside(self):
        """Test point inside polygon."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.contains_point(Point2D(2, 1)) is True

    def test_contains_point_outside(self):
        """Test point outside polygon."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.contains_point(Point2D(5, 5)) is False

    def test_is_convex_true(self):
        """Test convex polygon detection."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.is_convex() is True

    def test_is_convex_false(self):
        """Test concave polygon detection."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(2, 1), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert polygon.is_convex() is False

    def test_repr(self):
        """Test string representation."""
        vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)]
        polygon = Polygon(vertices)
        assert "4 vertices" in repr(polygon)


class TestTriangle:
    """Test cases for Triangle class."""

    def test_initialization(self):
        """Test triangle initialization."""
        triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
        assert len(triangle.vertices) == 3

    def test_vertex_properties(self):
        """Test vertex properties."""
        p1, p2, p3 = Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)
        triangle = Triangle(p1, p2, p3)
        assert triangle.a == p1
        assert triangle.b == p2
        assert triangle.c == p3

    def test_side_lengths(self):
        """Test side length calculation."""
        triangle = Triangle(Point2D(0, 0), Point2D(3, 0), Point2D(0, 4))
        sides = triangle.side_lengths()
        assert sides[0] == 5.0  # Hypotenuse
        assert sides[1] == 4.0
        assert sides[2] == 3.0

    def test_angles(self):
        """Test angle calculation."""
        triangle = Triangle(Point2D(0, 0), Point2D(3, 0), Point2D(0, 4))
        angles = triangle.angles()
        # Should have a right angle
        assert any(math.isclose(angle, math.pi / 2, abs_tol=1e-9) for angle in angles)

    def test_is_right_triangle_true(self):
        """Test right triangle detection."""
        triangle = Triangle(Point2D(0, 0), Point2D(3, 0), Point2D(0, 4))
        assert triangle.is_right_triangle() is True

    def test_is_right_triangle_false(self):
        """Test non-right triangle."""
        triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
        assert triangle.is_right_triangle() is False

    def test_area(self):
        """Test triangle area."""
        triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
        assert triangle.area() == 6.0

    def test_repr(self):
        """Test string representation."""
        triangle = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))
        assert "Triangle" in repr(triangle)


class TestRectangle:
    """Test cases for Rectangle class."""

    def test_initialization(self):
        """Test rectangle initialization."""
        rect = Rectangle(Point2D(0, 0), 4, 3)
        assert rect.width == 4.0
        assert rect.height == 3.0

    def test_initialization_negative_width_raises_error(self):
        """Test that negative width raises error."""
        with pytest.raises(ValueError):
            Rectangle(Point2D(0, 0), -4, 3)

    def test_initialization_zero_height_raises_error(self):
        """Test that zero height raises error."""
        with pytest.raises(ValueError):
            Rectangle(Point2D(0, 0), 4, 0)

    def test_vertices(self):
        """Test rectangle vertices."""
        rect = Rectangle(Point2D(0, 0), 4, 3)
        assert len(rect.vertices) == 4

    def test_area(self):
        """Test rectangle area."""
        rect = Rectangle(Point2D(0, 0), 4, 3)
        assert rect.area() == 12.0

    def test_perimeter(self):
        """Test rectangle perimeter."""
        rect = Rectangle(Point2D(0, 0), 4, 3)
        assert rect.perimeter() == 14.0

    def test_diagonal_length(self):
        """Test diagonal length calculation."""
        rect = Rectangle(Point2D(0, 0), 3, 4)
        assert rect.diagonal_length() == 5.0

    def test_centroid(self):
        """Test rectangle centroid."""
        rect = Rectangle(Point2D(0, 0), 4, 6)
        centroid = rect.centroid()
        assert centroid.x == 2.0
        assert centroid.y == 3.0

    def test_repr(self):
        """Test string representation."""
        rect = Rectangle(Point2D(0, 0), 4, 3)
        assert "Rectangle" in repr(rect)


class TestSquare:
    """Test cases for Square class."""

    def test_initialization(self):
        """Test square initialization."""
        square = Square(Point2D(0, 0), 5)
        assert square.side_length == 5.0
        assert square.width == 5.0
        assert square.height == 5.0

    def test_initialization_negative_side_raises_error(self):
        """Test that negative side length raises error."""
        with pytest.raises(ValueError):
            Square(Point2D(0, 0), -5)

    def test_area(self):
        """Test square area."""
        square = Square(Point2D(0, 0), 5)
        assert square.area() == 25.0

    def test_perimeter(self):
        """Test square perimeter."""
        square = Square(Point2D(0, 0), 5)
        assert square.perimeter() == 20.0

    def test_diagonal_length(self):
        """Test square diagonal."""
        square = Square(Point2D(0, 0), 5)
        expected = 5 * math.sqrt(2)
        assert math.isclose(square.diagonal_length(), expected)

    def test_repr(self):
        """Test string representation."""
        square = Square(Point2D(0, 0), 5)
        assert "Square" in repr(square)


class TestRegularPolygon:
    """Test cases for RegularPolygon class."""

    def test_initialization(self):
        """Test regular polygon initialization."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        assert polygon.num_sides == 6
        assert polygon.radius == 5.0
        assert len(polygon.vertices) == 6

    def test_initialization_too_few_sides_raises_error(self):
        """Test that fewer than 3 sides raises error."""
        with pytest.raises(ValueError):
            RegularPolygon(Point2D(0, 0), 2, 5)

    def test_initialization_negative_radius_raises_error(self):
        """Test that negative radius raises error."""
        with pytest.raises(ValueError):
            RegularPolygon(Point2D(0, 0), 6, -5)

    def test_side_length(self):
        """Test side length calculation."""
        polygon = RegularPolygon(Point2D(0, 0), 4, 5)
        side = polygon.side_length()
        assert side > 0

    def test_apothem(self):
        """Test apothem calculation."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        apothem = polygon.apothem()
        expected = 5 * math.cos(math.pi / 6)
        assert math.isclose(apothem, expected)

    def test_interior_angle(self):
        """Test interior angle calculation."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        angle = polygon.interior_angle()
        # Hexagon interior angle is 120 degrees
        expected = (6 - 2) * math.pi / 6
        assert math.isclose(angle, expected)

    def test_exterior_angle(self):
        """Test exterior angle calculation."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        angle = polygon.exterior_angle()
        # Exterior angle = 360 / n
        expected = 2 * math.pi / 6
        assert math.isclose(angle, expected)

    def test_area(self):
        """Test regular polygon area."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        area = polygon.area()
        assert area > 0

    def test_perimeter(self):
        """Test regular polygon perimeter."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        perimeter = polygon.perimeter()
        assert perimeter > 0

    def test_equilateral_triangle(self):
        """Test regular triangle (equilateral)."""
        triangle = RegularPolygon(Point2D(0, 0), 3, 5)
        assert triangle.num_sides == 3
        # All sides should be equal
        side_length = triangle.side_length()
        for i in range(3):
            dist = triangle.vertices[i].distance_to(triangle.vertices[(i + 1) % 3])
            assert math.isclose(dist, side_length, abs_tol=1e-10)

    def test_vertices_on_circle(self):
        """Test that vertices lie on the circumcircle."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        for vertex in polygon.vertices:
            distance = polygon.center_point.distance_to(vertex)
            assert math.isclose(distance, 5.0)

    def test_with_rotation(self):
        """Test regular polygon with rotation."""
        polygon = RegularPolygon(Point2D(0, 0), 4, 5, math.pi / 4)
        assert polygon.rotation_angle == math.pi / 4

    def test_repr(self):
        """Test string representation."""
        polygon = RegularPolygon(Point2D(0, 0), 6, 5)
        assert "RegularPolygon" in repr(polygon)
        assert "6 sides" in repr(polygon)
