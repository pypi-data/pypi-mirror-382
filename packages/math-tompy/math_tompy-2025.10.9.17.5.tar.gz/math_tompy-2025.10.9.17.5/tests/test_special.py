from src.math_tompy.special import Range1Df, Point1Df, clamp_svg_value_to_range


def test_clamp_value_to_range_in_range_unchanged_success():
    # Setup
    axis0: Range1Df = Range1Df(minimum=0.0, maximum=1.0)
    point0: Point1Df = Point1Df(0.5)

    # Execution
    point1: Point1Df = clamp_svg_value_to_range(svg_image_point=point0, svg_image_axis=axis0)

    # Validation
    assert point0 == point1


def test_clamp_value_to_range_lower_increased_success():
    # Setup
    axis0: Range1Df = Range1Df(minimum=1.0, maximum=5.0)
    point0: Point1Df = Point1Df(-2.5)

    # Execution
    point1: Point1Df = clamp_svg_value_to_range(svg_image_point=point0, svg_image_axis=axis0)

    # Validation
    assert axis0[0] == point1


def test_clamp_value_to_range_higher_reduced_success():
    # Setup
    axis0: Range1Df = Range1Df(minimum=-10.0, maximum=22.0)
    point0: Point1Df = Point1Df(45.9)

    # Execution
    point1: Point1Df = clamp_svg_value_to_range(svg_image_point=point0, svg_image_axis=axis0)

    # Validation
    assert axis0[1] == point1

