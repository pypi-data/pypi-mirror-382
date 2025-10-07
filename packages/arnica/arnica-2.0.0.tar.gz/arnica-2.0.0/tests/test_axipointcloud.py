import numpy as np
from arnica.utils.axipointcloud import AxiPointCloud


def test_axipointcloud():
    """Testing the axipoint cloud utility"""

    pnt_cloud = AxiPointCloud(
        xcoor=[0, 1, 2],
        ycoor=[0, 1, 2],
        zcoor=[0, 0, 0],
        vars={
            "var1": [1, 1, 1],
            "var2": [2, 2, 2],
        },
    )

    str_ = """
AxiPointCloud object "Unnamed"

 Angle section (deg.):0.0

 Coordinates:
-X coor (m)----
shape :(3,)
min/max :0/2
-Y coor (m)----
shape :(3,)
min/max :0/2
-Z coor (m)----
shape :(3,)
min/max :0/0
-R coor (m)----
shape :(3,)
min/max :0.0/2.0
-Theta coor (deg)----
shape :(3,)
min/max :0.0/0.0

 Data:
-var1----
shape :(3,)
min/max :1/1
-var2----
shape :(3,)
min/max :2/2"""
    assert pnt_cloud.__str__() == str_

    assert np.allclose(
        pnt_cloud.xyz(),
        np.array(
            [
                [0, 0, 0],
                [1, 1, 0],
                [2, 2, 0],
            ]
        ),
    )

    assert np.allclose(
        pnt_cloud.vars_stack(),
        np.array(
            [
                [1, 2],
                [1, 2],
                [1, 2],
            ]
        ),
    )
    assert np.allclose(pnt_cloud.rad(), np.array([0.0, 1.0, 2.0]))
    pnt_cloud.recompute_theta_range_from_coords()

    assert pnt_cloud.theta_range == 0.0

    pnt_cloud.rotate(np.deg2rad(90.0))

    assert np.allclose(
        pnt_cloud.xyz(),
        np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 1.0],
                [2.0, 0.0, 2.0],
            ]
        ),
    )

    pnt_cloud.theta_range = np.deg2rad(90.0)
    pnt_cloud.dupli_rotate(1)

    assert np.allclose(
        pnt_cloud.xyz(),
        np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 1.0],
                [2.0, 0.0, 2.0],
                [0.0, 0.0, 0.0],
                [1.0, -1.0, 0.0],
                [2.0, -2.0, 0.0],
            ]
        ),
    )
    assert pnt_cloud.theta_range == np.deg2rad(180.0)

    print(pnt_cloud.theta_range)
