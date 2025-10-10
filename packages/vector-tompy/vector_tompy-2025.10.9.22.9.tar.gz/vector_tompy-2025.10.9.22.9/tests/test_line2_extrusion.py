from decimal import Decimal

from src.vector_tompy.line2 import Line2, Line2Injector
from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_line2_extrusion_success():
    # Setup
    width0: Decimal = Decimal("2")
    point0: Vector2 = Vector2Injector.from_decimal(x=Decimal(3), y=Decimal(4))
    point1: Vector2 = Vector2Injector.from_decimal(x=Decimal(11), y=Decimal(4))
    line0: Line2 = Line2Injector.from_vectors(point0=point0, point1=point1)
    extruded0: Vector2 = Vector2Injector.from_decimal(x=Decimal(3), y=Decimal(5))
    extruded1: Vector2 = Vector2Injector.from_decimal(x=Decimal(11), y=Decimal(5))
    extruded2: Vector2 = Vector2Injector.from_decimal(x=Decimal(11), y=Decimal(3))
    extruded3: Vector2 = Vector2Injector.from_decimal(x=Decimal(3), y=Decimal(3))
    points0: tuple[Vector2, Vector2, Vector2, Vector2] = (extruded0, extruded1, extruded2, extruded3)

    # Execution
    points1: tuple[Vector2, Vector2, Vector2, Vector2] = line0.extrusion(width=width0)

    # Validation
    assert points0 == points1
