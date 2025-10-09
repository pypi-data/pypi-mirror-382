"""Functions for interpolating numpy arrays with 1D  regularly spaced data

This provides a generic interface RegularInterpolator as well as two interpolation
methods, linear and Lagrange. The latter is written from scratch, see module
regular_interpolator_dsp for another one based on the dsp.timeshift Lagrange interpolator.
"""

from __future__ import annotations

import functools
import operator
from typing import Final, Protocol

import numpy as np
from numpy.polynomial import Polynomial

from lisainstrument.sigpro.fir_filters_numpy import (
    DefFilterFIR,
    EdgeHandling,
    FilterFirNumpyType,
    make_filter_fir_numpy,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d


class RegularInterpCore(Protocol):
    """Protocol for interpolator engine interface for regularly spaced samples

    This defines an interface for core functionality of interpolating regularly
    spaced samples in 1D, using numpy arrays. It is not intended for direct use
    but for use in the RegularInterpolator class.

    Boundary treatment is not part of this protocol. Implementations should only
    accept locations that can be interpolated to without using any form of boundary
    conditions, and raise an exception otherwise. The margin sizes required by the
    interpolation method are exposed as properties.
    """

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) on the left boundary

        The interpolator cannot be called with locations within this margin from the leftmost sample.
        """

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) on the right boundary

        The interpolator cannot be called with locations within this margin from the rightmost sample.
        """

    def apply(
        self,
        samples: NumpyArray1D,
        locations: NumpyArray1D,
        int_offsets: NumpyArray1D | int = 0,
    ) -> np.ndarray:
        """Interpolate regularly spaced data to location in index-space

        The locations to interpolate to are the sum of the locations and int_offsets arguments.
        The location argument is an 1D array with arbitrary floating point locations, and the
        int_offset argument is an integer or integer array with additional integer offsets. The locations
        argument is not restricted, i.e. it is not necessarily the residual fractional locations but
        can have arbitrary values.

        The locations refer to the index of the array with the sampled data, starting at 0.
        The length of samples array does not have to match the size of the location arrays.
        If int_offsets is an array, it needs to have same size arrays location and. All
        arrays need to be onedimensional.

        Implementations do not need to check the array dimensionality, size consistency, and types.
        This is done in RegularInterpolator.

        Arguments:
            samples: 1D numpy array with sampled data
            locations: real-valued 1D numpy array with locations to interpolate to
            int_offsets: integer or integer 1D array with additional offsets to the locations

        Returns:
            Interpolated samples
        """

    def apply_shift(
        self,
        samples: NumpyArray1D,
        shift: NumpyArray1D,
        shift_offset: int,
    ) -> np.ndarray:
        """Iterpolate to location specified in terms of shifts instead absolute locations

        The locations are specified via an array s of real-valued shifts. For the element s[i] of
        the shift array with array index i, the absolute location within the index space of the
        input samples is given by i + s[i] + ofs, where ofs is a constant integer offset. A zero
        shift means the output sample with index i is the input sample with index i+ofs.
        The offset can be positive or negative. Shift values that would require samples not
        in the input are not allowed. The output should be the same as for

        apply(samples, shift, shift_offset + np.arange(shift.shape[0]))

        Arguments:
            samples: 1D numpy array with sampled data
            shift: 1D float numpy array with shifts
            shift_offset: constant integer offset

        Returns:
            Interpolated samples
        """


def make_lagrange_polynomials(length: int, offset: int) -> list[Polynomial]:
    r"""Construct lagrange interpolating polynomials

    This constructs Lagrange interpolation polynomials with given order,
    specialized to regularly spaced coordinates with spacing of one, with a
    center specified in terms of an integer offset.

    This produces $N$ polynomials $p_j(x)$ of order $N-1$, which satisfy
    $p_j(k) = 1$ if $k = j+D$ and $p_j(k) = 0$ for integers $k=0 \ldots N-1, k \ne j$

    Arguments:
        length: The number $N$ of polynomials of order $N-1$
        offset: The offset $D$

    Returns:
        List of polynomials $p_j$ given as numpy Polynomial objects
    """

    def k_j(j: int) -> Polynomial:
        x = Polynomial([0.0, 1.0])
        ms = [i for i in range(length) if i != j]
        pm = [(x - offset - m) / (j - m) for m in ms]
        return functools.reduce(operator.mul, pm)

    return [k_j(j) for j in range(length)]


class RegularInterpLagrange(RegularInterpCore):
    r"""Class implementing interpolation of regularly spaced 1D data using Lagrange polynomials.

    The algorithm uses Lagrange interpolation is specialized to regularly spaced data.
    The coefficients of the Lagrange polynomials are computed in advance, and converted
    to a set of FIR filters. The FIR filters will be applied to the samples and the result
    at the integer locations multiplied with the corresponding power of the fractional
    locations.


    The formulation in terms of FIR filters works as follows. In general each interpolation
    location :math:`x` will use a Lagrange polynomial centered around a sample index we
    denote :math:`n(x)`. The interpolated function can be written as

    .. math::

       y(x) = \sum_{a=0}^P (x-x_{n(x)})^a C_{n(x)}^a

    where the :math:`x_n` are the sample point locations and :math:`C_{n}^a`
    are the coefficients of the interpolating polynomial centered around :math:`n`.
    The latter in turn depend linearly on the data samples, as

    .. math::

       C_n^a = \sum_{k=D}^{D+N-1} y_{n+k} L_k^a

    For fixed :math:`a`, the above obviously describes a FIR filter, where
    :math:`D` is the offset and :math:`N` the length of the convolution kernel.
    Thus, to evaluate the interpolation function, we apply :math:`P` different
    FIR filters to the sample data, and compute a weigthed sum with weights
    that depend on the interpolation locations.

    For the Lagrange polynomials, we have :math:`N = P + 1`. The choice for
    :math:`n(x)` and for the offset :math:`D` are related. The goal is to
    use the polynomial build from a stencil with center closest to the
    given interpolation location.
    For odd length, the center point is obtained by rounding the
    location, and that the remaining fractional shift is within
    :math:`[-1/2,1/2]`. For even length, the center points is the floor
    of the location, with remaining fractional shift within
    :math:`[0,1)`



    See RegularInterpCore for general properties not specific to the interpolation method.
    """

    @staticmethod
    @functools.cache
    def _make_firs(length: int, offset: int) -> list[FilterFirNumpyType]:
        """Set up lagrange polynomials and convert coefficients to FIR filters"""
        plag = make_lagrange_polynomials(length, offset)
        coeffs = np.array([p.convert().coef for p in plag]).T
        filts: list[FilterFirNumpyType] = []
        for c in coeffs:
            fdef = DefFilterFIR(filter_coeffs=c, offset=offset)
            filt = make_filter_fir_numpy(fdef, EdgeHandling.VALID, EdgeHandling.VALID)
            filts.append(filt)
        return filts

    def __init__(self, order: int):
        """Set up interpolation parameters.

        The order parameter specifies the order of the interpolation polynomials. The
        number of samples used for each interpolation point is order + 1. The order of
        the interpolating polynomials is also the order of polynomials that are interpolated
        with zero error.

        Arguments:
            order: order of the interpolation polynomials
        """
        length = order + 1
        if length <= 1:
            msg = f"RegularInterpLagrange: order must be >= 1, got {length}"
            raise ValueError(msg)

        offset = -((length - 1) // 2)
        self._length: Final[int] = length
        self._offset: Final[int] = offset
        self._fir_filt: Final[list[FilterFirNumpyType]] = self._make_firs(
            length, offset
        )

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) on the left boundary

        The interpolator cannot be called with locations within this margin from the leftmost sample.
        """
        return -self._offset

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) on the right boundary

        The interpolator cannot be called with locations within this margin from the rightmost sample.
        """
        return self._length - 1 + self._offset

    def apply(
        self,
        samples: NumpyArray1D,
        locations: NumpyArray1D,
        int_offsets: NumpyArray1D | int = 0,
    ) -> np.ndarray:
        """Interpolate regularly spaced data to location in index-space

        See RegularInterpCore.apply()

        Arguments:
            samples: real-valued 1D numpy array with sampled data
            locations: real-valued 1D numpy array with locations to interpolate to
            int_offsets: integer or integer 1D array with additional offsets to the locations.

        Returns:
            Interpolated samples.
        """

        if self._length % 2 == 0:
            loc_int = np.floor(locations).astype(int)
        else:
            loc_int = np.round(locations).astype(int)
        loc_frac = locations - loc_int
        k = loc_int + int_offsets - self.margin_left

        if np.any(k < 0):
            msg = "RegularInterpLagrange: interpolation requires samples below provided range"
            raise RuntimeError(msg)
        if np.any(k >= samples.shape[0] - self._length + 1):
            msg = "RegularInterpLagrange: interpolation requires samples above provided range"
            raise RuntimeError(msg)

        result = self._fir_filt[0](samples)[k]
        xpow = loc_frac.copy()
        for fir in self._fir_filt[1:]:
            result[:] += fir(samples)[k] * xpow
            xpow[:] *= loc_frac

        return result

    def apply_shift(
        self,
        samples: NumpyArray1D,
        shift: NumpyArray1D,
        shift_offset: int,
    ) -> np.ndarray:
        """Iterpolate to location specified in terms of shifts instead absolute locations

        See RegularInterpCore.apply_shift().

        Arguments:
            samples: 1D numpy array with sampled data
            shift: 1D float numpy array with shifts
            shift_offset: constant integer offset

        Returns:
            Interpolated samples
        """
        offsets = shift_offset + np.arange(shift.shape[0])
        return self.apply(
            samples, make_numpy_array_1d(shift), make_numpy_array_1d(offsets)
        )


class RegularInterpLinear(RegularInterpCore):
    """Class implementing interpolation of regularly spaced 1D data using linear interpolation.

    See RegularInterpCore for general properties not specific to the interpolation method.
    """

    @property
    def margin_left(self) -> int:
        """Margin size (= 0) on the left boundary

        The linear interpolator can be called for all locations within the sample range.
        """
        return 0

    @property
    def margin_right(self) -> int:
        """Margin size (= 0) on the right boundary

        The linear interpolator can be called for all locations within the sample range.
        """
        return 0

    def apply(
        self,
        samples: NumpyArray1D,
        locations: NumpyArray1D,
        int_offsets: NumpyArray1D | int = 0,
    ) -> np.ndarray:
        """Interpolate regularly spaced data to location in index-space

        See RegularInterpCore.apply()

        Arguments:
            samples: 1D numpy array with sampled data
            locations: real-valued 1D numpy array with locations to interpolate to
            int_offsets: integer or integer 1D array with additional offsets to the locations.

        Returns:
            Interpolated samples.
        """

        loc_floor = np.floor(locations)
        loc_frac = locations - loc_floor

        k = loc_floor.astype(int) + int_offsets

        if np.any(k < 0) or np.any(k + 1 >= samples.shape[0]):
            msg = "RegularInterpLinear: interpolation requires samples out of provided range"
            raise RuntimeError(msg)

        return samples[k] * (1.0 - loc_frac) + samples[k + 1] * loc_frac

    def apply_shift(
        self,
        samples: NumpyArray1D,
        shift: NumpyArray1D,
        shift_offset: int,
    ) -> np.ndarray:
        """Iterpolate to location specified in terms of shifts instead absolute locations

        See RegularInterpCore.apply_shift().

        Arguments:
            samples: 1D numpy array with sampled data
            shift: 1D float numpy array with shifts
            shift_offset: constant integer offset

        Returns:
            Interpolated samples
        """
        offsets = shift_offset + np.arange(shift.shape[0])
        return self.apply(
            samples, make_numpy_array_1d(shift), make_numpy_array_1d(offsets)
        )


class RegularInterpolator:
    """User-facing class for interpolation of regularly spaced data

    The interpolation method is not fixed but given by an interpolation engine.
    The main purpose of this class is to provide the parameter checks common
    to all interpolation methods.
    """

    def __init__(self, core: RegularInterpCore):
        """Constructor not intended for direct use.

        Use named constructors make_regular_interpolator_lagrange() or
        make_regular_interpolator_linear() to get interpolators employing specific methods.
        """
        self._core: Final = core

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) on the left boundary

        The interpolator cannot be called with locations within this margin from the leftmost sample.
        """
        return self._core.margin_left

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) on the right boundary

        The interpolator cannot be called with locations within this margin from the rightmost sample.
        """
        return self._core.margin_right

    def __call__(
        self,
        samples_: np.ndarray,
        locations_: np.ndarray,
        int_offsets_: np.ndarray | int,
    ) -> NumpyArray1D:
        """Interpolate regularly spaced data to location in index-space

        The locations to interpolate to are the sum of the locations and int_offsets arguments.
        The location argument is an 1D array with arbitrary floating point locations, and the
        int_offset argument is an integer or integer array with additional integer offsets. The locations
        argument is not restricted, i.e. it is not necessarily the residual fractional locations but
        can have arbitrary values.

        The locations refer to the index of the array with the sampled data, starting at 0.
        The length of samples array does not have to match the size of the location arrays.
        If int_offsets is an array, it needs to have same size arrays location and. All
        arrays need to be onedimensional.

        The locations must be within the margins given by the margin_left and margin_right
        properties.

        Arguments:
            samples: 1D numpy array with sampled data
            locations: real-valued 1D numpy array with locations to interpolate to
            int_offsets: integer or integer 1D array with additional offsets to the locations.

        Returns:
            Interpolated samples.
        """

        samples = make_numpy_array_1d(samples_)
        if not np.issubdtype(samples_.dtype, np.floating):
            msg = "RegularInterpolator: non-float dtype for samples not allowed"
            raise TypeError(msg)

        locations = make_numpy_array_1d(locations_)
        if not np.issubdtype(locations_.dtype, np.floating):
            msg = "RegularInterpolator: non-float dtype for locations not allowed"
            raise TypeError(msg)

        int_offsets: NumpyArray1D | int

        if isinstance(int_offsets_, np.ndarray):
            int_offsets = make_numpy_array_1d(int_offsets_)
            if int_offsets_.shape != locations_.shape:
                msg = (
                    f"RegularInterpolator: inconsistent arrays sizes of "
                    f"locations ({locations_.shape}) and offsets ({int_offsets_.shape})"
                )
                raise ValueError(msg)
            if not np.issubdtype(int_offsets_.dtype, np.integer):
                msg = (
                    "RegularInterpolator: non-integer dtype for int_offsets not allowed"
                )
                raise TypeError(msg)
        elif isinstance(int_offsets_, int):
            int_offsets = int_offsets_
        else:
            msg = "RegularInterpolator: int_offset must be integer or integer array"
            raise TypeError(msg)

        res = self._core.apply(samples, locations, int_offsets)
        return make_numpy_array_1d(res)

    def apply_shift(
        self,
        samples_: np.ndarray,
        shift_: np.ndarray,
        shift_offset: int,
    ) -> NumpyArray1D:
        """Iterpolate to location specified in terms of shifts instead absolute locations

        See RegularInterpCore.apply_shift().

        Arguments:
            samples: 1D numpy array with sampled data
            shifts: 1D float numpy array with shifts
            shift_offset: constant integer offset

        Returns:
            Interpolated samples
        """

        samples = make_numpy_array_1d(samples_)
        if not np.issubdtype(samples_.dtype, np.floating):
            msg = "RegularInterpolator: non-float dtype for samples not allowed"
            raise TypeError(msg)

        shift = make_numpy_array_1d(shift_)
        if not np.issubdtype(shift_.dtype, np.floating):
            msg = "RegularInterpolator: non-float dtype for shifts not allowed"
            raise TypeError(msg)

        res = self._core.apply_shift(samples, shift, shift_offset)
        return make_numpy_array_1d(res)


def make_regular_interpolator_lagrange(order: int) -> RegularInterpolator:
    """Create an interpolator using Lagrange interpolation

    See RegularInterpLagrange for details of the method.

    Arguments:
        order: order of the interpolating polynomials
    Returns:
        Interpolation function
    """
    return RegularInterpolator(RegularInterpLagrange(order))


def make_regular_interpolator_linear() -> RegularInterpolator:
    """Create an interpolator using linear interpolation

    Returns:
        Interpolation function
    """
    return RegularInterpolator(RegularInterpLinear())
