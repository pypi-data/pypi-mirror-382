"""Functions for applying fixed real-valued shifts to numpy arrays using Lagrange interpolation

This provides a generic interface FixedShiftCore as well as an implementation using
Lagrange interpolation. The latter is written from scratch, see module
fixed_shift_dsp for another one based on the dsp.timeshift Lagrange interpolator.
"""

from __future__ import annotations

from typing import Callable, Final, Protocol, TypeAlias

import numpy as np
from typing_extensions import assert_never

from lisainstrument.sigpro.dynamic_delay_numpy import ShiftBC
from lisainstrument.sigpro.fir_filters_numpy import (
    DefFilterFIR,
    EdgeHandling,
    make_filter_fir_numpy,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d


def make_numpy_array_1d_float(a: np.ndarray) -> NumpyArray1D:
    """Ensure numpy array is 1D and floating point type"""
    a1 = make_numpy_array_1d(a)
    if not np.issubdtype(a.dtype, np.floating):
        msg = f"Expected numpy array with floating type, got {a.dtype}"
        raise TypeError(msg)
    return a1


class FixedShiftCore(Protocol):
    """Protocol for applying fixed shift to regularly spaced samples

    This defines an interface for applying a fixed shift to regularly spaced
    samples in 1D, provided as numpy arrays.

    Boundary treatment is not part of this protocol. Implementations only compute
    locations that can be interpolated to without using any form of boundary
    conditions. The corresponding margin sizes required by the interpolation
    method are exposed as properties.

    Arbitrary shifts are valid, but the main use case are shifts of magnitude around 1.
    For large shifts, the total margin size required will increase, in which case
    it might be more efficient to handle the integer shift before and then apply
    the remaining fractional shift.
    """

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) needed on the left boundary"""

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) needed on the right boundary"""

    @property
    def shift(self) -> float:
        """The shift"""

    def apply(self, samples: np.ndarray) -> NumpyArray1D:
        r"""Apply the fractional shift to a 1D numpy array.

        The output is the shifted input with left and right margins removed.
        Denoting the input data as :math:`y_i` with :math:`i=0 \ldots N-1`, and the interpolated
        input data as :math:`y(t)`, such that :math:`y(i)=y_i`, the output :math:`z_k` is given by
        :math:`z_k = y(k + M_L + s), k=0 \ldots N - 1 - M_L - M_R`, where :math:`M_L` and :math:`M_R`
        are the left and right margin sizes.

        Arguments:
            samples: 1D numpy array with sampled data
            start: integer part of
            size: number of points to return

        Returns:
            Interpolated samples
        """


FixedShiftFactory: TypeAlias = Callable[[float], FixedShiftCore]


def make_fir_lagrange_fixed(length: int, frac_shift: float) -> DefFilterFIR:
    r"""Create FIR filter corresponding to non-integer shift using Lagrange interpolation

    This creates a FIR filter with coefficients given by an Lagrangian
    interpolation polynomial evaluated at a fixed location :math:`s`.

    We work completely in index space of the input sequence, i.e. the
    coordinate of a given index is the index. The location :math:`s` also refers
    to index space.

    Thus, we specialize Lagrange interpolation to the case where
    the sample locations are
    :math:`t_j = j + D`, whith :math:`j=0 \ldots L-1`, and :math:`L` being the number of
    points to use. The integer offset :math:`D` determines which points to use,
    and should be chosen such that the center :math:`D + L/2` lies near :math:`s`.
    In other words, the input sequence indices :math:`D \ldots D+L-1` are used
    to interpolate to (fractional) index :math:`s`.

    So far we described interpolation to one location. The FIR filter
    is defined by simple translation, such that the element with index 0
    in the output sequence corresponds to the input sequence interpolated
    to fractional index :math:`s`, and any element :math:`a` to :math:`s+a`.

    .. math::

       y_a &= \sum_{j=0}^{L-1} K_j x_{a+j+D} \\
       K_j &= \prod_{\substack{m=0\\m \neq j}}^{L-1} \frac{s-D-m}{j-m}


    The offset is chosen to center the stencil around a shift
    :math:`s=0` for odd length and :math:`s=1/2` for even length. The shift should
    not exceed the bounds :math:`-1/2 < s < 1/2` for odd length or :math:`0 < s < 1`
    for even length significantly, to avoid large overshoots that inherently
    occur off-center for high order lagrange interpolation.

    Arguments:
        length: Number of FIR coefficients (=Lagrange order + 1)
        frac_shift: The shift :math:`s`

    Returns:
        FIR filter definition
    """

    if length <= 1:
        msg = f"make_fir_lagrange_fixed: stencil length must be 2 or more, got {length}"
        raise ValueError(msg)

    offset = -((length - 1) // 2)
    r = np.arange(length)
    m2, j2 = np.meshgrid(r, r)
    msk = m2 != j2
    s = np.array(frac_shift)
    x = s - offset
    p = np.ones_like(m2, dtype=np.float64)
    p[msk] = (x - m2[msk]) / (j2 - m2)[msk]
    kj = np.prod(p, axis=1)
    kj /= np.sum(kj)  # only to reduce rounding errors

    return DefFilterFIR(filter_coeffs=kj, offset=offset)


class FixedShiftLagrange(FixedShiftCore):
    r"""Class implementing fixed shift of regularly spaced 1D data using Lagrange interpolation.

    The algorithm uses Lagrange interpolation, using a FIR filter based on lagrange polynomials
    evaluated at fixed fractional shift. This uses a stencil with center as close to the
    location as possible. For odd length, the center point is obtained by rounding the
    location, and that the remaining fractional shift is within :math:`[-1/2,1/2]`. For even
    locations, the center points is the floor of the location, with remaining fractional
    shift within :math:`[0,1)`

    See FixedShiftCore for general properties not specific to the interpolation method.
    """

    def __init__(self, order: int, shift: float):
        """Set up interpolation parameters.

        The order parameter specifies the order of the interpolation polynomials. The
        number of samples used for each interpolation point is order + 1. The order of
        the interpolating polynomials is also the order of plynomials that are interpolated
        with zero error.

        The shift sign is defined such that positive values refer to locations
        to the right of the output sample at hand.

        Arguments:
            order: Order of the interpolation polynomials
            shift: The constant shift
        """

        length = order + 1
        loc = float(shift)
        if length % 2 == 0:
            loc_int = int(np.floor(loc))
        else:
            loc_int = int(np.round(loc))
        loc_frac = loc - loc_int

        firdef = make_fir_lagrange_fixed(length, loc_frac)

        self._margin_left = max(0, -firdef.domain_of_dependence[0] - loc_int)
        self._margin_right = max(0, firdef.domain_of_dependence[1] + loc_int)
        self._filt = make_filter_fir_numpy(
            firdef, EdgeHandling.VALID, EdgeHandling.VALID
        )
        self._shift = shift

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) needed on the left boundary"""
        return self._margin_left

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) needed on the right boundary"""
        return self._margin_right

    @property
    def shift(self) -> float:
        """The shift"""
        return self._shift

    def apply(self, samples: np.ndarray) -> NumpyArray1D:
        """Apply shift, see FixedShiftCore.apply()

        Arguments:
            samples: 1D numpy array with sampled data

        Returns:
            Shifted input excluding margins
        """
        a = make_numpy_array_1d_float(samples)
        return make_numpy_array_1d(self._filt(a))

    @staticmethod
    def factory(order: int) -> FixedShiftFactory:
        """Factory for making FixedShiftLagrange instances

        Arguments:
            order: The order of the Lagrange polynomials to use

        Returns:
            Factory function for making FixedShiftLagrange instances from shift
        """

        def factory(shift: float) -> FixedShiftCore:
            """FixedShiftLagrange instances from shift using preselected order

            Arguments:
                shift: The fixed shift

            Returns:
                FixedShiftLagrange instance
            """
            return FixedShiftLagrange(order, shift)

        return factory


class FixedShiftNumpy:  # pylint: disable=too-few-public-methods
    """Interpolate to locations given by a const shift.

    This allows to interpolate samples in a numpy array to locations specified
    by a fixed shift. The shift is specified in units of the array index, i.e.
    there is no separate coordinate array. A positive shift refers to values
    right of a given sample, negative shifts to values on the left.

    The boundary treatment can be specified for each boundary in terms of
    ShiftBC enums.

    The interpolation method is not fixed but provided via an interpolator
    instance implementing the FixedShiftCore protocol.

    """

    def __init__(
        self,
        left_bound: ShiftBC,
        right_bound: ShiftBC,
        interp_fac: FixedShiftFactory,
    ):
        """Not intended for direct use, employ named constructors instead

        Arguments:
            left_bound: boundary treatment on the left
            right_bound: boundary treatment on the right
            interp_fac: Function to create interpolator engine for given shift
        """
        self._left_bound: Final = left_bound
        self._right_bound: Final = right_bound
        self._interp_fac: Final = interp_fac

    def _padding_left(self, samples: np.ndarray, margin_left: int) -> np.ndarray:
        if margin_left > 0:
            match self._left_bound:
                case ShiftBC.ZEROPAD:
                    samples = np.pad(
                        samples, (margin_left, 0), mode="constant", constant_values=0.0
                    )
                case ShiftBC.FLAT:
                    samples = np.pad(
                        samples,
                        (margin_left, 0),
                        mode="constant",
                        constant_values=samples[0],
                    )
                case ShiftBC.EXCEPTION:
                    msg = (
                        f"FixedShiftNumpy: left edge handling {self._left_bound.name} not "
                        f"possible for given delay, need margin of {margin_left}."
                    )
                    raise RuntimeError(msg)
                case _ as unreachable:
                    assert_never(unreachable)
        elif margin_left < 0:
            samples = samples[-margin_left:]
        return samples

    def _padding_right(self, samples: np.ndarray, margin_right: int) -> np.ndarray:
        if margin_right > 0:
            match self._right_bound:
                case ShiftBC.ZEROPAD:
                    samples = np.pad(
                        samples, (0, margin_right), mode="constant", constant_values=0.0
                    )
                case ShiftBC.FLAT:
                    samples = np.pad(
                        samples,
                        (0, margin_right),
                        mode="constant",
                        constant_values=samples[-1],
                    )
                case ShiftBC.EXCEPTION:
                    msg = (
                        f"FixedShiftNumpy: right edge handling {self._right_bound.name} not "
                        f"possible for given delay, need margin of {margin_right}."
                    )
                    raise RuntimeError(msg)
                case _ as unreachable:
                    assert_never(unreachable)
        elif margin_right < 0:
            samples = samples[:margin_right]

        return samples

    def __call__(self, samples: np.ndarray, shift: float) -> NumpyArray1D:
        r"""Apply shift :math:`s` to samples in numpy array.

        Denoting the input data as :math:`y_i` with :math:`i=0 \ldots N-1`, and the interpolated
        input data as :math:`y(t)`, such that :math:`y(i)=y_i`, the output :math:`z_k` is given by
        :math:`z_k = y(k + s), k=0 \ ldots N - 1`.

        Required data outside the provided samples is created if the specified
        boundary condition allows it, or an exception is raised if the BC disallows it.
        The output has same length as the input.


        Arguments:
            samples: 1D numpy array with data samples
            shift: The shift :math:`s`

        Returns:
            Numpy array with interpolated samples
        """

        # pylint: disable=duplicate-code
        loc = float(shift)
        loc_int = int(np.floor(loc))
        loc_frac = loc - loc_int
        # pylint: enable=duplicate-code

        interp = self._interp_fac(loc_frac)

        margin_left = interp.margin_left - loc_int
        margin_right = interp.margin_right + loc_int

        samples_checked = make_numpy_array_1d(samples)
        samples_padleft = self._padding_left(samples_checked, margin_left)
        samples_padded = self._padding_right(samples_padleft, margin_right)

        return interp.apply(samples_padded)


def make_fixed_shift_lagrange_numpy(
    left_bound: ShiftBC, right_bound: ShiftBC, order: int
) -> FixedShiftNumpy:
    """Create a FixedShiftNumpy instance that uses Lagrange interpolator

    Arguments:
        left_bound: boundary treatment on the left
        right_bound: boundary treatment on the right
        order: Order of the Lagrange plolynomials

    Returns:
        Fixed shift interpolator
    """
    fac = FixedShiftLagrange.factory(order)
    return FixedShiftNumpy(left_bound, right_bound, fac)
