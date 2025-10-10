import sympy as sp

from angle_tompy.angle import Angle

from src.math_tompy.symbolic_point2d import revolve


def test_revolve_point_at_basis_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(0, 0)
    point1: sp.Point2D = sp.Point2D(0, 0)
    point2: sp.Point2D = sp.Point2D(0, 0)
    angle0: Angle = Angle(degree=123)

    # Execution
    point3: sp.Point2D = revolve(point=point0, angle=angle0, basis=point1)

    # Validation
    assert point2 == point3


def test_revolve_zero_angle_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 1)
    point1: sp.Point2D = sp.Point2D(0, 0)
    point2: sp.Point2D = sp.Point2D(1, 1)
    angle0: Angle = Angle(degree=0)

    # Execution
    point3: sp.Point2D = revolve(point=point0, angle=angle0, basis=point1)

    # Validation
    assert point2 == point3


def test_revolve_q1_to_q4_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(2, 2)
    point1: sp.Point2D = sp.Point2D(0, 0)
    point2: sp.Point2D = sp.Point2D(2, -2)
    angle0: Angle = Angle(degree=-90)

    # Execution
    point3: sp.Point2D = revolve(point=point0, angle=angle0, basis=point1)

    # Validation
    assert point2 == point3


def test_revolve_q2_to_q4_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-3, 3)
    point1: sp.Point2D = sp.Point2D(0, 0)
    point2: sp.Point2D = sp.Point2D(3, -3)
    angle0: Angle = Angle(degree=180)

    # Execution
    point3: sp.Point2D = revolve(point=point0, angle=angle0, basis=point1)

    # Validation
    assert point2 == point3
