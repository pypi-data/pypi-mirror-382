import math

import pytest

from src.angle_tompy.angle import Angle, fit_value_to_option
from src.angle_tompy.exceptions import AngleOptionsNotInExpectedRangeError


def test_fit_value_to_option_60_from_60_90_120_success():
    # Setup
    options0: frozenset[Angle] = frozenset([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    value0: Angle = Angle(degree=60)
    value1: Angle = Angle(degree=60)

    # Execution
    value2: Angle = fit_value_to_option(value=value0, options=options0)

    # Validation
    assert value1 == value2


def test_fit_value_to_option_90_from_60_90_120_success():
    # Setup
    options0: frozenset[Angle] = frozenset([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    value0: Angle = Angle(degree=90)
    value1: Angle = Angle(degree=90)

    # Execution
    value2: Angle = fit_value_to_option(value=value0, options=options0)

    # Validation
    assert value1 == value2


def test_fit_value_to_option_120_from_60_90_120_success():
    # Setup
    options0: frozenset[Angle] = frozenset([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    value0: Angle = Angle(degree=120)
    value1: Angle = Angle(degree=120)

    # Execution
    value2: Angle = fit_value_to_option(value=value0, options=options0)

    # Validation
    assert value1 == value2


def test_fit_value_to_option_89_9_from_60_90_120_success():
    # Setup
    options0: frozenset[Angle] = frozenset([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    value0: Angle = Angle(degree=282.743338823081/math.pi)
    value1: Angle = Angle(degree=90)

    # Execution
    value2: Angle = fit_value_to_option(value=value0, options=options0)

    # Validation
    assert value1 == value2


def test_fit_value_to_option_45_from_60_90_120_failure():
    # Setup
    options0: frozenset[Angle] = frozenset([Angle(degree=60), Angle(degree=90), Angle(degree=120)])
    value0: Angle = Angle(degree=45)

    # Validation
    with pytest.raises(AngleOptionsNotInExpectedRangeError):
        _: Angle = fit_value_to_option(value=value0, options=options0)
