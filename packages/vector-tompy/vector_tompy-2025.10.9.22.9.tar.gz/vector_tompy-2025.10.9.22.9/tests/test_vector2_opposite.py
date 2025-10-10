from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_vector2_opposite_no_basis_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    vector1: Vector2 = Vector2Injector.from_number(x=1, y=-1)

    # Execution
    vector2: Vector2 = vector0.opposite()

    # Validation
    assert vector1 == vector2


def test_vector2_opposite_basis_origin_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    vector1: Vector2 = Vector2Injector.from_number(x=1, y=-1)

    # Execution
    vector2: Vector2 = vector0.opposite(basis=basis0)

    # Validation
    assert vector1 == vector2


def test_vector2_opposite_basis_transform_success():
    # Setup
    vector0: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    basis0: Vector2 = Vector2Injector.from_number(x=1, y=-2)
    vector1: Vector2 = Vector2Injector.from_number(x=3, y=-5)

    # Execution
    vector2: Vector2 = vector0.opposite(basis=basis0)

    # Validation
    assert vector1 == vector2
