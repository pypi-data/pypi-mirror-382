"""Matrix classes for 2D and 3D transformations."""

import math
from typing import List, Optional

from geomkit.primitives.point import Point2D, Point3D
from geomkit.primitives.vector import Vector2D, Vector3D


class Matrix2D:
    """Represents a 2x3 transformation matrix for 2D transformations.

    The matrix is stored in the form:
    | a  b  tx |
    | c  d  ty |

    Examples:
        >>> m = Matrix2D.identity()
        >>> p = Point2D(1, 2)
        >>> m.transform_point(p)
        Point2D(1.0, 2.0)
    """

    def __init__(
        self, a: float = 1, b: float = 0, c: float = 0, d: float = 1, tx: float = 0, ty: float = 0
    ) -> None:
        """
        Initialize a 2D transformation matrix.

        Args:
            a: Scale/rotation component (1,1)
            b: Rotation/shear component (1,2)
            c: Rotation/shear component (2,1)
            d: Scale/rotation component (2,2)
            tx: Translation x
            ty: Translation y

        Examples:
            >>> m = Matrix2D(1, 0, 0, 1, 5, 10)
            >>> (m.tx, m.ty)
            (5.0, 10.0)
        """
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)
        self.tx = float(tx)
        self.ty = float(ty)

    @staticmethod
    def identity() -> "Matrix2D":
        """Create an identity matrix.

        Examples:
            >>> m = Matrix2D.identity()
            >>> (m.a, m.d)
            (1.0, 1.0)
        """
        return Matrix2D(1, 0, 0, 1, 0, 0)

    @staticmethod
    def translation(tx: float, ty: float) -> "Matrix2D":
        """Create a translation matrix.

        Args:
            tx: Translation in x direction
            ty: Translation in y direction

        Examples:
            >>> m = Matrix2D.translation(5, 10)
            >>> m.transform_point(Point2D(0, 0))
            Point2D(5.0, 10.0)
        """
        return Matrix2D(1, 0, 0, 1, tx, ty)

    @staticmethod
    def rotation(angle: float) -> "Matrix2D":
        """Create a rotation matrix.

        Args:
            angle: Rotation angle in radians

        Examples:
            >>> m = Matrix2D.rotation(math.pi / 2)
            >>> p = m.transform_point(Point2D(1, 0))
            >>> abs(p.x) < 1e-10 and abs(p.y - 1.0) < 1e-10
            True
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Matrix2D(cos_a, -sin_a, sin_a, cos_a, 0, 0)

    @staticmethod
    def scaling(sx: float, sy: float) -> "Matrix2D":
        """Create a scaling matrix.

        Args:
            sx: Scale factor in x direction
            sy: Scale factor in y direction

        Examples:
            >>> m = Matrix2D.scaling(2, 3)
            >>> m.transform_point(Point2D(1, 1))
            Point2D(2.0, 3.0)
        """
        return Matrix2D(sx, 0, 0, sy, 0, 0)

    @staticmethod
    def shearing(shx: float, shy: float) -> "Matrix2D":
        """Create a shearing matrix.

        Args:
            shx: Shear factor in x direction
            shy: Shear factor in y direction

        Examples:
            >>> m = Matrix2D.shearing(1, 0)
            >>> m.transform_point(Point2D(0, 2))
            Point2D(2.0, 2.0)
        """
        return Matrix2D(1, shx, shy, 1, 0, 0)

    def transform_point(self, point: Point2D) -> Point2D:
        """Transform a point using this matrix.

        Args:
            point: Point to transform

        Returns:
            Transformed point

        Examples:
            >>> m = Matrix2D.translation(5, 10)
            >>> m.transform_point(Point2D(1, 2))
            Point2D(6.0, 12.0)
        """
        x = self.a * point.x + self.b * point.y + self.tx
        y = self.c * point.x + self.d * point.y + self.ty
        return Point2D(x, y)

    def transform_vector(self, vector: Vector2D) -> Vector2D:
        """Transform a vector using this matrix (ignores translation).

        Args:
            vector: Vector to transform

        Returns:
            Transformed vector

        Examples:
            >>> m = Matrix2D.rotation(math.pi / 2)
            >>> v = m.transform_vector(Vector2D(1, 0))
            >>> abs(v.x) < 1e-10 and abs(v.y - 1.0) < 1e-10
            True
        """
        x = self.a * vector.x + self.b * vector.y
        y = self.c * vector.x + self.d * vector.y
        return Vector2D(x, y)

    def multiply(self, other: "Matrix2D") -> "Matrix2D":
        """Multiply this matrix with another matrix.

        Args:
            other: Another Matrix2D

        Returns:
            Result of matrix multiplication

        Examples:
            >>> m1 = Matrix2D.translation(5, 10)
            >>> m2 = Matrix2D.scaling(2, 2)
            >>> m3 = m1.multiply(m2)
            >>> m3.transform_point(Point2D(1, 1))
            Point2D(7.0, 12.0)
        """
        return Matrix2D(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d,
            self.a * other.tx + self.b * other.ty + self.tx,
            self.c * other.tx + self.d * other.ty + self.ty,
        )

    def determinant(self) -> float:
        """Calculate the determinant of the matrix.

        Examples:
            >>> Matrix2D.identity().determinant()
            1.0
            >>> Matrix2D.scaling(2, 3).determinant()
            6.0
        """
        return self.a * self.d - self.b * self.c

    def inverse(self) -> "Matrix2D":
        """Calculate the inverse of the matrix.

        Returns:
            Inverse matrix

        Raises:
            ValueError: If matrix is not invertible (determinant is 0)

        Examples:
            >>> m = Matrix2D.translation(5, 10)
            >>> inv = m.inverse()
            >>> inv.transform_point(Point2D(5, 10))
            Point2D(0.0, 0.0)
        """
        det = self.determinant()
        if abs(det) < 1e-10:
            raise ValueError("Matrix is not invertible (determinant is 0)")

        inv_det = 1.0 / det
        return Matrix2D(
            self.d * inv_det,
            -self.b * inv_det,
            -self.c * inv_det,
            self.a * inv_det,
            (self.b * self.ty - self.d * self.tx) * inv_det,
            (self.c * self.tx - self.a * self.ty) * inv_det,
        )

    def __repr__(self) -> str:
        return (
            f"Matrix2D(a={self.a}, b={self.b}, c={self.c}, d={self.d}, tx={self.tx}, ty={self.ty})"
        )

    def __str__(self) -> str:
        return (
            f"[{self.a:.2f} {self.b:.2f} {self.tx:.2f}]\n[{self.c:.2f} {self.d:.2f} {self.ty:.2f}]"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix2D):
            return False
        return (
            math.isclose(self.a, other.a)
            and math.isclose(self.b, other.b)
            and math.isclose(self.c, other.c)
            and math.isclose(self.d, other.d)
            and math.isclose(self.tx, other.tx)
            and math.isclose(self.ty, other.ty)
        )

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash(
            (
                round(self.a, 9),
                round(self.b, 9),
                round(self.c, 9),
                round(self.d, 9),
                round(self.tx, 9),
                round(self.ty, 9),
            )
        )


class Matrix3D:
    """Represents a 4x4 transformation matrix for 3D transformations.

    The matrix is stored as a flat list of 16 values in row-major order.

    Examples:
        >>> m = Matrix3D.identity()
        >>> p = Point3D(1, 2, 3)
        >>> m.transform_point(p)
        Point3D(1.0, 2.0, 3.0)
    """

    def __init__(self, values: Optional[List[float]] = None) -> None:
        """
        Initialize a 3D transformation matrix.

        Args:
            values: List of 16 values in row-major order (defaults to identity)

        Examples:
            >>> m = Matrix3D()
            >>> m.values[0]
            1.0
        """
        if values is None:
            # Identity matrix
            self.values = [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ]
        else:
            if len(values) != 16:
                raise ValueError("Matrix3D requires exactly 16 values")
            self.values = [float(v) for v in values]

    @staticmethod
    def identity() -> "Matrix3D":
        """Create an identity matrix.

        Examples:
            >>> m = Matrix3D.identity()
            >>> m.values[0]
            1.0
        """
        return Matrix3D()

    @staticmethod
    def translation(tx: float, ty: float, tz: float) -> "Matrix3D":
        """Create a translation matrix.

        Args:
            tx: Translation in x direction
            ty: Translation in y direction
            tz: Translation in z direction

        Examples:
            >>> m = Matrix3D.translation(5, 10, 15)
            >>> m.transform_point(Point3D(0, 0, 0))
            Point3D(5.0, 10.0, 15.0)
        """
        return Matrix3D([1, 0, 0, tx, 0, 1, 0, ty, 0, 0, 1, tz, 0, 0, 0, 1])

    @staticmethod
    def rotation_x(angle: float) -> "Matrix3D":
        """Create a rotation matrix around the X axis.

        Args:
            angle: Rotation angle in radians

        Examples:
            >>> m = Matrix3D.rotation_x(math.pi / 2)
            >>> p = m.transform_point(Point3D(0, 1, 0))
            >>> abs(p.y) < 1e-10 and abs(p.z - 1.0) < 1e-10
            True
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Matrix3D([1, 0, 0, 0, 0, cos_a, -sin_a, 0, 0, sin_a, cos_a, 0, 0, 0, 0, 1])

    @staticmethod
    def rotation_y(angle: float) -> "Matrix3D":
        """Create a rotation matrix around the Y axis.

        Args:
            angle: Rotation angle in radians

        Examples:
            >>> m = Matrix3D.rotation_y(math.pi / 2)
            >>> p = m.transform_point(Point3D(1, 0, 0))
            >>> abs(p.x) < 1e-10 and abs(p.z + 1.0) < 1e-10
            True
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Matrix3D([cos_a, 0, sin_a, 0, 0, 1, 0, 0, -sin_a, 0, cos_a, 0, 0, 0, 0, 1])

    @staticmethod
    def rotation_z(angle: float) -> "Matrix3D":
        """Create a rotation matrix around the Z axis.

        Args:
            angle: Rotation angle in radians

        Examples:
            >>> m = Matrix3D.rotation_z(math.pi / 2)
            >>> p = m.transform_point(Point3D(1, 0, 0))
            >>> abs(p.x) < 1e-10 and abs(p.y - 1.0) < 1e-10
            True
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Matrix3D([cos_a, -sin_a, 0, 0, sin_a, cos_a, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

    @staticmethod
    def scaling(sx: float, sy: float, sz: float) -> "Matrix3D":
        """Create a scaling matrix.

        Args:
            sx: Scale factor in x direction
            sy: Scale factor in y direction
            sz: Scale factor in z direction

        Examples:
            >>> m = Matrix3D.scaling(2, 3, 4)
            >>> m.transform_point(Point3D(1, 1, 1))
            Point3D(2.0, 3.0, 4.0)
        """
        return Matrix3D([sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, 0, 0, 0, 1])

    def transform_point(self, point: Point3D) -> Point3D:
        """Transform a point using this matrix.

        Args:
            point: Point to transform

        Returns:
            Transformed point

        Examples:
            >>> m = Matrix3D.translation(5, 10, 15)
            >>> m.transform_point(Point3D(1, 2, 3))
            Point3D(6.0, 12.0, 18.0)
        """
        x = (
            self.values[0] * point.x
            + self.values[1] * point.y
            + self.values[2] * point.z
            + self.values[3]
        )
        y = (
            self.values[4] * point.x
            + self.values[5] * point.y
            + self.values[6] * point.z
            + self.values[7]
        )
        z = (
            self.values[8] * point.x
            + self.values[9] * point.y
            + self.values[10] * point.z
            + self.values[11]
        )
        return Point3D(x, y, z)

    def transform_vector(self, vector: Vector3D) -> Vector3D:
        """Transform a vector using this matrix (ignores translation).

        Args:
            vector: Vector to transform

        Returns:
            Transformed vector

        Examples:
            >>> m = Matrix3D.scaling(2, 3, 4)
            >>> m.transform_vector(Vector3D(1, 1, 1))
            Vector3D(2.0, 3.0, 4.0)
        """
        x = self.values[0] * vector.x + self.values[1] * vector.y + self.values[2] * vector.z
        y = self.values[4] * vector.x + self.values[5] * vector.y + self.values[6] * vector.z
        z = self.values[8] * vector.x + self.values[9] * vector.y + self.values[10] * vector.z
        return Vector3D(x, y, z)

    def multiply(self, other: "Matrix3D") -> "Matrix3D":
        """Multiply this matrix with another matrix.

        Args:
            other: Another Matrix3D

        Returns:
            Result of matrix multiplication
        """
        result = [0.0] * 16
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i * 4 + j] += self.values[i * 4 + k] * other.values[k * 4 + j]
        return Matrix3D(result)

    def __repr__(self) -> str:
        return f"Matrix3D({self.values})"

    def __str__(self) -> str:
        lines = []
        for i in range(4):
            row = self.values[i * 4 : (i + 1) * 4]
            lines.append(f"[{row[0]:.2f} {row[1]:.2f} {row[2]:.2f} {row[3]:.2f}]")
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix3D):
            return False
        return all(math.isclose(a, b) for a, b in zip(self.values, other.values))

    def __hash__(self) -> int:
        """Return hash value for use in sets and as dict keys."""
        return hash(tuple(round(v, 9) for v in self.values))
