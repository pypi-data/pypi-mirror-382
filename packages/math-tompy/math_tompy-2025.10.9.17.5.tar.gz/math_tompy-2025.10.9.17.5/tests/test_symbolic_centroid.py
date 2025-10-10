from typing import Iterator

import pytest
import sympy as sp

from src.math_tompy.exceptions import EmptyListError
from src.math_tompy.symbolic_point2d import centroid


def test_centroid_empty_failure():
    # Setup
    points0: list[sp.Point2D] = []

    # Validation
    with pytest.raises(EmptyListError):
        _: sp.Point2D = centroid(points=points0)


def test_centroid_middle_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 1)
    point1: sp.Point2D = sp.Point2D(-1, 1)
    point2: sp.Point2D = sp.Point2D(-1, -1)
    point3: sp.Point2D = sp.Point2D(1, -1)
    point4: sp.Point2D = sp.Point2D(0, 0)
    points0: list[sp.Point2D] = [point0, point1, point2, point3]

    # Execution
    point5: sp.Point2D = centroid(points=points0)

    # Validation
    assert point4 == point5


def test_centroid_iterator_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 1)
    point1: sp.Point2D = sp.Point2D(-1, 1)
    point2: sp.Point2D = sp.Point2D(-1, -1)
    point3: sp.Point2D = sp.Point2D(1, -1)
    point4: sp.Point2D = sp.Point2D(0, 0)
    points0: Iterator[sp.Point2D] = (point for point in [point0, point1, point2, point3])

    # Execution
    point5: sp.Point2D = centroid(points=points0)

    # Validation
    assert point4 == point5


def test_centroid_q1_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(4, 5)
    point1: sp.Point2D = sp.Point2D(7, 5)
    point2: sp.Point2D = sp.Point2D(3, 7)
    point3: sp.Point2D = sp.Point2D(6, 7)
    point4: sp.Point2D = sp.Point2D(5, 6)
    points0: list[sp.Point2D] = [point0, point1, point2, point3]

    # Execution
    point5: sp.Point2D = centroid(points=points0)

    # Validation
    assert point4 == point5


def test_centroid_q3_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-4, -4)
    point1: sp.Point2D = sp.Point2D(-5, -4)
    point2: sp.Point2D = sp.Point2D(-6, -4)
    point3: sp.Point2D = sp.Point2D(-4, -5)
    point4: sp.Point2D = sp.Point2D(-6, -5)
    point5: sp.Point2D = sp.Point2D(-4, -6)
    point6: sp.Point2D = sp.Point2D(-5, -6)
    point7: sp.Point2D = sp.Point2D(-6, -6)
    point8: sp.Point2D = sp.Point2D(-5, -5)
    points0: list[sp.Point2D] = [point0, point1, point2, point3, point4, point5, point6, point7]

    # Execution
    point9: sp.Point2D = centroid(points=points0)

    # Validation
    assert point8 == point9


def test_centroid_q2_q3_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-1, 2)
    point1: sp.Point2D = sp.Point2D(-1, -3)
    point2: sp.Point2D = sp.Point2D(-2, 6)
    point3: sp.Point2D = sp.Point2D(-3, 8)
    point4: sp.Point2D = sp.Point2D(-3, -4)
    point5: sp.Point2D = sp.Point2D(-4, -2)
    point6: sp.Point2D = sp.Point2D(-5, 2)
    point7: sp.Point2D = sp.Point2D(-5, 7)
    point8: sp.Point2D = sp.Point2D(-3, 2)
    points0: list[sp.Point2D] = [point0, point1, point2, point3, point4, point5, point6, point7]

    # Execution
    point9: sp.Point2D = centroid(points=points0)

    # Validation
    assert point8 == point9


def test_centroid_q4_q1_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(-4, -4)
    point1: sp.Point2D = sp.Point2D(-5, -4)
    point2: sp.Point2D = sp.Point2D(-6, -4)
    point3: sp.Point2D = sp.Point2D(-4, -5)
    point4: sp.Point2D = sp.Point2D(-6, -5)
    point5: sp.Point2D = sp.Point2D(-4, -6)
    point6: sp.Point2D = sp.Point2D(-5, -6)
    point7: sp.Point2D = sp.Point2D(-6, -6)
    point8: sp.Point2D = sp.Point2D(-5, -5)
    points0: list[sp.Point2D] = [point0, point1, point2, point3, point4, point5, point6, point7]

    # Execution
    point9: sp.Point2D = centroid(points=points0)

    # Validation
    assert point8 == point9
