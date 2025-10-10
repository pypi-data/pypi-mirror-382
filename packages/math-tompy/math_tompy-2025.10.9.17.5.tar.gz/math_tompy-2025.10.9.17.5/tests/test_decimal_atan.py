import math
from decimal import Decimal

import pytest

from src.math_tompy.decimal import atan


def test_atan_ratio_one_success():
    # Setup
    ratio0: Decimal = Decimal("1")
    angle0: Decimal = Decimal(45 / 180 * math.pi)

    # Execution
    angle1: Decimal = atan(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_atan_ratio_sqrt_three_thirds_success():
    # Setup
    ratio0: Decimal = Decimal(math.sqrt(3) / 3)
    angle0: Decimal = Decimal(30 / 180 * math.pi)

    # Execution
    angle1: Decimal = atan(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_atan_ratio_zero_success():
    # Setup
    ratio0: Decimal = Decimal(0)
    angle0: Decimal = Decimal(0)

    # Execution
    angle1: Decimal = atan(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


def test_atan_ratio_infinite_success():
    # Setup
    ratio0: Decimal = Decimal("Infinity")
    angle0: Decimal = Decimal(90 / 180 * math.pi)

    # Execution
    angle1: Decimal = atan(ratio=ratio0)

    # Validation
    assert abs(angle0 - angle1) < Decimal("0.000000000000001")


# def test_atan_ratio_near_one_failure():
#     # Setup
#     ratio0: Decimal = Decimal("0.975")
#
#     # Validation
#     with pytest.raises(ValueError):
#         _: Decimal = atan(ratio=ratio0)
