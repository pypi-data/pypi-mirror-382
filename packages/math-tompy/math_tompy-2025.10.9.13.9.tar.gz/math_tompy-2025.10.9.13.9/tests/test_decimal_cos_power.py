import math
from decimal import Decimal

from src.math_tompy.decimal import cos_power


def test_cos_30_degrees_success():
    # Setup
    angle0: Decimal = Decimal(30 / 180 * math.pi)
    cos0: Decimal = Decimal(Decimal.sqrt(Decimal(3)) / 2)

    # Execution
    cos1: Decimal = cos_power(angle=angle0)

    # Validation
    assert abs(cos0 - cos1) < Decimal("0.000000000000001")


def test_cos_60_degrees_success():
    # Setup
    angle0: Decimal = Decimal(60 / 180 * math.pi)
    cos0: Decimal = Decimal(0.5)

    # Execution
    cos1: Decimal = cos_power(angle=angle0)

    # Validation
    assert abs(cos0 - cos1) < Decimal("0.000000000000001")


def test_cos_90_degrees_success():
    # Setup
    angle0: Decimal = Decimal(90 / 180 * math.pi)
    cos0: Decimal = Decimal(0)

    # Execution
    cos1: Decimal = cos_power(angle=angle0)

    # Validation
    assert abs(cos0 - cos1) < Decimal("0.000000000000001")


def test_cos_180_degrees_success():
    # Setup
    angle0: Decimal = Decimal(180 / 180 * math.pi)
    cos0: Decimal = Decimal(-1)

    # Execution
    cos1: Decimal = cos_power(angle=angle0)

    # Validation
    assert abs(cos0 - cos1) < Decimal("0.000000000000001")


def test_cos_315_degrees_success():
    # Setup
    angle0: Decimal = Decimal(315 / 180 * math.pi)
    cos0: Decimal = Decimal(Decimal.sqrt(Decimal(2)) / 2)

    # Execution
    cos1: Decimal = cos_power(angle=angle0)

    # Validation
    assert abs(cos0 - cos1) < Decimal("0.000000000000001")
