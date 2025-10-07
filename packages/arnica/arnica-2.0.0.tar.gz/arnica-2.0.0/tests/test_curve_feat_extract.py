import numpy as np
from arnica.utils.curve_feat_extract import (
    mask_boundary_layer,
    reptile,
    amax_keepshape,
    amin_keepshape,
)


def test_mask_boundary_layer(allclose):
    """Damo of a simplified set of graphs with showy"""
    source = np.array(
        [
            [0, 1, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 3, 2, 3, 4],
            [0, 1, -2, 3, 4],
            [0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4],
        ]
    )

    target = np.array(
        [
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]
    )

    assert allclose(target, mask_boundary_layer(source, eps=0.1, axis=1))


def test_reptile(allclose):
    """Damo of a simplified set of graphs with showy"""
    source = np.array([[0, 1, 0, 0, 0], [0, 1, 1, 1, 1], [0, 1, 2, 3, 4]])

    target = np.array([[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [3, 3, 3, 3, 3]])

    assert allclose(target, reptile(source, pos=3, axis=1))


def test_amax_keepshape(allclose):
    """Damo of a simplified set of graphs with showy"""
    source = np.array([[0, 1, 0, 0, 0], [0, 1, 1, 1, 1], [0, 1, 2, 3, 3]])

    target = np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [3, 3, 3, 3, 3]])

    assert allclose(target, amax_keepshape(source, axis=1))


def test_amin_keepshape(allclose):
    """Damo of a simplified set of graphs with showy"""
    source = np.array([[0, 1, 0, 0, 0], [0, 1, -1, 1, 1], [1, 1, 2, 3, 4]])

    target = np.array([[0, 0, 0, 0, 0], [-1, -1, -1, -1, -1], [1, 1, 1, 1, 1]])

    assert allclose(target, amin_keepshape(source, axis=1))
