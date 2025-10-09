"""Scheduler engine for parallel stream evaluation based on dask delayed"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import dask
from dask.delayed import Delayed, delayed

from lisainstrument.streams.scheduler_serial import ExecutorProtocol
from lisainstrument.streams.segments import Segment, join_segments, segment_empty
from lisainstrument.streams.streams import StreamBase


@dataclass
class _DelayedSegment:
    seg: Delayed
    istart: int
    istop: int


def _join_delayed_segments(*segs: _DelayedSegment) -> _DelayedSegment:
    d = delayed(join_segments)(*[s.seg for s in segs])
    istart = min((s.istart for s in segs))
    istop = max((s.istop for s in segs))
    return _DelayedSegment(d, istart, istop)


def _get_first(x):
    return x[0]


def _get_second(x):
    return x[1]


def _delayed_generate_segment(
    stream: StreamBase,
    state: Delayed,
    deps_ds: list[_DelayedSegment],
    istart: int,
    istop: int,
) -> tuple[_DelayedSegment, Delayed]:
    deps = [d.seg for d in deps_ds]

    def tsk(state: Any, istart: int, istop: int, *args: Segment) -> tuple[Segment, Any]:
        newseg, newstate = stream.generate(state, list(args), istart, istop)
        if newseg.istart != istart or newseg.istop != istop:
            msg = (
                f"BuilderDask: stream {stream} generated interval "
                f"({newseg.istart},{newseg.istop}) instead ({istart},{istop})"
            )
            raise RuntimeError(msg)
        return newseg, newstate

    gen = delayed(tsk)(state, istart, istop, *deps)
    dnewseg = delayed(_get_first)(gen)
    dnewstate = delayed(_get_second)(gen)

    return _DelayedSegment(dnewseg, istart, istop), dnewstate


def _delayed_trim_buffer(dbuf: _DelayedSegment, icut: int, dtype) -> _DelayedSegment:
    def trim(buf: Segment) -> Segment:
        return buf.tail(icut)

    if icut >= dbuf.istop:
        gen = delayed(segment_empty)(icut, dtype)
        return _DelayedSegment(gen, icut, icut)
    if dbuf.istart < icut:
        gen = delayed(trim)(dbuf.seg)
        return _DelayedSegment(gen, icut, dbuf.istop)
    return dbuf


def _delayed_load_buf(bufdict: dict[int, Segment], i: int) -> _DelayedSegment:
    def load_buf(k: int) -> Segment:
        return bufdict.pop(k)

    gen = delayed(load_buf)(i)
    seg = bufdict[i]
    return _DelayedSegment(gen, seg.istart, seg.istop)


class ExecutorDask(ExecutorProtocol):
    """Engine for evaluating streams, using dask for parallel execution"""

    def __init__(
        self,
        streams: dict[int, StreamBase],
        rg_first: dict[int, int],
        rg_stop: dict[int, int],
        num_workers: int,
    ) -> None:
        self._num_workers = int(num_workers)
        self._streams = streams
        self._rg_first: Final = rg_first
        self._rg_stop: Final = rg_stop
        self._buf: dict[int, _DelayedSegment] = {}
        self._states: dict[int, Any] = {}
        self._checkp_buf: dict[int, Segment] = {}
        self._checkp_state: dict[int, Any] = {i: None for i in self._streams}

    def load_checkpoint(self) -> None:
        """Load buffers from checkpointpoint"""
        self._buf = {
            b: _delayed_load_buf(self._checkp_buf, b) for b in self._checkp_buf
        }
        self._states = {
            b: delayed(self._checkp_state.pop)(b) for b in self._checkp_state
        }

    def compute_checkpoint(self) -> None:
        """Evaluate buffers and save to checkpoint"""
        needed = {}
        for i, b in self._buf.items():
            needed[(i, True)] = b.seg
        for i, s in self._states.items():
            needed[(i, False)] = s
        with dask.config.set(scheduler="threads", num_workers=self._num_workers):
            (data,) = dask.compute(needed, num_workers=self._num_workers)
        self._checkp_buf = {i: b for (i, isbuf), b in data.items() if isbuf}
        self._checkp_state = {i: s for (i, isbuf), s in data.items() if not isbuf}

    def done(self) -> bool:
        """Whether all streams have been comuted on required range"""
        return all((self.i_next(i) >= self._rg_stop[i] for i in self._streams))

    def i_next(self, i: int) -> int:
        """First index not yet computed for Stream ID i"""
        if i in self._buf:
            return self._buf[i].istop
        return self._rg_first[i]

    def generate_until(self, sid: int, istop: int) -> None:
        """Add task to evaluate stream until here

        This needs to be called for all dependencies first
        """
        istart = self.i_next(sid)
        istop = min(istop, self._rg_stop[sid])

        if istart >= istop:
            return

        stream = self._streams[sid]
        deps = [self._buf[d.stream.id] for d in stream.dependencies]
        state = self._states[sid]
        newseg, state = _delayed_generate_segment(stream, state, deps, istart, istop)
        self._states[sid] = state
        if sid in self._buf:
            self._buf[sid] = _join_delayed_segments(self._buf[sid], newseg)
        else:
            self._buf[sid] = newseg

    def trim_buffer(self, sid: int, icut: int) -> None:
        """Indicate that earlier indices will not be needed

        When calling this, the engine can assume that indices before icut will
        not be needed as dependency for computing remaining chunks of any stream
        """
        sdtype = self._streams[sid].dtype
        if sid in self._buf:
            self._buf[sid] = _delayed_trim_buffer(self._buf[sid], icut, sdtype)
