"""Module for creating streams with derivative of other streams

Use stream_gradient to create the first time derivative of a stream using
central finite differences.
"""

from __future__ import annotations

from typing import Any, Callable, Final

import numpy as np

from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamGradient(StreamBase):
    """Stream computing centered finite difference of other stream

    This computes the time derivative assuming regularly spaced samples, using
    numpy.gradient.
    """

    def __init__(self, refstream: StreamBase, sample_dt: float):
        """Not part of API, use stream_gradient instead

        Arguments:
            refstream: Stream to be filtered
            sample_dt: The constant sample rate
        """
        if refstream.dtype != np.dtype(float):
            msg = f"StreamGradient can only filter streams of floats, got {refstream.dtype}"
            raise RuntimeError(msg)

        dep = StreamDependency(stream=refstream, dod_first=-1, dod_last=1)
        super().__init__([dep], False, float)
        self._sample_dt: Final = float(sample_dt)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        i0 = istart - 1
        i1 = istop + 1

        if not seg.istart <= i0 <= i1 <= seg.istop:
            msg = f"StreamGradient: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        dat = np.empty(i1 - i0, dtype=self.dtype)
        seg.write(dat, istart=i0, istop=i1)
        res = np.gradient(dat, self._sample_dt, axis=0)[1:-1]

        return SegmentArray(res, istart), None


def stream_gradient(sample_dt: float) -> Callable[[StreamBase], StreamBase]:
    """Create stream operator applying central finite differences

    For the case of constant streams, a zero-valued constant stream is returned.

    The sample period is used only as division factor, it is legal to absorb
    other factors into it. Multiplying the sample rate by some factor means
    dividing the result by the same factor.

    Arguments:
        sample_dt: The constant sample rate

    Returns:
        Function accepting a stream and returning stream with first derivative
    """

    def op(s: StreamBase) -> StreamBase:
        match s:
            case StreamConst():
                return StreamConst(0.0)
            case StreamBase():
                return StreamGradient(s, sample_dt)
        msg = f"stream_gradient: need StreamBase or StreamConst, got {type(s)}"
        raise TypeError(msg)

    return op
