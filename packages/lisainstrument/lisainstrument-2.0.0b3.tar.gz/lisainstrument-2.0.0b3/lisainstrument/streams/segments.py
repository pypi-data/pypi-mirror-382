"""This module defines classes for handling segments of streams.

A segment of a stream is a contiguous subset of elements short enough
to fit in memory. There are different types of segments: constant segments
are represented by SegmentConst and non-constant segments by SegmentArray.
All segment types follow the Segment protocol.

The functions join_segments and segment_arange allow joining segments and
creating segments that contain an integer range as values.
"""

from __future__ import annotations

from typing import Final, Protocol

import numpy as np


class ArrayTarget(Protocol):  # pylint: disable = too-few-public-methods
    """Protocol intended for storing 1D data someplace chunk by chunk

    If x implements this protocol, one can do `x[12:15] = y`, with a numpy array y.
    Both numpy arrays and HDF5 dataset objects provide this.
    """

    def __setitem__(self, rg: slice, data: np.ndarray):
        """Write portion of data to storage"""


class Segment(Protocol):
    """Protocol for stream segments

    A stream segment represents a segment of a stream. It has a starting index
    referring to the global index space of the stream, and a size. Further,
    it has a data type given as numpy dtype. Empty (zero sized) segments are legal,
    but still have a data type and a start index.

    """

    @property
    def size(self) -> int:
        """length of segment"""

    @property
    def istart(self) -> int:
        """Global index of first element"""

    @property
    def istop(self) -> int:
        """Global index after the last element"""

    @property
    def dtype(self) -> np.dtype:
        """Data dtype"""

    def write(
        self,
        out: ArrayTarget,
        *,
        loc_out: int = 0,
        istart: int | None = None,
        istop: int | None = None,
    ) -> None:
        """Write segment data into array out at index loc"""

    def shrink(self, nleft: int, nright: int) -> Segment:
        """Return segment with given number of points removed"""

    def tail(self, istart: int) -> Segment:
        """Cut segment and return right part"""


class SegmentArray(Segment):
    """Class representing non-constant or empty stream segments"""

    def __init__(self, data: np.ndarray, istart: int) -> None:
        """Create segment from data array and start index"""
        self._istart: Final[int] = int(istart)
        self._data: Final[np.ndarray] = data

    @property
    def size(self) -> int:
        """length of segment"""
        return self.data.shape[0]

    @property
    def istart(self) -> int:
        """Global index of first element"""
        return self._istart

    @property
    def istop(self) -> int:
        """Global index after the last element"""
        return self.istart + self.size

    @property
    def dtype(self) -> np.dtype:
        """Data dtype"""
        return self._data.dtype

    def write(
        self,
        out: ArrayTarget,
        *,
        loc_out: int = 0,
        istart: int | None = None,
        istop: int | None = None,
    ) -> None:
        """Write segment data into array out at index loc"""
        istart = self.istart if istart is None else istart
        istop = self.istop if istop is None else istop

        if self.istart <= istart <= istop <= self.istop:
            size = istop - istart
            out[loc_out : loc_out + size] = self._data[
                istart - self.istart : istop - self.istart
            ]
        else:
            msg = f"SegmentArray.write invalid range {istart=}, {istop=}"
            raise RuntimeError(msg)

    def shrink(self, nleft: int, nright: int) -> Segment:
        """Return segment with given number of points removed"""

        size = self.size - nleft - nright
        if size < 0:
            msg = "Cannot shrink SegmentArray to negative size"
            raise RuntimeError(msg)
        return SegmentArray(self._data[nleft : self.size - nright], self.istart + nleft)

    def tail(self, istart: int) -> Segment:
        """Cut segment and return right part"""
        if istart > self.istop or istart < self.istart:
            msg = f"SegmentArray.tail: cut at {istart} not within segment"
            raise RuntimeError(msg)
        return SegmentArray(self._data[istart - self.istart :], istart)

    @property
    def data(self) -> np.ndarray:
        """Numpy array with segment elements"""
        return self._data


class SegmentConst(Segment):
    """Class representing a constant stream segment"""

    def __init__(self, const: complex | float | int, istart: int, size: int) -> None:
        """Create constant segment from value, start index, and size"""
        self._istart: Final[int] = int(istart)
        self._size: Final[int] = int(size)
        self._const: Final = const
        if size < 0:
            msg = "Negative size ({size}) for SegmentConst"
            raise ValueError(msg)

    @property
    def const(self):
        """The constant value of all segment elements"""
        return self._const

    @property
    def size(self) -> int:
        """length of segment"""
        return self._size

    @property
    def istart(self) -> int:
        """Global index of first element"""
        return self._istart

    @property
    def istop(self) -> int:
        """Global index after the last element"""
        return self.istart + self.size

    @property
    def dtype(self) -> np.dtype:
        """Data dtype"""
        return np.dtype(type(self._const))

    def write(
        self,
        out: ArrayTarget,
        *,
        loc_out: int = 0,
        istart: int | None = None,
        istop: int | None = None,
    ) -> None:
        """Write segment data into array out at index loc"""
        istart = self.istart if istart is None else istart
        istop = self.istop if istop is None else istop
        if self.istart <= istart <= istop <= self.istop:
            size = istop - istart
            out[loc_out : loc_out + size] = np.array(self._const)
        else:
            msg = f"SegmentConst.write invalid range {istart=}, {istop=}"
            raise RuntimeError(msg)

    def shrink(self, nleft: int, nright: int) -> Segment:
        """Return segment with given number of points removed"""
        size = self.size - nleft - nright
        if size < 0:
            msg = "Cannot shrink SegmentConst to negative size"
            raise RuntimeError(msg)
        return SegmentConst(self.const, self.istart + nleft, size)

    def tail(self, istart: int) -> Segment:
        """Cut segment and return right part"""
        if istart > self.istop or istart < self.istart:
            msg = f"SegmentConst.tail: cut at {istart} not within segment"
            raise RuntimeError(msg)
        return SegmentConst(self._const, istart, self.istop - istart)


def join_segments(*args: Segment) -> Segment:
    """Join one or more segments together

    If all segments are constant with the same value, a constant segment is returned.
    For any other combination of constant and non-constant segments, a non-const
    segment is produced
    """

    if not args:
        msg = "join_segments needs at least one segment"
        raise RuntimeError(msg)

    ordered = sorted(args, key=lambda x: (x.istart, x.istop))

    for s0, s1 in zip(ordered[:-1], ordered[1:]):
        if s0.istop != s1.istart:
            msg = "join_segments: index range mimatch between segments"
            raise RuntimeError(msg)

    nonempty = [s for s in ordered if s.size > 0]

    if not nonempty:
        return ordered[0]

    size = sum((s.size for s in nonempty))
    istart = nonempty[0].istart

    constsegs = [s for s in nonempty if isinstance(s, SegmentConst)]
    if len(constsegs) == len(nonempty):
        values = np.array([s.const for s in constsegs])
        if np.all(values == values[0]):
            return SegmentConst(values[0], istart, size)

    out = np.empty(size, dtype=nonempty[0].dtype)
    for s in nonempty:
        s.write(out, loc_out=s.istart - istart)

    return SegmentArray(out, istart)


def segment_arange(istart: int, istop: int, offset: int = 0) -> SegmentArray:
    """Create segment covering a given global index range, with values given
    by the global index offset by a constant.
    """
    return SegmentArray(np.arange(istart + offset, istop + offset), istart)


def segment_empty(istart: int, dtype) -> SegmentArray:
    """Create and empty segment

    Empty segments still have a (degenerate) index range and a dtype. Currently
    empty segments are represented by SegmentArray but this may change.
    """
    nothing = np.array([], dtype=dtype)
    return SegmentArray(nothing, istart)
