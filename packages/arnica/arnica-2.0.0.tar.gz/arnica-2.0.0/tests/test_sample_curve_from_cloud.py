""" module to test sample_curve_from_cloud.py of Arnica"""

import numpy as np
from scipy import spatial

from arnica.utils.sample_curve_from_cloud import (
    sort_points_by_dist,
    sample_arrays_by_dist_interval,
    sample_points_from_cloud,
    get_neighbor,
)


def test_get_neighbor():
    """Testing get_neighbor"""

    points_coor = np.array([[0.0, 0.0], [0.0, 3.0], [1.0, 0.0], [1.0, 3.0]])
    kdtree = spatial.cKDTree(points_coor)  # pylint: disable=not-callable
    list_points = [0, 2]
    point = points_coor[2]

    index, dist = get_neighbor(kdtree, point, list_points)

    index_target = 3
    assert index == index_target
    dist_target = 3.0
    assert dist == dist_target


def test_sort_points_by_dist():
    """Testing sort_points_by_dist"""

    starting_pt = np.array([-1.0, 0.0])
    points_coor = np.array([[2.0, 1.0], [1.0, 2.0], [0.0, 0.0], [2.0, 0.0], [2.0, 2.0]])

    ordered_indexes, ordered_dists = sort_points_by_dist(points_coor, starting_pt)

    indexes_target = np.array([2, 3, 0, 4, 1])
    np.testing.assert_array_equal(ordered_indexes, indexes_target)

    dists_target = np.array([0.0, 2.0, 1.0, 1.0, 1.0])
    np.testing.assert_array_equal(ordered_dists, dists_target)


def test_sample_arrays_by_dist_interval():
    """Testing sample_arrays_by_dist_interval"""

    dists = np.zeros(7)
    dists[1:] = 1.0
    sample_res = 1.5
    args = np.arange(7.0)

    dists_sampled, (args_sampled,) = sample_arrays_by_dist_interval(
        dists, sample_res, args
    )

    args_sampled_target = np.array([0.0, 2.0, 3.0, 6.0])
    np.testing.assert_array_equal(args_sampled, args_sampled_target)
    dists_sampled_target = np.array([0.0, 1.0, 1.0, 1.0])
    np.testing.assert_array_equal(dists_sampled, dists_sampled_target)


def test_sample_points_from_cloud():
    """Testing sample_points_from_cloud"""

    idx_in = np.arange(16)
    np.random.shuffle(idx_in)
    abs_curv = np.linspace(0.0, 2 * np.pi, len(idx_in) + 1)[:-1]
    abs_curv = abs_curv[idx_in]
    points_coor = np.stack((np.cos(abs_curv), np.sin(abs_curv)), axis=1)
    starting_pt = np.array([1.2, 0.0])
    n_samples = 8

    out_points = sample_points_from_cloud(points_coor, starting_pt, n_samples=n_samples)

    abs_curv = np.linspace(0.0, 2 * np.pi, n_samples + 1)[:-1]
    abs_curv[-1] = 15 / 16 * 2 * np.pi
    out_points_target = np.stack((np.cos(abs_curv), np.sin(abs_curv)), axis=1)
    np.testing.assert_allclose(out_points, out_points_target)

    idx_in = np.arange(100)
    np.random.shuffle(idx_in)
    points_coor = np.zeros((100, 2))
    points_coor[:, 0] = np.linspace(0.0, 99.0, 100)[idx_in]
    out_points = sample_points_from_cloud(points_coor, starting_pt)
    np.testing.assert_allclose(len(out_points), 80, atol=2, rtol=2)
