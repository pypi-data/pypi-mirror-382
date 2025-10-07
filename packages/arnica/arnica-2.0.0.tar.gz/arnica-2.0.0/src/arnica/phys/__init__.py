"""
==================
Physical utilities
==================

The `phys` package provides physical utilities for computational fluid dynamics (CFD)
problems. It includes modules for thermodynamic properties, solid materials, and wall
thermal equilibrium.

* `thermodyn_properties`: computes thermal constants and values related to turbulence.
* `solid_material`: represents a solid material with methods for calculating thermal
  conductivity and resistance.
* `yk_from_phi`: calculates mass fractions of species from a given Phi coefficient.
* `wall_thermal_equilibrium`: computes the thermal equilibrium for a 2-layer wall
  (Metal/ceramic) by iteratively estimating temperatures until convergence.

"""

from arnica.phys.solid_material import *
from arnica.phys.thermodyn_properties import *
from arnica.phys.wall_thermal_equilibrium import *
from arnica.phys.yk_from_phi import *
