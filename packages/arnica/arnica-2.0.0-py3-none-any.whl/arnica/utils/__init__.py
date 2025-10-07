"""
=========
The utils
=========

The `utils` package provides helpers around CFD-related problems. They are categorized
into several groups, including:

1. **show_mat**: A matplotlib helper function for fast matrix plotting with legend and
   axis naming.
2. **cloud2cloud**: An inverse distance interpolator without connectivity.
3. **directed_projection**: A projection of vector clouds along their directions.
4. **vector_actions**: A set of vector transformation helpers.
5. **plot_density_mesh**: A mesh rendering tool using matplotlib hist2d.
6. **axi_shell**: A 2D i-j structured mesh mapping axycylindrical splaine-based
   surfaces.
7. **nparray2xmf**: A 1-2-3D i-j-k structured numpy datastructure dumping facility to
   XDMF format.

The code also mentions several untested and deprecated routines, including:

1. **unstructured_adjacency**: An untested mesh handling routine using connectivity.
2. **mesh_tools**: An untested 2D mesh generation routine in numpy for solvers.
3. **datadict2file**: A deprecated dumping facility for dictionary-like data.

"""

from arnica.utils.cloud2cloud import *
