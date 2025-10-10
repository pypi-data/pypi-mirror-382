from decimal import Decimal

import pytest

from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test__getitem__index_zero_success():
    # Setup
    value0: Decimal = Decimal("1")
    vector0: Vector2 = Vector2Injector.from_number(x=1, y=0)

    # Validation
    assert value0 == vector0[0]


def test__getitem__index_one_success():
    # Setup
    value0: Decimal = Decimal("1")
    vector0: Vector2 = Vector2Injector.from_number(x=0, y=1)

    # Validation
    assert value0 == vector0[1]


def test__getitem__index_two_failure():
    vector0: Vector2 = Vector2Injector.from_number(x=0, y=0)

    # Validation
    with pytest.raises(IndexError):
        _ = vector0[2]
