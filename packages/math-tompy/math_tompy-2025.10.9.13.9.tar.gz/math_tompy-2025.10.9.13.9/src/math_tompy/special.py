from decimal import Decimal
from fractions import Fraction
from typing import NamedTuple

# TODO: use Numeric to make parts of this more generic
Numeric = int | float | Decimal | Fraction

# TODO: Point1Df as Vector1 in Decimal
#       although that would just be a wrapper for Decimal which is unlikely to be helpful
Point1Df = float
Point2Df = tuple[float, float]
Point1Di = int
Point2Di = tuple[int, int]


class Range1Df(NamedTuple):
    minimum: float
    maximum: float

    # TODO: implement as __len__
    def size(self) -> float:
        # Measuring stretch between fence posts
        # TODO: confirm that '1.0' should not be added here, because it is measuring between, not at
        return self.maximum - self.minimum + 1.0
        # return self.maximum - self.minimum


class Range1Di(NamedTuple):
    minimum: int
    maximum: int

    # TODO: implement as __len__
    def size(self) -> int:
        # Measuring amount of fence posts
        # TODO: confirm that '1' should not be added here,
        #       as range should be understood as [x:y[ rather than [x:y]
        return self.maximum - self.minimum + 1


class Range2Df(NamedTuple):
    x_axis: Range1Df
    y_axis: Range1Df

    def area(self) -> float:
        return self.x_axis.size() * self.y_axis.size()


class Range2Di(NamedTuple):
    x_axis: Range1Di
    y_axis: Range1Di

    def area(self) -> float:
        return self.x_axis.size() * self.y_axis.size()


# TODO: improve naming with words specific to bucketed int values and tiny-mini float values
def clamp_svg_value_to_range(svg_image_point: Point1Df, svg_image_axis: Range1Df) -> Point1Df:
    value: Point1Df
    if svg_image_point < svg_image_axis.minimum:
        value = svg_image_axis.minimum
    elif svg_image_point > svg_image_axis.maximum:
        value = svg_image_axis.maximum
    else:
        value = svg_image_point
    return value


# TODO: improve naming with words specific to bucketed int values and tiny-mini float values
def clamp_image_value_to_range(coloring_image_point: Point1Di, coloring_image_axis: Range1Di) -> Point1Di:
    value: Point1Di
    if coloring_image_point < coloring_image_axis.minimum:
        value = coloring_image_axis.minimum
    elif coloring_image_point > coloring_image_axis.maximum:
        value = coloring_image_axis.maximum
    else:
        value = coloring_image_point
    return value


# TODO: make naming generic to not focus on
def get_coloring_image_fraction(svg_image_point: Point1Df,
                                svg_axis_range: Range1Df) -> float:
    clamped_svg_image_y_axis_point: Point1Df = clamp_svg_value_to_range(svg_image_point=svg_image_point,
                                                                        svg_image_axis=svg_axis_range)
    axis_scaler: float = 1.0 / svg_axis_range.size()
    coloring_image_scaled_y_axis_point: float = clamped_svg_image_y_axis_point * axis_scaler
    return coloring_image_scaled_y_axis_point
