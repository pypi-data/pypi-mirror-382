# Changelog

All notable changes to GeomKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-09

### Added

#### 3D Shapes
- **Sphere** class with volume, surface area, and point containment
- **Cube** class for cubic geometry operations
- **RectangularPrism** class for 3D rectangular prisms

#### Transformation Matrices
- **Matrix2D** class for 2D transformations (translation, rotation, scaling, shearing)
- **Matrix3D** class for 3D transformations (translation, rotation around axes, scaling)
- Matrix multiplication and composition support
- Point and vector transformation methods

#### Bézier Curves
- **QuadraticBezier** class for quadratic Bézier curves
- **CubicBezier** class for cubic Bézier curves
- Point evaluation at parameter t
- Derivative calculations
- Curve splitting functionality

#### Bounding Boxes
- **AABB2D** class for 2D axis-aligned bounding boxes
- **AABB3D** class for 3D axis-aligned bounding boxes
- Intersection and containment tests
- Union and expansion operations

#### Advanced Algorithms
- **Convex Hull** algorithm (Graham scan) for 2D points
- **Line segment intersection** detection and calculation
- Enhanced geometric utility functions

#### Code Quality Improvements
- Added comprehensive docstring examples with doctests
- Implemented `__repr__`, `__str__`, `__eq__`, and `__hash__` for all classes
- Full type hints with proper `Optional` annotations
- Added assertions for type safety with mypy
- Configured ruff for linting and formatting (removed black)
- Set up pre-commit hooks for code quality

### Changed
- Updated minimum Python version enforcement to 3.8
- Improved type safety across all modules
- Enhanced error handling and validation
- Single source of truth for version number in `__init__.py`
- Migrated from black to ruff for code formatting

### Fixed
- Fixed mypy type checking errors throughout codebase
- Resolved optional type handling in Line2D class
- Fixed long line formatting issues
- Removed unused variables

### Technical Details
- Python 3.8+ support maintained
- Zero external runtime dependencies
- Comprehensive type annotations
- Pre-commit hooks configured
- Ruff-based code formatting and linting

## [0.1.0] - 2025-01-XX

### Added

#### Primitives
- **Point2D** class with distance, midpoint, translation, and rotation operations
- **Point3D** class for 3D point operations
- **Vector2D** class with magnitude, normalization, dot/cross product, and rotation
- **Vector3D** class with 3D vector operations
- **Line2D** class for infinite line operations (slope, parallel, perpendicular, intersections)
- **LineSegment2D** class for line segment operations (length, midpoint, intersections)

#### Shapes
- **Circle** class with area, circumference, point containment, intersections, and tangent calculations
- **Ellipse** class with area, perimeter, eccentricity, focal points, and rotation support
- **Polygon** class for general polygons with area, perimeter, centroid, and convexity tests
- **Triangle** class with side lengths, angles, and right triangle detection
- **Rectangle** class with diagonal calculations
- **Square** class as specialized rectangle
- **RegularPolygon** class for n-sided regular polygons with apothem and angle calculations

#### Utilities
- `distance()` function for calculating distance between points (2D/3D)
- `angle_between()` function for calculating angles between vectors
- `collinear()` function for testing point collinearity
- `triangle_area()` function for area calculation from three points
- `lerp()` function for linear interpolation between points
- `degrees_to_radians()` and `radians_to_degrees()` conversion functions

#### Structure
- Organized package structure with `primitives/`, `shapes/`, and `operations/` modules
- Comprehensive test suite using pytest
- Extensive documentation and examples
- Type hints throughout the codebase

#### Examples
- `basic_usage.py` - Introduction to all core features
- `advanced_geometry.py` - Advanced geometric operations
- `shapes_demo.py` - Comprehensive shape demonstrations
- `transformations.py` - Geometric transformations and animations

### Features
- ✨ No external dependencies (uses only Python standard library)
- 🎯 Fully typed with type hints
- 📚 Comprehensive documentation
- ✅ Extensive test coverage
- 🚀 Pure Python implementation
- 🔧 Easy to use API

### Technical Details
- Python 3.8+ support
- MIT License
- Modular architecture
- pytest-based testing framework

---

## [Unreleased]

### Planned Features
- 3D shape support (Sphere, Cube, etc.)
- More advanced geometric algorithms
- Performance optimizations
- Additional transformation methods
- Comprehensive API documentation
- More examples and tutorials

---

[0.1.0]: https://github.com/mmssajith/geomkit/releases/tag/v0.1.0
