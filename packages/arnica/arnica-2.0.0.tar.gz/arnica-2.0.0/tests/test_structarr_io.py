from arnica.utils.structarr_io import sa2da, da2sa

import numpy as np


def test_structarr_io():

    data_dict = {
        "a": np.array([1, 2, 3]),
        "b": np.array([4.5, 5.5, 6.5]),
        "c": np.array(["x", "y", "z"]),
    }

    dtype = [("a", "i4"), ("b", "f8"), ("c", "U1")]  # Integer, float, string
    structured_array = np.array(
        [(1, 4.5, "x"), (2, 5.5, "y"), (3, 6.5, "z")], dtype=dtype
    )

    assert np.allclose(structured_array["a"], data_dict["a"])
    assert np.allclose(structured_array["b"], data_dict["b"])
    assert list(structured_array["c"]) == list(data_dict["c"])

    assert np.allclose(structured_array["a"], da2sa(data_dict)["a"])
    assert np.allclose(structured_array["b"], da2sa(data_dict)["b"])
    assert list(structured_array["c"]) == list(da2sa(data_dict)["c"])

    assert np.allclose(data_dict["a"], sa2da(structured_array)["a"])
    assert np.allclose(data_dict["b"], sa2da(structured_array)["b"])
    assert list(data_dict["c"]) == list(sa2da(structured_array)["c"])
    # print(structured_array)
    # print( da2sa(data_dict))
