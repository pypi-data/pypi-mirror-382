""" unit tests for arnica.utils

OST : I heard it through the grapevine, by Leo. Moracchioli
"""

import numpy as np
from arnica.utils.vector_actions import (
    renormalize,
    angle_btw_vects,
    yz_to_theta,
    rtheta2yz,
    rotate_vect_around_x,
    rotate_vect_around_axis,
    dilate_vect_around_x,
    cart_to_cyl,
    clip_by_bounds,
    cyl_to_cart,
    vect_to_quat,
    make_radial_vect,
    mask_cloud,
)


SMALL = 3e-16
DIM1 = 5
DIM2 = 7


def test_clip_by_bounds():
    """test the clip of a cloud of points by bounds"""

    point_cloud = np.array(
        [[0.0, 0.0, 1.0], [1.0, np.cos(np.pi / 4), np.sin(np.pi / 4)], [2.0, 1.0, 0.0]]
    )
    bounds_dict = {"x": (0.5, 3.0), "y": (0.0, 0.8)}
    exp_out = clip_by_bounds(point_cloud, bounds_dict, keep="out")
    exp_target = np.array([[0.0, 0.0, 1.0], [2.0, 1.0, 0.0]])

    exp_out = clip_by_bounds(point_cloud, bounds_dict, keep="in")
    exp_target = np.array([[1.0, np.cos(np.pi / 4), np.sin(np.pi / 4)]])

    np.testing.assert_array_equal(exp_out, exp_target)


def test_renormalize():
    """test renormalize in 1D an 2D arrays of 3D components"""
    in_x = np.ones((DIM1, 3))
    out_x = in_x / np.sqrt(3)
    assert np.all(renormalize(in_x) == out_x)
    in_x = np.ones((DIM1, DIM2, 3))
    out_x = in_x / np.sqrt(3)
    assert np.all(renormalize(in_x) == out_x)


def test_angle_btw_vects():
    """test angle btw vects in 1D an 2D arrays of 3D components"""
    # todo : failing test to fix
    in_x1 = np.zeros((DIM1, 3))
    in_x1[:, 2] = 1.0
    in_x2 = np.zeros((DIM1, 3))
    in_x2[:, 1] = 1.0
    out = angle_btw_vects(in_x1, in_x2, convert_to_degree=True)

    assert np.all(out == np.ones((DIM1)) * 90.0)

    in_x1 = np.zeros((DIM1, DIM2, 3))
    in_x1[:, :, 2] = 1.0
    in_x2 = np.zeros((DIM1, DIM2, 3))
    in_x2[:, :, 1] = 1.0
    out = angle_btw_vects(in_x1, in_x2, convert_to_degree=True)
    assert np.all(out == np.ones((DIM1, DIM2)) * 90.0)


def test_yz_to_theta():
    """test convertion to theta
               0pi=0deg
                  Y
                  ^
                  |
                  |
    -0.5pi=-90deg     o------>Z   0.5pi=90deg
    """
    in_x = np.zeros((DIM1, 3))
    in_x[:, 2] = 1.0
    out = yz_to_theta(in_x)
    assert np.all(out == np.ones((DIM1)) * np.pi * 0.5)

    in_x = np.zeros((DIM1, 3))
    in_x[:, 1] = 1.0
    out = yz_to_theta(in_x)
    assert np.all(out == np.ones((DIM1)) * 0.0)

    in_x = np.zeros((DIM1, DIM2, 3))
    in_x[:, :, 2] = -1.0
    out = yz_to_theta(in_x)
    assert np.all(out == np.ones((DIM1, DIM2)) * -0.5 * np.pi)


def test_rtheta2yz():
    """test conversion of r, theta to y, z-axis"""

    in_r = np.ones(DIM1) * 2.0
    in_theta = np.ones(DIM1) * np.pi / 4.0
    out = rtheta2yz(in_r, in_theta)
    np.testing.assert_allclose(out[0], np.ones(DIM1) * 1.414213562373095)
    np.testing.assert_allclose(out[1], np.ones(DIM1) * 1.414213562373095)

    in_r = np.ones((DIM1, DIM2)) * 2.0
    in_theta = np.ones((DIM1, DIM2)) * np.pi * 3 / 4
    out = rtheta2yz(in_r, in_theta)
    np.testing.assert_allclose(out[0], np.ones((DIM1, DIM2)) * -1.414213562373095)
    np.testing.assert_allclose(out[1], np.ones((DIM1, DIM2)) * 1.414213562373095)


def test_rotate_vect_around_x():
    """test the rotation of vectors"""
    in_x = np.zeros((DIM1, 3))
    in_x[:, 2] = 1.0
    out = rotate_vect_around_x(in_x, 90.0)
    exp_out = np.zeros((DIM1, 3))
    exp_out[:, 1] = -1.0
    assert np.all(np.abs(out - exp_out) < SMALL)

    in_x = np.zeros((DIM1, DIM2, 3))
    in_x[:, :, 2] = 1.0
    out = rotate_vect_around_x(in_x, 90.0)
    exp_out = np.zeros((DIM1, DIM2, 3))
    exp_out[:, :, 1] = -1.0
    assert out.shape == exp_out.shape
    assert np.all(np.abs(out - exp_out) < SMALL)


def test_rotate_vect_around_axis():
    """test of rotation of vectors around several axis"""

    in_x = np.zeros((DIM1, 3))
    in_x[:, 2] = 1.0
    out = rotate_vect_around_axis(in_x, ([1, 0, 0], 90.0))
    exp_out = np.zeros((DIM1, 3))
    exp_out[:, 1] = -1.0
    assert np.all(np.abs(out - exp_out) < SMALL)

    out = rotate_vect_around_axis(in_x, ([0, 1, 0], 45.0), ([4.0, 0.0, 2.1], 64.0))
    exp_out = np.tile([0.55922829, -0.79579036, 0.232339], (DIM1, 1))
    np.testing.assert_allclose(out, exp_out)


def test_dilate_vect_around_x():
    """test the dilatation of vectors around x"""

    azimuth = np.array([-45.0, 0.0, 45.0])
    np_ar_vect = np.array(
        [
            [0.0, np.cos(np.pi / 4), -np.sin(np.pi / 4)],
            [0.0, 1.0, 0.0],
            [0.0, np.cos(np.pi / 4), np.sin(np.pi / 4)],
        ]
    )
    exp_out = dilate_vect_around_x(azimuth, np_ar_vect)
    exp_target = np.array([[0.0, -1.0, 0.0], [0.0, 1.0, 0.0], [0.0, -1.0, 0.0]])

    np.testing.assert_allclose(exp_out, exp_target, atol=1e-8)


def test_cart_to_cyl():
    """test the conversion from xyz-system to cyl-system"""

    vects_xyz = np.array(
        [[0.0, 0.0, 1.0], [1.0, np.cos(np.pi / 4), np.sin(np.pi / 4)], [2.0, 1.0, 0.0]]
    )
    exp_out = cart_to_cyl(vects_xyz)
    exp_target = np.array(
        [[0.0, 1.0, np.pi / 2], [1.0, 1.0, np.pi / 4], [2.0, 1.0, 0.0]]
    )

    np.testing.assert_allclose(exp_out, exp_target)


def test_cyl_to_cart():
    """test the conversion from cyl-system to xyz-system"""

    vects_cyl = np.array(
        [[0.0, 1.0, np.pi / 2], [1.0, 1.0, np.pi / 4], [2.0, 1.0, 0.0]]
    )
    exp_out = cyl_to_cart(vects_cyl)
    exp_target = np.array(
        [[0.0, 0.0, 1.0], [1.0, np.cos(np.pi / 4), np.sin(np.pi / 4)], [2.0, 1.0, 0.0]]
    )

    np.testing.assert_allclose(exp_out, exp_target, atol=1e-8)


def test_clip_by_bounds():
    """test of the clip of field by bounds dict"""

    points_coord = np.arange(DIM2 * 3.0).reshape((DIM2, 3))
    bounds = {"x": (3.0, 13.0)}
    out = clip_by_bounds(points_coord, bounds, keep="in", return_mask=False)
    out_target = [
        [3.0, 4.0, 5.0],
        [6.0, 7.0, 8.0],
        [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0],
    ]
    np.testing.assert_array_equal(out, out_target)

    bounds = {"x": (3.0, 13.0), "z": (6.0, 1.0e6)}
    out = clip_by_bounds(points_coord, bounds, keep="out", return_mask=True)
    out_target = np.array([1, 1, 0, 0, 0, 1, 1], dtype=bool)
    np.testing.assert_array_equal(out, out_target)


def test_vect_to_quat():
    """test the building of a quaternion from two vects"""

    vect_t = np.array([0.0, 1.0, 1.0])
    vect_s = np.array([0.0, 0.0, 2.0])
    exp_out = vect_to_quat(vect_t, vect_s).as_rotvec()
    exp_target = np.array([-np.pi / 4, 0.0, 0.0])

    np.testing.assert_allclose(exp_out, exp_target, atol=1e-8)

    vect_t = np.array([[0.0, 1.0, 1.0], [1.0, 2.0, 0.0]])
    vect_s = np.array([[0.0, 0.0, 2.0], [0.0, 2.0, 1.0]])
    exp_out = vect_to_quat(vect_t, vect_s).as_rotvec()
    exp_target = np.array(
        [[-0.78539816, 0.0, 0.0], [-0.42900074, 0.21450037, -0.42900074]]
    )

    np.testing.assert_allclose(exp_out, exp_target, atol=1e-8)


def test_make_radial_vect():
    """test function making vectors radial"""

    coord = np.zeros((DIM1, 3))
    coord[:, 1] = 1.0
    coord[:, 2] = -1.0
    vects = np.zeros((DIM1, 3))
    vects[:, 0] = 1.0
    vects[:, 1] = 1.0
    vects = renormalize(vects)

    out = make_radial_vect(coord, vects)
    np.testing.assert_allclose(out, vects, atol=1e-6)

    coord[:, 1] = 6.0
    out = make_radial_vect(coord, vects)
    out_target = [
        [0.70710678, 0.69748583, -0.11624764],
        [0.70710678, 0.69748583, -0.11624764],
        [0.70710678, 0.69748583, -0.11624764],
        [0.70710678, 0.69748583, -0.11624764],
        [0.70710678, 0.69748583, -0.11624764],
    ]
    np.testing.assert_allclose(out, out_target, atol=1e-6)


def test_mask_cloud():
    """test vector masking"""
    in_x = np.stack(
        (np.linspace(-2, 2, DIM1), np.linspace(-2, 2, DIM1), np.linspace(-2, 2, DIM1)),
        axis=0,
    )
    for i, axe in enumerate(["x", "y", "z"]):
        out = mask_cloud(in_x, axis=axe, support=(-1.0, 1.0))
        exp_out = (in_x[:, i] >= -1.0) * (in_x[:, i] < 1.0)
        assert np.all(out == exp_out)

    in_x = np.repeat(in_x[:, np.newaxis, :], DIM2, axis=1)
    for i, axe in enumerate(["x", "y", "z"]):
        out = mask_cloud(in_x, axis=axe, support=(-1.0, 1.0))
        exp_out = (in_x[:, :, i] >= -1.0) * (in_x[:, :, i] < 1.0)
        assert out.shape == exp_out.shape
        assert np.all(out == exp_out)

    in_x = np.stack((np.zeros(DIM1), np.ones(DIM1), np.linspace(-2, 2, DIM1)), axis=0)
    out = mask_cloud(in_x, axis="r", support=(0, 2.0))
    exp_out = np.hypot(np.take(in_x, 1, axis=-1), np.take(in_x, 2, axis=-1)) < 2.0
    assert np.all(out == exp_out)

    out = mask_cloud(in_x, axis="theta", support=(-20.0, 20))
    theta = np.rad2deg(yz_to_theta(in_x))
    exp_out = (theta >= -20.0) * (theta < 20.0)
    assert np.all(out == exp_out)

    exception_reached = False
    try:
        mask_cloud(in_x, axis="dummy", support=(-20.0, 20))
    except IOError:
        exception_reached = True

    assert exception_reached
