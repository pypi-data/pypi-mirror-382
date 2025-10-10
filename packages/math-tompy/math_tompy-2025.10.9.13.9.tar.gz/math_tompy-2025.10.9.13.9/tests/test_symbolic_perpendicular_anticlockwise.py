import sympy as sp

from src.math_tompy.symbolic_point2d import perpendicular_anticlockwise


def test_perpendicular_anticlockwise_1_1_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 1)
    point1: sp.Point2D = sp.Point2D(-1, 1)

    # Execution
    point2: sp.Point2D = perpendicular_anticlockwise(vector=point0)

    # Validation
    assert point1 == point2
