import pytest
from arnica.phys.yk_from_phi import yk_from_phi


def test_ykfromphi():
    yf_methane = yk_from_phi(1.0, 1, 4)["fuel"]
    yf_c3h8 = yk_from_phi(1.0, 3, 8)["fuel"]
    yf_c8h18 = yk_from_phi(1.0, 3, 8)["fuel"]
    yf_h2 = yk_from_phi(1.0, 3, 8)["fuel"]
    pytest.approx(yf_methane, 0.001) == 0.055
    pytest.approx(yf_c3h8, 0.001) == 0.06
    pytest.approx(yf_c8h18, 0.001) == 0.062
    pytest.approx(yf_h2, 0.001) == 0.028
