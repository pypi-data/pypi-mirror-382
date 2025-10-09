# Dependencies
import numpy as np


def three_band_depth(
    Ra: np.ndarray,
    Rb: np.ndarray,
    Rc: np.ndarray,
    Wa: float,
    Wb: float,
    Wc: float,
):
    """
    Finds the band depth given two shoulder bands (Ra, Rc) and a central band
    (Rb) and their corresponding wavelengths (Wa, Wb, Wc).

    Parameters
    ----------
    Ra: np.ndarray
        Reflectance at lower shoulder.
    Rb: np.ndarray
        Reflectance at the band center.
    Rc: np.ndarray
        Reflectance at upper shoulder.
    Wa: float
        Wavelength at lower shoulder.
    Wb: float
        Wavelength at the band center.
    Wc: float
        Reflectance at upper shoulder.

    """
    Rb_proj = (((Rc - Ra) / (Wc - Wa)) * (Wb - Wa)) + Ra
    return Rb_proj - Rb
