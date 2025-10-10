from decimal import Decimal

from angle_tompy.angle_decimal import Angle

from .line2 import Line2
from .vector2 import Vector2


# TODO: Make Area2 immutable
class Area2:

    def __init__(self, width: Decimal, height: Decimal) -> None:
        self._width: Decimal = width
        self._height: Decimal = height

    @property
    def width(self) -> Decimal:
        return self._width

    @property
    def height(self) -> Decimal:
        return self._height

    @property
    def area(self) -> Decimal:
        return self.width * self.height


def points_in_cone(points: list[Vector2], peak: Vector2, cut: Line2) -> list[Vector2]:
    # TODO: create "Cone" class from peak Vector2 and cut Line2
    points_in_cone_: list[Vector2] = []

    for point in points:
        local_point: Vector2 = point.global_to_local(basis=peak)
        local_start: Vector2 = cut.point0.global_to_local(basis=peak)
        local_end: Vector2 = cut.point1.global_to_local(basis=peak)

        is_point_left_of_right_segment: bool = local_point.cross(other=local_start) > 0.0
        is_point_right_of_left_segment: bool = local_point.cross(other=local_end) < 0.0
        # TODO: include check for whether point is inside/outside cone "cap/end/top" line
        #       by checking whether point is closer than line intersection point
        is_point_inside_cone: bool = is_point_left_of_right_segment and is_point_right_of_left_segment

        if is_point_inside_cone:
            points_in_cone_.append(point)

    return points_in_cone_


def is_inside_cone(apex_to_axis_point: Line2, other: Vector2, span: Angle) -> bool:
    # TODO: The oddity of comparing to span instead of normalized span
    #       happened because I couldn't think of a more consistent way of doing it.
    #       I think it is a poor idea that is screaming for a better solution,
    #       that unfortunately I don't have the capacity to think of in this moment.

    normalized_span: Angle = span % Angle(degree=360)
    half_span: Angle = normalized_span / 2

    right_span: Vector2 = apex_to_axis_point.point1.revolve(angle=half_span, basis=apex_to_axis_point.point0)
    left_span: Vector2 = apex_to_axis_point.point1.revolve(angle=-half_span, basis=apex_to_axis_point.point0)

    local_other: Vector2 = other.global_to_local(basis=apex_to_axis_point.point0)
    local_right: Vector2 = left_span.global_to_local(basis=apex_to_axis_point.point0)
    local_left: Vector2 = right_span.global_to_local(basis=apex_to_axis_point.point0)

    epsilon: Decimal = Decimal("0.0000000000001")  # Counter numerical imprecision from floating point noise.

    if span <= Angle(degree=180):
        is_point_to_left_of_right_span: bool = local_right.cross(other=local_other) > -epsilon
        is_point_to_right_of_left_span: bool = local_left.cross(other=local_other) < epsilon
        is_point_in_cone: bool = is_point_to_left_of_right_span and is_point_to_right_of_left_span

        if span == Angle(degree=0):
            is_point_in_cone &= -epsilon < apex_to_axis_point.point1.dot(other=other) - 1 < epsilon
    else:
        is_point_to_right_of_right_span: bool = local_right.cross(other=local_other) < -epsilon
        is_point_to_left_of_left_span: bool = local_left.cross(other=local_other) > epsilon
        is_point_in_cone: bool = not (is_point_to_right_of_right_span and is_point_to_left_of_left_span)

    return is_point_in_cone


def is_inside_n_gon_margin(point: Vector2, edges: list[Line2], margin: Decimal) -> bool:
    # This assumes that the point is already known to be inside the polygon.

    edge_distances: list[Decimal] = [edge.perpendicular_distance(point=point)
                                     for edge in edges]

    is_all_distances_inside_margin: bool = any(distance <= margin for distance in edge_distances)

    return is_all_distances_inside_margin
