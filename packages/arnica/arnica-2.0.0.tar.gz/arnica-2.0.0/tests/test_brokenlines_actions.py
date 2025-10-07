from arnica.utils.brokenlines_actions import (
    coords_real_2_pix,
    coords_pix_2_real,
    project_on_line,
    relative_position_segment,
    dist_segment,
    closest_segment_in_line,
    closest_line,
    point_from_curvi,
)


def test_real_2_pix():
    assert [5, 5] == coords_real_2_pix(0.5, 0.5, [[0, 0], [10, 10]], [[0, 0], [1, 1]])


def test_pix_2_real():
    assert [0.5, 0.5] == coords_pix_2_real(5, 5, [[0, 0], [10, 10]], [[0, 0], [1, 1]])


def test_project_on_line():
    assert project_on_line(0, 0, 1, 0, 0.5, 0.3) == (0.5, 0.0)
    assert project_on_line(0, 0, 1, 0, 0.5, 0) == (0.5, 0.0)
    assert project_on_line(0, 0, 1, 0, 0.0, 0.3) == (0.0, 0.0)
    assert project_on_line(0, 0, 1, 0, 0.3, 0.3) == (0.3, 0.0)


def test_relative_position_segment():
    assert relative_position_segment(0, 0, 10, 0, 0, 0) == 0.0
    assert relative_position_segment(0, 0, 10, 0, 10, 0) == 1.0
    assert relative_position_segment(0, 0, 10, 0, 5, 0) == 0.5
    assert relative_position_segment(0, 0, 10, 0, 15, 0) == 1.5
    assert relative_position_segment(0, 0, 10, 0, -5, 0) == -0.5
    assert relative_position_segment(10, 10, 0, 0, 5, 5) == 0.5
    assert relative_position_segment(10, 10, 0, 0, 20, 20) == -1
    assert relative_position_segment(10, 10, 0, 0, -10, -10) == 2


def test_dist_segment():
    assert dist_segment(10, 10, 0, 0, 5, 5) == (0, 0, 0.5)
    assert dist_segment(10, 10, 0, 0, 10, 0) == (7.0710678118654755, 0, 0.5)
    assert dist_segment(10, 10, 0, 0, 20, 20) == (0, 14.142135623730951, 0.0)
    assert dist_segment(10, 10, 0, 0, -10, -10) == (0, 14.142135623730951, 1.0)
    assert dist_segment(0.5, 0.1, 1.0, 0.1, 0.6, 0) == (0.1, 0, 0.19999999999999996)


def test_closest_segment_in_line():
    assert closest_segment_in_line([[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]], 0, 0) == (
        0,
        0.1,
        0.0,
    )
    assert closest_segment_in_line([[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]], 0.5, 0) == (
        0,
        0.1,
        1.0,
    )
    assert closest_segment_in_line([[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]], 0.6, 0) == (
        1,
        0.1,
        0.19999999999999996,
    )
    assert closest_segment_in_line([[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]], 10, 0.1) == (
        1,
        9.0,
        1,
    )
    assert closest_segment_in_line([[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]], -10, 0.1) == (
        0,
        10.0,
        0,
    )


def test_closest_line():
    lines = [
        [[0.0, 0.1], [0.5, 0.1], [1.0, 0.1]],
        [[0.0, 0.9], [0.5, 0.9], [1.0, 0.9]],
    ]
    assert closest_line(lines, 0.5, 0.4) == (0, 0, 1.0)
    assert closest_line(lines, 0.8, 0.6) == (1, 1, 0.6000000000000001)


def test_point_from_curvi():

    line = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    assert point_from_curvi(line, 3, 0.5) == (0.0, 0.5, 3.5)

    assert closest_segment_in_line(line, 0.0, 0.5) == (3, 0.0, 0.5)
