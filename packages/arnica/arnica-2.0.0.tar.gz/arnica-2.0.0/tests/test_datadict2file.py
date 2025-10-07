""" Module to test the dump of dicts into files """

import os
import pytest
import numpy as np
import h5py
from arnica.utils.datadict2file import (
    dump_dico_2d_nparrays,
    dump_dico_2d_time_nparrays,
    dump_dico_1d_nparrays,
    dump_dico_0d,
    plot_dict_data_as_file,
)

DIM1 = 5
DIM2 = 11


def test_dump_dico_2d_nparrays(datadir):
    """test of dumping of dico of 2d nparrays into file"""

    x_arr = np.linspace(0.0, 1.0, DIM2)
    y_arr = np.linspace(0.0, 1.0, DIM2)
    z_arr = np.linspace(0.0, 1.0, DIM2)
    grid_3d = np.stack(np.meshgrid(x_arr, y_arr, z_arr), axis=-1)
    grid_2d = grid_3d[:, :, 0, :]

    case = datadir
    path_actu = os.getcwd()
    os.chdir(case)

    data_dict = {}
    dump_dico_2d_nparrays(
        data_dict,
        "tmp_2d.h5",
        np.take(grid_2d, 0, -1),
        np.take(grid_2d, 1, -1),
        np.take(grid_2d, 2, -1),
    )
    size_target = DIM2**2
    with h5py.File("tmp_2d.h5", "r") as fin:
        assert fin["mesh/x"][()].size == size_target
        assert fin["mesh/y"][()].size == size_target
        assert fin["mesh/z"][()].size == size_target

    data_dict["field_1"] = np.ones((DIM2, DIM2, DIM2))
    data_dict["field_2"] = np.zeros((DIM2, DIM2, DIM2))
    dump_dico_2d_nparrays(
        data_dict,
        "tmp_3d.h5",
        np.take(grid_3d, 0, -1),
        np.take(grid_3d, 1, -1),
        np.take(grid_3d, 2, -1),
    )
    size_target = DIM2**3
    with h5py.File("tmp_3d.h5", "r") as fin:
        assert fin["mesh/x"][()].size == size_target
        assert fin["mesh/y"][()].size == size_target
        assert fin["mesh/z"][()].size == size_target
        assert fin["variables/field_1"][()].size == size_target
        assert fin["variables/field_2"][()].size == size_target

    os.chdir(path_actu)


def test_dump_dico_2d_time_nparrays(datadir):
    """test of dumping of dico of 2d nparrays along time into files"""

    grid = np.zeros((DIM2, DIM2, 3))

    data_dict = {}
    data_dict["field"] = np.ones((DIM1, DIM2, DIM2))

    case = datadir
    path_actu = os.getcwd()
    os.chdir(case)

    dump_dico_2d_time_nparrays(
        data_dict,
        "./",
        "tmp",
        np.take(grid, 0, -1),
        np.take(grid, 1, -1),
        np.take(grid, 2, -1),
    )

    for step in range(DIM1):
        assert os.path.isfile(f"./tmp_{step:08}.h5")
        size_target = DIM2**2
        with h5py.File(f"./tmp_{step:08}.h5", "r") as fin:
            assert fin["mesh/x"][()].size == size_target
            assert fin["mesh/y"][()].size == size_target
            assert fin["mesh/z"][()].size == size_target
            assert fin["variables/field"][()].size == size_target
    assert os.path.isfile("./tmp_collection.xmf")

    os.chdir(path_actu)


def test_dump_dico_1d_nparrays(datadir):
    """test of dumping of dico of 1d nparrays into xlsx or csv file"""

    data_dict = {}
    data_dict["field_1"] = np.ones(DIM2)
    data_dict["field_2"] = np.ones(DIM2)

    case = datadir
    path_actu = os.getcwd()
    os.chdir(case)

    filename = "./dir1/tmp_1d.csv"
    dump_dico_1d_nparrays(filename, data_dict)
    assert os.path.isfile(filename)
    with open(filename, "r") as fin:
        lines = fin.readlines()
    assert lines[0] == "# field_1 ; field_2\n"
    assert len(lines) == DIM2 + 1

    filename = "./dir1/tmp_1d.xlsx"
    try:
        import pandas
        import openpyxl

        packages_exist = True
    except ImportError:
        packages_exist = False
    if packages_exist:
        dump_dico_1d_nparrays(filename, data_dict)
        assert os.path.isfile(filename)
    else:
        with pytest.raises(ImportError):
            dump_dico_1d_nparrays(filename, data_dict)

    os.chdir(path_actu)


def test_dump_dico_0d(datadir):
    """test of dumping of dico of 0d float into xlsx or csv file"""

    data_dict = {}
    data_dict["float_1"] = 4.0
    data_dict["float_2"] = 2.0

    case = datadir
    path_actu = os.getcwd()
    os.chdir(case)

    filename = "./dir2/tmp_0d.csv"
    dump_dico_0d(filename, data_dict)
    assert os.path.isfile(filename)
    with open(filename, "r") as fin:
        lines = fin.readlines()
    assert lines[0] == "# float_1 , float_2\n"
    assert len(lines) == 2

    filename = "./dir2/tmp_0d.xlsx"
    try:
        import pandas
        import openpyxl

        packages_exist = True
    except ImportError:
        packages_exist = False
    if packages_exist:
        dump_dico_0d(filename, data_dict)
        assert os.path.isfile(filename)
    else:
        with pytest.raises(ImportError):
            dump_dico_0d(filename, data_dict)

    os.chdir(path_actu)


def test_plot_dict_data_as_file(datadir):
    """test of the plot of dict data"""

    filename = "./dir3/tmp_plot.dummy_format"
    data_dict = {}
    data_dict["x_axis"] = np.linspace(0, DIM2 - 1, DIM2)
    data_dict["y_axis"] = np.ones(DIM2)

    case = datadir
    path_actu = os.getcwd()
    os.chdir(case)

    plot_dict_data_as_file(data_dict, filename, "x_axis", "y_axis")
    assert os.path.isfile("./dir3/tmp_plot.pdf")

    os.chdir(path_actu)
