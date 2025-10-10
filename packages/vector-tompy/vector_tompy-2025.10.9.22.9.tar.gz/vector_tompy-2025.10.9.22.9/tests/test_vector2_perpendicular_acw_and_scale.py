from decimal import Decimal

from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_vector2_perpendicular_acw_and_scale_basis_none_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=2, y=-3)
    factor0: Decimal = Decimal(2)
    vector1: Vector2 = Vector2Injector.from_number(x=6, y=4)

    # Execution
    vector2: Vector2 = vector0.perpendicular_acw_and_scale(factor=factor0)

    # Validation
    assert vector1 == vector2


def test_vector2_perpendicular_acw_and_scale_basis_origin_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=2, y=-3)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    factor0: Decimal = Decimal(2)
    vector1: Vector2 = Vector2Injector.from_number(x=6, y=4)

    # Execution
    vector2: Vector2 = vector0.perpendicular_acw_and_scale(factor=factor0, basis=basis0)

    # Validation
    assert vector1 == vector2


def test_vector2_perpendicular_acw_and_scale_basis_transform_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=4, y=6)
    basis0: Vector2 = Vector2Injector.from_number(x=-2, y=-4)
    factor0: Decimal = Decimal("2.5")
    vector1: Vector2 = Vector2Injector.from_number(x=-27, y=11)

    # Execution
    vector2: Vector2 = vector0.perpendicular_acw_and_scale(factor=factor0, basis=basis0)

    # Validation
    assert vector1 == vector2
