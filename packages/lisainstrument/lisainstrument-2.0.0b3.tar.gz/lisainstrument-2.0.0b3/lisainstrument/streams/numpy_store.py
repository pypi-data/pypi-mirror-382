"""Function for storing StreamBundle to memory as numpy arrays

The DataStorageNumpy class stores numpy arrays and makes them available as
targets for evaluating streams. The purpose is to use the same infrastructure
for problems that fit into memory as for large problems that don't, by
exchanging file storage with DataStorageNumpy.

Use store_bundle_numpy to evaluate a StreamBundle and obtain the results as a
dictionary of numpy arrays.
For simple cases (testing etc) use eval_stream_list_numpy to directly evaluate
a list of streams into a list of numpy arrays.
"""

from typing import Final

import numpy as np

from lisainstrument.streams.scheduler import SchedulerConfigTypes, store_bundle
from lisainstrument.streams.segments import ArrayTarget
from lisainstrument.streams.store import DatasetIdentifier, DataStorage
from lisainstrument.streams.streams import StreamBase, StreamBundle


class DataStorageNumpy(DataStorage):  # pylint: disable = too-few-public-methods
    """Provide DataStorage based on numpy arrays in memory

    This serves as a temporary object for using with streams.scheduler.store_bundle to
    evaluate streams into a collection of numpy arrays. Once this is done, the as_dict()
    method can be used to get the data.

    This is not intended for direct use. To directly evaluate a StreamBundle to a dict of
    numpy arrays, use the function store_bundle_numpy()
    """

    def __init__(self, identifiers: set[DatasetIdentifier]):
        self._identifiers: Final = set(identifiers)
        self._store: dict[DatasetIdentifier, np.ndarray] = {}
        self._ranges: dict[DatasetIdentifier, tuple[int, int]] = {}

    @property
    def valid_identifiers(self) -> set[DatasetIdentifier]:
        """Set with identifiers of all required datasets"""
        return self._identifiers.copy()

    def _check_ident(self, ident: DatasetIdentifier) -> None:
        """Ensure that identifier can be added"""
        if not ident in self.valid_identifiers:
            msg = f"DataStorageNumpy: attempt to create dataset with invalid indentifier {ident}"
            raise RuntimeError(msg)
        if ident in self._store:
            msg = (
                f"DataStorageNumpy: attempt to create already existing dataset {ident}"
            )
            raise RuntimeError(msg)

    def dataset(
        self, ident: DatasetIdentifier, istart: int, istop: int, dtype: np.dtype
    ) -> ArrayTarget:
        """Create a target for a dataset identifier."""
        self._check_ident(ident)

        shape = (istop - istart,)
        self._store[ident] = np.zeros(shape, dtype=dtype)
        self._ranges[ident] = (istart, istop)
        return self._store[ident]

    def dataset_const(
        self,
        ident: DatasetIdentifier,
        istart: int,
        istop: int,
        const: int | float | complex,
    ) -> None:
        """Create a dataset that is constant"""
        self._check_ident(ident)
        shape = (istop - istart,)
        self._store[ident] = np.full(shape, const)
        self._ranges[ident] = (istart, istop)

    def as_dict(self) -> dict[DatasetIdentifier, np.ndarray]:
        """Return data as dictionary

        This can be called after data has been stored here, e.g. using store_bundle_numpy.
        Calling it before makes no sense and will return an empty dictionary.
        """
        return self._store.copy()

    def ranges(self) -> dict[DatasetIdentifier, tuple[int, int]]:
        """Return dictionary with the index ranges of the stored data

        This refers to the index range of the stream the data was transfered from.
        """
        return self._ranges


def store_bundle_numpy(
    source: StreamBundle,
    datasets: set[DatasetIdentifier] | None = None,
    *,
    cfgscheduler: SchedulerConfigTypes | None = None,
) -> DataStorageNumpy:
    """Store a generic StreamBundle to memory as dictionary of numpy arrays

    The resulting dictionary is keyed using the requested identifiers (DatasetIdentifier)

    Arguments:
        source: Data source as StreamBundle
        datasets: Which datasets to save. Defaults to all.
        cfgscheduler: Parameters for the scheduling

    Returns:
        Dictionary with output stream data as arrays
    """

    if datasets is None:
        datasets = source.output_ids

    store = DataStorageNumpy(datasets)
    store_bundle(source, store, cfgscheduler)
    return store


def eval_stream_list_numpy(
    streams: list[StreamBase],
    out_range: tuple[int, int],
    cfgscheduler: SchedulerConfigTypes | None = None,
) -> list[np.ndarray]:
    """Directly evaluate a list of streams to a list of numpy arrays.

    The purpose of this function is to simplify working with simple stream collections
    in memory, without storing to disk, and using the same output range for all streams.
    This is used for unit testing.

    Arguments:
        streams: List of streams to evaluate
        out_range: index range to evaluate for all streams
        cfgscheduler: Parameters for the scheduling

    Returns:
        List of numpy arrays with output of each stream.
    """
    i = np.arange(len(streams))
    dsids = [(str(i),) for i in np.arange(len(streams))]
    stb = StreamBundle()
    for s, dsid in zip(streams, dsids):
        stb.add(dsid, s, out_range)
    store = DataStorageNumpy(set(dsids))
    store_bundle(stb, store, cfgscheduler)
    res = store.as_dict()

    return [res[dsid] for dsid in dsids]
