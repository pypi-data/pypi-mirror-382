from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from iterable_tompy.head import head
from math_tompy.decimal import clamp_value

from .exceptions import NoLinesIntersectionError, UnexpectedUnpredictableError
from .vector2 import Vector2, Vector2Injector


# TODO: Make Line2 immutable
@dataclass
class Line2:
    point0: Vector2
    point1: Vector2

    def reverse(self) -> None:
        self.point0, self.point1 = self.point1, self.point0

    # TODO: possible to create intersection check based on maybe 4x cross calculations?
    #       did the thing in shape field project
    #       only useful for line segments
    #       only return bool for intersection existence -- not a vector for the intersection position
    #       I wonder if it is faster than this intersection function
    def intersection(self, other: Self) -> Vector2:
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        l0p0: Vector2 = self.point0
        l0p1: Vector2 = self.point1
        l1p0: Vector2 = other.point0
        l1p1: Vector2 = other.point1
        denominator = (l0p0.x - l0p1.x) * (l1p0.y - l1p1.y) - (l0p0.y - l0p1.y) * (l1p0.x - l1p1.x)

        if denominator != Decimal("0"):
            x: Decimal = ((l0p0.x * l0p1.y - l0p0.y * l0p1.x) * (l1p0.x - l1p1.x) -
                          (l0p0.x - l0p1.x) * (l1p0.x * l1p1.y - l1p0.y * l1p1.x)) / denominator
            y: Decimal = ((l0p0.x * l0p1.y - l0p0.y * l0p1.x) * (l1p0.y - l1p1.y) -
                          (l0p0.y - l0p1.y) * (l1p0.x * l1p1.y - l1p0.y * l1p1.x)) / denominator
            intersection_: Vector2 = Vector2Injector.from_decimal(x=x, y=y)
        elif denominator == Decimal("0"):
            raise NoLinesIntersectionError(f"Lines are parallel as denominator is 0 "
                                           f"and thus does not have a single intersection.")
        else:
            raise UnexpectedUnpredictableError(f"The comparison of two values ('{0}', '{denominator}') "
                                               f"just went extremely unexpectedly wrong.")

        return intersection_

    def perpendicular_distance(self, point: Vector2, clamp_to_segment: bool = False) -> Decimal:
        line_direction: Vector2 = self.point1 - self.point0
        line_start_to_point: Vector2 = point - self.point0
        line_direction_squared: Decimal = line_direction.dot(other=line_direction)

        if line_direction_squared == Decimal("0"):
            perpendicular_distance: Decimal = line_start_to_point.magnitude()
        else:
            projection_scale: Decimal = line_start_to_point.dot(other=line_direction) / line_direction_squared

            if clamp_to_segment:
                projection_scale = clamp_value(value=projection_scale, low_bound=Decimal("0"), high_bound=Decimal("1"))

            closest_point_on_line: Vector2 = self.point0 + line_direction.scale(factor=projection_scale)
            perpendicular_vector: Vector2 = point - closest_point_on_line
            perpendicular_distance: Decimal = perpendicular_vector.magnitude()

        return perpendicular_distance

    def extrusion(self, width: Decimal) -> tuple[Vector2, Vector2, Vector2, Vector2]:
        """Extrude rectangular polygon along line on both sides equally."""

        factor: Decimal = width / Decimal(2)
        width_unit: Vector2 = self.point1.normalize(basis=self.point0)
        half_width_from_p0: Vector2 = width_unit.scale(factor=factor, basis=self.point0)
        half_width_from_p1: Vector2 = self.point1 + half_width_from_p0.global_to_local(basis=self.point0)

        p0_perpendicular_cw: Vector2 = half_width_from_p0.perpendicular_clockwise(basis=self.point0)
        p0_perpendicular_acw: Vector2 = half_width_from_p0.perpendicular_anticlockwise(basis=self.point0)
        p1_perpendicular_cw: Vector2 = half_width_from_p1.perpendicular_clockwise(basis=self.point1)
        p1_perpendicular_acw: Vector2 = half_width_from_p1.perpendicular_anticlockwise(basis=self.point1)

        point0: Vector2 = p0_perpendicular_acw
        point1: Vector2 = p1_perpendicular_acw
        point2: Vector2 = p1_perpendicular_cw
        point3: Vector2 = p0_perpendicular_cw

        return point0, point1, point2, point3


class Line2Injector:
    @staticmethod
    def from_vectors(point0: Vector2, point1: Vector2) -> Line2:
        line: Line2 = Line2(point0=point0, point1=point1)
        return line

    @staticmethod
    def from_base_scalar(base: Vector2, scalar: Vector2) -> Line2:
        point0: Vector2 = base
        point1: Vector2 = base + scalar
        line: Line2 = Line2(point0=point0, point1=point1)
        return line


def first_segment_from_points(segments: list[Line2], point0: Vector2, point1: Vector2) -> Line2 | None:
    first_segment: Line2 | None = None

    for segment in segments:
        if ((segment.point0 is point0 and segment.point1 is point1) or
                (segment.point0 is point1 and segment.point1 is point0)):
            first_segment = segment
            break  # Stop iterating when a segment has been found.

    return first_segment


def ordered_points_from_connected_segments(lines: list[Line2]) -> list[Vector2]:
    # Create ordered points list from line segments with intersecting end points.
    ordered_positions: list[Vector2] = []

    if len(lines) > 0:
        start_segment: Line2 = head(lines)
        current_segment: Line2 = start_segment
        ordered_positions.append(start_segment.point0)

        while True:
            for next_segment in lines:
                if next_segment is not current_segment:
                    is_next_segment_start_intersecting: bool = (current_segment.point1 == next_segment.point0 and
                                                                current_segment.point0 != next_segment.point1)
                    is_next_segment_end_intersecting: bool = (current_segment.point1 == next_segment.point1 and
                                                              current_segment.point0 != next_segment.point0)

                    if is_next_segment_start_intersecting:
                        pass  # all in place
                    elif is_next_segment_end_intersecting:
                        next_segment.reverse()
                    else:
                        continue  # skip to next segment

                    ordered_positions.append(next_segment.point0)
                    current_segment = next_segment
                    break
            else:
                raise ValueError(f"Segment ring is discontinuous.")

            if len(ordered_positions) > 2 * len(lines):
                raise ValueError(f"Registering way too many points. Something is not right.")

            if current_segment is start_segment:
                break

    return ordered_positions
