from angle_tompy.angle_decimal import Angle

from src.vector_tompy.vector2 import Vector2Injector, Vector2


def test_vector2_sweep_between_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: Vector2 = Vector2Injector.from_number(x=4, y=1)
    vector1: Vector2 = Vector2Injector.from_number(x=-4, y=-1)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q1_q2_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: Vector2 = Vector2Injector.from_number(x=1, y=1)
    vector1: Vector2 = Vector2Injector.from_number(x=-1, y=1)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q2_q3_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=-90)
    vector0: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    vector1: Vector2 = Vector2Injector.from_number(x=-1, y=1)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q3_q4_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    vector1: Vector2 = Vector2Injector.from_number(x=1, y=-1)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_q4_q1_basis_none_success():
    # Setup
    angle0: Angle = Angle(degree=90)
    vector0: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    vector1: Vector2 = Vector2Injector.from_number(x=1, y=1)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1)

    # Validation
    assert angle0 == angle1


def test_vector2_sweep_between_basis_middle_success():
    # Setup
    angle0: Angle = Angle(degree=180)
    vector0: Vector2 = Vector2Injector.from_number(x=4, y=5)
    vector1: Vector2 = Vector2Injector.from_number(x=-6, y=5)
    basis0: Vector2 = Vector2Injector.from_number(x=-1, y=5)

    # Execution
    angle1: Angle = vector0.sweep_between(other=vector1, basis=basis0)

    # Validation
    assert angle0 == angle1
