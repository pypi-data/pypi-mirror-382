"""Module for time integration of streams

Use stream_int_trapz to obtain streams with the time integral of streams approximated
by trapezoidal rule, or stream_int_cumsum for an approximation using cumulative sum.
Internally, this uses StreamIntTrapz or StreamCumSum.
"""

from __future__ import annotations

from typing import Any, Callable, Final

import numpy as np
from scipy.integrate import cumulative_trapezoid

from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamIntTrapz(StreamBase):
    """Stream integrating other stream using trapezoidal rule

    This computes the time integral assuming regularly spaced samples. The
    sample rate needs to be provided.
    """

    def __init__(self, refstream: StreamBase, sample_dt: float, initial_value: float):
        """Not part of API, use stream_int_trapz instead

        Arguments:
            refstream: Stream to be filtered
            sample_dt: The constant sample rate
            initial_value: Integration constant
        """
        if refstream.dtype != np.dtype(float):
            msg = f"StreamIntTrapz can only filter streams of floats, got {refstream.dtype}"
            raise RuntimeError(msg)

        dep = StreamDependency(stream=refstream)
        super().__init__([dep], True, float)
        self._sample_dt: Final = float(sample_dt)
        self._initial_value: Final = float(initial_value)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        if not seg.istart <= istart <= istop <= seg.istop:
            msg = f"StreamIntTrapz: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        dat = np.empty(istop - istart, dtype=self.dtype)
        seg.write(dat, istart=istart, istop=istop)

        if state is None:
            intprev = self._initial_value
        else:
            datprev, intprev = state
            intprev += (datprev + dat[0]) * self._sample_dt / 2

        res = intprev + cumulative_trapezoid(dat, dx=self._sample_dt, initial=0)
        newstate = float(dat[-1]), float(res[-1])
        newseg = SegmentArray(res, istart)
        return newseg, newstate


class StreamCumSum(StreamBase):
    """Stream integrating other stream using cumulative sum

    This computes the time integral assuming regularly spaced samples. The
    sample period needs to be provided. It is only used as multiplicative factor
    for the cumulative sum of samples and nothing else. It is explicitly allowed
    to absorb other multiplicative factors into the sample period parameter.
    """

    def __init__(self, refstream: StreamBase, sample_dt: float, initial_value: float):
        """Not part of API, use stream_int_cumsum instead

        Arguments:
            refstream: Stream to be filtered
            sample_dt: The constant sample rate
            initial_value: Integration constant
        """
        if refstream.dtype != np.dtype(float):
            msg = (
                f"StreamCumSum can only filter streams of floats, got {refstream.dtype}"
            )
            raise RuntimeError(msg)

        dep = StreamDependency(stream=refstream)
        super().__init__([dep], True, float)
        self._sample_dt: Final = float(sample_dt)
        self._initial_value: Final = float(initial_value)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        if not seg.istart <= istart <= istop <= seg.istop:
            msg = f"StreamCumSum: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        dat = np.empty(istop - istart, dtype=self.dtype)
        seg.write(dat, istart=istart, istop=istop)

        if state is None:
            intprev = self._initial_value
        else:
            intprev = state

        res = np.cumsum(dat)
        np.multiply(res, self._sample_dt, out=res)
        np.add(res, intprev, out=res)

        newstate = float(res[-1])
        newseg = SegmentArray(res, istart)
        return newseg, newstate


def stream_int_trapz(
    sample_dt: float, initial_value: float = 0.0
) -> Callable[[StreamBase], StreamBase]:
    """Create stream operator applying trapezoidal integration

    For the case of zero-valued constant streams, a constant stream with the
    initial value is returned.

    Note that integrating streams is problematic because the starting index
    from where streams are evaluated depends on the required range of all dependent
    streams. One use case is integration of noise, such that the statistical
    properties are independent of the start point. However, this is still not
    valid for all noise PSDs, in particular if the initial value is not randomized as
    well.

    Arguments:
        sample_dt: The constant sample rate
        initial_value: Integration constant

    Returns:
        Function accepting a stream and returning stream with time integral
    """

    def op(s: StreamBase) -> StreamBase:
        match s:
            case StreamConst() if s.const == 0:
                return StreamConst(initial_value)
            case StreamBase():
                return StreamIntTrapz(s, sample_dt, initial_value)
        msg = f"stream_int_trapz: need StreamBase or StreamConst, got {type(s)}"
        raise TypeError(msg)

    return op


def stream_int_cumsum(
    sample_dt: float, initial_value: float = 0.0
) -> Callable[[StreamBase], StreamBase]:
    """Create stream operator applying integration using cumulative sum

    For the case of zero-valued constant streams, a constant stream with the
    initial value is returned.

    Note that integrating streams is problematic, see note in stream_int_trapz.

    Arguments:
        sample_dt: The constant sample rate
        initial_value: Integration constant

    Returns:
        Function accepting a stream and returning stream with time integral
    """

    def op(s: StreamBase) -> StreamBase:
        match s:
            case StreamConst() if s.const == 0:
                return StreamConst(initial_value)
            case StreamBase():
                return StreamCumSum(s, sample_dt, initial_value)
        msg = f"stream_int_cumsum: need StreamBase or StreamConst, got {type(s)}"
        raise TypeError(msg)

    return op
