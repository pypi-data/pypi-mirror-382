import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Self

import sympy as sp

from .exceptions import ExpressionTypeUnsupportedError


# TODO: move to subfolder "symbolic"


@dataclass
class Calculation:
    operation: Callable
    value0: Self | Decimal
    value1: Self | Decimal

    def result(self):
        value0: Calculation | Decimal = self.value0
        value1: Calculation | Decimal = self.value1

        if isinstance(value0, Calculation):
            value0 = value0.result()
        if isinstance(value1, Calculation):
            value1 = value1.result()

        return self.operation(value0, value1)


def expr_to_calc(expression: sp.S) -> Calculation:
    calculation: Calculation | None = None
    operation: Callable | None = None
    value0: Calculation | Decimal | None = None
    value1: Calculation | Decimal | None = None

    if len(expression.args) == 0:
        if isinstance(expression, sp.Rational | sp.Integer | sp.core.numbers.Half):
            operation = Decimal.__truediv__
            value0 = Decimal(expression.p)
            value1 = Decimal(expression.q)
        elif isinstance(expression, sp.Float):
            operation = Decimal.__add__
            value0 = Decimal(float(expression.num))
            value1 = Decimal(0)
        elif isinstance(expression, sp.core.numbers.Pi):
            operation = Decimal.__add__
            value0 = Decimal(math.pi)
            value1 = Decimal(0)
        else:
            raise ExpressionTypeUnsupportedError(f"Expression type '{type(expression)}' not yet supported.")
    else:
        if isinstance(expression, sp.Add):
            operation = Decimal.__add__
        elif isinstance(expression, sp.Mul):
            operation = Decimal.__mul__
        elif isinstance(expression, sp.Pow):
            operation = Decimal.__pow__
        elif isinstance(expression, sp.Expr):
            if isinstance(expression.args[0], sp.Expr):
                calculation = expr_to_calc(expression=expression.args[0])
            elif isinstance(expression.args[0], int):
                calculation = Calculation(Decimal.__add__, value0=expression.args[0], value1=Decimal(0))
        else:
            raise ExpressionTypeUnsupportedError(f"Expression type '{type(expression)}' not yet supported.")

        if calculation is None:
            value0 = expr_to_calc(expression=expression.args[0])
            value1 = expr_to_calc(expression=expression.args[1])

    if calculation is None and operation is not None and value0 is not None and value1 is not None:
        calculation = Calculation(operation=operation, value0=value0, value1=value1)

    return calculation
