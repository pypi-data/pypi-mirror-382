import sympy as sp

from src.math_tompy.symbolic_point2d import perpendicular_extrusion


def test_perpendicular_extrusion_0_0_1_0_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(0, 0)
    point1: sp.Point2D = sp.Point2D(1, 0)
    fraction0: float = 6.0
    points0: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = (sp.Point2D(0, -3), sp.Point2D(1, -3),
                                                                      sp.Point2D(1, 3), sp.Point2D(0, 3))

    # Execute
    points1: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = perpendicular_extrusion(start=point0,
                                                                                             end=point1,
                                                                                             fraction=fraction0)

    # Validate
    assert points0 == points1


def test_perpendicular_extrusion_1__7__2__4_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, -7)
    point1: sp.Point2D = sp.Point2D(-2, -4)
    fraction0: float = 2.0
    points0: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = (sp.Point2D(4, -4), sp.Point2D(1, -1),
                                                                      sp.Point2D(-5, -7), sp.Point2D(-2, -10))

    # Execute
    points1: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = perpendicular_extrusion(start=point0,
                                                                                             end=point1,
                                                                                             fraction=fraction0)

    # Validate
    assert points0 == points1


def test_perpendicular_extrusion__1_8__1_10_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-1, 8)
    point1: sp.Point2D = sp.Point2D(-1, 10)
    fraction0: float = 5.0
    points0: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = (sp.Point2D(4, 8), sp.Point2D(4, 10),
                                                                      sp.Point2D(-6, 10), sp.Point2D(-6, 8))

    # Execute
    points1: tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D] = perpendicular_extrusion(start=point0,
                                                                                             end=point1,
                                                                                             fraction=fraction0)

    # Validate
    assert points0 == points1
