"""Pytest configuration and shared fixtures for GeomKit tests."""

import math

import pytest

from geomkit import Point2D, Point3D, Vector2D


@pytest.fixture
def origin_2d():
    """Fixture for 2D origin point."""
    return Point2D(0, 0)


@pytest.fixture
def origin_3d():
    """Fixture for 3D origin point."""
    return Point3D(0, 0, 0)


@pytest.fixture
def unit_vector_x():
    """Fixture for unit vector along x-axis."""
    return Vector2D(1, 0)


@pytest.fixture
def unit_vector_y():
    """Fixture for unit vector along y-axis."""
    return Vector2D(0, 1)


@pytest.fixture
def right_triangle_points():
    """Fixture for right triangle vertices (3-4-5 triangle)."""
    return Point2D(0, 0), Point2D(3, 0), Point2D(0, 4)


@pytest.fixture
def square_vertices():
    """Fixture for square vertices."""
    return [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]


# Custom assertion helper
def assert_points_close(p1, p2, abs_tol=1e-9):
    """Assert that two points are approximately equal."""
    assert math.isclose(p1.x, p2.x, abs_tol=abs_tol)
    assert math.isclose(p1.y, p2.y, abs_tol=abs_tol)
    if hasattr(p1, "z") and hasattr(p2, "z"):
        assert math.isclose(p1.z, p2.z, abs_tol=abs_tol)
