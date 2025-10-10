import math
from decimal import Decimal

from src.math_tompy.decimal import sin_power


def test_sin_30_degrees_success():
    # Setup
    angle0: Decimal = Decimal(30 / 180 * math.pi)
    sin0: Decimal = Decimal(0.5)

    # Execution
    sin1: Decimal = sin_power(angle=angle0)

    # Validation
    assert abs(sin0 - sin1) < Decimal("0.000000000000001")


def test_sin_60_degrees_success():
    # Setup
    angle0: Decimal = Decimal(60 / 180 * math.pi)
    sin0: Decimal = Decimal(Decimal.sqrt(Decimal(3))/2)

    # Execution
    sin1: Decimal = sin_power(angle=angle0)

    # Validation
    assert abs(sin0 - sin1) < Decimal("0.000000000000001")


def test_sin_90_degrees_success():
    # Setup
    angle0: Decimal = Decimal(90 / 180 * math.pi)
    sin0: Decimal = Decimal(1)

    # Execution
    sin1: Decimal = sin_power(angle=angle0)

    # Validation
    assert abs(sin0 - sin1) < Decimal("0.000000000000001")


def test_sin_180_degrees_success():
    # Setup
    angle0: Decimal = Decimal(180 / 180 * math.pi)
    sin0: Decimal = Decimal(0)

    # Execution
    sin1: Decimal = sin_power(angle=angle0)

    # Validation
    assert abs(sin0 - sin1) < Decimal("0.000000000000001")


def test_sin_315_degrees_success():
    # Setup
    angle0: Decimal = Decimal(315 / 180 * math.pi)
    sin0: Decimal = Decimal(-Decimal.sqrt(Decimal(2)) / 2)

    # Execution
    sin1: Decimal = sin_power(angle=angle0)

    # Validation
    assert abs(sin0 - sin1) < Decimal("0.000000000000001")
