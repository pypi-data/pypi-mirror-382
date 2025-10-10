from decimal import Decimal

from src.vector_tompy.vector2 import Vector2, Vector2Injector, positions_from


def test_positions_from_one_sample_one_resolution_success():
    # Setup
    samples_x0: int = 1
    samples_y0: int = 1
    resolution0: Decimal = Decimal(1)

    vector0: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal(0))
    vectors0: list[Vector2] = [vector0]

    # Execution
    vectors1: list[Vector2] = list(positions_from(samples_x=samples_x0, samples_y=samples_y0, resolution=resolution0))

    # Validation
    assert vectors0 == vectors1


def test_positions_from_four_sample_two_resolution_success():
    # Setup
    samples_x0: int = 2
    samples_y0: int = 2
    resolution0: Decimal = Decimal(2)

    vector0: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal(0))
    vector1: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal(2))
    vector2: Vector2 = Vector2Injector.from_decimal(x=Decimal(2), y=Decimal(0))
    vector3: Vector2 = Vector2Injector.from_decimal(x=Decimal(2), y=Decimal(2))
    vectors0: list[Vector2] = [vector0, vector1, vector2, vector3]

    # Execution
    vectors1: list[Vector2] = list(positions_from(samples_x=samples_x0, samples_y=samples_y0, resolution=resolution0))

    # Validation
    assert vectors0 == vectors1


def test_positions_from_three_and_four_sample_half_resolution_success():
    # Setup
    samples_x0: int = 3
    samples_y0: int = 4
    resolution0: Decimal = Decimal("0.5")

    vector0: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal(0))
    vector1: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal("0.5"))
    vector2: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal(1))
    vector3: Vector2 = Vector2Injector.from_decimal(x=Decimal(0), y=Decimal("1.5"))
    vector4: Vector2 = Vector2Injector.from_decimal(x=Decimal("0.5"), y=Decimal(0))
    vector5: Vector2 = Vector2Injector.from_decimal(x=Decimal("0.5"), y=Decimal("0.5"))
    vector6: Vector2 = Vector2Injector.from_decimal(x=Decimal("0.5"), y=Decimal(1))
    vector7: Vector2 = Vector2Injector.from_decimal(x=Decimal("0.5"), y=Decimal("1.5"))
    vector8: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal(0))
    vector9: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal("0.5"))
    vector10: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal(1))
    vector11: Vector2 = Vector2Injector.from_decimal(x=Decimal(1), y=Decimal("1.5"))
    vectors0: list[Vector2] = [vector0, vector1, vector2, vector3,
                               vector4, vector5, vector6, vector7,
                               vector8, vector9, vector10, vector11]

    # Execution
    vectors1: list[Vector2] = list(positions_from(samples_x=samples_x0, samples_y=samples_y0, resolution=resolution0))

    # Validation
    assert vectors0 == vectors1
