import sympy as sp

from src.math_tompy.symbolic_point2d import along_line


def test_along_line_positive_positive_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 4)
    point1: sp.Point2D = sp.Point2D(3, 4)
    point2: sp.Point2D = sp.Point2D(2, 4)

    # Execution
    point3: sp.Point2D = along_line(start=point0, end=point1, fraction=0.5)

    # Validation
    assert point2 == point3


def test_along_line_positive_negative_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(2, 1)
    point1: sp.Point2D = sp.Point2D(-6, -3)
    point2: sp.Point2D = sp.Point2D(-4, -2)

    # Execution
    point3: sp.Point2D = along_line(start=point0, end=point1, fraction=0.75)

    # Validation
    assert point2 == point3


def test_along_line_negative_positive_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-2, -4)
    point1: sp.Point2D = sp.Point2D(3, 6)
    point2: sp.Point2D = sp.Point2D(1, 2)

    # Execution
    point3: sp.Point2D = along_line(start=point0, end=point1, fraction=0.6)

    # Validation
    assert point2 == point3


def test_along_line_negative_negative_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(7, -3)
    point1: sp.Point2D = sp.Point2D(-8, 2)
    point2: sp.Point2D = sp.Point2D(-5, 1)

    # Execution
    point3: sp.Point2D = along_line(start=point0, end=point1, fraction=0.8)

    # Validation
    assert point2 == point3
