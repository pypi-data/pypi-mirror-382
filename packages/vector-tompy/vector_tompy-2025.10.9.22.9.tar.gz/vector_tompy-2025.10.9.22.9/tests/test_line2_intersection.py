from decimal import Decimal

import pytest

from src.vector_tompy.exceptions import NoLinesIntersectionError
from src.vector_tompy.line2 import Line2, Line2Injector
from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_intersection_q1_q3_q4_success():
    # Setup
    line0_start: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal(2))
    line0_end: Vector2 = Vector2Injector.from_decimal(x=Decimal(4), y=Decimal(4))
    line0: Line2 = Line2Injector.from_vectors(point0=line0_start, point1=line0_end)
    line1_start: Vector2 = Vector2Injector.from_decimal(x=Decimal(3), y=Decimal(-2))
    line1_end: Vector2 = Vector2Injector.from_decimal(x=Decimal(-2), y=Decimal(-2))
    line1: Line2 = Line2Injector.from_vectors(point0=line1_start, point1=line1_end)
    intersection0: Vector2 = Vector2Injector.from_decimal(x=Decimal(-5), y=Decimal(-2))

    # Execution
    intersection1: Vector2 = line0.intersection(other=line1)

    # Validation
    assert intersection0 == intersection1


def test_intersection_parallel_failure():
    # Setup
    line0_start: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal(2))
    line0_end: Vector2 = Vector2Injector.from_decimal(x=Decimal(4), y=Decimal(4))
    line0: Line2 = Line2Injector.from_vectors(point0=line0_start, point1=line0_end)
    line1_start: Vector2 = Vector2Injector.from_decimal(x=Decimal(-3), y=Decimal(1))
    line1_end: Vector2 = Vector2Injector.from_decimal(x=Decimal(-6), y=Decimal(-1))
    line1: Line2 = Line2Injector.from_vectors(point0=line1_start, point1=line1_end)

    # Validation
    with pytest.raises(NoLinesIntersectionError):
        line0.intersection(other=line1)
