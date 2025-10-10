from decimal import Decimal

from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_vector2_scale_no_basis_success():
    # Setup
    factor0: Decimal = Decimal(3)
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=2)
    vector1: Vector2 = Vector2Injector.from_number(x=-6, y=6)

    # Execution
    vector2: Vector2 = vector0.scale(factor=factor0)

    # Validation
    assert vector1 == vector2


def test_vector2_scale_basis_origin_success():
    # Setup
    factor0: Decimal = Decimal(-4)
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=2)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    vector1: Vector2 = Vector2Injector.from_number(x=8, y=-8)

    # Execution
    vector2: Vector2 = vector0.scale(factor=factor0, basis=basis0)

    # Validation
    assert vector1 == vector2


def test_vector2_scale_basis_transform_success():
    # Setup
    factor0: Decimal = Decimal(2)
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=2)
    basis0: Vector2 = Vector2Injector.from_number(x=4, y=2)
    vector1: Vector2 = Vector2Injector.from_number(x=-8, y=2)

    # Execution
    vector2: Vector2 = vector0.scale(factor=factor0, basis=basis0)

    # Validation
    assert vector1 == vector2
