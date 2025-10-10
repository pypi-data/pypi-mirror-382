from typing import Iterable

import pytest
import sympy as sp

from src.math_tompy.exceptions import EmptyListError
from src.math_tompy.symbolic_point2d import bounding_box


def test_bounding_box_from_empty_list_failure():
    # Setup
    list0: list = []

    # Validation
    with pytest.raises(EmptyListError):
        bounding_box(points=list0)


def test_bounding_box_from_list_with_single_success():
    # Setup
    point0 = sp.Point2D(0, 0)
    list0: list = [point0]
    bounding_box0: tuple = (sp.Point2D(0, 0), 0, 0)

    # Execution
    bounding_box1: tuple = bounding_box(points=list0)

    # Validation
    assert bounding_box0 == bounding_box1


def test_bounding_box_from_list_with_two_success():
    # Setup
    point0 = sp.Point2D(0, 0)
    point1 = sp.Point2D(1, 1)
    list0: list = [point0, point1]
    bounding_box0: tuple = (sp.Point2D(0, 0), 1, 1)

    # Execution
    bounding_box1: tuple = bounding_box(points=list0)

    # Validation
    assert bounding_box0 == bounding_box1


def test_bounding_box_from_list_with_five_success():
    # Setup
    point0 = sp.Point2D(-5, -3)
    point1 = sp.Point2D(2, 4)
    point2 = sp.Point2D(-3, 1)
    point3 = sp.Point2D(6, -1)
    point4 = sp.Point2D(1, 1)
    list0: list = [point0, point1, point2, point3, point4]
    bounding_box0: tuple = (sp.Point2D(-5, -3), 11, 7)

    # Execution
    bounding_box1: tuple = bounding_box(points=list0)

    # Validation
    assert bounding_box0 == bounding_box1


def test_bounding_box_from_list_with_five_in_iterable_success():
    # Setup
    point0 = sp.Point2D(-5, -3)
    point1 = sp.Point2D(2, 4)
    point2 = sp.Point2D(-3, 1)
    point3 = sp.Point2D(6, -1)
    point4 = sp.Point2D(1, 1)
    list0: Iterable[sp.Point2D] = (point for point in [point0, point1, point2, point3, point4])
    bounding_box0: tuple = (sp.Point2D(-5, -3), 11, 7)

    # Execution
    bounding_box1: tuple = bounding_box(points=list0)

    # Validation
    assert bounding_box0 == bounding_box1
