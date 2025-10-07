"""
Utility functions.

This module provides utility functions for usual linear algebra operations on
Numpy arrays.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

from typing import Any, Callable, Generator

import numpy as np
from lisaconstants.indexing import mosa2sc
from numpy.typing import ArrayLike
from scipy.interpolate import make_interp_spline


def dot(a: ArrayLike, b: ArrayLike) -> np.ndarray:
    """Dot product on the last axis.

    Args:
        a: Input array.
        b: Input array.
    """
    a = np.asanyarray(a)
    b = np.asanyarray(b)
    return np.einsum("...j, ...j", a, b)


def norm(a: ArrayLike) -> Any:
    """Norm on the last axis.

    Args:
        a: Input array.
    """
    return np.linalg.norm(a, axis=-1)


def arrayindex(x: ArrayLike, a: ArrayLike) -> np.ndarray:
    """Return the array indices for ``x`` in ``a``.

    >>> a = [1, 3, 5, 7]
    >>> arrayindex([3, 7, 1], a)
    array([1, 3, 0])

    Args:
        x: Elements to search for, of shape ``(N,)``.
        a: Array in which elements are searched for.

    Returns:
        Indices of elements in ``a``, of shape ``(N,)``.

    Raises:
        ValueError: If not all elements of ``x`` cannot be found in ``a``.
    """
    if not np.all(np.isin(x, a)):
        raise ValueError("cannot find all items")
    return np.searchsorted(a, x)


def atleast_2d(a: ArrayLike) -> np.ndarray:
    """View inputs as arrays with at least two dimensions.

    Contrary to numpy's function, we here add the missing dimension
    on the last axis if needed.

    >>> np.atleast_2d(3.0)
    array([[3.]])
    >>> x = np.arange(3.0)
    >>> np.atleast_2d(x)
    array([[0., 1., 2.]])
    >>> np.atleast_2d(x).base is x
    True
    >>> np.atleast_2d(1, [1, 2], [[1, 2]])
    (array([[1]]), array([[1, 2]]), array([[1, 2]]))

    Args:
        a: Input array.

    Returns:
        An array (or an array view, when possible) with ``ndim >= 2``.
    """
    a = np.asanyarray(a)
    if a.ndim == 0:
        return a.reshape(1, 1)
    if a.ndim == 1:
        return a[:, np.newaxis]
    return a


@np.vectorize
def emitter(link: int) -> int:
    """Return emitter spacecraft index from link index.

    >>> emitter(12)
    array(2)
    >>> emitter([12, 31, 21])
    array([2, 1, 1])
    >>> emitter(np.array([23, 12]))
    array([3, 2])

    Args:
        link: Link index.

    Returns:
        Emitter spacecraft index.

    Raises:
        ValueError: If the link index is invalid.
    """
    return mosa2sc(link)[1]


@np.vectorize
def receiver(link: int) -> int:
    """Return receiver spacecraft index from a link index.

    >>> receiver(12)
    array(1)
    >>> receiver([12, 31, 21])
    array([1, 3, 2])
    >>> receiver(np.array([23, 12]))
    array([2, 1])

    Args:
        link: Link index.

    Returns:
        Receiver spacecraft index.

    Raises:
        ValueError: If the link index is invalid.
    """
    return mosa2sc(link)[0]


def chunk_slices(
    iterable_size: int, chunk_size: int | None
) -> Generator[slice, None, None]:
    """Generate slices for chunking an iterable.

    >>> list(chunk_slices(10, 3))
    [slice(0, 3, None), slice(3, 6, None), slice(6, 9, None), slice(9, 10, None)]

    Args:
        iterable_size: Size of the iterable.
        chunk_size: Size of the chunks.

    Yields:
        Slice objects for chunking the iterable.

    Raises:
        ValueError: If the iterable size or the chunk size is invalid.
    """
    if chunk_size is None:
        yield slice(None, None)
        return

    if iterable_size <= 0:
        raise ValueError(f"expected a positive iterable size, got {iterable_size}")
    if chunk_size <= 0:
        raise ValueError(f"expected a positive chunk size, got {chunk_size}")

    for start in range(0, iterable_size, chunk_size):
        end = min(start + chunk_size, iterable_size)
        yield slice(start, end)


def bspline_interp(
    t: ArrayLike, data: ArrayLike, k: int = 5, ext: str = "zeros"
) -> Callable[[ArrayLike], np.ndarray]:
    """Compute B-spline interpolants with control over extrapolation mode.

    Parameters
    ----------
    t : Array-like of shape (N,)
        Time coordinates between which to interpolate.
    data : Array-like of shape (N,)
        Data samples to interpolate (the spline interpolant will pass through
        those points).
    k : int
        Degree of the spline.
    ext : str, 'zeros' or 'raise'
        Controls the extrapolation mode for elements not in the interval
        defined by ``t``. If set to 'zeros', return 0. If set to 'raise',
        raise a ValueError.

    Returns
    -------
    Callable
        Spline interpolant as a callable object.

    Raises
    ------
    ValueError
        If the ``t`` and ``data`` sizes are not the same.
        If the ``ext`` parameter is not 'zeros' or 'raise'.
    """
    t = np.asanyarray(t)
    data = np.asanyarray(data)

    if t.size != data.size:
        raise ValueError("time and data sizes must be the same")

    scipy_interp = make_interp_spline(t, data, k=k)

    # Builds the interpolant function wth zero padding
    def interp_zeros(x: ArrayLike) -> np.ndarray:
        x = np.asarray(x)
        y = np.zeros_like(x)
        int_indices = np.logical_and(x >= t[0], x <= t[-1])
        y[int_indices] = scipy_interp(x[int_indices])
        return y

    # Builds the interpolant function with exception raising
    def interp_raise(x: ArrayLike) -> np.ndarray:
        x = np.asarray(x)
        if np.any(x < t[0]) or np.any(x > t[-1]):
            out_of_bound = x[(x < t[0]) | (x > t[-1])][0]
            raise ValueError(
                f"Interpolated times out of the allowed time range [{t[0]}, {t[-1]}] "
                f"(for example, {out_of_bound} is outside the range). Use ext='zeros' "
                "to get 0 for out-of-range values."
            )
        return scipy_interp(x)

    if ext == "zeros":
        return interp_zeros
    if ext == "raise":
        return interp_raise

    raise ValueError(
        f"Invalid option for 'ext': got '{ext}', expected 'zeros' or 'raise'."
    )
