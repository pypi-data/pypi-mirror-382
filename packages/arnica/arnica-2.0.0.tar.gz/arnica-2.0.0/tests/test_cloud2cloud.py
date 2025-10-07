""" unit tests for arnica.utils

OST : I heard it through the grapevine, by Leo. Moracchioli
"""

import numpy as np

from arnica.utils.cloud2cloud import cloud2cloud

SMALL = 3e-16
DIM1 = 5
DIM2 = 7
BINS = 100


def squared_func(xxx, yyy, zzz):
    """test function"""
    return (3 * xxx**2 + 5 * yyy**2 + 7 * zzz * 2) / (3**2 * 5**2 * 7**2)


def test_cloud2cloud():
    """
    small test of cloud2cloud projection
    """
    size = 1000
    x_coor = np.linspace(0, 1.0, DIM2 * 10)
    y_coor = np.linspace(0, 1.0, DIM2 * 10)
    z_coor = np.linspace(0, 1.0, DIM2 * 10)

    source_xyz = np.stack(np.meshgrid(x_coor, y_coor, z_coor), axis=-1)
    target_xyz = np.stack(
        (
            np.random.rand(DIM1 * size) * 1.0,
            np.random.rand(DIM1 * size) * 1.0,
            np.random.rand(DIM1 * size) * 1.0,
        ),
        axis=-1,
    )

    source_val = {}
    source_val["v"] = squared_func(
        np.take(source_xyz, 0, axis=-1),
        np.take(source_xyz, 1, axis=-1),
        np.take(source_xyz, 2, axis=-1),
    )

    target_ref = squared_func(
        target_xyz[:, 0],
        target_xyz[:, 1],
        target_xyz[:, 2],
    )

    target_estimate5 = cloud2cloud(source_xyz, source_val, target_xyz, stencil=5)

    target_estimate1 = cloud2cloud(
        source_xyz, source_val, target_xyz, stencil=1, limitsource=100000
    )
    assert np.all(np.abs(target_ref - target_estimate1["v"]) < 1e-4)
    assert np.all(np.abs(target_ref - target_estimate5["v"]) < 1e-5)
