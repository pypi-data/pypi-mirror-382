import pytest
import sympy as sp

from src.math_tompy.exceptions import EmptyListError
from src.math_tompy.symbolic_point2d import middle


def test_middle_from_empty_list_failure():
    # Setup
    list0: list = []

    # Validation
    with pytest.raises(EmptyListError):
        middle(points=list0)


def test_middle_from_list_with_one_success():
    # Setup
    point0 = sp.Point(0, 0)
    list0: list = [point0]
    middle0: sp.Point2D = sp.Point(0, 0)

    # Execution
    middle1: sp.Point2D = middle(points=list0)

    # Validation
    assert middle0 == middle1


def test_middle_from_list_with_two_success():
    # Setup
    point0 = sp.Point(0, 0)
    point1 = sp.Point(1, 1)
    list0: list = [point0, point1]
    middle0: sp.Point2D = sp.Point(0.5, 0.5)

    # Execution
    middle1: sp.Point2D = middle(points=list0)

    # Validation
    assert middle0 == middle1


def test_middle_from_list_with_five_success():
    # Setup
    point0 = sp.Point(-5, -3)
    point1 = sp.Point(2, 4)
    point2 = sp.Point(-3, 1)
    point3 = sp.Point(6, -1)
    point4 = sp.Point(1, 1)
    list0: list = [point0, point1, point2, point3, point4]
    middle0: sp.Point2D = sp.Point(0.5, 0.5)

    # Execution
    middle1: sp.Point2D = middle(points=list0)

    # Validation
    assert middle0 == middle1
