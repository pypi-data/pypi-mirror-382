"""Tools to turn function operating on numpy arrays into function operating on streams

This allows to formulate any pointwise function of streams as an ordinary function
acting on numpy arrays. This is for streams that share the same index space, with
each output sample based on the input stream samples with the same index.

The user-facing interface is the decorator stream_expression. Internally, it creates
an instance of the StreamExpression class, which is not intended for direct use.
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


def _unpack_segment(seg: Segment, istart: int, istop: int) -> Any:
    """Helper function for use in StreamExpression"""
    if isinstance(seg, SegmentConst):
        return seg.const
    if isinstance(seg, SegmentArray):
        return seg.data[istart - seg.istart : istop - seg.istart]
    msg = f"_unpack_segment: need SegmentConst or SegmentArray, got {type(seg)}"
    raise RuntimeError(msg)


class StreamExpression(StreamBase):
    """Stream applying ordinary numpy-based functions element-wise to input streams"""

    def __init__(self, func: Callable, *args: StreamBase, dtype=float):
        if not args:
            msg = "StreamExpression needs at least one input stream"
            raise RuntimeError(msg)
        deps = [StreamDependency(stream=d) for d in args]
        super().__init__(deps, False, dtype)
        self._func = func

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generator of the stream

        The output is a SegmentArray or SegmentConst created from the output
        of the wrapped function. The wrapped function may return a 1D numpy array,
        which must have same size as the input arrays, or a scalar value to represent
        constant segment.

        The internal state of the stream is a list of leftover data that could not
        be used before (which happens if chunks of input streams are non-aligned)
        or None for the first call.
        """
        segs = deps
        size = istop - istart
        if size < 0:
            msg = f"StreamExpression: cannot generate negative number of points {size}"
            raise RuntimeError(msg)

        i0 = max((s.istart for s in segs))
        i1 = min((s.istop for s in segs))

        if not i0 <= istart <= istop <= i1:
            msg = (
                f"StreamExpression: cannot generate requested range [{istart}, {istop})"
            )
            raise RuntimeError(msg)

        if size == 0:
            return segment_empty(istart, self.dtype), None

        common = [_unpack_segment(s, istart, istop) for s in segs]
        raw = self._func(*common)
        res: Segment
        if isinstance(raw, np.ndarray):
            if raw.shape != (size,):
                msg = f"StreamExpression: wrapped function returned wrong shape {raw.shape}"
                raise RuntimeError(msg)
            res = SegmentArray(raw, istart)
        else:
            res = SegmentConst(raw, istart, size)

        return res, None


def stream_expression(dtype=np.float64):
    """Decorator to turn ordinary functions into functions acting on stream elements.

    The decorator has a parameter for the data type of the output stream, and can
    be applied to a function with the following signature. The function should have
    one or more positional arguments, each accepting both 1D numpy arrays and scalar
    constants. The function should expect that all passed numpy arrays are of same size,
    and it should operate strictly element-wise on the arrays. If all inputs are constants,
    the function should return a scalar. Otherwise, it has to return a numpy array with
    same shape as each of the input arrays, with the same dtype specified to the decorator.
    The function can have arbitrary keyword arguments. The use of keyword arguments should
    be restricted to simple numerical parameters or simple functions, no large data and,
    most important, no streams.

    The decorated function accepts only streams as positional arguments, while keyword
    arguments are passed through unmodified. If all positional arguments are constant streams
    (StreamConst) then the wrapped function is called just once and a constant stream is
    returned. Otherwise, it returns a StreamExpression wrapping the original function.
    """

    def decorate(func):
        def wrapped(*args, **kwargs):
            if not all((isinstance(a, StreamBase) for a in args)):
                msg = "Stream expression arguments must be StreamBase or StreamConst"
                raise TypeError(msg)

            mskc = [isinstance(a, StreamConst) for a in args]

            def tsk(*stream_args):
                sa = list(stream_args)
                inner_args = [
                    (args[i].const if m else sa.pop(0)) for i, m in enumerate(mskc)
                ]
                return func(*inner_args, **kwargs)

            sargs = [a for a, m in zip(args, mskc) if not m]
            if not sargs:
                return StreamConst(tsk())
            return StreamExpression(tsk, *sargs, dtype=dtype)

        return wrapped

    return decorate
