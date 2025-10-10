from math import inf
from typing import Any, Iterable

import sympy as sp
from angle_tompy.angle import Angle

from .exceptions import EmptyListError


# TODO: move to subfolder "symbolic"


def sweep_between(first: sp.Point2D, second: sp.Point2D, basis: sp.Point2D | None = None) -> Angle:
    if basis is None:
        basis = sp.Point2D(0, 0)

    first_local: sp.Point2D = first - basis
    second_local: sp.Point2D = second - basis

    first_local_sweep: sp.Expr = sp.atan2(first_local.y, first_local.x) % (2 * sp.pi)
    second_local_sweep: sp.Expr = sp.atan2(second_local.y, second_local.x) % (2 * sp.pi)

    sweep_difference: sp.Expr = second_local_sweep - first_local_sweep

    if sweep_difference <= -sp.pi or sweep_difference > sp.pi:
        sweep_difference %= sp.pi

    sweep_angle: Angle = Angle(radian=sweep_difference)

    return sweep_angle


def bounding_box(points: Iterable[sp.Point2D]) -> tuple[sp.Point2D, sp.Expr, sp.Expr]:
    # Calculates axis-oriented bounding box for point cloud
    # Outputs min-x/y point, followed by positive height, and width values

    x_min = inf
    x_max = -inf
    y_min = inf
    y_max = -inf

    point_amount: int = 0

    for index, point in enumerate(points):
        x = point.x
        y = point.y

        if x < x_min:
            x_min = x
        if x > x_max:
            x_max = x
        if y < y_min:
            y_min = y
        if y > y_max:
            y_max = y

        point_amount = index + 1

    is_points_in_iterable: bool = point_amount > 0
    if not is_points_in_iterable:
        raise EmptyListError(f"Input iterable is empty.")

    point = sp.Point2D(x_min, y_min)
    width = x_max - x_min
    height = y_max - y_min
    return point, width, height


def middle(points: Iterable[sp.Point2D]) -> sp.Point2D:
    point, width, height = bounding_box(points=points)

    x = point.x + (width / 2)
    y = point.y + (height / 2)

    point: sp.Point2D = sp.Point2D(x, y)

    return point


def centroid(points: Iterable[sp.Point2D]) -> sp.Point2D:
    xs: list[sp.Point2D] = []
    ys: list[sp.Point2D] = []
    point_amount: int = 0

    for index, point in enumerate(points):
        xs.append(point.x)
        ys.append(point.y)
        point_amount = index + 1

    is_points_in_iterable: bool = point_amount > 0
    if not is_points_in_iterable:
        raise EmptyListError(f"Input iterable is empty.")

    x = sum(xs) / point_amount
    y = sum(ys) / point_amount

    point: sp.Point2D = sp.Point2D(x, y)

    return point


# TODO: create "normalize" with basis


# TODO: refactor as "scale" with basis
def along_line(start: sp.Point2D, end: sp.Point2D, fraction: float) -> sp.Point2D:
    x_difference = end.x - start.x
    y_difference = end.y - start.y

    x_modified = x_difference * fraction
    y_modified = y_difference * fraction

    x = start.x + x_modified
    y = start.y + y_modified

    point: sp.Point2D = sp.Point2D(x, y)

    return point


# TODO: refactor as "magnitude" with basis
def distance(position0: sp.Point2D, position1: sp.Point2D) -> Any:
    distance_ = position0.distance(other=position1)
    return distance_


def revolve(point: sp.Point2D, angle: Angle, basis: sp.Point2D | None = None) -> sp.Point2D:
    if basis is None:
        basis = sp.Point2D(0, 0)

    precalculated_cos: sp.Expr = sp.cos(angle.as_radian()).nsimplify()
    precalculated_sin: sp.Expr = sp.sin(angle.as_radian()).nsimplify()

    pc_x: sp.Expr = (point.x - basis.x)
    pc_y: sp.Expr = (point.y - basis.y)

    revolved_x: sp.Expr = precalculated_cos * pc_x - \
                          precalculated_sin * pc_y + \
                          basis.x
    revolved_y: sp.Expr = precalculated_sin * pc_x + \
                          precalculated_cos * pc_y + \
                          basis.y

    revolved_point: sp.Point2D = sp.Point2D(revolved_x, revolved_y)

    return revolved_point


def perpendicular_clockwise(vector: sp.Point2D) -> sp.Point2D:
    point: sp.Point2D = sp.Point2D(vector.y, -vector.x)
    return point


def perpendicular_anticlockwise(vector: sp.Point2D) -> sp.Point2D:
    point: sp.Point2D = sp.Point2D(-vector.y, vector.x)
    return point


def perpendicular_extrusion(start: sp.Point2D,
                            end: sp.Point2D,
                            fraction: float
                            ) -> tuple[sp.Point2D, sp.Point2D, sp.Point2D, sp.Point2D]:

    base_vector: sp.Point2D = (start - end) * (fraction / 2)  # Halving fraction for diameter instead of radius
    perpendicular_cw: sp.Point2D = perpendicular_clockwise(vector=base_vector)
    perpendicular_acw: sp.Point2D = perpendicular_anticlockwise(vector=base_vector)

    point0: sp.Point2D = start + perpendicular_acw
    point1: sp.Point2D = end + perpendicular_acw
    point2: sp.Point2D = end + perpendicular_cw
    point3: sp.Point2D = start + perpendicular_cw

    return point0, point1, point2, point3


def shape_node_positions(edges: int, radius: sp.Expr, direction: sp.Point2D) -> list[sp.Point2D]:
    positions: list[sp.Point2D] = []
    angle_step_size: sp.Expr = 2 * sp.pi / edges
    angle: Angle = Angle(radian=angle_step_size)
    first_position: sp.Point2D = direction.unit * radius
    positions.append(first_position)
    _type: type = type(direction)
    for _ in range(edges-1):
        revolved_position: sp.Point2D = revolve(point=positions[-1],
                                                angle=angle,
                                                basis=_type(0, 0))
        positions.append(revolved_position)

    return positions


def nearest_point(line: sp.Line2D, point: sp.Point2D) -> sp.Point2D:
    line_start: sp.Point2D = line.points[0]
    line_end: sp.Point2D = line.points[1]
    unit_vector: sp.Point2D = (line_end - line_start).unit
    lp: sp.Point2D = point - line_start
    lambda_: sp.Expr = unit_vector.dot(lp)
    vv: sp.Point2D = unit_vector * lambda_
    new_point: sp.Point2D = line_start + vv
    return new_point


def transform(position: sp.Point2D, translation: sp.Point2D, rotation: Angle, basis: sp.Point2D) -> sp.Point2D:
    rotated: sp.Point2D = revolve(point=position, angle=rotation, basis=basis)
    transformed: sp.Point2D = rotated - translation
    return transformed
