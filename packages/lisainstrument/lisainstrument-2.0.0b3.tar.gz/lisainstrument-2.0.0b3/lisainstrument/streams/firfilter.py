"""Module for applying FIR filters to streams


This defines a stream which applies the numpy-based FIR filters from fir_filters_numpy
module to each incoming data segment from another stream. The resulting output stream
shares the index space of the input, but depends on additional margin points required
by the filter. There are no boundary conditions. Instead, evaluating the filtered stream
on a given range will evaluate the unfiltered stream on a wider range.

Use stream_filter_fir to create a stream operator from a FIR filter definition.
"""

from __future__ import annotations

from typing import Any, Callable, Final

import numpy as np

from lisainstrument.sigpro.fir_filters_numpy import DefFilterFIR, FIRCoreOp
from lisainstrument.sigpro.types_numpy import make_numpy_array_1d
from lisainstrument.streams.segments import (
    Segment,
    SegmentArray,
    SegmentConst,
    segment_empty,
)
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamFIR(StreamBase):
    """Stream representing FIR filter applied to other stream"""

    def __init__(self, refstream: StreamBase, firdef: DefFilterFIR):
        """Not part of API, use stream_filter_fir instead

        Arguments:
            refstream: Stream to be filtered
            firdef: FIR filter definition
        """
        if refstream.dtype != np.dtype(float):
            msg = f"StreamFIR can only filter streams of floats, got {refstream.dtype}"
            raise RuntimeError(msg)
        opfir = FIRCoreOp(firdef)
        dep = StreamDependency(
            stream=refstream,
            dod_first=-opfir.margin_left,
            dod_last=opfir.margin_right,
        )
        super().__init__([dep], False, float)
        self._firdef: Final[DefFilterFIR] = firdef
        self._opfir: Final[FIRCoreOp] = opfir

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        size = istop - istart

        if size < 0:
            msg = f"StreamFIR: cannot generate negative number of points {size}"
            raise RuntimeError(msg)

        i0 = seg.istart + self._opfir.margin_left
        i1 = seg.istop - self._opfir.margin_right

        if not i0 <= istart <= istop <= i1:
            msg = f"StreamFIR: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if size == 0:
            return segment_empty(istart, self.dtype), None

        res: Segment
        match seg:
            case SegmentConst():
                res = SegmentConst(self._firdef.gain * seg.const, istart, size)
            case SegmentArray():
                k0 = istart - self._opfir.margin_left - seg.istart
                k1 = istop + self._opfir.margin_right - seg.istart
                datfilt = self._opfir(make_numpy_array_1d(seg.data[k0:k1]))
                res = SegmentArray(datfilt, istart)
            case _:
                msg = f"StreamFIR.generate got segment of unkonwn type {type(seg)}"
                raise TypeError(msg)

        return res, None


def stream_filter_fir(
    firdef: DefFilterFIR,
) -> Callable[[StreamBase], StreamBase]:
    """Create a FIR filter operating on streams from FIR definition

    There are no boundary conditions, the input stream will be evaluated on
    a range larger by the number of left and right margin points needed for the
    FIR filtering.

    When applied to a constant stream (StreamConst) the the return value is
    the constant times the filter gain.

    Arguments:
        firdef: Definition of the filter

    Returns:
        Function accepting a stream and returning filtered stream
    """

    def op(s: StreamBase) -> StreamBase:
        if isinstance(s, StreamConst):
            return StreamConst(float(s.const) * firdef.gain)
        return StreamFIR(s, firdef)

    return op
