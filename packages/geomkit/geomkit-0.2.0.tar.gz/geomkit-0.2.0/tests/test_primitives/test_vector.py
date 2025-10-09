"""Test cases for Vector2D and Vector3D classes using pytest."""

import math

import pytest

from geomkit import Vector2D, Vector3D


class TestVector2D:
    """Test cases for Vector2D class."""

    def test_initialization(self):
        """Test vector initialization."""
        v = Vector2D(3, 4)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_magnitude(self):
        """Test magnitude calculation."""
        v = Vector2D(3, 4)
        assert v.magnitude() == 5.0

    def test_magnitude_zero_vector(self):
        """Test magnitude of zero vector."""
        v = Vector2D(0, 0)
        assert v.magnitude() == 0.0

    def test_normalize(self):
        """Test vector normalization."""
        v = Vector2D(3, 4)
        normalized = v.normalize()
        assert math.isclose(normalized.magnitude(), 1.0)
        assert math.isclose(normalized.x, 0.6)
        assert math.isclose(normalized.y, 0.8)

    def test_normalize_zero_vector_raises_error(self):
        """Test that normalizing zero vector raises error."""
        v = Vector2D(0, 0)
        with pytest.raises(ValueError):
            v.normalize()

    def test_dot_product(self):
        """Test dot product calculation."""
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        assert v1.dot(v2) == 11.0

    def test_dot_product_perpendicular(self):
        """Test dot product of perpendicular vectors."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        assert v1.dot(v2) == 0.0

    def test_cross_product(self):
        """Test cross product (returns scalar in 2D)."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        assert v1.cross(v2) == 1.0

    def test_angle_to(self):
        """Test angle calculation between vectors."""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        angle = v1.angle_to(v2)
        assert math.isclose(angle, math.pi / 2)

    def test_rotate(self):
        """Test vector rotation."""
        v = Vector2D(1, 0)
        rotated = v.rotate(math.pi / 2)
        assert math.isclose(rotated.x, 0.0, abs_tol=1e-10)
        assert math.isclose(rotated.y, 1.0, abs_tol=1e-10)

    def test_addition(self):
        """Test vector addition."""
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        result = v1 + v2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector2D(5, 7)
        v2 = Vector2D(2, 3)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        v = Vector2D(2, 3)
        result = v * 3
        assert result.x == 6.0
        assert result.y == 9.0

    def test_scalar_multiplication_reverse(self):
        """Test reverse scalar multiplication."""
        v = Vector2D(2, 3)
        result = 3 * v
        assert result.x == 6.0
        assert result.y == 9.0

    def test_scalar_division(self):
        """Test scalar division."""
        v = Vector2D(6, 9)
        result = v / 3
        assert result.x == 2.0
        assert result.y == 3.0

    def test_scalar_division_by_zero_raises_error(self):
        """Test that division by zero raises error."""
        v = Vector2D(1, 2)
        with pytest.raises(ValueError):
            v / 0

    def test_negation(self):
        """Test vector negation."""
        v = Vector2D(3, 4)
        neg = -v
        assert neg.x == -3.0
        assert neg.y == -4.0

    def test_repr(self):
        """Test string representation."""
        v = Vector2D(3, 4)
        assert repr(v) == "Vector2D(3.0, 4.0)"


class TestVector3D:
    """Test cases for Vector3D class."""

    def test_initialization(self):
        """Test 3D vector initialization."""
        v = Vector3D(1, 2, 3)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_magnitude(self):
        """Test 3D magnitude calculation."""
        v = Vector3D(2, 3, 6)
        assert v.magnitude() == 7.0

    def test_normalize(self):
        """Test 3D vector normalization."""
        v = Vector3D(2, 3, 6)
        normalized = v.normalize()
        assert math.isclose(normalized.magnitude(), 1.0)

    def test_dot_product(self):
        """Test 3D dot product."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        assert v1.dot(v2) == 32.0

    def test_cross_product(self):
        """Test 3D cross product (returns vector)."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        result = v1.cross(v2)
        assert result.x == 0.0
        assert result.y == 0.0
        assert result.z == 1.0

    def test_cross_product_perpendicular(self):
        """Test cross product creates perpendicular vector."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        cross = v1.cross(v2)
        # Cross product should be perpendicular to both vectors
        assert math.isclose(v1.dot(cross), 0.0)
        assert math.isclose(v2.dot(cross), 0.0)

    def test_angle_to(self):
        """Test 3D angle calculation."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        angle = v1.angle_to(v2)
        assert math.isclose(angle, math.pi / 2)

    def test_addition(self):
        """Test 3D vector addition."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        result = v1 + v2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

    def test_subtraction(self):
        """Test 3D vector subtraction."""
        v1 = Vector3D(5, 7, 9)
        v2 = Vector3D(2, 3, 4)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 4.0
        assert result.z == 5.0

    def test_scalar_multiplication(self):
        """Test 3D scalar multiplication."""
        v = Vector3D(1, 2, 3)
        result = v * 2
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

    def test_scalar_division(self):
        """Test 3D scalar division."""
        v = Vector3D(6, 9, 12)
        result = v / 3
        assert result.x == 2.0
        assert result.y == 3.0
        assert result.z == 4.0

    def test_negation(self):
        """Test 3D vector negation."""
        v = Vector3D(1, 2, 3)
        neg = -v
        assert neg.x == -1.0
        assert neg.y == -2.0
        assert neg.z == -3.0

    def test_repr(self):
        """Test 3D string representation."""
        v = Vector3D(1, 2, 3)
        assert repr(v) == "Vector3D(1.0, 2.0, 3.0)"
