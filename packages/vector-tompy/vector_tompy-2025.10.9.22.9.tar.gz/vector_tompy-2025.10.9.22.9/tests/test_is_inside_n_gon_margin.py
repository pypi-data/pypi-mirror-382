from decimal import Decimal

from src.vector_tompy.area2 import is_inside_n_gon_margin
from src.vector_tompy.line2 import Line2, Line2Injector
from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_is_inside_n_gon_margin_outside_success():
    # Setup
    edge0: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=1, y=1),
                                              point1=Vector2Injector.from_number(x=1, y=3))
    edges0: list[Line2] = [edge0]
    point0: Vector2 = Vector2Injector.from_number(x=3, y=2)
    margin0: Decimal = Decimal("1")
    boolean0: bool = False

    # Execution
    boolean1: bool = is_inside_n_gon_margin(edges=edges0, point=point0, margin=margin0)

    # Validation
    assert boolean0 is boolean1


def test_is_inside_n_gon_margin_inside_success():
    # Setup
    edge0: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=1, y=1),
                                              point1=Vector2Injector.from_number(x=1, y=3))
    edges0: list[Line2] = [edge0]
    point0: Vector2 = Vector2Injector.from_number(x=2, y=2)
    margin0: Decimal = Decimal("2")
    boolean0: bool = True

    # Execution
    boolean1: bool = is_inside_n_gon_margin(edges=edges0, point=point0, margin=margin0)

    # Validation
    assert boolean0 is boolean1


def test_is_inside_n_gon_margin_inside_and_outside_success():
    # Setup
    edge0: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=0, y=0),
                                              point1=Vector2Injector.from_number(x=1, y=0))
    edge1: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=1, y=0),
                                              point1=Vector2Injector.from_number(x=1, y=1))
    edge2: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=1, y=1),
                                              point1=Vector2Injector.from_number(x=0, y=1))
    edge3: Line2 = Line2Injector.from_vectors(point0=Vector2Injector.from_number(x=0, y=1),
                                              point1=Vector2Injector.from_number(x=0, y=0))
    edges0: list[Line2] = [edge0, edge1, edge2, edge3]
    point0: Vector2 = Vector2Injector.from_number(x=0.5, y=0.5)
    point1: Vector2 = Vector2Injector.from_number(x=0.4, y=0.4)
    point2: Vector2 = Vector2Injector.from_number(x=0.6, y=0.6)
    point3: Vector2 = Vector2Injector.from_number(x=0.5, y=0.4)
    point4: Vector2 = Vector2Injector.from_number(x=0.6, y=0.5)
    margin0: Decimal = Decimal("0.45")

    # Execution
    boolean0: bool = is_inside_n_gon_margin(edges=edges0, point=point0, margin=margin0)
    boolean1: bool = is_inside_n_gon_margin(edges=edges0, point=point1, margin=margin0)
    boolean2: bool = is_inside_n_gon_margin(edges=edges0, point=point2, margin=margin0)
    boolean3: bool = is_inside_n_gon_margin(edges=edges0, point=point3, margin=margin0)
    boolean4: bool = is_inside_n_gon_margin(edges=edges0, point=point4, margin=margin0)

    # Validation
    assert boolean0 is False
    assert boolean1 is True
    assert boolean2 is True
    assert boolean3 is True
    assert boolean4 is True
