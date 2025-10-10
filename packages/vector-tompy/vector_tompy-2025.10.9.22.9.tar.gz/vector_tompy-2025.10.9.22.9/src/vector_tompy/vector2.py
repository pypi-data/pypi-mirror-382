from decimal import Decimal
from math import sqrt
from statistics import median as stat_median, StatisticsError
from typing import Iterator, Union, Sequence, Iterable

import sympy as sp

from angle_tompy.angle_decimal import Angle
from math_tompy.decimal import cos, sin, acos, PI
from math_tompy.symbolic import expr_to_calc

from .exceptions import EmptyIterableError


# TODO: Make Vector2 immutable
class Vector2:

    def __init__(self, x: Decimal, y: Decimal) -> None:
        self._x: Decimal = x
        self._y: Decimal = y

    def __add__(self, other: "Vector2") -> "Vector2":
        x_: Decimal = self.x + other.x
        y_: Decimal = self.y + other.y
        vector: "Vector2" = Vector2Injector.from_decimal(x=x_, y=y_)
        return vector

    def __iadd__(self, other: "Vector2") -> "Vector2":
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Vector2") -> "Vector2":
        x_: Decimal = self.x - other.x
        y_: Decimal = self.y - other.y
        vector: "Vector2" = Vector2Injector.from_decimal(x=x_, y=y_)
        return vector

    def __isub__(self, other: "Vector2") -> "Vector2":
        self.x = self.x - other.x
        self.y = self.y - other.y
        return self

    def __mul__(self, other: Decimal) -> "Vector2":
        x_: Decimal = self.x * other
        y_: Decimal = self.y * other
        vector: "Vector2" = Vector2Injector.from_decimal(x=x_, y=y_)
        return vector

    def __rmul__(self, other: Decimal) -> "Vector2":
        vector: "Vector2" = self * other
        return vector

    def __imul__(self, other: Decimal) -> "Vector2":
        self.x *= other
        self.y *= other
        return self

    def __abs__(self) -> Decimal:
        length = self.magnitude()
        return length

    def __iter__(self) -> Iterator[Decimal]:
        return iter([self.x, self.y])

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int | slice) -> Decimal:
        if isinstance(index, int):
            if index == 0:
                value: Decimal = self.x
            elif index == 1:
                value: Decimal = self.y
            else:
                raise IndexError(f"Index '{index}' out of valid range [0, 1].")
        elif isinstance(index, slice):
            # if wraparound:
            #     value: "Vector2" = self._get_slice_with_wraparound(slice_=index)
            # else:
            #     value: "Vector2" = self._get_slice(slice_=index)
            raise ValueError(f"__getitem__ does not support slice.")
        else:
            raise ValueError(f"__getitem__ requires an integer or a slice, not a {type(index)}.")
        return value

    def __eq__(self, other: "Vector2") -> bool:
        equality: bool = False
        same_type: bool = isinstance(other, type(self))
        if same_type:
            same_x: bool = self.x == other.x
            same_y: bool = self.y == other.y
            equality = same_x and same_y
        return equality

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    def __copy__(self) -> "Vector2":
        duplicate: "Vector2" = Vector2Injector.from_vector(vector=self)
        return duplicate

    @property
    def x(self) -> Decimal:
        return self._x

    @x.setter
    def x(self, value: Decimal) -> None:
        self._x = value

    @property
    def y(self) -> Decimal:
        return self._y

    @y.setter
    def y(self, value: Decimal) -> None:
        self._y = value

    def as_tuple(self) -> tuple[Decimal, Decimal]:
        tuple_: tuple[Decimal, Decimal] = (self.x, self.y)
        return tuple_

    def copy(self) -> "Vector2":
        duplicate: "Vector2" = self.__copy__()
        return duplicate

    def normalize(self, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        length: Decimal = local_vector.magnitude()
        if length != 0:
            x_: Decimal = local_vector.x / length
            y_: Decimal = local_vector.y / length
        else:
            x_: Decimal = Decimal("0")
            y_: Decimal = Decimal("0")
        vector: "Vector2" = Vector2Injector.from_decimal(x=x_, y=y_)
        global_vector: "Vector2" = vector.local_to_global(basis=basis)
        return global_vector

    def magnitude(self, basis: Union["Vector2", None] = None) -> Decimal:
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        pair_squares: list[Decimal] = [Decimal((value0 - value1) ** 2) for value0, value1 in zip(self, basis)]
        square_sum: Decimal = Decimal(sum(pair_squares))
        root_of_pair_square_sum: Decimal = Decimal(sqrt(square_sum))
        return root_of_pair_square_sum

    def scale(self, factor: Decimal, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        scaled_vector: "Vector2" = local_vector * factor
        global_vector: "Vector2" = scaled_vector.local_to_global(basis=basis)
        return global_vector

    def dot(self, other: "Vector2") -> Decimal:
        dot_: Decimal = self.x * other.x + self.y * other.y
        return dot_

    def cross(self, other: "Vector2") -> Decimal:
        cross_: Decimal = self.x * other.y - self.y * other.x
        return cross_

    def opposite(self, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        opposite_vector: "Vector2" = Vector2Injector.from_decimal(x=-local_vector.x, y=-local_vector.y)
        global_vector: "Vector2" = opposite_vector.local_to_global(basis=basis)
        return global_vector

    def perpendicular_clockwise(self, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        perpendicular_vector: "Vector2" = Vector2Injector.from_decimal(x=local_vector.y, y=-local_vector.x)
        global_vector: "Vector2" = perpendicular_vector.local_to_global(basis=basis)
        return global_vector

    def perpendicular_anticlockwise(self, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        perpendicular_vector: "Vector2" = Vector2Injector.from_decimal(x=-local_vector.y, y=local_vector.x)
        global_vector: "Vector2" = perpendicular_vector.local_to_global(basis=basis)
        return global_vector

    def perpendicular_cw_and_scale(self, factor: Decimal, basis: Union["Vector2", None] = None) -> "Vector2":
        perpendicular_vector: Vector2 = self.perpendicular_clockwise(basis=basis)
        scaled_vector: Vector2 = perpendicular_vector.scale(factor=factor, basis=basis)
        return scaled_vector

    def perpendicular_acw_and_scale(self, factor: Decimal, basis: Union["Vector2", None] = None) -> "Vector2":
        perpendicular_vector: Vector2 = self.perpendicular_anticlockwise(basis=basis)
        scaled_vector: Vector2 = perpendicular_vector.scale(factor=factor, basis=basis)
        return scaled_vector

    # TODO: create version of *cw_and_scale that creates specific magnitude *cw_with_magnitude ?

    def revolve(self, angle: Angle, basis: Union["Vector2", None] = None) -> "Vector2":
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector: "Vector2" = self.global_to_local(basis=basis)
        x_revolved: Decimal = cos(angle=angle.as_radian()) * local_vector.x - \
                              sin(angle=angle.as_radian()) * local_vector.y
        y_revolved: Decimal = sin(angle=angle.as_radian()) * local_vector.x + \
                              cos(angle=angle.as_radian()) * local_vector.y
        revolved_vector: Vector2 = Vector2Injector.from_decimal(x=x_revolved, y=y_revolved)
        global_vector: "Vector2" = revolved_vector.local_to_global(basis=basis)
        return global_vector

    def sweep_between(self, other: "Vector2", basis: Union["Vector2", None] = None) -> Angle:
        if basis is None:
            basis = Vector2Injector.from_number(x=0, y=0)
        local_vector_self: "Vector2" = self.global_to_local(basis=basis)
        local_vector_other: "Vector2" = other.global_to_local(basis=basis)
        magnitudes: Decimal = local_vector_self.magnitude() * local_vector_other.magnitude()
        dot_prod: Decimal = local_vector_self.dot(other=local_vector_other)
        ratio: Decimal = dot_prod / magnitudes
        angle_value: Decimal = acos(ratio=ratio)
        cross_prod: Decimal = self.cross(other=other)
        angle_sign: Decimal = Decimal("1").copy_sign(cross_prod)
        angle_: Angle = Angle(radian=angle_value) * angle_sign
        return angle_

    def global_to_local(self, basis: "Vector2") -> "Vector2":
        local_vector: "Vector2" = self - basis
        return local_vector

    def local_to_global(self, basis: "Vector2") -> "Vector2":
        global_vector: "Vector2" = self + basis
        return global_vector


class Vector2Injector:
    @staticmethod
    def from_vector(vector: Vector2) -> Vector2:
        new_vector: Vector2 = Vector2Injector.from_decimal(x=vector.x, y=vector.y)
        return new_vector

    @staticmethod
    def from_point(point: sp.Point2D) -> Vector2:
        x: Decimal = Decimal(expr_to_calc(expression=point.x).result())
        y: Decimal = Decimal(expr_to_calc(expression=point.y).result())
        vector: Vector2 = Vector2Injector.from_decimal(x=x, y=y)
        return vector

    @staticmethod
    def from_decimal(x: Decimal, y: Decimal) -> Vector2:
        vector: Vector2 = Vector2(x=x, y=y)
        return vector

    @staticmethod
    def from_decimals(items: Sequence[Decimal]) -> list[Vector2]:
        vectors: list[Vector2] = []

        if len(items) % 2 == 0:
            iterator: Iterator[Decimal] = iter(items)
            for first, second in zip(iterator, iterator):
                vector: Vector2 = Vector2(x=first, y=second)
                vectors.append(vector)
        else:
            raise ValueError(f"'{len(items)}' is not an even amount.")

        return vectors

    @staticmethod
    def from_number(x: int | float, y: int | float) -> Vector2:
        x: Decimal = Decimal(x)
        y: Decimal = Decimal(y)
        vector: Vector2 = Vector2Injector.from_decimal(x=x, y=y)
        return vector


def positions_from(samples_x: int, samples_y: int, resolution: Decimal) -> Iterator[Vector2]:
    x_positions: list[Decimal] = [sample * resolution for sample in range(0, samples_x)]
    y_positions: list[Decimal] = [sample * resolution for sample in range(0, samples_y)]

    positions: Iterator[Vector2] = (Vector2Injector.from_decimal(x=x, y=y) for x in x_positions for y in y_positions)

    return positions


def bounding_box(points: Sequence[Vector2]) -> tuple[Vector2, Decimal, Decimal]:
    # Calculates axis-oriented bounding box for point cloud
    # Outputs min-x/y point, followed by positive height, and width values
    if len(points) == 0:
        raise EmptyIterableError(f"Input list is empty.")

    x_min = Decimal('Infinity')
    x_max = Decimal('-Infinity')
    y_min = Decimal('Infinity')
    y_max = Decimal('-Infinity')

    for point in points:
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

    point = Vector2Injector.from_decimal(x=x_min, y=y_min)
    width: Decimal = x_max - x_min
    height: Decimal = y_max - y_min
    return point, width, height


def centroid(points: Sequence[Vector2]) -> Vector2:
    point_amount: int = len(points)

    xs = [point.x for point in points]
    ys = [point.y for point in points]

    x = sum(xs) / point_amount
    y = sum(ys) / point_amount

    point: Vector2 = Vector2Injector.from_decimal(x=Decimal(x), y=Decimal(y))

    return point


def median(points: Iterable[Vector2]) -> Vector2:
    xs: list[Decimal] = [point.x for point in points]
    ys: list[Decimal] = [point.y for point in points]

    try:
        x_median: Decimal = stat_median(data=xs)
        y_median: Decimal = stat_median(data=ys)
    except StatisticsError as exception:
        if "no median for empty data" in exception.args:
            raise EmptyIterableError(f"Iterable is empty.") from exception
        else:
            raise exception

    point: Vector2 = Vector2Injector.from_decimal(x=x_median, y=y_median)

    return point


def shape_node_positions(edges: int, radius: Decimal, direction: Vector2) -> list[Vector2]:
    angle_step_size: Angle = Angle(radian=2 * PI / edges)
    first_position: Vector2 = direction.normalize() * radius

    positions: list[Vector2] = [first_position]

    for _ in range(edges-1):
        revolved_position: Vector2 = positions[-1].revolve(angle=angle_step_size)
        positions.append(revolved_position)

    return positions
