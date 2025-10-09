from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
from typing import TypeAlias, Union, Iterable

import sympy as sp
from iterable_tompy import first, indices_around_index
from py_cdll import CDLL

from .exceptions import AngleInitValueError, ValueIsNotAnAngleError, AngleOptionsNotInExpectedRangeError, \
    WrongValueAmountError, NoAngleLeftInSubsetToMatchError

Numeric: TypeAlias = Union[sp.Expr, float, int, Fraction, Decimal]


class Angle:
    # TODO: check Angle for performance and see where edges can be trimmed to reduce impact of using nsimplify

    def __init__(self, degree: Numeric | None = None, radian: Numeric | None = None) -> None:
        if (degree is None and radian is None) or (degree is not None and radian is not None):
            raise AngleInitValueError(f"Please input either degree or radian value, not neither or both!")

        self._radian: sp.Expr

        if degree is not None:
            # NOTE: Applying nsimplify at init is much more expensive than only applying it when calculating
            # self._radian = sp.nsimplify(degree / 180.0 * sp.pi, constants=[sp.pi], rational=True)
            self._radian = degree / 180.0 * sp.pi

        if radian is not None:
            # NOTE: Applying nsimplify at init is much more expensive than only applying it when calculating
            # self._radian = sp.nsimplify(radian, constants=[sp.pi], rational=True)
            self._radian = radian

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.as_degree():.1f})"

    def __add__(self, other: "Angle") -> "Angle":
        try:
            # NOTE: Significantly cheaper to apply nsimplify when calculating than on init
            angle_sum_in_radians: sp.Expr = sp.nsimplify(expr=self.as_radian() + other.as_radian(),
                                                         constants=[sp.pi],
                                                         rational=True)
            angle: Angle = Angle(radian=angle_sum_in_radians)
        except AttributeError:
            raise ValueIsNotAnAngleError(f"Other '{other}' of type '{type(other)}' is not an Angle.")
        return angle

    def __sub__(self, other: "Angle") -> "Angle":
        try:
            # NOTE: Significantly cheaper to apply nsimplify when calculating than on init
            angle_sub_in_radians: sp.Expr = sp.nsimplify(expr=self.as_radian() - other.as_radian(),
                                                         constants=[sp.pi],
                                                         rational=True)
            angle: Angle = Angle(radian=angle_sub_in_radians)
        except AttributeError:
            raise ValueIsNotAnAngleError(f"Other '{other}' of type '{type(other)}' is not an Angle.")
        return angle

    def __mul__(self, other) -> "Angle":
        new_angle: sp.Expr = self.as_radian() * other
        angle: Angle = Angle(radian=new_angle)
        return angle

    def __truediv__(self, other) -> "Angle":
        new_angle: sp.Expr = self.as_radian() / other
        angle: Angle = Angle(radian=new_angle)
        return angle

    def __neg__(self) -> "Angle":
        negated_value: sp.Expr = -1 * self._radian
        negated_angle: Angle = Angle(radian=negated_value)
        return negated_angle

    def __mod__(self, other: "Angle") -> "Angle":
        modulo_value: sp.Expr = self._radian % other._radian
        modulo_angle: Angle = Angle(radian=modulo_value)
        return modulo_angle

    def __lt__(self, other: "Angle") -> bool:
        less_than: bool = False
        if self._radian < other._radian:
            less_than = True
        return less_than

    def __le__(self, other: "Angle") -> bool:
        less_than_or_equal: bool = False
        if self._radian <= other._radian:
            less_than_or_equal = True
        return less_than_or_equal

    def __gt__(self, other: "Angle") -> bool:
        greater_than: bool = False
        if self._radian > other._radian:
            greater_than = True
        return greater_than

    def __ge__(self, other: "Angle") -> bool:
        greater_than_or_equal: bool = False
        if self._radian >= other._radian:
            greater_than_or_equal = True
        return greater_than_or_equal

    def __eq__(self, other: "Angle") -> bool:
        same_type: bool = isinstance(self, type(other))
        same_value: bool = False

        if same_type:
            # NOTE: Appears to not benefit from simplifying, when nsimplify is called on calculating value
            # same_value = sp.nsimplify(self._radian - other._radian, constants=[sp.pi], rational=True) == 0
            # same_value = self._radian - other._radian == 0
            difference: sp.Expr = self._radian - other._radian
            same_value = difference == 0
            # same_value = self._radian.equals(other=other._radian)

        return same_type and same_value

    def __hash__(self):
        # TODO: research whether sympy values are hashable
        return hash(self._radian)

    def as_radian(self) -> sp.Expr:
        return self._radian

    def as_degree(self) -> sp.Expr:
        return self._radian / sp.pi * 180.0


def sum_angles(angles: Iterable[Angle]) -> Angle:
    try:
        angle: Angle = sum(angles, Angle(degree=0))
    except TypeError:
        raise ValueIsNotAnAngleError(f"Not able to calculate Angle sum, as some values are not Angles.")
    return angle


# TODO: Create Angles as CDLL inheritance with "is_order_valid" method
Angles = list[Angle]

AngleCombination = dict[Angle, int]
AngleCombinations = list[AngleCombination]


def fit_value_to_option(value: Angle, options: frozenset[Angle]) -> Angle:
    maximum_deviation: float = 0.00000000001
    fitted_value: Angle | None = None

    for option in options:
        deviation: float = abs(value.as_radian()) - abs(option.as_radian())
        if abs(deviation) < maximum_deviation:
            fitted_value = option
            break

    if fitted_value is None:
        raise AngleOptionsNotInExpectedRangeError(f"No angle option '{[option.as_degree() for option in options]}' "
                                                  f"fit angle value '{value.as_degree()}'")

    return fitted_value


def merge_parts(first_part: AngleCombination, second_part: AngleCombination) -> AngleCombination:
    new_combination: AngleCombination = defaultdict(int)
    new_combination |= first_part
    for key, value in second_part.items():
        new_combination[key] += value
    return new_combination


def merge_combinations(combinations: AngleCombinations, combination: AngleCombinations) -> AngleCombinations:
    new_combinations = [merge_parts(first_part=old_part, second_part=new_part)
                        for new_part in combination
                        for old_part in combinations]
    return new_combinations


def opposite_angle_rules_generator() -> tuple[dict[frozenset[Angle], Angle], dict[frozenset[Angle], Angle]]:
    # TODO: how do I generate the two derived angle list sets from the all_angles ground truth?
    #       missing definition of what is a valid set of angles? what will generate those?
    all_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)]])

    multiple_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=90)],
                                                      [Angle(degree=60), Angle(degree=120)],
                                                      [Angle(degree=90)],
                                                      [Angle(degree=60), Angle(degree=120)]])

    single_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=90)],
                                                    [Angle(degree=60)],
                                                    [Angle(degree=90)],
                                                    [Angle(degree=120)]])

    angle_comparisons: frozenset[Angle] = frozenset({angle
                                                     for angle_groups in single_angles
                                                     for angle in angle_groups})

    opposite_angle_requires: dict[frozenset[Angle], Angle] = {}
    opposite_angle_disallows: dict[frozenset[Angle], Angle] = {}

    for angle_combinations in [single_angles, multiple_angles, all_angles]:
        for angle in angle_combinations:
            opposite: list[Angle] = angle_combinations.opposite_unique(value=angle)
            if len(opposite) == 3:
                pass  # with all 3 options there is no way to decide requirements or disallowedness
            elif len(opposite) == 2:
                disallows = set(angle).symmetric_difference(angle_comparisons)
                opposite_angle_disallows[frozenset(opposite)] = first(list(disallows))
            elif len(opposite) == 1:
                opposite_angle_requires[frozenset(opposite)] = first(angle)
            else:
                raise WrongValueAmountError(f"Unexpected amount of items '{len(opposite)}' in opposite list of angles")

    return opposite_angle_requires, opposite_angle_disallows


OPPOSITE_ANGLE_REQUIRES, OPPOSITE_ANGLE_DISALLOWS = opposite_angle_rules_generator()


def adjacent_angle_rules_generator() -> tuple[dict[frozenset[Angle], Angle], dict[frozenset[Angle], Angle]]:
    all_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)],
                                                 [Angle(degree=60), Angle(degree=90), Angle(degree=120)]])

    multiple_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=90)],
                                                      [Angle(degree=60), Angle(degree=120)],
                                                      [Angle(degree=90)],
                                                      [Angle(degree=60), Angle(degree=120)]])

    single_angles: CDLL[list[Angle]] = CDLL(values=[[Angle(degree=90)],
                                                    [Angle(degree=60)],
                                                    [Angle(degree=90)],
                                                    [Angle(degree=120)]])

    angle_comparisons: frozenset[Angle] = frozenset({angle
                                                     for angle_groups in single_angles
                                                     for angle in angle_groups})

    adjacent_angle_requires: dict[frozenset[Angle], Angle] = {}
    adjacent_angle_disallows: dict[frozenset[Angle], Angle] = {}

    for angle_combinations in [single_angles, multiple_angles, all_angles]:
        for angle in angle_combinations:
            # opposite: list[Angle] = angle_combinations.opposite_unique(value=angle)
            angle_corner_before, angle_corner_after = angle_combinations.before_and_after_unique(value=angle)

            # before
            if len(angle_corner_before) == 3:
                pass  # with all 3 options there is no way to decide requirements or disallowedness
            elif len(angle_corner_before) == 2:
                requires = set(angle_corner_before).symmetric_difference(angle_comparisons)
                adjacent_angle_requires[frozenset(angle_corner_before)] = first(requires)
            elif len(angle_corner_before) == 1:
                angle_corner_before_angle: Angle = first(angle_corner_before)
                if (angle_corner_before_angle == min(angle_comparisons) or
                        angle_corner_before_angle == max(angle_comparisons)):
                    adjacent_angle_requires[frozenset(angle_corner_before)] = first(angle)
                else:
                    adjacent_angle_disallows[frozenset(angle_corner_before)] = angle_corner_before_angle
            else:
                raise WrongValueAmountError(f"Unexpected amount of items '{len(angle_corner_before)}' "
                                            f"in opposite list of angles")

            # after
            if len(angle_corner_after) == 3:
                pass  # with all 3 options there is no way to decide requirements or disallowedness
            elif len(angle_corner_after) == 2:
                requires = set(angle_corner_after).symmetric_difference(angle_comparisons)
                adjacent_angle_requires[frozenset(angle_corner_after)] = first(requires)
            elif len(angle_corner_after) == 1:
                angle_corner_after_angle: Angle = first(angle_corner_after)
                if (angle_corner_after_angle == min(angle_comparisons) or
                        angle_corner_after_angle == max(angle_comparisons)):
                    adjacent_angle_requires[frozenset(angle_corner_after)] = first(angle)
                else:
                    adjacent_angle_disallows[frozenset(angle_corner_after)] = angle_corner_after_angle
            else:
                raise WrongValueAmountError(f"Unexpected amount of items '{len(angle_corner_after)}' "
                                            f"in opposite list of angles")

    return adjacent_angle_requires, adjacent_angle_disallows


ADJACENT_ANGLES_REQUIRES, ADJACENT_ANGLES_DISALLOWS = adjacent_angle_rules_generator()


def required_and_disallowed_angles(angles: frozenset[Angle],
                                   required: dict[frozenset[Angle], Angle],
                                   disallowed: dict[frozenset[Angle], Angle]) -> tuple[set[Angle], set[Angle]]:
    outputs: list[set[Angle]] = []

    for mapping in [required, disallowed]:
        try:
            output: set[Angle] = {mapping[angles]}
        except KeyError:
            output: set[Angle] = set()
        outputs.append(output)

    return outputs[0], outputs[1]


def required_and_disallowed_corner_angles(location_angles: list[frozenset[Angle]]) -> tuple[set[Angle], set[Angle]]:
    corner_required: set[Angle] = set()
    corner_disallowed: set[Angle] = set()

    requires: list[dict[frozenset[Angle], Angle]] = [OPPOSITE_ANGLE_REQUIRES, ADJACENT_ANGLES_REQUIRES,
                                                     ADJACENT_ANGLES_REQUIRES]
    disallows: list[dict[frozenset[Angle], Angle]] = [OPPOSITE_ANGLE_DISALLOWS, ADJACENT_ANGLES_DISALLOWS,
                                                      ADJACENT_ANGLES_DISALLOWS]

    for angle, required, disallowed in zip(location_angles, requires, disallows):
        required_angle, disallowed_angle = required_and_disallowed_angles(angles=angle,
                                                                          required=required,
                                                                          disallowed=disallowed)
        corner_required |= required_angle
        corner_disallowed |= disallowed_angle

    return corner_required, corner_disallowed


def is_angle_combo_match_angles_subset(angle_combination: tuple[Angle, ...],
                                       angle_subset: tuple[Angle, ...],
                                       subset_index: int
                                       ) -> bool:
    """
    Is this ordered list of angles,
    present from the beginning of the Angles surrounding a selected index
    in the subset of Angles belonging to a shape?
    """

    if len(angle_combination) < len(angle_subset):
        indices_around_angle: list[int] = indices_around_index(index=subset_index, collection=angle_subset)

        angles_around_angle: list[Angle] = [angle_subset[index] for index in indices_around_angle]

        is_all_angles_matching: bool = all((angle_from_combination == angle_from_angles
                                            for angle_from_combination, angle_from_angles in
                                            zip(angle_combination, angles_around_angle)))
    else:
        raise NoAngleLeftInSubsetToMatchError(f"{angle_combination} has so many items that {angle_subset} "
                                              f"does not have any items remaining to match with.")

    return is_all_angles_matching


def matching_angle_options_in_angles_subset(angle_combination: tuple[Angle, ...],
                                            angle_subset: tuple[Angle, ...],
                                            subset_amount: int
                                            ) -> set[Angle]:
    angle_options: set[Angle] = set()

    for subset_index in range(subset_amount):
        """Trying each possibility in the subset amount, as the position we are finding solution for."""
        try:
            is_all_angles_matching: bool = is_angle_combo_match_angles_subset(angle_combination=angle_combination,
                                                                              angle_subset=angle_subset,
                                                                              subset_index=subset_index)
        except NoAngleLeftInSubsetToMatchError as _:
            is_all_angles_matching: bool = False

        if is_all_angles_matching:
            angle_option: Angle = angle_subset[subset_index]
            angle_options.add(angle_option)
            break

    return angle_options


def options_from_combinations_and_subsets(angle_combinations: set[tuple[Angle, ...]],
                                          angle_subsets: dict[tuple[Angle, ...], int]
                                          ) -> set[Angle]:
    angle_options: set[Angle] = set()

    for angle_combination in angle_combinations:
        for angle_subset, subset_amount in angle_subsets.items():
            angle_options |= matching_angle_options_in_angles_subset(angle_combination=angle_combination,
                                                                     angle_subset=angle_subset,
                                                                     subset_amount=subset_amount)

    return angle_options


def merge_angle_combinations(combinations: set[tuple[Angle, ...]],
                             combination: set[tuple[Angle, ...]]
                             ) -> set[tuple[Angle, ...]]:
    """
    Adding both orders of combination variations is done as a substitute for the much harder problem of
    analyzing how the Angles are ordered in relation to other Angles in the sequence.
    """

    new_combinations: set[tuple[Angle, ...]] = set()

    for old_combination in combinations:
        for new_combination in combination:
            new_combinations.add((old_combination + new_combination))
            new_combinations.add((new_combination + old_combination))

    return new_combinations


def combine_angles(angles: list[frozenset[Angle]]) -> set[tuple[Angle, ...]]:
    angle_combinations: set[tuple[Angle, ...]] = {()}
    for angles_ in angles:
        angle_combination = {tuple([angle]) for angle in angles_}
        _ = (angle_combinations := merge_angle_combinations(angle_combinations, angle_combination))
    return angle_combinations
