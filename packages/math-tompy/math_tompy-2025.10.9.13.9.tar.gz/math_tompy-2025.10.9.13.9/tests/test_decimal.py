from decimal import Decimal

from src.math_tompy.decimal import normalize_value


def test_normalize_value_zero_half_one_success():
    # Setup
    value0: Decimal = Decimal("0.5")
    minimum0: Decimal = Decimal("0")
    maximum0: Decimal = Decimal("1")
    normalized_value0: Decimal = Decimal("0.5")

    # Execution
    normalized_value1: Decimal = normalize_value(value=value0, minimum=minimum0, maximum=maximum0)

    # Validation
    assert normalized_value0 == normalized_value1


def test_normalize_value_minus_one_zero_one_success():
    # Setup
    value0: Decimal = Decimal("0")
    minimum0: Decimal = Decimal("-1")
    maximum0: Decimal = Decimal("1")
    normalized_value0: Decimal = Decimal("0.5")

    # Execution
    normalized_value1: Decimal = normalize_value(value=value0, minimum=minimum0, maximum=maximum0)

    # Validation
    assert normalized_value0 == normalized_value1


def test_normalize_value_minus_ten_ten_thirty_success():
    # Setup
    value0: Decimal = Decimal("10")
    minimum0: Decimal = Decimal("-10")
    maximum0: Decimal = Decimal("30")
    normalized_value0: Decimal = Decimal("0.5")

    # Execution
    normalized_value1: Decimal = normalize_value(value=value0, minimum=minimum0, maximum=maximum0)

    # Validation
    assert normalized_value0 == normalized_value1
