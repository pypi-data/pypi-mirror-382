from src.angle_tompy.angle import Angle, combine_angles, options_from_combinations_and_subsets


def test_success():
    # Setup
    angle0: Angle = Angle(degree=60)
    angle1: Angle = Angle(degree=120)
    angle2: Angle = Angle(degree=90)
    set0: frozenset[Angle] = frozenset([angle0, angle2])
    set1: frozenset[Angle] = frozenset([angle1, angle0])
    angles0: list[set0] = [set0, set1]
    angle_combinations1: set[tuple[Angle, ...]] = combine_angles(angles=angles0)

    angle_subsets1: dict[tuple[Angle, ...], int] = {(Angle(degree=60), Angle(degree=60), Angle(degree=60)): 1,
                                                    (Angle(degree=90), Angle(degree=90), Angle(degree=90), Angle(degree=90)): 1,
                                                    (Angle(degree=120), Angle(degree=120), Angle(degree=120), Angle(degree=120), Angle(degree=120), Angle(degree=120)): 1,
                                                    (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120)): 2}
    angle_options0: set[Angle] = {Angle(degree=60), Angle(degree=120)}

    # Execution
    angle_options1: set[Angle] = options_from_combinations_and_subsets(angle_combinations=angle_combinations1,
                                                                       angle_subsets=angle_subsets1)

    # Validation
    assert angle_options0 == angle_options1
