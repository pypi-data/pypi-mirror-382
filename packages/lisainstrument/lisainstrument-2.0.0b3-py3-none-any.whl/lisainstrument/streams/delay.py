"""Module with stream types for dynamic and constant delays using interpolation

Use stream_delay_lagrange to create a delay operator acting on streams using
Lagrange interpolation with given order. This allows delaying one stream by an
amount given by another stream.

It is worth noting that no boundary conditions are required. The input streams
will be evaluatd on a larger range to account for the margins.

Internally, this is implemented in the classes StreamDelayDyn and StreamDelayFix
for delays with dynamic or fixed shift respectively. The public interface,
stream_delay_lagrange, uses the suitable one based on whether data and/or delay
are constant streams.

StreamDelayDyn is using any RegularInterpolator from sigpro.regular_interpolators
for interpolation. StreamDelayFix uses FixedShiftFactory (which is just a function
yielding a FixedShiftCore interpolator for a given shift) from sigpro.fixed_shift_numpy.
"""

from __future__ import annotations

from typing import Any, Callable, Final

import numpy as np

from lisainstrument.sigpro.fixed_shift_numpy import (
    FixedShiftFactory,
    FixedShiftLagrange,
)
from lisainstrument.sigpro.regular_interpolators import (
    RegularInterpolator,
    make_regular_interpolator_lagrange,
)
from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamDelayDyn(StreamBase):
    """Stream representing dynamic delay filter

    This delays one stream by an amount specified by another stream. The delay
    is given as a time delay, assuming a constant sampling rate for the stream.
    For technical reasons, the delay must be bounded and the bounds specified in
    advance. There are no boundary conditions, the undelayed stream is evaluated
    on a sufficiently larger interval automatically.
    """

    def __init__(
        self,
        data: StreamBase,
        time_delay: StreamBase,
        delay_min: float,
        delay_max: float,
        sample_dt: float,
        interp: RegularInterpolator,
    ):
        """Not part of API, use stream_filter_delay instead

        Note: the sampling period is only used for converting the time delays
        to delays in index space. The delay in terms of indices is
        delay_idx = delay_time / sample_dt

        One can also specify the delay with respect to indices by setting sample_dt=1

        Arguments:
            data: Stream to be delayed
            time_delay: Stream with delay [s]
            delay_min: Minimum delay [s]
            delay_max: Maximum delay [s]
            sample_dt: Sampling period for converting time delay [s]
            interp: Iterpolator to use
        """
        if data.dtype != np.dtype(float):
            msg = f"StreamDelayDyn can only delay streams of floats, got {data.dtype}"
            raise RuntimeError(msg)
        if time_delay.dtype != np.dtype(float):
            msg = f"StreamDelayDyn: time_delay data type must be float, got {time_delay.dtype}"
            raise RuntimeError(msg)
        if sample_dt <= 0:
            msg = (
                f"StreamDelayDyn: sample_dt must be strictly positive, got {sample_dt}"
            )
            raise RuntimeError(msg)
        if delay_max < delay_min:
            msg = f"StreamDelayDyn: got invalid delay bounds {delay_min=}, {delay_max=}"
            raise RuntimeError(msg)

        self._sample_rate: Final = 1.0 / float(sample_dt)
        self._int_delay_min: Final = -int(
            np.ceil(interp.margin_right - delay_min * self._sample_rate)
        )
        self._int_delay_max: Final = int(
            np.ceil(interp.margin_left + delay_max * self._sample_rate)
        )
        self._interp: Final = interp

        dep1 = StreamDependency(
            stream=data,
            dod_first=-self._int_delay_max,
            dod_last=-self._int_delay_min,
        )
        dep2 = StreamDependency(stream=time_delay)

        super().__init__([dep1, dep2], False, float)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        seg_dat, seg_del = deps

        if not seg_del.istart <= istart <= istop <= seg_del.istop:
            msg = f"StreamDelayDyn: delay data not covering requested interval {istart}, {istop}"
            raise RuntimeError(msg)

        i0, i1 = istart - self._int_delay_max, istop - self._int_delay_min

        if not seg_dat.istart <= i0 <= i1 <= seg_dat.istop:
            msg = (
                f"StreamDelayDyn: sample data not covering required interval {i0}, {i1}"
            )
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, dtype=self.dtype), None

        shift = np.empty(istop - istart, dtype=self.dtype)
        seg_del.write(shift, istart=istart, istop=istop)
        # shift = -delay
        np.multiply(shift, -self._sample_rate, out=shift)

        data = np.empty(i1 - i0, dtype=self.dtype)
        seg_dat.write(data, istart=i0, istop=i1)

        shifted = self._interp.apply_shift(data, shift, self._int_delay_max)
        return SegmentArray(shifted, istart), None


class StreamDelayFix(StreamBase):
    """Stream representing fixed delay filter

    This delays one stream by a fixed amount. The delay is given as a time delay,
    assuming a constant sampling rate for the stream. There are no boundary conditions,
    the undelayed stream is evaluated on a sufficiently larger interval automatically.
    """

    def __init__(
        self,
        data: StreamBase,
        time_delay: float,
        sample_dt: float,
        mkshift: FixedShiftFactory,
    ):
        """Not part of API, use stream_filter_delay instead

        Arguments:
            data: Stream to be delayed
            time_delay: Time delay [s]
            sample_dt: Constant sampling period of data stream [s]
            mkshift: Function creating interpolator for given shift
        """
        if data.dtype != np.dtype(float):
            msg = f"StreamDelayFix can only delay streams of floats, got {data.dtype}"
            raise RuntimeError(msg)
        if sample_dt <= 0:
            msg = (
                f"StreamDelayFix: sample_dt must be strictly positive, got {sample_dt}"
            )
            raise RuntimeError(msg)

        shift_tot = -time_delay / float(sample_dt)

        shift_int = int(shift_tot)
        shift_frac = shift_tot - shift_int

        self._interp: Final = mkshift(shift_frac)
        self._int_shift_min: Final = shift_int - self._interp.margin_left
        self._int_shift_max: Final = shift_int + self._interp.margin_right

        dep = StreamDependency(
            stream=data, dod_first=self._int_shift_min, dod_last=self._int_shift_max
        )

        super().__init__([dep], False, data.dtype)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg_dat,) = deps

        i0, i1 = istart + self._int_shift_min, istop + self._int_shift_max

        if not seg_dat.istart <= i0 <= i1 <= seg_dat.istop:
            msg = (
                f"StreamDelayFix: sample data not covering required interval {i0}, {i1}"
            )
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, dtype=self.dtype), None

        data = np.empty(i1 - i0, dtype=self.dtype)
        seg_dat.write(data, istart=i0, istop=i1)

        shifted = self._interp.apply(data)
        return SegmentArray(shifted, istart), None


def stream_delay_lagrange(
    delay_min: float,
    delay_max: float,
    sample_dt: float,
    order: int,
) -> Callable[[StreamBase, StreamBase], StreamBase]:
    """Create stream operator representing time delays

    There are no boundary conditions, the input stream will be evaluated on
    a longer range. The required range depends on the minimum and maximum delay.
    It is further expanded by the left and right margin points needed for the
    interpolation.

    Delays don't need to be positive. One should avoid unnecessarily wide bounds
    for the delay, as this will cause the input stream to be evaluated on a correspondingly
    larger range.

    When delaying a constant stream, represented as StreamConst, this returns
    the same constant stream, allowing for transparent propagation of constant
    optimizations.

    When the shift is a StreamConst and the data stream a regular one, a more
    efficient implementation for fixed shifts is used automatically. If the
    constant shift is zero, the original stream is returned.

    Arguments:
        delay_min: Minimum delay [s]
        delay_max: Maximum delay [s]
        sample_dt: Sampling period for converting time delay [s]
        order: Order of the Lagrange interpolator

    Returns:
        Function accepting data and time delay streams, returning delayed stream
    """

    interp = make_regular_interpolator_lagrange(order)
    fixfac = FixedShiftLagrange.factory(order)

    def op(data: StreamBase, delay: StreamBase) -> StreamBase:
        match (data, delay):
            case StreamConst(), StreamBase() | StreamConst():
                return data
            case StreamBase(), StreamConst():
                if delay.const == 0:
                    return data
                return StreamDelayFix(data, delay.const, sample_dt, fixfac)
            case StreamBase(), StreamBase():
                return StreamDelayDyn(
                    data, delay, delay_min, delay_max, sample_dt, interp
                )
        msg = "stream_delay_lagrange: arguments must be StreamBase or StreamConst"
        raise TypeError(msg)

    return op
