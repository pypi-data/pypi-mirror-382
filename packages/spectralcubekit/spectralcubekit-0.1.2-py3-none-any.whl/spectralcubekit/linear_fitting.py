# Standard Libraries
from typing import Annotated, Callable
from dataclasses import dataclass
import os
from pathlib import Path

# Dependencies
import numpy as np
import numpy.typing as npt
from astropy.io import fits  # type: ignore

Numpy4D = Annotated[npt.NDArray[np.float32], (4,)]
Numpy3D = Annotated[npt.NDArray[np.float32], (3,)]
Numpy2D = Annotated[npt.NDArray[np.float32], (2,)]
Numpy1D = Annotated[npt.NDArray[np.float32], (1,)]

PathLike = str | os.PathLike | Path


@dataclass
class FitResult:
    """
    Base class for linear fitting results.

    Attributes
    ----------
    xdata: Numpy1D or Numpy3D
        X data (wavelengths) used in the fit. 1D if uniform, 3D if variable by
        pixel.
    ydata: Numpy3D
        Y data (reflectance) used in the fit.
    model: Numpy3D
        Cube of fitted lines.
    beta: Numpy3D
        Cube of slope and intercept.
    res: Numpy3D
        Residual errors on the fit.
    """

    xdata: Numpy1D | Numpy3D
    ydata: Numpy3D
    model: Numpy3D
    beta: Numpy3D
    res: Numpy3D

    def r_squared(self) -> Numpy2D:
        """
        Returns the coefficient of determination (R<sup>2</sup>)
        """
        ss_res = np.sum(self.res**2, axis=2)
        ss_tot = np.sum(
            (self.ydata - np.mean(self.ydata, axis=-1)[:, :, None]) ** 2
        )
        return 1 - (ss_res / ss_tot)


@dataclass
class ErrorFitResult(FitResult):
    """
    Specialized fit result class for returning linear fits with errors.

    Attributes
    ----------
    yerr: Callable
        A function that returns the error on the y value at a given x value.
    beta_err: Numpy3D
        A cube of errors on the slope and intercept.
    """

    yerr: Callable
    beta_err: Numpy3D


def save_fit(fit: FitResult, fits_file: PathLike) -> None:
    """
    Saves a FitResult object to a *.fits file.

    Parameters
    ----------
    fit: FitResult
        FitResult object to be saved.
    fits_file: PathLike
        Path to *.fits file save.
    """
    fits_file = Path(fits_file).with_suffix(".fits")
    primary_HDU = fits.PrimaryHDU(np.transpose(fit.beta, (2, 0, 1)))
    if isinstance(fit, ErrorFitResult):
        param_error = fits.ImageHDU(
            np.transpose(fit.beta_err, (2, 0, 1)), name="ERROR"
        )
        hdul = fits.HDUList([primary_HDU, param_error])
        hdul.writeto(fits_file, overwrite=True)
        return

    hdul = fits.HDUList([primary_HDU])
    hdul.writeto(fits_file, overwrite=True)


def _fit_cube_sharedX(G: Numpy2D, d: Numpy3D) -> FitResult:
    """
    Solves a pixel-by-pixel linear least squares regression where each pixel
    has one shared design matrix.

    G: 2D numpy array
        A shared design matrix for all pixels of shape [NxM] where N is the
        number of samples and M is the number of fit parameters.
    d: 3D number array
        Data cube to fit with shape [IxJxN] where I and J are pixel dimensions
        and N is the number of samples.
    """
    prefix = np.linalg.inv(G.T @ G) @ G.T
    beta = np.einsum("ij,...j->...i", prefix, d)
    model = np.einsum("ij,...j->...i", G, beta)
    res = model - d
    return FitResult(G[:, 0], d, model, beta, res)


def _fit_cube_varX(G: Numpy4D, d: Numpy3D) -> FitResult:
    """
    Solves a pixel-by-pixel linear least squares regression where each pixel
    has a different design matrix.

    G: 4D numpy array
        Pixel-by-pixel design matrices with shape [IxJxNxM] where I and J are
        pixel dimensions, N is the number of samples and M is the number of
        fit parameters.
    d: 3D numpy array
        Data cube to fit with shape [IxJxN] where I and J are pixel dimensions
        and N is the number of samples.
    """
    GtG = np.einsum("...ij,...jk->...ik", G.transpose(0, 1, 3, 2), G)
    GtG_inv = np.linalg.inv(GtG)
    prefix = np.einsum("...ij,...jk->...ik", GtG_inv, G.transpose(0, 1, 3, 2))

    beta = np.einsum("...ij,...j->...i", prefix, d)
    model = np.einsum("...ij,...j->...i", G, beta)
    res = model - d
    return FitResult(G[..., 0], d, model, beta, res)


def _fit_cube_sharedX_weighted(
    G: Numpy2D, d: Numpy3D, W: Numpy4D
) -> ErrorFitResult:
    """
    Same as `_fit_cubed_sharedX` but allows for a 2D weights matrix.
    """
    GtW = np.einsum("ij,...jk->...ik", G.T, W)
    GtWG = np.einsum("...ij,jk->...ik", GtW, G)
    GtWG_inv = np.linalg.inv(GtWG)
    prefix = np.einsum("...ij,...jk->...ik", GtWG_inv, GtW)

    beta = np.einsum("...ij,...j->...i", prefix, d)
    model = np.einsum("...ij,...j->...i", G, beta)
    res = model - d
    beta_err = np.sqrt(np.abs(np.diagonal(GtWG_inv, axis1=-2, axis2=-1)))

    def yerr(x: np.ndarray) -> np.ndarray:
        return (
            GtWG[:, :, 1, 1][:, :, None]
            + 2 * GtWG[:, :, 0, 1][:, :, None] * x[None, None, :]
            + GtWG[:, :, 0, 0][:, :, None] * x[None, None, :] ** 2
        )

    return ErrorFitResult(G[..., 0], d, model, beta, res, yerr, beta_err)


def _fit_cube_varX_weighted(
    G: Numpy4D, d: Numpy3D, W: Numpy4D
) -> ErrorFitResult:
    """
    Same as `_fit_cube_varX` but allows for a 4D weights matrix.
    """
    GtW = np.einsum("...ij,...jk->...ik", G.transpose(0, 1, 3, 2), W)
    GtWG = np.einsum("...ij,...jk->...ik", GtW, G)
    GtWG_inv = np.linalg.inv(GtWG)
    prefix = np.einsum("...ij,...jk->...ik", GtWG_inv, GtW)

    beta = np.einsum("...ij,...j->...i", prefix, d)
    model = np.einsum("...ij,...j->...i", G, beta)
    res = model - d
    beta_err = np.sqrt(np.abs(np.diagonal(GtWG_inv, axis1=-2, axis2=-1)))

    def yerr(x: float) -> float:
        return GtWG[1, 1] + 2 * GtWG[0, 1] * x + GtWG[0, 0] * x**2

    return ErrorFitResult(G[..., 0], d, model, beta, res, yerr, beta_err)


def fit_linear_cube(
    cube: Numpy3D, xdata: Numpy1D | Numpy3D, bandsfirst: bool = False
) -> FitResult:
    """
    Fits a line to each pixel in an image cube. Each pixel can either have
    unique X-data or the entire image can have one set of shared X-data for
    every pixel.

    Parameters
    ----------
    cube: 3D numpy array
        Data cube to fit with shape [IxJxN] where I and J are pixel dimensions
        and N is the number of samples.
    xdata: 1D or 3D numpy array
        Either a shared set of X-data for all pixels of shape [N] where N
        is the number of samples or a cube of X-data of shape [IxJxN] where I
        and J are the pixel dimensions and N is the number of samples.

    Returns
    -------
    model: FitResult
        Results of the fitting. No errors included.
    """
    if bandsfirst:
        cube = np.transpose(cube, (1, 2, 0))
        xdata = np.transpose(xdata, (1, 2, 0))

    if xdata.ndim == 1:
        G = np.stack([xdata, np.ones(xdata.shape)], axis=1, dtype=np.float32)
        d = cube.astype(np.float32)
        fitresult = _fit_cube_sharedX(G, d)
    elif xdata.ndim == 3:
        G = np.stack([xdata, np.ones(xdata.shape)], axis=3, dtype=np.float32)
        d = cube.astype(np.float32)
        fitresult = _fit_cube_varX(G, d)
    else:
        raise ValueError(f"{xdata.ndim} is an invalid number of dimensions.")

    return fitresult


def fit_linear_cube_with_error(
    cube: Numpy3D,
    xdata: Numpy1D | Numpy3D,
    yerr: Numpy3D,
    bandsfirst: bool = False,
) -> ErrorFitResult:
    """
    Same as `fit_linear_cube` but allows for the input of y errors.

    Parameters
    ----------
    cube: 3D numpy array
        Data cube to fit with shape [IxJxN] where I and J are pixel dimensions
        and N is the number of samples.
    xdata: 1D or 3D numpy array
        Either a shared set of X-data for all pixels of shape [N] where N
        is the number of samples or a cube of X-data of shape [IxJxN] where I
        and J are the pixel dimensions and N is the number of samples.
    yerr: 3D numpy array

    Returns
    -------
    """
    if bandsfirst:
        cube = np.transpose(cube, (1, 2, 0))
        yerr = np.transpose(yerr, (1, 2, 0))
        if xdata.ndim == 3:
            xdata = np.transpose(xdata, (1, 2, 0))

    weights = np.ones(yerr.shape[:2])[:, :, None] / yerr**2
    W = weights[..., None].astype(np.float32) * np.eye(
        yerr.shape[2], dtype=np.float32
    )
    if xdata.ndim == 1:
        G = np.stack([xdata, np.ones(xdata.shape)], axis=1, dtype=np.float32)
        d = cube.astype(np.float32)
        fitresult = _fit_cube_sharedX_weighted(G, d, W)
    elif xdata.ndim == 3:
        G = np.stack([xdata, np.ones(xdata.shape)], axis=3, dtype=np.float32)
        d = cube.astype(np.float32)
        fitresult = _fit_cube_varX_weighted(G, d, W)
    else:
        raise ValueError(f"{xdata.ndim} is an invalid number of dims.")

    return fitresult


def fit_single_line(x: np.ndarray, y: np.ndarray):
    n = x.size
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xx = np.sum(x * x)
    sum_xy = np.sum(x * y)

    denominator = n * sum_xx - sum_x**2
    if denominator == 0:
        raise ValueError("Denominator in least squares fit is zero.")

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y * sum_xx - sum_x * sum_xy) / denominator

    model = slope * x + intercept

    sum_squared_res = np.sum((y - model) ** 2)
    x_variance = np.sum((x - np.mean(x)) ** 2)
    sum_squared_meandiff = np.sum((y - np.mean(y)) ** 2)

    r_squared = 1 - (sum_squared_res / sum_squared_meandiff)
    slope_err = np.sqrt((1 / (n - 2)) * sum_squared_res / x_variance)

    return slope, slope_err, intercept, r_squared


def fit_single_line_with_error(x: np.ndarray, y: np.ndarray, yerr: np.ndarray):
    """
    Fits a single line.

    Parameters
    ----------
    x: np.ndarray
        X Data
    y: np.ndarray
        Y Data
    yerr: np.ndarray
        Errors on Y Data

    Returns
    -------
    xfit, yfit, error_envelope, slope, slope_err, intercept, intercept_err
    """
    G = np.concat([x[:, np.newaxis], np.ones([len(x), 1])], axis=1)
    b = y[:, None] / yerr[:, None]
    A = G / yerr[:, None]
    C = np.linalg.inv(A.T @ A)
    m = C @ A.T @ b

    slope = m[0, 0]
    slope_err = np.sqrt(C[0, 0])
    intercept = m[1, 0]
    intercept_err = np.sqrt(C[1, 1])

    def fit(x):
        return slope * x + intercept

    def error_envelope(x):
        return np.sqrt(C[1, 1] + 2 * C[0, 1] * x + C[0, 0] * x**2)

    return fit, error_envelope, slope, slope_err, intercept, intercept_err
