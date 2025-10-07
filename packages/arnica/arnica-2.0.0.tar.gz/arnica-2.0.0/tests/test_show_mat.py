import numpy as np
from arnica.utils.show_mat import show_mat


def test_show_mat():
    def samplemat(dims):
        """Make a matrix with all zeros and increasing elements
        on the diagonal ans last dim"""
        aa = np.zeros(dims)
        for i in range(min(dims)):
            aa[i, :i] = i
        return aa

    # Display matrix
    show_mat(samplemat((15, 15)), "trout", show=False)
