from enum import Enum, auto
from math import inf
from random import normalvariate

Variability = float


class Rounding(Enum):
    ROUND = auto()
    CEILING = auto()
    FLOOR = auto()


def round_to_nearest_multiple(number, round_to, rounding: Rounding = Rounding.ROUND):
    if round_to <= 0:
        raise ValueError(f"Rounding factor can not be 0 or negative.")

    remainder = number % round_to

    if rounding == Rounding.ROUND:
        nearest = number + round_to - remainder if 2 * remainder >= round_to else number - remainder
    elif rounding == Rounding.CEILING:
        nearest = number + round_to - remainder
    elif rounding == Rounding.FLOOR:
        nearest = number - remainder
    else:
        raise ValueError(f"rounding is not a valid Rounding value: '{rounding}'")

    return nearest


def get_variability_amount(variability: Variability,
                           coloring_image_axis_size: int) -> float:
    if variability == 0.0:
        variability_amount: float = variability
    else:
        # TODO: get scaled or truncated value rather than retrying until value generated that fits in desired range
        #       search term: Truncated normal distribution
        # https://scipy.github.io/devdocs/reference/generated/scipy.stats.truncnorm.html
        # https://github.com/jessemzhang/tn_test/blob/master/truncated_normal/truncated_normal.py
        # package name: truncnorm
        # package name: pydistributions
        variation_value: float = inf
        while variation_value < -1.0 or variation_value > 1.0:
            variation_value: float = normalvariate(mu=0.0, sigma=0.25)

        # Maximum extent of axis considered around point
        variability_radius: float = variability * coloring_image_axis_size
        # Specific extent selected with normal distribution value
        variability_amount: float = variation_value * variability_radius

    return variability_amount
