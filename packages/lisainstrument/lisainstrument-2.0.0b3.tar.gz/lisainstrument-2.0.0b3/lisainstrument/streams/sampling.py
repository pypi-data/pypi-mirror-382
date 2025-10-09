"""Module for turning a function of time into a stream


Given a FuncOfTime instance, the stream_func_of_time function can be used to
turn it into a stream expression that operates exclusively on streams of type
StreamTimeGrid. Even though one could simply use the more generic stream_expression
with a time stream as single argument, stream_func_of_time should be preferred
as it formalizes the intent and thus readability. Also, the static type checking
detects accidental use with stream which are not a time coordinate.
"""

from __future__ import annotations

from typing import Callable

from lisainstrument.sigpro.types_numpy import ConstFuncOfTime, FuncOfTimeTypes, SeqChunk
from lisainstrument.streams.expression import StreamExpression
from lisainstrument.streams.streams import StreamBase, StreamConst
from lisainstrument.streams.time import StreamTimeGrid


def _apply_func_of_time(func: FuncOfTimeTypes, t: StreamTimeGrid) -> StreamBase:
    if isinstance(func, ConstFuncOfTime):
        return StreamConst(func.const)

    def tsk(t):
        return func(SeqChunk(t)).samples

    return StreamExpression(tsk, t, dtype=func.dtype)


def stream_func_of_time(
    func: FuncOfTimeTypes,
) -> Callable[[StreamTimeGrid], StreamBase]:
    """This turns a function of type FuncOfTime or ConstFuncOfTime into a
    a function operating on time streams (specifically StreamTimeGrid streams).

    The resulting function takes a single argument of type StreamTimeGrid.
    For a function of type FuncOfTime, the output stream is the result of the
    wrapped function on the chunks of the timestamps in the time stream.

    For a function of type ConstFuncOfTime, the output is a ConstStream, allowing
    for further optimizations.

    Arguments:
        func: Function of time operating on 1D numpy arrays

    Returns:
        Function operating on time streams.
    """

    def wrapped(t: StreamTimeGrid):
        return _apply_func_of_time(func, t)

    return wrapped
