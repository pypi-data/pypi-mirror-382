import sympy as sp

from angle_tompy.angle import Angle

from src.math_tompy.symbolic_point2d import sweep_between


def test_vector2_sweep_between_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: sp.Point2D = sp.Point2D(4, 1)
    vector1: sp.Point2D = sp.Point2D(-4, -1)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q1_q2_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: sp.Point2D = sp.Point2D(1, 1)
    vector1: sp.Point2D = sp.Point2D(-1, 1)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q2_q3_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=-90)
    vector0: sp.Point2D = sp.Point2D(-1, -1)
    vector1: sp.Point2D = sp.Point2D(-1, 1)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q3_q4_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: sp.Point2D = sp.Point2D(-1, -1)
    vector1: sp.Point2D = sp.Point2D(1, -1)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q4_q1_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: sp.Point2D = sp.Point2D(1, -1)
    vector1: sp.Point2D = sp.Point2D(1, 1)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_basis_middle_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: sp.Point2D = sp.Point2D(4, 5)
    vector1: sp.Point2D = sp.Point2D(-6, 5)
    basis0: sp.Point2D = sp.Point2D(-1, 5)

    # Execution
    angle1: Angle = sweep_between(first=vector0, second=vector1, basis=basis0)

    # Validation
    assert angle0 == angle1
