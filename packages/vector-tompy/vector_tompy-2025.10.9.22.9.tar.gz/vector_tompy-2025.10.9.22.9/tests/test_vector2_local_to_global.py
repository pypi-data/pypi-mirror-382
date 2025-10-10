from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_local_to_global_basis_origin_no_change_success():
    # Setup
    global0: Vector2 = Vector2Injector.from_number(x=3, y=5)
    basis0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    local0: Vector2 = Vector2Injector.from_number(x=3, y=5)

    # Execution
    local1: Vector2 = global0.local_to_global(basis=basis0)

    # Validation
    assert local0 == local1


def test_local_to_global_basis_other_translation_success():
    # Setup
    global0: Vector2 = Vector2Injector.from_number(x=-1, y=3)
    basis0: Vector2 = Vector2Injector.from_number(x=4, y=2)
    local0: Vector2 = Vector2Injector.from_number(x=3, y=5)

    # Execution
    local1: Vector2 = global0.local_to_global(basis=basis0)

    # Validation
    assert local0 == local1
