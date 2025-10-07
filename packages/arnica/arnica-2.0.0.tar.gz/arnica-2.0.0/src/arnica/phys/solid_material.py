"""
 This module defines a class `SolidMaterial` that represents a solid material for
 thermal computations.

 This class has two main methods: `lambda_th` and `thermal_resistance` : The `lambda_th`
 method returns the thermal conductivity (`lambda`) of the material at a given
 temperature. It clips the input temperature to ensure it falls within the valid range
 defined by `_lambda_range`. The method then uses the polynomial representation of the
 material's thermal conductivity to calculate the value at the clipped temperature.

 The `thermal_resistance` method calculates the thermal resistance of a layer with a
 given width and estimated temperature (`t_est`). It returns the thermal resistance in
 units of square meters per Kelvin per Watt (m2.K/W).


 """

import numpy as np

__all__ = ["SolidMaterial"]


class SolidMaterial:
    """define properties of a solid material object"""

    def __init__(self, lambda_poly, lambda_range):
        """startup class"""
        self._lambda_range = lambda_range
        self._lambda_raw = np.poly1d(lambda_poly[::-1])

    def lambda_th(self, temperature):
        """return the lambda of ceramics material [W/mK]"""
        t_clip = np.minimum(temperature, self._lambda_range[1])
        t_clip = np.maximum(t_clip, self._lambda_range[0])
        return self._lambda_raw(t_clip)

    def thermal_resistance(self, width, t_est):
        """return the thermal resistance  [m2.K/W]
        width : width of the layer
        t_est : estimated temperature of the layer"""
        return width / self.lambda_th(t_est)
