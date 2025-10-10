import math
from decimal import Decimal

import pytest

from src.math_tompy.decimal import asin


def test_asin_ratio_one_success():
    # Setup
    ratio0: Decimal = Decimal("1")
    angle0: Decimal = Decimal(90 / 180 * math.pi)

    # Execution
    angle1: Decimal = asin(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_asin_ratio_sqrt_two_halves_success():
    # Setup
    ratio0: Decimal = Decimal(math.sqrt(2) / 2)
    angle0: Decimal = Decimal(45 / 180 * math.pi)

    # Execution
    angle1: Decimal = asin(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_asin_ratio_sqrt_three_halves_success():
    # Setup
    ratio0: Decimal = Decimal(math.sqrt(3) / 2)
    angle0: Decimal = Decimal(60 / 180 * math.pi)

    # Execution
    angle1: Decimal = asin(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_asin_ratio_sqrt_four_fourths_success():
    # Setup
    ratio0: Decimal = Decimal(math.sqrt(4) / 4)
    angle0: Decimal = Decimal(30 / 180 * math.pi)

    # Execution
    angle1: Decimal = asin(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


# def test_asin_ratio_near_one_failure():
#     # Setup
#     ratio0: Decimal = Decimal("0.975")
#
#     # Validation
#     with pytest.raises(ValueError):
#         _: Decimal = asin(ratio=ratio0)
