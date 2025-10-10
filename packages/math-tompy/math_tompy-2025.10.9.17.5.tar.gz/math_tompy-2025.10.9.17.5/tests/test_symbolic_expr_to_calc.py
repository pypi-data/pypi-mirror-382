from decimal import Decimal

import sympy as sp

from src.math_tompy.symbolic import Calculation, expr_to_calc


def test_expr_to_calc_one_success():
    # Setup
    expression0: sp.Expr = sp.Expr(1)
    calc0: Calculation = Calculation(operation=Decimal.__add__, value0=Decimal(1), value1=Decimal(0))

    # Execution
    calc1: Calculation = expr_to_calc(expression=expression0)

    # Validation
    assert calc0 == calc1


def test_expr_to_calc_one_half_success():
    # Setup
    expression0: sp.Expr = sp.Expr(sp.Rational(1/2))
    calc0: Calculation = Calculation(operation=Decimal.__truediv__, value0=Decimal(1), value1=Decimal(2))

    # Execution
    calc1: Calculation = expr_to_calc(expression=expression0)

    # Validation
    assert calc0 == calc1


def test_expr_to_calc_sqrt_two_thirds_success():
    # Setup
    expression0: sp.Expr = sp.Expr(sp.sqrt(2)/3)
    calc0: Calculation = Calculation(operation=Decimal.__mul__,
                                     value0=Calculation(operation=Decimal.__truediv__,
                                                        value0=Decimal(1),
                                                        value1=Decimal(3)),
                                     value1=Calculation(operation=Decimal.__pow__,
                                                        value0=Calculation(operation=Decimal.__truediv__,
                                                                           value0=2,
                                                                           value1=1),
                                                        value1=Calculation(operation=Decimal.__truediv__,
                                                                           value0=1,
                                                                           value1=2)))

    # Execution
    calc1: Calculation = expr_to_calc(expression=expression0)

    # Validation
    assert calc0 == calc1


def test_expr_to_calc_sqrt_two_thirds_plus_one_success():
    # Setup
    expression0: sp.Expr = sp.Expr(sp.sqrt(2)/3 + 1)
    calc0: Calculation = Calculation(operation=Decimal.__add__,
                                     value0=Calculation(operation=Decimal.__truediv__,
                                                        value0=Decimal(1),
                                                        value1=Decimal(1)),
                                     value1=Calculation(operation=Decimal.__mul__,
                                                        value0=Calculation(operation=Decimal.__truediv__,
                                                                           value0=Decimal(1),
                                                                           value1=Decimal(3)),
                                                        value1=Calculation(operation=Decimal.__pow__,
                                                                           value0=Calculation(
                                                                               operation=Decimal.__truediv__,
                                                                               value0=2,
                                                                               value1=1),
                                                                           value1=Calculation(
                                                                               operation=Decimal.__truediv__,
                                                                               value0=1,
                                                                               value1=2))))

    # Execution
    calc1: Calculation = expr_to_calc(expression=expression0)

    # Validation
    assert calc0 == calc1


def test_expr_to_calc_point_values_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(sp.sqrt(2)/3, 0.5)
    x0: Calculation = Calculation(operation=Decimal.__mul__,
                                     value0=Calculation(operation=Decimal.__truediv__,
                                                        value0=Decimal(1),
                                                        value1=Decimal(3)),
                                     value1=Calculation(operation=Decimal.__pow__,
                                                        value0=Calculation(operation=Decimal.__truediv__,
                                                                           value0=2,
                                                                           value1=1),
                                                        value1=Calculation(operation=Decimal.__truediv__,
                                                                           value0=1,
                                                                           value1=2)))
    y0: Calculation = Calculation(operation=Decimal.__truediv__,
                                  value0=1,
                                  value1=2)

    # Execution
    x1: Calculation = expr_to_calc(expression=point0.x)
    y1: Calculation = expr_to_calc(expression=point0.y)

    # Validation
    assert x0 == x1 and y0 == y1
