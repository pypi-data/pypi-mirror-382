"""This module contains the core definitions of streams and bundles of streams

See the streams package docstring for an introduction to the concepts and
terminology of the streams package. This module contains the StreamBase class
representing the common interface for all streams, and two trivial implementations.
The most important one is StreamConst, which represents a stream yielding a
sequence of constant values. This stream is special since many functions in
this package operating on streams have optimizations for the case of constant
streams, to the extent that StreamConst is rarely actually evaluated.
The other implementation is StreamIndices, which just provides the index of each
sequence element as sequence value.

StreamDependency collects information how exactly a stream depends on another
stream. The important concept is the domain of dependence, defined as the index
range in the input stream required to compute an element with given index in
the output stream. Further, it defines an optional downsampling ratio of the input
stream. Note that upsampling and fractional ratios are currently not supported,
the sampling rate of the input must be an integer multiple of the output sampling
rate.

The StreamBundle class is for collecting streams that should be stored (i.e.
final results, not intermediate values) and attach an identifier to the streams,
which is used to name datasets in the storage container. Importantly, this is
also where the range to be stored for each output stream is specified.



A stream is a potentially infinite stream of scalar values that is computed
from other streams using a generator function. There are different stream types
characterized mostly by their generator function. All are derived from the
StreamBase abstract interface. A stream can have an internal state that is
returned by the generator function together with the generated segment,
and which needs to passed to the generator function for computing the
following segment.

A stream stores references to the streams it depends on. Each stream has its own
index space and a prescription to obtain the index ranges needed from each stream
it depends on for computing a given element. This includes the possibility of
downsampling, such that a stream has lower sample rate than a stream it depends on.
Upsampling is currently not forseen.

StreamBundle represents a collection of interdependent streams, some of which
are output streams. The output streams have an associated identifier and a range (with
respect to their own index space) that should be computed. The purpose of a
StreamBundle is to be used as input to a task scheduler that evaluates and stored
the streams to some storage location such as files.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Final, TypeAlias

import numpy as np

from lisainstrument.streams.segments import Segment, SegmentConst, segment_arange

DatasetIdentifier: TypeAlias = tuple[str, ...]


@dataclass(frozen=True)
class StreamDependency:
    """Class describing a single dependency of a stream

    This stores a stream dependency and the parameters describing the domain of dependence.
    In detail, a point with indek k in the output stream requires point with indices
    in the range starting with index `(k * sample_ratio + dod_first` up to and including
    index `k * sample_ratio + dod_last)`, both in the index space of the dependency.
    """

    stream: StreamBase
    dod_first: int = 0
    dod_last: int = 0
    sample_ratio: int = 1

    def range_req(self, irange: tuple[int, int]) -> tuple[int, int]:
        """Given a range in the output stream, compute required range in the dependency"""
        i0 = irange[0] * self.sample_ratio + self.dod_first
        i1 = irange[1] * self.sample_ratio + self.dod_last
        return (i0, i1)


class StreamBase(ABC):
    """Abstract interface for streams"""

    def __init__(
        self,
        dependencies: list[StreamDependency],
        has_state: bool,
        dtype,
        prefix_size: int = 0,
    ) -> None:
        self._has_state: Final = bool(has_state)
        self._prefix_size: Final = int(prefix_size)
        self._dependencies: Final = tuple(dependencies)
        self._dtype: Final = dtype
        self._description: str | None = None

        if self._prefix_size < 0:
            msg = f"StreamBase: got negative prefix_size {self._prefix_size}"
            raise RuntimeError(msg)

    @property
    def has_state(self) -> bool:
        """Whether the stream has internal state"""
        return self._has_state

    @property
    def prefix_size(self) -> int:
        """Number of additional elements to be computed before output range"""
        return self._prefix_size

    @property
    def dependencies(self) -> tuple[StreamDependency, ...]:
        """The dependencies of the stream"""
        return self._dependencies

    @property
    def id(self) -> int:
        """Unique stream identifier"""
        return id(self)

    @property
    def dtype(self):
        """Data type of samples generated by the stream"""
        return self._dtype

    @abstractmethod
    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate a segment of the stream

        This functions will be passed a data segment from each stream it depends on,
        and should return a segment for the given output range. The input segments
        may span a larger range than required (such extra elements should not be used
        in any way). Segments can also be constant, represented by SegmentConst, allowing
        for potential optimizations.

        If the stream has internal state, the state returned by the generator function
        needs to be passed to the generator when computing the next segment. If not, the
        states passed to and returned from the generator are irrelevant and should be set
        to None. For example, the internal state of a stream for IIR filtering could be
        the IIR filter's state.

        For the first segment, the state passed to the generator is always None. The
        stream then has to compute its own initial conditions, if required.

        Arguments:
            state: state returned by earlier call or None
            args: Segments computed by the stream dependencies
            istart: Start index of range to be computed
            istart: Stop index of range to be computed (not included)

        Returns:
            A segment of the stream, and the internal state or None
        """

    def set_description(self, text: str) -> None:
        """Provide optional description text"""
        self._description = str(text)

    @property
    def description(self) -> str | None:
        """Optional description text, if available, else None"""
        return self._description

    def __str__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(ID={self.id}) {self.description}"


class StreamConst(StreamBase):
    """Class to formally represents a constant stream

    This stream is special as many stream operations will optimize for this case,
    e.g. FIR-filtering a StreamConst just returns another StreamConst.
    """

    def __init__(self, const):
        self._dtype = np.dtype(type(const))
        self._const = const
        super().__init__([], False, self._dtype)

    @property
    def const(self):
        """The constant value"""
        return self._const

    @property
    def dtype(self) -> np.dtype:
        """Data dtype"""
        return self._dtype

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        res = SegmentConst(self._const, istart, istop - istart)
        return res, None


class StreamIndices(StreamBase):
    """Stream providing the index of each sequence element as its value

    Optionally, one can add a constant offset to the values.
    """

    def __init__(self, offset: int = 0):
        """Constructor"""
        super().__init__([], False, int)
        self._offset = int(offset)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        res = segment_arange(istart, istop, offset=self._offset)
        return res, None


class StreamBundle:
    """Class representing an interdependent collection of streams

    This is used to build a graph of dependencies. One sets up one StreamBundle
    instance and then add streams to it using the add method. Only streams that
    potentially need to be stored somewhere, i.e. results, need to be added.
    Intermediate results that are dependencies of those output streams are handled
    internally. The actual evaluation and storage is not within the scope of
    StreamBundle, but handled by a task scheduler. See also the streams.scheduler module.

    When adding a result stream to the bundle, one has to provide a unique identifier
    that will be used when storing the results (not to be confused with the
    Stream.id property, which is an automatically computed unique identifier).
    Further, one has to provide a range for which a given output will be stored.
    The range refers to the index space of the stream. When evaluating a StreamBundle
    using a task scheduler, all output ranges will be considered to automatically
    compute the range that needs to be computed for each stream. This takes into account
    the domain of dependence between each stream and its dependencies. Only the specified
    range of each output will be stored, even if the stream needs to be evaluated on a
    larger range as dependency to another stream.

    Output identifiers consist of tuples of strings, as defined by the DatasetIdentifier
    type. They organize the results into a hirachical folder-like structure. The same
    DatasetIdentifier is used in the DataStorage objects where the stream results will
    ultimately be stored.
    """

    def __init__(self) -> None:
        self._streams: dict[int, StreamBase] = {}
        self._req_range: dict[int, tuple[int, int]] = {}
        self._out_range: dict[DatasetIdentifier, tuple[int, int]] = {}
        self._out_dsid: dict[DatasetIdentifier, int] = {}

    def _add_stream(self, s: StreamBase) -> None:
        """Internal method to add a stream and its dependencies"""
        if not s.id in self._streams:
            self._streams[s.id] = s
            for dep in s.dependencies:
                self._add_stream(dep.stream)

    def _add_req(self, s: StreamBase, newrg: tuple[int, int]) -> None:
        """Internal method to register the range a stream needs to be computed on

        This can be called multiple times and will enlarge the range to
        cover all required ranges.
        """
        if s.id in self._req_range:
            oldrg = self._req_range[s.id]
            newrg = (min(newrg[0], oldrg[0]), max(newrg[1], oldrg[1]))

        self._req_range[s.id] = newrg
        for dep in s.dependencies:
            self._add_req(dep.stream, dep.range_req(newrg))

    def add(
        self, dsid: DatasetIdentifier, stream: StreamBase, irange: tuple[int, int]
    ) -> None:
        """Adds a stream as output of the bundle

        Each output (result) needs to be given a unique identifier in form of a
        DatasetIdentifier, which is just a tuple of string.
        One also needs to specify the range that will be stored when evaluating
        the stream. The reange is given as tuple (start, stop), where start is the
        first index to be stored and stop the first index not to be stored.
        Both refer to the index space of the stream.

        Arguments:
            dsid: Unique identifier of the result
            stream: A stream instance
            irange: The range to be stored
        """
        self._add_stream(stream)
        self._add_req(stream, irange)
        self._out_range[dsid] = irange
        self._out_dsid[dsid] = stream.id

    @property
    def output_ids(self) -> set[DatasetIdentifier]:
        """Set of DatasetIdentifier of all results

        This is mainly for use by task schedulers, not end users.
        """
        return set(self._out_dsid.keys())

    def output_from_dsid(self, dsid: DatasetIdentifier) -> int:
        """Get output stream ID from its DatasetIdentifier

        This is mainly for use by task schedulers, not end users.
        """
        return self._out_dsid[dsid]

    def stream_from_dsid(self, dsid: DatasetIdentifier) -> StreamBase:
        """Get output stream for a given DatasetIdentifier"""
        return self.get_stream(self.output_from_dsid(dsid))

    def get_streams(self) -> dict[int, StreamBase]:
        """Dictionary storing all streams by stream id"""
        return self._streams

    def get_needed_streams(self, required: set[int]) -> dict[int, StreamBase]:
        """Obtain specified streams and all their dependencies"""
        needed: set[int] = set()

        if not required <= set(self._streams.keys()):
            msg = "StreamBundle: requested dependencies for nonexistent streams"
            raise RuntimeError(msg)

        def rec(i):
            s = self._streams[i]
            if not i in needed:
                for d in s.dependencies:
                    rec(d.stream.id)
            needed.add(i)

        for i in required:
            rec(i)

        return {i: self._streams[i] for i in needed}

    def get_stream(self, sid: int) -> StreamBase:
        """Get any stream in the bundle from its stream identifier

        This is mainly for use by task schedulers, not end users."""
        return self._streams[sid]

    def get_out_range(self, dsid: DatasetIdentifier) -> tuple[int, int]:
        """Get range that needs to be computed for output, in its own index space

        This is mainly for use by task schedulers, not end users."""
        return self._out_range[dsid]


def describe_streams_dict(streams: dict[str, StreamBase], descr: str) -> None:
    """Convenience function to add descriptions to all streams in a dictionary"""
    for k, v in streams.items():
        v.set_description(descr % k)
