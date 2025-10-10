from decimal import Decimal

import pytest

from src.math_tompy.decimal import factorial


def test_factorial_one_success():
    # Setup
    value0: Decimal = Decimal("1")
    factorial0: Decimal = Decimal("1")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1


def test_factorial_two_success():
    # Setup
    value0: Decimal = Decimal("2")
    factorial0: Decimal = Decimal("2")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1


def test_factorial_seven_success():
    # Setup
    value0: Decimal = Decimal("7")
    factorial0: Decimal = Decimal("5040")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1


def test_factorial_twenty_success():
    # Setup
    value0: Decimal = Decimal("20")
    factorial0: Decimal = Decimal("2432902008176640000")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1


def test_factorial_zero_success():
    # Setup
    value0: Decimal = Decimal("0")
    factorial0: Decimal = Decimal("1")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1


def test_factorial_minus_two_success():
    # Setup
    value0: Decimal = Decimal("-2")

    # Validation
    with pytest.raises(ValueError):
        _: Decimal = factorial(value=value0)


def test_factorial_non_whole_number_success():
    # Setup
    value0: Decimal = Decimal("9.738")
    factorial0: Decimal = Decimal("362880")

    # Execution
    factorial1: Decimal = factorial(value=value0)

    # Validation
    assert factorial0 == factorial1
