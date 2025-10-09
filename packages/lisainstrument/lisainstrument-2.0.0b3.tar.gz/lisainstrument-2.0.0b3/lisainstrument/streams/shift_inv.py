"""Module with stream types for coordinate transform inversion

Given a stream with a time shift defining a time coordinate transform,
this allows to compute a stream with the time shift for the inverted coordinate
transform.
Use stream_shift_inv_lagrange to create a shift inversion acting on streams using
Lagrange interpolation with given order, in conjunction with fixed point iteration.

Internally, this is implemented in the classes StreamShiftInv, which can employ
any RegularInterpolator from sigpro.regular_interpolators for interpolation.
"""

from __future__ import annotations

from typing import Any, Callable, Final

import numpy as np

from lisainstrument.sigpro.regular_interpolators import (
    RegularInterpolator,
    make_regular_interpolator_lagrange,
)
from lisainstrument.sigpro.shift_inversion_numpy import fixed_point_iter
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d
from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamShiftInv(StreamBase):
    """Stream representing inversion of time coordinate transform

    See sigpro.shift_inversion_numpy.ShiftInverseNumpy for the mathematical
    definitions.
    """

    def __init__(
        self,
        time_delay: StreamBase,
        sample_dt: float,
        max_abs_shift: float,
        interp: RegularInterpolator,
        max_iter: int,
        tolerance: float,
    ):
        """Not part of API, use stream_shift_inv_lagrange instead"""
        if time_delay.dtype != np.dtype(float):
            msg = f"StreamShiftInv: time_delay data type must be float, got {time_delay.dtype}"
            raise RuntimeError(msg)
        if sample_dt <= 0:
            msg = (
                f"StreamShiftInv: sample_dt must be strictly positive, got {sample_dt}"
            )
            raise RuntimeError(msg)
        if max_abs_shift < 0:
            msg = f"StreamShiftInv: got invalid negative {max_abs_shift=}"
            raise RuntimeError(msg)
        if max_iter <= 0:
            msg = f"StreamShiftInv: max_iter must be strictly positive integer, got {max_iter}"
            raise RuntimeError(msg)
        if tolerance <= 0:
            msg = (
                f"StreamShiftInv: tolerance must be strictly positive, got {tolerance}"
            )
            raise RuntimeError(msg)

        self._sample_dt: Final = float(sample_dt)
        self._max_abs_shift_idx: Final = int(np.ceil(max_abs_shift / self._sample_dt))

        self._interp: Final = interp
        self._max_iter: Final = int(max_iter)
        self._tolerance_idx: Final = float(tolerance / self._sample_dt)
        self._margin_left: Final = self._interp.margin_left + self._max_abs_shift_idx
        self._margin_right: Final = self._interp.margin_right + self._max_abs_shift_idx

        dep = StreamDependency(
            stream=time_delay,
            dod_first=-self._margin_left,
            dod_last=self._margin_right,
        )

        super().__init__([dep], False, float)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg_shift,) = deps

        i0, i1 = istart - self._margin_left, istop + self._margin_right

        if not seg_shift.istart <= i0 <= i1 <= seg_shift.istop:
            msg = (
                f"StreamShiftInv: sample data not covering required interval {i0}, {i1}"
            )
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, dtype=self.dtype), None

        dx_pad = np.empty(i1 - i0, dtype=self.dtype)
        seg_shift.write(dx_pad, istart=i0, istop=i1)
        np.divide(dx_pad, self._sample_dt, out=dx_pad)
        dx = dx_pad[self._margin_left : -self._margin_right]

        dx_pad = make_numpy_array_1d(dx_pad)
        dx = make_numpy_array_1d(dx)

        def f_iter(x: NumpyArray1D) -> NumpyArray1D:
            return self._interp.apply_shift(dx_pad, -x, self._margin_left)

        def f_err(x1: NumpyArray1D, x2: NumpyArray1D) -> float:
            return np.max(np.abs(x1 - x2))

        shift_inv = fixed_point_iter(
            f_iter, f_err, dx, self._tolerance_idx, self._max_iter
        )
        np.multiply(shift_inv, self._sample_dt, out=shift_inv)

        return SegmentArray(shift_inv, istart), None


def stream_shift_inv_lagrange(
    max_abs_shift: float,
    sample_dt: float,
    max_iter: int,
    tolerance: float,
    order: int,
) -> Callable[[StreamBase], StreamBase]:
    """Create shift inversion stream operator based on Lagrange interpolator

    See sigpro.shift_inversion_numpy.ShiftInverseNumpy for the mathematical
    definitions.

    For the time coordinate transform defined by the time shift, this computes
    the the time shift for the inverse transform.
    Note we define the sign of time shifts such that the corresponding time delay
    has oppsoite sign.

    As an optimization, providing a constant shift returns the same shift.
    This is justified since a constant shift is a solution to the fixed point iteration.

    Arguments:
        max_abs_shift: Upper limit for absolute coordinate shift [s]
        sample_dt: Sample period
        max_iter: Maximum iterations before fail
        tolerance: Maximum absolute error of result
        order: Order of the Lagrange polynomials

    Returns:
        Function accepting time shift stream, returning stream with inverted shift
    """
    interp = make_regular_interpolator_lagrange(order)

    def op(shift: StreamBase) -> StreamBase:
        match shift:
            case StreamConst():
                return shift
            case StreamBase():
                return StreamShiftInv(
                    shift, sample_dt, max_abs_shift, interp, max_iter, tolerance
                )
        msg = "stream_shift_inv_lagrange: arguments must be StreamBase or StreamConst"
        raise TypeError(msg)

    return op
