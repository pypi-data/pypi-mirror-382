from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_vector2_perpendicular_clockwise_no_basis_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=-2)
    vector1: Vector2 = Vector2Injector.from_number(x=-2, y=2)

    # Execution
    vector2: Vector2 = vector0.perpendicular_clockwise()

    # Validation
    assert vector1 == vector2


def test_vector2_perpendicular_clockwise_basis_origin_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=-2)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    vector1: Vector2 = Vector2Injector.from_number(x=-2, y=2)

    # Execution
    vector2: Vector2 = vector0.perpendicular_clockwise(basis=basis0)

    # Validation
    assert vector1 == vector2


def test_vector2_perpendicular_clockwise_basis_transform_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-2, y=-2)
    basis0: Vector2 = Vector2Injector.from_number(x=-4, y=-2)
    vector1: Vector2 = Vector2Injector.from_number(x=-4, y=-4)

    # Execution
    vector2: Vector2 = vector0.perpendicular_clockwise(basis=basis0)

    # Validation
    assert vector1 == vector2
