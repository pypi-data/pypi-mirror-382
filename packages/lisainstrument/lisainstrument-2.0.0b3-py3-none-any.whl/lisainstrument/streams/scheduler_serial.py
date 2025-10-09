"""Scheduler engine for serial stream evaluation with minimal memory use"""

from __future__ import annotations

from typing import Any, Final, Protocol

from lisainstrument.streams.segments import Segment, join_segments, segment_empty
from lisainstrument.streams.streams import StreamBase


class ExecutorProtocol(Protocol):
    """Interface for scheduler engine"""

    def load_checkpoint(self) -> None:
        """Continue execution after hard memory-purge"""

    def compute_checkpoint(self) -> None:
        """Perform hard memory purge, save only what is still needed"""

    def done(self) -> bool:
        """Whether all streams have been comuted on required range"""

    def i_next(self, i: int) -> int:
        """First index not yet computed for Stream ID i"""

    def generate_until(self, sid: int, istop: int) -> None:
        """Add task to evaluate stream until here"""

    def trim_buffer(self, sid: int, icut: int) -> None:
        """Indicate that earlier indices will not be needed"""


class ExecutorSerial(ExecutorProtocol):
    """Engine for evaluating streams, using serial processing and limited memory"""

    def __init__(
        self,
        streams: dict[int, StreamBase],
        rg_first: dict[int, int],
        rg_stop: dict[int, int],
    ) -> None:
        self._streams = streams
        self._rg_first: Final = rg_first
        self._rg_stop: Final = rg_stop
        self._buf: dict[int, Segment] = {
            i: segment_empty(self._rg_first[i], self._streams[i].dtype)
            for i in self._streams
        }
        self._states: dict[int, Any] = {i: None for i in self._streams}

    def load_checkpoint(self) -> None:
        """Not needed for this engine"""

    def compute_checkpoint(self) -> None:
        """Not needed for this engine"""

    def done(self) -> bool:
        """Whether all streams have been comuted on required range"""
        return all((self._buf[i].istop >= self._rg_stop[i] for i in self._streams))

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
        newseg, state = stream.generate(state, deps, istart, istop)

        if newseg.istart != istart or newseg.istop != istop:
            msg = (
                f"BuilderSerial: stream {stream} generated interval "
                f"({newseg.istart},{newseg.istop}) instead ({istart},{istop})"
            )
            raise RuntimeError(msg)

        self._states[sid] = state
        self._buf[sid] = join_segments(self._buf[sid], newseg)

    def trim_buffer(self, sid: int, icut: int) -> None:
        """Indicate that earlier indices will not be needed

        When calling this, the engine can assume that indices before icut will
        not be needed as dependency for computing remaining chunks of any stream
        """
        buf = self._buf[sid]
        if icut >= buf.istop:
            self._buf[sid] = segment_empty(icut, self._streams[sid].dtype)
        elif buf.istart < icut:
            self._buf[sid] = buf.tail(icut)
