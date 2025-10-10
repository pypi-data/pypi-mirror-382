from decimal import Decimal

import sympy as sp

from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_from_point_success():
    # Setup
    point0: sp.Point2D = sp.Point2D(1, 2)
    x0: Decimal = Decimal("1")
    y0: Decimal = Decimal("2")

    # Execution
    vector0: Vector2 = Vector2Injector.from_point(point=point0)

    # Validation
    assert x0 == vector0.x
    assert y0 == vector0.y
    assert isinstance(vector0.x, Decimal)
    assert isinstance(vector0.y, Decimal)
