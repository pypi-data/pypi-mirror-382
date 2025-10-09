from src.angle_tompy.angle import Angle, matching_angle_options_in_angles_subset


def test_matching_angle_options_in_angles_subset_60_in_triangle_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    subset_amount0: int = 1
    match0: set[Angle] = {Angle(degree=60)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_90_in_square_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=90),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=90), Angle(degree=90), Angle(degree=90), Angle(degree=90))
    subset_amount0: int = 1
    match0: set[Angle] = {Angle(degree=90)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_120_and_120_and_120_in_hexagon_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=120), Angle(degree=120))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=120), Angle(degree=120),
                                        Angle(degree=120), Angle(degree=120), Angle(degree=120))
    subset_amount0: int = 1
    match0: set[Angle] = {Angle(degree=120)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_60_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60),)
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_amount0: int = 2
    match0: set[Angle] = {Angle(degree=120)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_60_and_120_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_amount0: int = 2
    match0: set[Angle] = {Angle(degree=120)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_120_and_60_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=60))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_amount0: int = 2
    match0: set[Angle] = {Angle(degree=60)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_120_and_60_and_120_in_rhombus_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=120), Angle(degree=60), Angle(degree=120))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=120), Angle(degree=60), Angle(degree=120))
    subset_amount0: int = 2
    match0: set[Angle] = {Angle(degree=60)}

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


def test_matching_angle_options_in_angles_subset_60_and_60_and_60_in_triangle_success():
    # Setup
    angle_combination0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    angle_subset0: tuple[Angle, ...] = (Angle(degree=60), Angle(degree=60), Angle(degree=60))
    subset_amount0: int = 1
    match0: set[Angle] = set()

    # Execution
    match1: set[Angle] = matching_angle_options_in_angles_subset(angle_combination=angle_combination0,
                                                                 angle_subset=angle_subset0,
                                                                 subset_amount=subset_amount0)

    # Validation
    assert match0 == match1


