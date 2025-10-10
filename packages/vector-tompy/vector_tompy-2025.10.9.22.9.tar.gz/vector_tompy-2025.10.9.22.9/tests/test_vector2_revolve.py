from decimal import Decimal

from angle_tompy.angle_decimal import Angle

from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_vector2_revolve_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: Vector2 = Vector2Injector.from_number(x=4, y=1)
    vector1: Vector2 = Vector2Injector.from_number(x=-4, y=-1)

    # Execution
    vector2: Vector2 = vector0.revolve(angle=angle0)

    # Validation
    assert abs(vector1.x - vector2.x) < Decimal("0.000000000000001")
    assert abs(vector1.y - vector2.y) < Decimal("0.000000000000001")


def test_vector2_revolve_basis_origin_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: Vector2 = Vector2Injector.from_number(x=4, y=1)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    vector1: Vector2 = Vector2Injector.from_number(x=-4, y=-1)

    # Execution
    vector2: Vector2 = vector0.revolve(angle=angle0, basis=basis0)

    # Validation
    assert abs(vector1.x - vector2.x) < Decimal("0.000000000000001")
    assert abs(vector1.y - vector2.y) < Decimal("0.000000000000001")


def test_vector2_revolve_basis_transform_success():
    # Setup
    angle0: Angle = Angle(degree=-90)
    vector0: Vector2 = Vector2Injector.from_number(x=-7, y=6)
    basis0: Vector2 = Vector2Injector.from_number(x=-3, y=2)
    vector1: Vector2 = Vector2Injector.from_number(x=1, y=6)

    # Execution
    vector2: Vector2 = vector0.revolve(angle=angle0, basis=basis0)

    # Validation
    assert abs(vector1.x - vector2.x) < Decimal("0.000000000000001")
    assert abs(vector1.y - vector2.y) < Decimal("0.000000000000001")
