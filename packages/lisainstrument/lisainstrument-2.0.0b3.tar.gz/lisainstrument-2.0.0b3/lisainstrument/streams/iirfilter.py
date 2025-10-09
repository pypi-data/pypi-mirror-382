"""Module for applying IIR filters to streams

This defines a stream which applies the numpy-based IIR filters from iir_filters_numpy
module to each incoming data segment from another stream. Besides single filters, one can
also apply filter chains directly.

To turn a filter definition and initial condition into a function operating on streams,
use stream_filter_iir. For the case of filter chains, use stream_filter_iir_chain instead.
Internally, those use the stream type StreamIIR, which is not intended for direct use.

"""

from __future__ import annotations

from typing import Any, Callable, Final, Iterable

import numpy as np

from lisainstrument.sigpro.iir_filters_numpy import (
    DefFilterIIR,
    IIRChainCoreOp,
    IIRCoreOp,
    IIRFilterIC,
    get_iir_chain_steady_state,
    get_iir_steady_state,
)
from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst, StreamDependency


class StreamIIR(StreamBase):
    """Stream representing IIR filter(s) applied to other stream"""

    def __init__(
        self,
        refstream: StreamBase,
        iirop: IIRCoreOp | IIRChainCoreOp,
        burn_in_size: int = 0,
    ):
        """Not part of API, use stream_filter_iir instead

        Arguments:
            refstream: Stream to be filtered
            iirop: low-level IIR operator
        """
        if refstream.dtype != np.dtype(float):
            msg = f"StreamIIR can only filter streams of floats, got {refstream.dtype}"
            raise RuntimeError(msg)

        dep = StreamDependency(stream=refstream)
        super().__init__([dep], True, float, prefix_size=burn_in_size)
        self._iirop: Final = iirop

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        (seg,) = deps

        if not seg.istart <= istart <= istop <= seg.istop:
            msg = f"StreamIIR: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        dat = np.empty(istop - istart, dtype=self.dtype)
        seg.write(dat, istart=istart, istop=istop)

        if state is None:
            state = self._iirop.initial_state(dat[0])

        fdat, newstate = self._iirop.apply(dat, state)
        newseg = SegmentArray(fdat, istart)

        return newseg, newstate


def stream_filter_iir(
    iirdef: DefFilterIIR, ic: IIRFilterIC, burn_in_size: int = 0
) -> Callable[[StreamBase], StreamBase]:
    """Create stream operator for applying IIR filters to streams

    The recommended way to handle the initial conditions is to use a nonzero
    burn_in_size parameter. Most useful infinite response filters in practive
    have a finite response duration after which the contribution from a pulse
    becomes negligible. The burn_in_size parameter declares how many points
    at the beginning should be considered invalid and discarded. This means
    that the unfiltered stream will be evaluated earlier by the same amount,
    compared to the requested range of the filtered output. Regardless, the
    initial conditions of the filtered stream are constructed according to the
    ic parameter.

    When applied to a StreamConst, it returns another StreamConst with the
    constant result of applying the IIR filter to an infinite constant sequence.
    This raises an exception if the filter does not allow for such a steady
    state.

    Arguments:
        iirdef: Definition of the filter
        ic: Initial condition

    Returns:
        Function accepting a stream and returning filtered stream
    """

    opiir = IIRCoreOp(iirdef, ic)

    def op(s: StreamBase) -> StreamBase:
        match s:
            case StreamConst():
                return StreamConst(get_iir_steady_state(iirdef, s.const))
            case StreamBase():
                return StreamIIR(s, opiir, burn_in_size=burn_in_size)
        msg = f"stream_filter_iir: need StreamBase or StreamConst, got {type(s)}"
        raise TypeError(msg)

    return op


def stream_filter_iir_chain(
    iirdefs: Iterable[DefFilterIIR], ic: IIRFilterIC, burn_in_size: int = 0
) -> Callable[[StreamBase], StreamBase]:
    """Like stream_filter_iir but for an IIR filter chain

    The filters are applied in the same order as the iirdef argument, i,e,
    first the filter defined by the first entry is applied, then the second,
    and so on.
    """

    opiir = IIRChainCoreOp(iirdefs, ic)

    def op(s: StreamBase) -> StreamBase:
        match s:
            case StreamConst():
                return StreamConst(get_iir_chain_steady_state(iirdefs, s.const))
            case StreamBase():
                return StreamIIR(s, opiir, burn_in_size=burn_in_size)
        msg = f"stream_filter_iir_chain: need StreamBase or StreamConst, got {type(s)}"
        raise TypeError(msg)

    return op
