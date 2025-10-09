class BaseAngleException(Exception):
    """Base exception for Angle project."""


class AngleInitValueError(BaseAngleException):
    """Raise for angles initialized with incorrect value(s)."""


class ValueIsNotAnAngleError(BaseAngleException):
    """Raise when comparing an Angle to a value that is not an Angle."""


class AngleOptionsNotInExpectedRangeError(BaseAngleException):
    """Raise when none of the Angle options fit with the comparison."""


class WrongValueAmountError(BaseAngleException):
    """Unexpected amount of values."""


class NoAngleLeftInSubsetToMatchError(BaseAngleException):
    """Too few Angles in subset compared with Angles in combination."""
