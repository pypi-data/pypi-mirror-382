"""Implements a stream that transfers its input to a DataStorage instance


This is used internally by the task scheduler and should not be used directly.
StreamStore is a special stream type in that it has side effects, the output is
not used, and it is not part of the StreamBundle but injected by the task scheduler.
The side effect is to store the incoming results using the DataStorage framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeAlias

import numpy as np

from lisainstrument.streams.segments import ArrayTarget, Segment, SegmentConst
from lisainstrument.streams.streams import StreamBase, StreamDependency

DatasetIdentifier: TypeAlias = tuple[str, ...]
ValidMetaDataTypes: TypeAlias = int | float | str | dict | list | np.ndarray | None


class DataStorage(ABC):  # pylint: disable = too-few-public-methods
    """Interface representing something where stream data can be written to.

    This provides a mapping of dataset identifiers onto targets for storing
    chunks of a single stream. Dataset identifiers are tuples of strings.

    When creating a datasets, one has to specify the index range of the stream that
    will be written. The resulting low level ArrayTarget has a corresponding size,
    but indexing starts at zero. Thus, one can use numpy arrays or hdf5 datasets
    as ArrayTarget. The abstract index range should be stored by implementations
    such that the stored data can be used to reproduce the streams it was created
    from.
    """

    @property
    @abstractmethod
    def valid_identifiers(self) -> set[DatasetIdentifier]:
        """Set with identifiers of all required datasets"""

    @abstractmethod
    def dataset(
        self, ident: DatasetIdentifier, istart: int, istop: int, dtype: np.dtype
    ) -> ArrayTarget:
        """Create a target for a dataset identifier

        Arguments:
            ident: Identifier to be used in the storage container
            istart: Start index of the stream that will be written
            istop: End index (not included) of the stream that will be written
            dtype: Data type of stream that will be written

        Returns:
            Object with numpy-like interface for writing setting slices
        """

    @abstractmethod
    def dataset_const(
        self,
        ident: DatasetIdentifier,
        istart: int,
        istop: int,
        const: int | float | complex,
    ) -> None:
        """Create a dataset that is constant

        This directly creates the data in the storage, taking advantage of the constant
        data. This should not be confused with scalar data. It represents an array
        that happens to be constant. Storage implementations may chose to store it as a
        scalar, however, for optimization.

        Since this represents the output of a constant stream, the logical index range
        must still be given and should be stored by the implementation of a given container
        format.

        Arguments:
            ident: Identifier to be used in the storage container
            istart: Start index of the constant stream
            istop: End index (not included) of the constant stream
            const: The constant value
        """


class StreamStore(StreamBase):
    """Stream that passes through its input but copies it to DataStorage."""

    def __init__(
        self, target: ArrayTarget, stream: StreamBase, irange: tuple[int, int]
    ):
        """Constructor.

        This requires a storage location given as any object satisfying the ArrayTarget
        protocol, e.g. numpy arrays or h5py datasets. The size of the ArrayTarget needs
        to match the size of the specified output range.

        This stream is defined as stateful, such that it is always evaluated serially
        in ascending order. This is motivated by the main use case of file storage.

        Arguments:
            target: an ArrayTarget to store the results
            stream: The input stream to store
            irange: The range in the input stream index space that will be stored.
        """
        dep = StreamDependency(stream=stream)
        super().__init__([dep], True, float)
        self._target = target
        self._irange = irange

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generator of the stream

        The output is not supposed to be used, the side effects of the generator are
        its whole purpose. The side effect is to store the results of the input stream,
        after cutting off any elements not in the range to be stored.

        This also cross-checks that there are no gaps, by defining the last index written
        as its state.
        """
        (seg,) = deps
        i0, i1 = self._irange

        if state is None:
            if istart > i0:
                msg = f"StreamStore: missing {seg.istart-i0} elements at beginning"
                raise RuntimeError(msg)
            state = istart

        if not seg.istart <= istart <= istop <= seg.istop:
            msg = f"StreamStore: cannot generate requested range [{istart}, {istop})"
            raise RuntimeError(msg)

        if istart != state:
            msg = f"StreamStore: gap or overlap in data transfer ({state} != {istart})"
            raise RuntimeError(msg)

        if i0 <= istart < istop <= i1:
            seg.write(self._target, loc_out=istart - i0, istart=istart, istop=istop)
        elif istart <= i0 < istop <= i1:
            seg.write(self._target, loc_out=0, istart=i0, istop=istop)
        elif i0 <= istart < i1 <= istop:
            seg.write(self._target, loc_out=istart - i0, istart=istart, istop=i1)
        elif istart <= i0 < i1 <= istop:
            seg.write(self._target, loc_out=0, istart=i0, istop=i1)

        dummy = SegmentConst(0.0, istart, istop - istart)

        return dummy, istop
