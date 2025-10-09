import pytest

from src.angle_tompy.angle import Angle, is_angle_combo_match_angles_subset
from src.angle_tompy.exceptions import NoAngleLeftInSubsetToMatchError


def test_is_angle_combo_match_angles_subset_60_in_triangle_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    subset_index0: int = 0
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_90_in_square_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=90),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=90), Angle(degree=90), Angle(degree=90), Angle(degree=90))
    subset_index0: int = 0
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_120_and_120_and_120_in_hexagon_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=120), Angle(degree=120))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=120), Angle(degree=120),
                                        Angle(degree=120), Angle(degree=120), Angle(degree=120))
    subset_index0: int = 0
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_60_second_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 0
    is_match0: bool = False

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_60_third_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 1
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_120_second_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 0
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_120_and_60_second_and_third_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=60))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 0
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_60_and_120_third_and_fourth_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 1
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_60_and_120_and_60_third_and_fourth_and_first_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_index0: int = 1
    is_match0: bool = True

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_90_in_hexagon_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=90),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=120), Angle(degree=120),
                                        Angle(degree=120), Angle(degree=120), Angle(degree=120))
    subset_index0: int = 0
    is_match0: bool = False

    # Execution
    is_match1: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                        angle_subset=angle_subset0,
                                                        subset_index=subset_index0)

    # Validation
    assert is_match0 == is_match1


def test_is_angle_combo_match_angles_subset_60_and_60_and_60_in_triangle_failure():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    subset_index0: int = 0
    is_match0: bool = False

    # Validation
    with pytest.raises(NoAngleLeftInSubsetToMatchError):
        _: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination0,
                                                     angle_subset=angle_subset0,
                                                     subset_index=subset_index0)
