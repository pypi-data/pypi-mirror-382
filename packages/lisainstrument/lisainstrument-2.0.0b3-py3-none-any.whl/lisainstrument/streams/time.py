"""Module for creating timestamping streams and basic downsampling

Use the function timestamp_stream to create a stream with regularly spaced
sample times computed from the element indices.
Use stream_downsample to create an operator that shifts and downsamples
streams, with integer sampling ratio.

A difference to working with time grids in arrays is that a time stream is
conceptually infinite. Therefore, one only has to provide the parameters
mapping indices to times, but no boundaries. Further, on can use the same
time stream as input for streams that are evaluated over different ranges,
as long as the mapping of indices to times is the same.


Internally, those functions are realized by classes StreamTimeGrid representing
a stream of sample times, and StreamDowsample representing a downsampled stream.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from lisainstrument.streams.segments import (
    Segment,
    SegmentArray,
    SegmentConst,
    segment_empty,
)
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamTimeGrid(StreamBase):
    """Stream providing regularly spaced timestamps

    The resulting data stream is a linear transformation of the element indices.
    An element with index i has value `t = i * dt + t0`.

    Note: streams are conceptually infinite, so there is no index range involved
    as is typically the case when setting up time grids e.g. in numpy.
    """

    def __init__(self, *, dt: float, t0: float):
        """Not part of API, use timestamp_stream instead

        Arguments:
            dt: constant sample period [Hz]
            t0: timestamp for index i=0
        """
        super().__init__([], False, float)
        self._dt = float(dt)
        self._t0 = float(t0)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        t = np.arange(istart, istop) * self._dt + self._t0
        res = SegmentArray(t, istart)
        return res, None


class StreamDowsample(StreamBase):
    """Stream for basic downsampling without filtering

    The output stream simply contains every n-th element of the input,
    with reference to a given offset. Element with index k in the output
    is given by element i in the input according to

    i = k*ratio + offs


    Note: this can also be used as an integer shift by setting ratio=1
    """

    def __init__(self, refstream: StreamBase, *, ratio: int, offset: float):
        """Not part of API, use downsample_stream instead

        Arguments:
            refstream: Stream to be downsampled
            ratio: integer downsample rate (must be strictly positive)
            offset: arbitrary integer offset
        """
        self._ratio = int(ratio)
        self._offs = int(offset)

        if self._ratio <= 0:
            msg = f"StreamDowsample: sample ratio must be positive, got {ratio}"
            raise RuntimeError(msg)

        dep = StreamDependency(
            stream=refstream,
            dod_first=self._offs,
            dod_last=self._offs,
            sample_ratio=self._ratio,
        )
        super().__init__([dep], False, refstream.dtype)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        i0 = istart * self._ratio + self._offs
        i1 = 1 + (istop - 1) * self._ratio + self._offs

        if not seg.istart <= i0 <= i1 <= seg.istop:
            msg = (
                f"StreamDownsample: cannot generate requested range [{istart}, {istop})"
            )
            raise RuntimeError(msg)

        size = istop - istart

        if size == 0:
            return segment_empty(istart, self.dtype), None

        res: Segment
        match seg:
            case SegmentConst():
                res = SegmentConst(seg.const, istart, size)
            case SegmentArray():
                dat = seg.data[(i0 - seg.istart) : (i1 - seg.istart) : self._ratio]
                res = SegmentArray(dat, istart)
            case _:
                msg = (
                    f"StreamDownsample.generate got segment of unkonwn type {type(seg)}"
                )
                raise TypeError(msg)

        return res, None


def timestamp_stream(dt: float, t0: float) -> StreamTimeGrid:
    """Construct a stream of timestamps computed from the indices

    Arguments:
        dt: Constant sample period [Hz]
        t0: Timestamp for index i=0

    Returns:
        Stream with timestamps
    """
    return StreamTimeGrid(dt=dt, t0=t0)


def stream_downsample(ratio: int, offset: int) -> Callable[[StreamBase], StreamBase]:
    """Create operator for downsampling streams

    The case of StreamConst is optimized returning another StreamConst

    Arguments:
        ratio: integer downsample rate (must be strictly positive)
        offset: arbitrary integer offset

    Returns:
        Function accepting a stream and returning downsampled stream
    """

    def op(s: StreamBase) -> StreamBase:
        if isinstance(s, StreamConst):
            # This needs to be a new instance
            # Otherwise, the same stream would have two different sample rates
            return StreamConst(s.const)
        if (ratio == 1) and (offset == 0):
            return s
        return StreamDowsample(s, ratio=ratio, offset=offset)

    return op
