import sympy as sp

from src.math_tompy.symbolic_point2d import shape_node_positions


def test_shape_node_positions_1_success():
    # Setup
    edges0: int = 1
    radius0: sp.S = sp.S(1)
    direction0: sp.Point2D = sp.Point2D(5, 0)
    points0: list[sp.Point2D] = [sp.Point2D(1, 0)]

    # Execution
    points1: list[sp.Point2D] = shape_node_positions(edges=edges0, radius=radius0, direction=direction0)

    # Validation
    assert points0 == points1


def test_shape_node_positions_2_success():
    # Setup
    edges0: int = 2
    radius0: sp.S = sp.S(2)
    direction0: sp.Point2D = sp.Point2D(0, -5)
    points0: list[sp.Point2D] = [sp.Point2D(0, -2), sp.Point2D(0, 2)]

    # Execution
    points1: list[sp.Point2D] = shape_node_positions(edges=edges0, radius=radius0, direction=direction0)

    # Validation
    assert points0 == points1


def test_shape_node_positions_3_success():
    # Setup
    edges0: int = 3
    radius0: sp.S = sp.S(1)
    direction0: sp.Point2D = sp.Point2D(-24, 0)
    points0: list[sp.Point2D] = [sp.Point2D(-1, 0), sp.Point2D(0.5, -sp.sqrt(3)/2), sp.Point2D(0.5, sp.sqrt(3)/2)]

    # Execution
    points1: list[sp.Point2D] = shape_node_positions(edges=edges0, radius=radius0, direction=direction0)

    # Validation
    assert points0 == points1


def test_shape_node_positions_4_success():
    # Setup
    edges0: int = 4
    radius0: float = 2 * sp.sqrt(2)
    direction0: sp.Point2D = sp.Point2D(3, 3)
    points0: list[sp.Point2D] = [sp.Point2D(2, 2),
                                 sp.Point2D(-2, 2),
                                 sp.Point2D(-2, -2),
                                 sp.Point2D(2, -2)]

    # Execution
    points1: list[sp.Point2D] = shape_node_positions(edges=edges0, radius=radius0, direction=direction0)

    # Validation
    assert points0 == points1
