"""
# spectralcubekit

A toolkit for working with any and all flavors of spectral data cubes.
"""

from .misc_utils import last_nonzero_val_3D
from .linear_fitting import fit_linear_cube, fit_linear_cube_with_error
from .band_parameters import three_band_depth

__all__ = [
    "last_nonzero_val_3D",
    "three_band_depth",
    "fit_linear_cube",
    "fit_linear_cube_with_error",
]
