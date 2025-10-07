""" module to test de phys parts of Arnica """

import numpy as np

from arnica.phys.solid_material import SolidMaterial
from arnica.phys.thermodyn_properties import h_kader
from arnica.phys.thermodyn_properties import h_stanton
from arnica.phys.thermodyn_properties import stanton_colburn
from arnica.phys.wall_thermal_equilibrium import compute_equilibrium

DIM1 = 5


def test_compute_equilibrium():
    """simple equilibrium for the ceramic + metal case"""

    cold_h = np.ones(DIM1) * 1000.0
    hot_h = 1000.0
    hot_t_ad = 2000.0
    cold_t_ad = 1000.0

    layer1 = SolidMaterial(lambda_poly=[10.0, 0], lambda_range=[100.0, 4000.0])
    ep_layer1 = 2.0e-4
    layer2 = SolidMaterial(lambda_poly=[10.0, 0.0], lambda_range=[100.0, 4000.0])
    ep_layer2 = 2.0e-4
    _, t_eq, _ = compute_equilibrium(
        hot_t_ad, cold_t_ad, hot_h, cold_h, layer1, layer2, ep_layer1, ep_layer2
    )

    np.testing.assert_allclose(t_eq, np.ones(DIM1) * 1500.0)


def test_h_kader():
    """test the h as in kader"""

    t_wall = np.ones(DIM1) * 1000.0
    rho_wall = 1.0
    y_wall = 1.0e-3
    u_2 = 40.0
    t_2 = 1400
    temp_adiab = 1400

    h_wall_expected = 273.12113446
    h_wall = h_kader(t_wall, rho_wall, y_wall, u_2, t_2, temp_adiab)

    np.testing.assert_allclose(h_wall, h_wall_expected)


def test_h_stanton():
    """Check H from stanton"""

    ones = np.ones(DIM1)
    stanton = ones
    rhou = 2 * ones
    c_p = 3 * ones

    h_wall = h_stanton(stanton, rhou, c_p)
    h_wall_expected = 6.0 * ones

    np.testing.assert_allclose(h_wall, h_wall_expected)


def test_stanton_colburn():
    """Check Stanton from colburn"""

    reynolds = 10000.0 * np.ones(DIM1)
    prandtl = 0.7 * np.ones(DIM1)

    st_0 = stanton_colburn(np.zeros_like(reynolds), prandtl)
    st_1 = stanton_colburn(reynolds, prandtl)
    print(st_1)
    np.testing.assert_allclose(st_0, 0.26624088 * np.ones(DIM1), rtol=1e-6)
    np.testing.assert_allclose(st_1, 0.00699792 * np.ones(DIM1), rtol=1e-6)
