"""Module for representing numpy arrays as streams and build StreamBundles

The main use case for this is to store results that have already been evaluated
and stored to in-memory numpy arrays to file, using the same infrastructure as
for evaluating directly to file.

The array_dict_as_stream_bundle function can be used to construct a StreamBundle
from a dictionary with ordinary numpy arrays.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from lisainstrument.streams.segments import Segment, SegmentArray
from lisainstrument.streams.store import DatasetIdentifier
from lisainstrument.streams.streams import StreamBase, StreamBundle


class StreamNumpyArray(StreamBase):
    """Stream providing elements of a numpy array

    Although streams are conceptually infinite, this one will raise an exception
    when evaluated out of bounds where the data is available. It is up to the user
    to avoid this, which means that all streams depending on the array stream need
    to respect the bounds, taking into account margins for filtering and similar.
    """

    def __init__(self, data: np.ndarray, i_start: int):
        """Not part of API, use array_dict_as_stream_bundle instead

        Arguments:
            data: The 1D array with the stream elements
            i_start: Stream index of the first array element
        """
        if len(data.shape) != 1:
            msg = f"StreamNumpyArray: data array must be 1D, got shape{data.shape}"
            raise RuntimeError(msg)
        super().__init__([], False, data.dtype)
        self._data = data
        self._istart = int(i_start)
        self._istop = self._istart + data.shape[0]

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        if not self._istart <= istart <= istop <= self._istop:
            msg = f"StreamNumpyArray: requested range {istart}, {istop} not available"
            raise RuntimeError(msg)
        d = self._data[istart - self._istart : istop - self._istart]
        res = SegmentArray(d, istart)
        return res, None


def array_dict_as_stream_bundle(
    data: dict[DatasetIdentifier, np.ndarray],
    istart: dict[DatasetIdentifier, int] | None = None,
) -> StreamBundle:
    """Make data in a dictionary of numpy arrays available as StreamBundle

    The DatasetIdentifier for each stream must be provided as the dictionary key.
    By default, the streams start at index 0, unless the optional istart dictionary
    has an entry for the dataset identifier.

    Arguments:
        data: Dictionary with stream data as arrays
        istart: Dictionary with optional entries for stream starting index

    Returns:
        StreamBundle with output streams labeled by the dictionary keys
    """
    if istart is None:
        istart = {}
    stb = StreamBundle()
    for dsid, dat in data.items():
        i0 = istart.get(dsid, 0)
        rg = (i0, i0 + len(dat))
        stream = StreamNumpyArray(dat, i0)
        stb.add(dsid, stream, rg)
    return stb
