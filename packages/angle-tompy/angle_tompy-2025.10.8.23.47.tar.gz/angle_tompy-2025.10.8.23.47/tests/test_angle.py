from typing import List, Iterator

from contextlib import nullcontext as does_not_raise

import pytest

from src.angle_tompy.angle import Angle, sum_angles, Angles
from src.angle_tompy.exceptions import AngleInitValueError, ValueIsNotAnAngleError


########################################################################################################################


def test_init_degree_success():
    # Validation
    with does_not_raise():
        Angle(degree=0)


def test_init_radian_success():
    # Validation
    with does_not_raise():
        Angle(radian=0)


def test_init_both_degree_and_radian_success():
    # Validation
    with pytest.raises(AngleInitValueError):
        Angle(degree=0, radian=0)


def test_init_neither_degree_or_radian_success():
    # Validation
    with pytest.raises(AngleInitValueError):
        Angle()


########################################################################################################################


def test_angle_add_precision_success():
    # Setup
    angle0: Angle = Angle(degree=60)
    angle1: Angle = Angle(degree=90)
    angle2: Angle = Angle(degree=120)
    angle_sum0: Angle = Angle(degree=270)

    # Execution
    addition0: Angle = angle0 + angle1 + angle2
    addition1: Angle = angle2 + angle1 + angle0

    # Validation
    assert addition0 == addition1
    assert addition0 == angle_sum0
    assert addition1 == angle_sum0


########################################################################################################################


def test_angle_sub_precision_success():
    # Setup
    angle0: Angle = Angle(degree=480)
    angle1: Angle = Angle(degree=370)
    angle2: Angle = Angle(degree=50)
    angle_sub0: Angle = Angle(degree=60)
    angle_sub1: Angle = Angle(degree=-800)

    # Execution
    subtraction0: Angle = angle0 - angle1 - angle2
    subtraction1: Angle = angle2 - angle1 - angle0

    # Validation
    assert subtraction0 == angle_sub0
    assert subtraction1 == angle_sub1


########################################################################################################################


def test_angle_sum_precision_success():
    # Setup
    angle0: Angle = Angle(degree=60)
    angle1: Angle = Angle(degree=90)
    angle2: Angle = Angle(degree=120)
    angle_sum0: Angle = Angle(degree=270)

    # Execution
    summing0: Angle = sum([angle0, angle1, angle2], Angle(degree=0))
    summing1: Angle = sum([angle2, angle1, angle0], Angle(degree=0))

    # Validation
    assert summing0 == summing1
    assert summing0 == angle_sum0
    assert summing1 == angle_sum0


def test_angle_sum_angles_precision_success():
    # Setup
    angle0: Angle = Angle(degree=60)
    angle1: Angle = Angle(degree=90)
    angle2: Angle = Angle(degree=120)
    angle_sum0: Angle = Angle(degree=270)

    # Execution
    summing0: Angle = sum_angles([angle0, angle1, angle2])
    # summing0: Angle = sum_angles([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    summing1: Angle = sum_angles([angle2, angle1, angle0])
    # summing1: Angle = sum_angles([Angle(degree=120), Angle(degree=90), Angle(degree=60)])

    # Validation
    assert summing0 == summing1
    assert summing0 == angle_sum0
    assert summing1 == angle_sum0


"""
def test_angle_sum_calculation_comparison_success():
    angle_basic: Angle = Angle(degree=180)
    angle_add: Angle = Angle(degree=50) + Angle(degree=60) + Angle(degree=70)
    angle_add_reverse: Angle = Angle(degree=70) + Angle(degree=60) + Angle(degree=50)
    angle_sum: Angle = sum([Angle(degree=50), Angle(degree=60), Angle(degree=70)], Angle(degree=0))
    angle_sum_reverse: Angle = sum([Angle(degree=70), Angle(degree=60), Angle(degree=50)], Angle(degree=0))
    angle_sum_generator: Angle = sum((Angle(degree=50), Angle(degree=60), Angle(degree=70)), Angle(degree=0))
    angle_sum_generator_reverse: Angle = sum((Angle(degree=70), Angle(degree=60), Angle(degree=50)), Angle(degree=0))
    angle_sum_angles: Angle = sum_angles([Angle(degree=50), Angle(degree=60), Angle(degree=70)])
    angle_sum_angles_reverse: Angle = sum_angles([Angle(degree=70), Angle(degree=60), Angle(degree=50)])
    angle_sum_angles_generator: Angle = sum_angles((Angle(degree=50), Angle(degree=60), Angle(degree=70)))
    angle_sum_angles_generator_reverse: Angle = sum_angles((Angle(degree=70), Angle(degree=60), Angle(degree=50)))

    print()
    print(angle_basic==angle_add)
    print(angle_basic==angle_add_reverse)
    print(angle_basic==angle_sum)
    print(angle_basic==angle_sum_reverse)
    print(angle_basic==angle_sum_generator)
    print(angle_basic==angle_sum_generator_reverse)
    print(angle_basic==angle_sum_angles)
    print(angle_basic==angle_sum_angles_reverse)
    print(angle_basic==angle_sum_angles_generator)
    print(angle_basic==angle_sum_angles_generator_reverse)

    angle_basic: Angle = Angle(degree=270)
    angle_add: Angle = Angle(degree=60) + Angle(degree=90) + Angle(degree=120)
    angle_add_reverse: Angle = Angle(degree=120) + Angle(degree=90) + Angle(degree=60)
    angle_sum: Angle = sum([Angle(degree=60), Angle(degree=90), Angle(degree=120)], Angle(degree=0))
    angle_sum_reverse: Angle = sum([Angle(degree=120), Angle(degree=90), Angle(degree=60)], Angle(degree=0))
    angle_sum_generator: Angle = sum((Angle(degree=60), Angle(degree=90), Angle(degree=120)), Angle(degree=0))
    angle_sum_generator_reverse: Angle = sum((Angle(degree=120), Angle(degree=90), Angle(degree=60)), Angle(degree=0))
    angle_sum_angles: Angle = sum_angles([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    angle_sum_angles_reverse: Angle = sum_angles([Angle(degree=120), Angle(degree=90), Angle(degree=60)])
    angle_sum_angles_generator: Angle = sum_angles((Angle(degree=60), Angle(degree=90), Angle(degree=120)))
    angle_sum_angles_generator_reverse: Angle = sum_angles((Angle(degree=120), Angle(degree=90), Angle(degree=60)))

    print()
    print(angle_basic==angle_add)
    print(angle_basic==angle_add_reverse)
    print(simplify(angle_basic.as_degree() - angle_add_reverse.as_degree()))
    print(angle_basic==angle_sum)
    print(angle_basic==angle_sum_reverse)
    print(angle_basic==angle_sum_generator)
    print(angle_basic==angle_sum_generator_reverse)
    print(angle_basic==angle_sum_angles)
    print(angle_basic==angle_sum_angles_reverse)
    print(angle_basic==angle_sum_angles_generator)
    print(angle_basic==angle_sum_angles_generator_reverse)
    print()
    print(angle_add_reverse==angle_sum_reverse)
    print(angle_add_reverse==angle_sum_generator_reverse)
    print(angle_add_reverse==angle_sum_angles_reverse)
    print(angle_add_reverse==angle_sum_angles_generator_reverse)

    angle_basic: Angle = Angle(degree=270)
    angle_add: Angle = Angle(degree=60) + Angle(degree=90) + Angle(degree=120)
    angle_add_reverse: Angle = Angle(degree=120) + Angle(degree=90) + Angle(degree=60)
    angle_sum: Angle = sum([Angle(degree=60), Angle(degree=90), Angle(degree=120)], Angle(degree=0))
    angle_sum_reverse: Angle = sum([Angle(degree=120), Angle(degree=90), Angle(degree=60)], Angle(degree=0))
    angle_sum_generator: Angle = sum((Angle(degree=60), Angle(degree=90), Angle(degree=120)), Angle(degree=0))
    angle_sum_generator_reverse: Angle = sum((Angle(degree=120), Angle(degree=90), Angle(degree=60)), Angle(degree=0))
    angle_sum_angles: Angle = sum_angles([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    angle_sum_angles_reverse: Angle = sum_angles([Angle(degree=120), Angle(degree=90), Angle(degree=60)])
    angle_sum_angles_generator: Angle = sum_angles((Angle(degree=60), Angle(degree=90), Angle(degree=120)))
    angle_sum_angles_generator_reverse: Angle = sum_angles((Angle(degree=120), Angle(degree=90), Angle(degree=60)))

    print()
    print("angle_basic:", angle_basic, angle_basic.as_radian(), type(angle_basic.as_radian()))
    print("angle_basic nsimplify:", sp.nsimplify(angle_basic.as_radian()), type(sp.nsimplify(angle_basic.as_radian())))
    print("basic=add", angle_basic==angle_add)
    print("basic=add_rev", angle_basic==angle_add_reverse)
    print("basic=add_rev as rad_nsimplify", 
          sp.nsimplify(angle_basic.as_radian()) == sp.nsimplify(angle_add_reverse.as_radian()))
    print("basic=add_rev simpl deg sub:", sp.simplify(angle_basic.as_degree() - angle_add_reverse.as_degree()))
    print("basic=add_rev simpl deg eq:", 
          sp.simplify(angle_basic.as_degree()) == sp.simplify(angle_add_reverse.as_degree()))
    print("basic=add_rev nsimplify deg eq:", 
          sp.nsimplify(angle_basic.as_degree()) == sp.nsimplify(angle_add_reverse.as_degree()))
    print("basic=add_rev simpl rad sub:", sp.simplify(angle_basic.as_radian() - angle_add_reverse.as_radian()))
    print("basic=add_rev nsimplify rad sub:", sp.nsimplify(angle_basic.as_radian() - angle_add_reverse.as_radian()))
    print("basic=add_rev nsimplify rad sub:", 
          sp.nsimplify(angle_basic.as_radian()) - sp.nsimplify(angle_add_reverse.as_radian()))
    print("basic=add_rev simpl rad eq:", 
          sp.simplify(angle_basic.as_radian()) == sp.simplify(angle_add_reverse.as_radian()))
    print("basic=add_rev nsimplify rad eq:", 
          sp.nsimplify(angle_basic.as_radian()) == sp.nsimplify(angle_add_reverse.as_radian()))
    print(angle_basic==angle_sum)
    print(angle_basic==angle_sum_reverse)
    print(angle_basic==angle_sum_generator)
    print(angle_basic==angle_sum_generator_reverse)
    print(angle_basic==angle_sum_angles)
    print(angle_basic==angle_sum_angles_reverse)
    print(angle_basic==angle_sum_angles_generator)
    print(angle_basic==angle_sum_angles_generator_reverse)
    print()
    print(angle_add_reverse==angle_sum_reverse)
    print(angle_add_reverse==angle_sum_generator_reverse)
    print(angle_add_reverse==angle_sum_angles_reverse)
    print(angle_add_reverse==angle_sum_angles_generator_reverse)
"""


########################################################################################################################


def test_sum_angles_list_empty_success():
    # Setup
    angles0: Angles = Angles([])
    angle_sum0: Angle = Angle(degree=0)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_list_wrong_type_failure():
    # Setup
    angles0: Angles = Angles([None])

    # Validation
    with pytest.raises(ValueIsNotAnAngleError):
        sum_angles(angles=angles0)


def test_sum_angles_list_1_element_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=120)])
    angle_sum0: Angle = Angle(degree=120)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_list_5_elements_success():
    # Setup
    angles0: Angles = Angles(
        [Angle(degree=10), Angle(degree=20), Angle(degree=30), Angle(degree=40), Angle(degree=50)])
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_3_elements_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=10), Angle(degree=20), Angle(degree=30)])
    angles_iter0: Iterator[Angle] = iter(angles0)
    angle_sum0: Angle = Angle(degree=60)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_3_elements_reversed_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=30), Angle(degree=20), Angle(degree=10)])
    angles_iter0: Iterator[Angle] = iter(angles0)
    angle_sum0: Angle = Angle(degree=60)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_empty_success():
    # Setup
    angles0: Angles = Angles([])
    angles_iter0: Iterator[Angle] = iter(angles0)
    angle_sum0: Angle = Angle(degree=0)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_filter_without_filtered_values_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=40), Angle(degree=50), Angle(degree=60)])
    angles_iter0: Iterator[Angle] = iter(angle for angle in angles0 if angle is not None)
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    # assert angle_sum0 == angle_sum1
    assert angle_sum0.as_radian().equals(angle_sum1.as_radian())


def test_sum_angles_generator_filter_with_filtered_values_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=40), None, Angle(degree=50), Angle(degree=60), None])
    angles_iter0: Iterator[Angle] = iter(angle for angle in angles0 if angle is not None)
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_filter_without_filtered_angles_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=40), Angle(degree=50), Angle(degree=60)])
    angles_iter0: Iterator[Angle] = iter(angle for angle in angles0 if isinstance(angle, Angle))
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_filter_with_filtered_angles_success():
    # Setup
    angles0: Angles = Angles([Angle(degree=40), None, Angle(degree=50), Angle(degree=60), None])
    angles_iter0: Iterator[Angle] = iter(angle for angle in angles0 if isinstance(angle, Angle))
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles_iter0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_with_list_success():
    # Setup
    angles0: List[Angle] = [Angle(degree=40), Angle(degree=50), Angle(degree=60)]
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles0)

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_generator_with_list_reverse_success():
    # Setup
    angles0: List[Angle] = [Angle(degree=40), Angle(degree=50), Angle(degree=60)]
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=reversed(angles0))

    # Validation
    assert angle_sum0 == angle_sum1


def test_sum_angles_list_5_elements_reverse_success():
    # Setup
    angles0: Angles = Angles(
        [Angle(degree=50), Angle(degree=40), Angle(degree=30), Angle(degree=20), Angle(degree=10)])
    angle_sum0: Angle = Angle(degree=150)

    # Execution
    angle_sum1: Angle = sum_angles(angles=angles0)

    # Validation
    assert angle_sum0 == angle_sum1


########################################################################################################################


def test_neg_0_success():
    # Setup
    value0: int = 0
    angle0: Angle = Angle(degree=value0)

    # Execution
    angle1: Angle = -angle0

    # Validation
    assert value0 == angle1.as_degree()


def test_neg_1_success():
    # Setup
    value0: int = 1
    value1: int = -1
    angle0: Angle = Angle(degree=value0)

    # Execution
    angle1: Angle = -angle0

    # Validation
    assert (angle1.as_degree() - value1).is_zero


def test_neg_minus_1_success():
    # Setup
    value0: int = -1
    value1: int = 1
    angle0: Angle = Angle(degree=value0)

    # Execution
    angle1: Angle = -angle0

    # Validation
    assert (angle1.as_degree() - value1).is_zero


########################################################################################################################
