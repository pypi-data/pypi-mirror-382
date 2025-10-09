# GeomKit Examples

This directory contains comprehensive examples demonstrating the capabilities of the GeomKit library.

## Available Examples

### 1. `basic_usage.py`
**Beginner-friendly introduction to GeomKit**

Covers:
- Point operations (2D and 3D)
- Vector operations and calculations
- Circle creation and operations
- Ellipse with eccentricity and focal points
- Triangle properties and angles
- Polygon shapes (Rectangle, Square, Regular Polygons)
- Line and line segment operations
- Utility functions

**Run:**
```bash
python examples/basic_usage.py
```

### 2. `advanced_geometry.py`
**Advanced geometric operations and algorithms**

Covers:
- Circle intersection analysis
- Tangent line calculations from external points
- Polygon triangulation techniques
- Line segment intersection detection
- Inscribed regular polygons
- Vector projection and decomposition
- Circle through three points
- Closest point on line calculations

**Run:**
```bash
python examples/advanced_geometry.py
```

### 3. `shapes_demo.py`
**Comprehensive shape demonstrations and comparisons**

Covers:
- Circle comparisons with different radii
- Ellipse variations (standard, rotated, eccentric)
- Triangle types (right, equilateral, isosceles)
- Quadrilateral family (Rectangle, Square, general polygons)
- Regular polygon series (Triangle to Dodecagon)
- Point containment tests across different shapes
- Shape efficiency analysis (area vs perimeter)

**Run:**
```bash
python examples/shapes_demo.py
```

### 4. `transformations.py`
**Geometric transformations and animations**

Covers:
- Point transformations (translation, rotation)
- Vector transformations (scaling, normalization, rotation)
- Triangle rotation around centroid
- Shape scaling from center
- Point interpolation (lerp)
- Polygon morphing between shapes
- Regular polygon rotation animation
- Reflection transformations
- Composite transformations

**Run:**
```bash
python examples/transformations.py
```

## Quick Start

Run all examples at once:
```bash
python examples/basic_usage.py
python examples/advanced_geometry.py
python examples/shapes_demo.py
python examples/transformations.py
```

## Example Output

Each example prints formatted output demonstrating the operations:

```
=== Circle Examples ===
Circle 1: Circle(center=Point2D(0.0, 0.0), radius=5)
Area: 78.54
Circumference: 31.42
Point Point2D(3.0, 4.0) inside circle: True
Circles intersect at: [Point2D(4.0, 3.0), Point2D(4.0, -3.0)]
```

## Topics Covered

### Primitives
- **Points**: 2D/3D point operations, distance, midpoint, rotation
- **Vectors**: Magnitude, normalization, dot/cross product, angles
- **Lines**: Slope, parallel/perpendicular detection, intersections

### Shapes
- **Circles**: Area, circumference, intersections, tangents
- **Ellipses**: Eccentricity, focal points, rotation
- **Triangles**: Side lengths, angles, right triangle detection
- **Rectangles/Squares**: Dimensions, diagonals
- **Regular Polygons**: Apothem, interior angles, inscribed shapes

### Operations
- Distance calculations
- Angle measurements
- Collinearity testing
- Triangle area from points
- Linear interpolation
- Transformations (rotation, translation, scaling, reflection)

## Learning Path

1. **Start with** `basic_usage.py` - Learn fundamental concepts
2. **Move to** `shapes_demo.py` - Explore different shapes
3. **Then** `advanced_geometry.py` - Learn complex operations
4. **Finally** `transformations.py` - Master transformations

## Integration Examples

These examples can be adapted for:
- Game development (collision detection, physics)
- CAD applications (geometric modeling)
- Data visualization (plotting, charting)
- Computer graphics (rendering, animations)
- Robotics (path planning, kinematics)
- Scientific computing (simulations)

## Tips

- Modify the examples to experiment with different values
- Combine concepts from different examples
- Use these as templates for your own applications
- Check the test files in `tests/` for more usage patterns
