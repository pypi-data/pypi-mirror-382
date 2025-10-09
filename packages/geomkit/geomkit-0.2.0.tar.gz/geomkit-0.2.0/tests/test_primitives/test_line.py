"""Test cases for Line2D and LineSegment2D classes using pytest."""

import math

import pytest

from geomkit import Line2D, LineSegment2D, Point2D


class TestLine2D:
    """Test cases for Line2D class."""

    def test_initialization(self):
        """Test line initialization."""
        p1 = Point2D(0, 0)
        p2 = Point2D(1, 1)
        line = Line2D(p1, p2)
        assert line.point1 == p1
        assert line.point2 == p2

    def test_initialization_same_points_raises_error(self):
        """Test that same points raise error."""
        p = Point2D(1, 1)
        with pytest.raises(ValueError):
            Line2D(p, p)

    def test_slope_calculation(self):
        """Test slope calculation."""
        line = Line2D(Point2D(0, 0), Point2D(2, 4))
        assert line.slope == 2.0

    def test_vertical_line(self):
        """Test vertical line properties."""
        line = Line2D(Point2D(5, 0), Point2D(5, 10))
        assert line.is_vertical is True
        assert line.slope is None

    def test_horizontal_line(self):
        """Test horizontal line properties."""
        line = Line2D(Point2D(0, 5), Point2D(10, 5))
        assert line.slope == 0.0

    def test_contains_point(self):
        """Test if point is on line."""
        line = Line2D(Point2D(0, 0), Point2D(1, 1))
        assert line.contains_point(Point2D(2, 2)) is True
        assert line.contains_point(Point2D(-1, -1)) is True
        assert line.contains_point(Point2D(1, 2)) is False

    def test_is_parallel(self):
        """Test parallel line detection."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(0, 1), Point2D(1, 2))
        assert line1.is_parallel(line2) is True

    def test_not_parallel(self):
        """Test non-parallel lines."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(0, 0), Point2D(1, 2))
        assert line1.is_parallel(line2) is False

    def test_parallel_vertical_lines(self):
        """Test parallel vertical lines."""
        line1 = Line2D(Point2D(0, 0), Point2D(0, 1))
        line2 = Line2D(Point2D(5, 0), Point2D(5, 1))
        assert line1.is_parallel(line2) is True

    def test_is_perpendicular(self):
        """Test perpendicular line detection."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(0, 0), Point2D(1, -1))
        assert line1.is_perpendicular(line2) is True

    def test_intersection(self):
        """Test line intersection."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(0, 1), Point2D(1, 0))
        intersection = line1.intersection(line2)
        assert math.isclose(intersection.x, 0.5)
        assert math.isclose(intersection.y, 0.5)

    def test_intersection_parallel_lines(self):
        """Test that parallel lines have no intersection."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(0, 1), Point2D(1, 2))
        assert line1.intersection(line2) is None

    def test_intersection_with_vertical_line(self):
        """Test intersection with vertical line."""
        line1 = Line2D(Point2D(0, 0), Point2D(1, 1))
        line2 = Line2D(Point2D(3, 0), Point2D(3, 5))
        intersection = line1.intersection(line2)
        assert intersection.x == 3.0
        assert intersection.y == 3.0

    def test_distance_to_point(self):
        """Test distance from point to line."""
        line = Line2D(Point2D(0, 0), Point2D(1, 0))
        point = Point2D(0.5, 3)
        assert line.distance_to_point(point) == 3.0

    def test_distance_to_point_on_line(self):
        """Test distance when point is on line."""
        line = Line2D(Point2D(0, 0), Point2D(1, 1))
        point = Point2D(2, 2)
        assert math.isclose(line.distance_to_point(point), 0.0)


class TestLineSegment2D:
    """Test cases for LineSegment2D class."""

    def test_initialization(self):
        """Test line segment initialization."""
        start = Point2D(0, 0)
        end = Point2D(3, 4)
        segment = LineSegment2D(start, end)
        assert segment.start == start
        assert segment.end == end

    def test_initialization_same_points_raises_error(self):
        """Test that same points raise error."""
        p = Point2D(1, 1)
        with pytest.raises(ValueError):
            LineSegment2D(p, p)

    def test_length(self):
        """Test segment length calculation."""
        segment = LineSegment2D(Point2D(0, 0), Point2D(3, 4))
        assert segment.length() == 5.0

    def test_midpoint(self):
        """Test segment midpoint."""
        segment = LineSegment2D(Point2D(0, 0), Point2D(4, 6))
        mid = segment.midpoint()
        assert mid.x == 2.0
        assert mid.y == 3.0

    def test_contains_point(self):
        """Test if point is on segment."""
        segment = LineSegment2D(Point2D(0, 0), Point2D(4, 4))
        assert segment.contains_point(Point2D(2, 2)) is True
        assert segment.contains_point(Point2D(5, 5)) is False  # On line but outside segment

    def test_contains_point_at_endpoints(self):
        """Test endpoints are on segment."""
        segment = LineSegment2D(Point2D(0, 0), Point2D(4, 4))
        assert segment.contains_point(Point2D(0, 0)) is True
        assert segment.contains_point(Point2D(4, 4)) is True

    def test_intersects(self):
        """Test segment intersection detection."""
        seg1 = LineSegment2D(Point2D(0, 0), Point2D(4, 4))
        seg2 = LineSegment2D(Point2D(0, 4), Point2D(4, 0))
        assert seg1.intersects(seg2) is True

    def test_not_intersects(self):
        """Test non-intersecting segments."""
        seg1 = LineSegment2D(Point2D(0, 0), Point2D(1, 1))
        seg2 = LineSegment2D(Point2D(2, 2), Point2D(3, 3))
        assert seg1.intersects(seg2) is False

    def test_parallel_segments_not_intersect(self):
        """Test parallel segments don't intersect."""
        seg1 = LineSegment2D(Point2D(0, 0), Point2D(2, 0))
        seg2 = LineSegment2D(Point2D(0, 1), Point2D(2, 1))
        assert seg1.intersects(seg2) is False

    def test_intersection_point(self):
        """Test intersection point calculation."""
        seg1 = LineSegment2D(Point2D(0, 0), Point2D(4, 4))
        seg2 = LineSegment2D(Point2D(0, 4), Point2D(4, 0))
        intersection = seg1.intersection_point(seg2)
        assert math.isclose(intersection.x, 2.0)
        assert math.isclose(intersection.y, 2.0)

    def test_intersection_point_no_intersection(self):
        """Test intersection point when segments don't intersect."""
        seg1 = LineSegment2D(Point2D(0, 0), Point2D(1, 1))
        seg2 = LineSegment2D(Point2D(2, 2), Point2D(3, 3))
        assert seg1.intersection_point(seg2) is None

    def test_t_shaped_intersection(self):
        """Test T-shaped intersection."""
        seg1 = LineSegment2D(Point2D(0, 2), Point2D(4, 2))
        seg2 = LineSegment2D(Point2D(2, 0), Point2D(2, 4))
        assert seg1.intersects(seg2) is True
        intersection = seg1.intersection_point(seg2)
        assert math.isclose(intersection.x, 2.0)
        assert math.isclose(intersection.y, 2.0)

    def test_repr(self):
        """Test string representation."""
        segment = LineSegment2D(Point2D(0, 0), Point2D(3, 4))
        assert "LineSegment2D" in repr(segment)
