from angle_tompy.angle_decimal import Angle

from src.vector_tompy.area2 import is_inside_cone
from src.vector_tompy.line2 import Line2, Line2Injector
from src.vector_tompy.vector2 import Vector2, Vector2Injector


def test_is_inside_cone_one_of_eight_zero_degree_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=0)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 1
    assert point0 in points1


def test_is_inside_cone_one_of_eight_one_degree_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=1)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 1
    assert point0 in points1


def test_is_inside_cone_one_of_eight_eighty_nine_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=89)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 1
    assert point0 in points1


def test_is_inside_cone_three_of_eight_ninety_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=90)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 3
    assert point0 in points1
    assert point1 in points1
    assert point7 in points1


def test_is_inside_cone_three_of_eight_ninety_one_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=91)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 3
    assert point0 in points1
    assert point1 in points1
    assert point7 in points1


def test_is_inside_cone_three_of_eight_one_hundred_seventy_nine_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=179)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 3
    assert point0 in points1
    assert point1 in points1
    assert point7 in points1


def test_is_inside_cone_five_of_eight_one_hundred_eighty_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=180)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 5
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_five_of_eight_one_hundred_eighty_one_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=181)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 5
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_five_of_eight_two_hundred_sixty_nine_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=269)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 5
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_seven_of_eight_two_hundred_seventy_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=270)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 7
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point3 in points1
    assert point5 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_seven_of_eight_two_hundred_seventy_one_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=271)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 7
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point3 in points1
    assert point5 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_seven_of_eight_three_hundred_fifty_nine_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=359)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 7
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point3 in points1
    assert point5 in points1
    assert point6 in points1
    assert point7 in points1


def test_is_inside_cone_seven_of_eight_three_hundred_sixty_degrees_success():
    # Setup
    point_center0: Vector2 = Vector2Injector.from_number(x=0, y=0)
    point0: Vector2 = Vector2Injector.from_number(x=1, y=0)
    point1: Vector2 = Vector2Injector.from_number(x=1, y=1)
    point2: Vector2 = Vector2Injector.from_number(x=0, y=1)
    point3: Vector2 = Vector2Injector.from_number(x=-1, y=1)
    point4: Vector2 = Vector2Injector.from_number(x=-1, y=0)
    point5: Vector2 = Vector2Injector.from_number(x=-1, y=-1)
    point6: Vector2 = Vector2Injector.from_number(x=0, y=-1)
    point7: Vector2 = Vector2Injector.from_number(x=1, y=-1)
    points0: list[Vector2] = [point0, point1, point2, point3, point4, point5, point6, point7]
    apex_to_axis0: Line2 = Line2Injector.from_vectors(point0=point_center0, point1=point0)
    sweep0: Angle = Angle(degree=360)

    # Execution
    points1: list[Vector2] = [point for point in points0 if is_inside_cone(apex_to_axis_point=apex_to_axis0,
                                                                           other=point,
                                                                           span=sweep0)]

    # Validation
    assert len(points1) == 8
    assert point0 in points1
    assert point1 in points1
    assert point2 in points1
    assert point3 in points1
    assert point4 in points1
    assert point5 in points1
    assert point6 in points1
    assert point7 in points1


