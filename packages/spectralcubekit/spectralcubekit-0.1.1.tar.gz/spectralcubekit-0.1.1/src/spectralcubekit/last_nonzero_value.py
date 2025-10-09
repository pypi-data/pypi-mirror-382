import numpy as np


def last_nonzero_val_3D(cube, return_index=False):
    """
    If you have an empty 3D image array with the first two dimensions being
    pixels and the third dimension of size N, and each pixel is filled in to a
    certain depth, M <= N, this function returns a 2D image array that picks
    out all the pixel values at position M.
    """
    nx, ny, _ = cube.shape
    result = np.full((nx, ny), np.nan, dtype=cube.dtype)
    for i in range(nx):
        for j in range(ny):
            vals = cube[i, j, :]
            nonzero_indices = np.nonzero(np.isfinite(vals))[0]
            if return_index:
                result[i, j] = (
                    nonzero_indices[-1] if nonzero_indices.size > 0 else np.nan
                )
            else:
                result[i, j] = (
                    vals[nonzero_indices[-1]]
                    if nonzero_indices.size > 0
                    else np.nan
                )
    return result
