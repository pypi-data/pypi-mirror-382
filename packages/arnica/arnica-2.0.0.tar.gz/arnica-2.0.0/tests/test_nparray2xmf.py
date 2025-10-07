""" unit tests for arnica.utils

OST : I heard it through the grapevine, by Leo. Moracchioli
"""

import numpy as np
from arnica.utils.nparray2xmf import NpArray2Xmf

SMALL = 3e-16
DIM1 = 5
DIM2 = 7

BINS = 100


def squared_func(xxx, yyy, zzz):
    """test function"""
    return (3 * xxx**2 + 5 * yyy**2 + 7 * zzz * 2) / (3**2 * 5**2 * 7**2)


def test_nparray2xmf():
    """test of nparray dump"""

    x_coor = np.linspace(0, 1.0, DIM2 * 10)
    y_coor = np.linspace(0, 1.0, DIM2 * 10)
    z_coor = np.linspace(0, 1.0, DIM2 * 10)

    source_xyz = np.stack(np.meshgrid(x_coor, y_coor, z_coor), axis=-1)

    xmf3d = NpArray2Xmf("dummy.h5")
    xmf3d.create_grid(
        np.take(source_xyz, 0, axis=-1),
        np.take(source_xyz, 1, axis=-1),
        np.take(source_xyz, 2, axis=-1),
    )

    xmf3d.add_field(
        squared_func(
            np.take(source_xyz, 0, axis=-1),
            np.take(source_xyz, 1, axis=-1),
            np.take(source_xyz, 2, axis=-1),
        ),
        "dummy",
    )
