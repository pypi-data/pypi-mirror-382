import pytest

from src.vector_tompy.exceptions import EmptyIterableError
from src.vector_tompy.vector2 import Vector2, median, Vector2Injector


def test_median_empty_success():
    # Setup
    points0: list[Vector2] = []

    # Validation
    with pytest.raises(EmptyIterableError):
        _ = median(points=points0)


def test_median_single_point_success():
    # Setup
    point0: Vector2 = Vector2Injector.from_number(x=3, y=5)
    point1: Vector2 = Vector2Injector.from_number(x=3, y=5)
    points0: list[Vector2] = [point0]

    # Execution
    point2: Vector2 = median(points=points0)

    # Validation
    assert point1 == point2


def test_median_two_points_success():
    # Setup
    point0: Vector2 = Vector2Injector.from_number(x=2, y=2)
    point1: Vector2 = Vector2Injector.from_number(x=4, y=4)
    point2: Vector2 = Vector2Injector.from_number(x=3, y=3)
    points0: list[Vector2] = [point0, point1]

    # Execution
    point3: Vector2 = median(points=points0)

    # Validation
    assert point2 == point3


def test_median_four_points_success():
    # Setup
    point0: Vector2 = Vector2Injector.from_number(x=5, y=5)
    point1: Vector2 = Vector2Injector.from_number(x=-3, y=5)
    point2: Vector2 = Vector2Injector.from_number(x=-3, y=-3)
    point3: Vector2 = Vector2Injector.from_number(x=5, y=-3)
    point4: Vector2 = Vector2Injector.from_number(x=1, y=1)
    points0: list[Vector2] = [point0, point1, point2, point3]

    # Execution
    point5: Vector2 = median(points=points0)

    # Validation
    assert point4 == point5
