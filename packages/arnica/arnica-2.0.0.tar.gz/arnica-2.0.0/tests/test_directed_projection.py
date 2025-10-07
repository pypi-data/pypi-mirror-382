""" unit tests for arnica.utils

OST : I heard it through the grapevine, by Leo. Moracchioli
"""

import numpy as np
from arnica.utils.vector_actions import (
    renormalize,
)

from arnica.utils.directed_projection import (
    projection_kdtree,
    compute_dists,
    project_points,
)

SMALL = 3e-16
DIM1 = 5
DIM2 = 7

BINS = 100


def test_projection_kdtree():
    r"""
    small test of directed projection

                  xyz(0,1,0)  dir(1,-1,0)
                x
                 \
                 _\|


                ^
                |
  ______________o______x________
  s0     s1     s2     s3     s4
               /          xyz(1,0,0)
xyz(0,0,0)  nml (0,1,0)
    """

    test_points_xyz = np.zeros((DIM2, 3))
    test_points_xyz[:, 1] = 1.0
    test_points_dir = np.zeros((DIM2, 3))
    test_points_dir[:, 0] = 1.0
    test_points_dir[:, 1] = -1.0
    test_points_dir = renormalize(test_points_dir)

    test_surf_xyz = np.zeros((DIM1, 3))
    test_surf_xyz[:, 0] = np.linspace(-2, 2, DIM1)
    test_surf_nml = np.zeros((DIM1, 3))
    test_surf_nml[:, 1] = 1.0

    neighb = 3

    projection = projection_kdtree(
        test_points_xyz,
        test_points_dir,
        test_surf_xyz,
        test_surf_nml,
        neigbors=neighb,
    )

    exp_xyz = np.zeros((DIM2, 3))
    exp_indexes = np.repeat(np.array([2, 3, 1])[np.newaxis, :], DIM2, axis=0)
    exp_cyl_dists = np.repeat(
        np.array([0.0, np.sqrt(2.0) * 0.5, np.sqrt(2.0) * 0.5])[np.newaxis, :],
        DIM2,
        axis=0,
    )

    np.testing.assert_allclose(projection.moved_pts, exp_xyz)
    np.testing.assert_equal(projection.indexes, exp_indexes)
    np.testing.assert_allclose(projection.cyl_dists, exp_cyl_dists, atol=1e-6)
    # assert out_xyz.shape == projection.moved_pts.shape
    # assert np.all(out_xyz == projection.moved_pts)
    # assert out_indexes.shape == projection.indexes.shape
    # assert np.all(out_indexes == projection.indexes)
    # assert out_cyl_dists.shape == exp_out_cyl_dists.shape
    # assert np.all(np.abs(exp_out_cyl_dists - out_cyl_dists) < SMALL)

    project = False
    projection = projection_kdtree(
        test_points_xyz,
        test_points_dir,
        test_surf_xyz,
        test_surf_nml,
        neigbors=neighb,
        project=project,
    )

    exp_xyz = np.tile([0.0, 1.0, 0.0], (DIM2, 1))
    exp_indexes = np.tile([2, 3, 1], (DIM2, 1))
    exp_cyl_dists = np.tile([0.70710678, 0.0, 1.4142135], (DIM2, 1))

    np.testing.assert_allclose(projection.moved_pts, exp_xyz)
    np.testing.assert_equal(projection.indexes, exp_indexes)
    np.testing.assert_allclose(projection.cyl_dists, exp_cyl_dists, atol=1e-6)


def test_compute_dists():
    """test of computation of cylindrical distances"""

    test_points_xyz = np.zeros((DIM2, 3))
    test_points_dir = np.zeros((DIM2, 3))
    test_points_dir[:, 0] = 1.0
    test_points_dir[:, 1] = -1.0
    test_points_dir = renormalize(test_points_dir)

    neighb = 3
    test_surf_xyz = np.zeros((DIM2, neighb, 3))
    test_surf_xyz[:, 1, 0] = 1.0
    test_surf_xyz[:, 2, 0] = -1.0
    test_surf_nml = np.zeros((DIM2, neighb, 3))
    test_surf_nml[:, :, 1] = 1.0

    tol = 1000.0

    _, out_cyl_dists = compute_dists(
        test_points_xyz,
        test_points_dir,
        test_surf_xyz,
        test_surf_nml,
        tol,
    )
    exp_out_cyl_dists = np.array(
        [
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
            [0.0, 0.70710678, 0.70710678],
        ]
    )

    assert out_cyl_dists.shape == exp_out_cyl_dists.shape
    np.testing.assert_allclose(out_cyl_dists, exp_out_cyl_dists)


def test_project_points():
    """test the projection of points on a plan defined by a point and a normal"""

    test_points_xyz = np.zeros((DIM2, 3))
    test_points_xyz[:, 1] = 1.0
    test_points_dir = np.zeros((DIM2, 3))
    test_points_dir[:, 1] = -1.0
    test_surf_xyz = np.zeros((DIM2, DIM1, 3))
    test_surf_xyz[:, :, 0] = np.linspace(-2.0, 2.0, DIM1)

    proj = project_points(test_points_xyz, test_points_dir, test_surf_xyz)

    exp_out_proj_pts = np.tile(np.array([0.0, 0.0, 0.0]), (DIM2, DIM1, 1))
    exp_out_axi_dists = np.tile(np.array([1.0, 1.0, 1.0, 1.0, 1.0]), (DIM2, 1))
    exp_out_rad_dists = np.tile(np.array([2.0, 1.0, 0.0, 1.0, 2.0]), (DIM2, 1))
    np.testing.assert_array_equal(exp_out_proj_pts, proj.proj_pts)
    np.testing.assert_array_equal(exp_out_axi_dists, proj.axi_dists)
    np.testing.assert_array_equal(exp_out_rad_dists, proj.rad_dists)
