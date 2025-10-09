"""Function for streaming to or from HDF5 files

The DataStorageHDF5 class implements the DataStorage interface used by
scheduler.store_bundle to store stream data while it is generated. The
generic DatasetIdentifiers used to label output streams define the structure
of the file. The string tuples given by DatasetIdentifiers are used to set up
datasets inside nested groups, all named after the elements of the tuple.
Created datasets are continuous, i.e. there is one dataset per stream, not per
stream chunk. Constant datasets are treated specially, by saving a scalar
dataset.

Use store_bundle_hdf5 to store all output streams of a StreamBundle, or a
subset, into a HDF5 file. This also allows creation of metadata, as well as
setting up alias names pointing to the same dataset.

Use hdf5_file_as_stream_bundle to create a StreamBundle for reading the data
from an existing HDF5 file created by store_bundle_hdf5.
"""

import pathlib
from typing import Any, Final, TypeAlias

import h5py
import numpy as np

from lisainstrument.streams.scheduler import SchedulerConfigTypes, store_bundle
from lisainstrument.streams.segments import ArrayTarget, Segment, SegmentArray
from lisainstrument.streams.store import DatasetIdentifier, DataStorage
from lisainstrument.streams.streams import StreamBase, StreamBundle, StreamConst

H5AttrValidTypes: TypeAlias = int | float | str | list[float] | list[int] | np.ndarray


class DataStorageHDF5(DataStorage):  # pylint: disable = too-few-public-methods
    """Provide DataStorage based on HDF5 file."""

    attr_name_index_start = "index_start"
    attr_name_index_stop = "index_stop"

    @staticmethod
    def _mkdir(grp: h5py.Group, sub: tuple[str, ...]) -> h5py.Group:
        if not sub:
            return grp
        i = sub[0]
        grp = grp[i] if i in grp else grp.create_group(i)
        return DataStorageHDF5._mkdir(grp, sub[1:])

    def __init__(self, h5file: h5py.File, identifiers: set[DatasetIdentifier]):
        if any((len(i) == 0 for i in identifiers)):
            msg = "DataStorageHDF5: got empty dataset identifier"
            raise RuntimeError(msg)
        self._file: Final = h5file
        self._identifiers: Final = set(identifiers)
        self._added: set[DatasetIdentifier] = set()

    @property
    def valid_identifiers(self) -> set[DatasetIdentifier]:
        """Set with identifiers of all required datasets"""
        return self._identifiers.copy()

    def _check_ident(self, ident: DatasetIdentifier) -> None:
        """Ensure that identifier can be added"""
        if not ident in self.valid_identifiers:
            msg = f"DataStorageHDF5: attempt to create dataset with invalid indentifier {ident}"
            raise RuntimeError(msg)

        if ident in self._added:
            msg = f"DataStorageHDF5: attempt to create same dataset {ident} twice"
            raise RuntimeError(msg)

        self._added.add(ident)

    def _range_attrs(self, ds: h5py.Dataset, istart: int, istop: int) -> None:
        """Set dataset attributes with original index range"""
        ds.attrs[self.attr_name_index_start] = istart
        ds.attrs[self.attr_name_index_stop] = istop

    def dataset(
        self, ident: DatasetIdentifier, istart: int, istop: int, dtype: np.dtype
    ) -> ArrayTarget:
        """Create a target for a dataset identifier.

        See DataStorage for general description.

        This creates a HDF5 dataset within a hierachy HDF5 groups. The last
        element of the dataset identifier is the dataset name. If the identifier
        contains more elements they are used as names for nested HDF5 groups. The
        groups are created automatically.
        """
        self._check_ident(ident)
        shape = (istop - istart,)

        grp = DataStorageHDF5._mkdir(self._file, ident[:-1])
        ds = grp.create_dataset(ident[-1], shape, dtype=dtype)
        self._range_attrs(ds, istart, istop)

        return ds

    def dataset_const(
        self,
        ident: DatasetIdentifier,
        istart: int,
        istop: int,
        const: int | float | complex,
    ) -> None:
        """Create a dataset that is constant

        See DataStorage for general description.

        This creates a scalar hdf5 dataset for efficiency.
        """
        self._check_ident(ident)

        grp = DataStorageHDF5._mkdir(self._file, ident[:-1])
        ds = grp.create_dataset(ident[-1], data=np.array(const))
        self._range_attrs(ds, istart, istop)


def alias_dataset_hdf5(
    grp: h5py.Group, idold: DatasetIdentifier, idlink: DatasetIdentifier
) -> None:
    """Create an alias name (a hard link) for a dataset in a HDF5 file.

    The locations of link and existing dataset are specified via generic
    DatasetIdentifier objects.

    Arguments:
        grp: Root group of the HDF5 file.
        idold: Identifier of the existing dataset
        idlink: Identifier for the link to be created
    """
    gold, glink = grp, grp
    for i in idold[:-1]:
        gold = gold[i]
    for i in idlink[:-1]:
        glink = glink[i] if (i in glink) else glink.create_group(i)
    glink[idlink[-1]] = gold[idold[-1]]


def store_bundle_hdf5(
    path: pathlib.Path | str,
    source: StreamBundle,
    metadata: dict[str, H5AttrValidTypes],
    datasets: set[DatasetIdentifier] | None = None,
    aliases: dict[DatasetIdentifier, DatasetIdentifier] | None = None,
    overwrite: bool = False,
    cfgscheduler: SchedulerConfigTypes | None = None,
) -> None:
    """Store a generic StreamBundle and metadata in a HDF5 file.

    In addition of storing all streams from the bundle into the file,
    this also created attributes for metadata, and allows to create aliases (links)
    for datasets.

    By default, the streams are evaluated with conservative resource usage. The
    number of CPUs and memory usage can be adjusted with cfgscheduler parameter (see
    streams.scheduler).

    Arguments:
        path: Path where to create the HDF5 file
        source: Data source as StreamBundle
        metadata: Dictionary to be written as HDF5 file attributes
        datasets: Identifiers of the datasets to save. Defaults to all.
        aliases: Dictionary mapping DatasetIdentifiers to alternative identifiers.
        overwrite: If True overwite existing files
        cfgscheduler: Parameters for the scheduling
    """

    if datasets is None:
        datasets = source.output_ids

    mode = "w" if overwrite else "w-"
    with h5py.File(path, mode) as h5f:
        store = DataStorageHDF5(h5f, datasets)
        store_bundle(source, store, cfgscheduler)
        for attr_name, attr_value in metadata.items():
            h5f.attrs[attr_name] = attr_value

        if aliases:
            for idold, idlink in aliases.items():
                alias_dataset_hdf5(h5f, idold, idlink)


class StreamDatasetHDF5(StreamBase):
    """Stream providing elements of a hdf5 dataset

    This reads back datasets produced by DataStorageHDF5 for non-const
    datasets. The case of const datasets is handled in stream_hdf5_dataset.
    """

    def __init__(self, dataset: h5py.Dataset, istart: int):
        """Not part of API, use stream_hdf5_dataset instead

        Arguments:
            dataset: The 1D hdf5 dataset with the stream elements
            istart: stream index of first element in dataset
        """
        (size,) = dataset.shape
        self._data = dataset
        self._istart = istart
        self._istop = self._istart + size
        super().__init__([], False, self._data.dtype)

    @property
    def available_range(self) -> tuple[int, int]:
        """Available index range"""
        return (self._istart, self._istop)

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""
        if not self._istart <= istart <= istop <= self._istop:
            msg = f"StreamDatasetHDF5: requested range {istart}, {istop} not available"
            raise RuntimeError(msg)
        d = self._data[istart - self._istart : istop - self._istart]
        res = SegmentArray(d, istart)
        return res, None


def stream_hdf5_dataset(dataset: h5py.Dataset) -> tuple[StreamBase, tuple[int, int]]:
    """Provide a stream for reading a hdf5 dataset produced by DataStorageHDF5.

    The special case of constant datasets, represented as scalars, is treated by returning
    a StreamConst.

    Arguments:
        dataset: The 1D hdf5 dataset with the stream elements

    Returns:
        Tuple with stream and available index range
    """
    for atreq in (
        DataStorageHDF5.attr_name_index_start,
        DataStorageHDF5.attr_name_index_stop,
    ):
        if atreq not in dataset.attrs:
            msg = "stream_hdf5_dataset: dataset missing attribute {atreq}."
            raise RuntimeError(msg)
    istart = int(dataset.attrs[DataStorageHDF5.attr_name_index_start])
    istop = int(dataset.attrs[DataStorageHDF5.attr_name_index_stop])
    rg = (istart, istop)
    size = istop - istart
    if size < 0:
        msg = f"stream_hdf5_dataset: size from range attributes is negative ({size}) "
        raise RuntimeError(msg)
    shape = dataset.shape
    dstr: StreamBase
    if len(shape) == 1:
        if shape[0] != istop - istart:
            msg = (
                f"stream_hdf5_dataset: size from range attributes ({size}) "
                f"and dataset ({shape[0]}) inconsistent"
            )
            raise RuntimeError(msg)
        dstr = StreamDatasetHDF5(dataset, istart)
    elif len(shape) == 0:
        dstr = StreamConst(dataset.dtype.type(dataset[()]))
    else:
        msg = "stream_hdf5_dataset: invalid dataset shape {shape}"
        raise RuntimeError(msg)
    return dstr, rg


def hdf5_file_as_stream_bundle(
    h5f: h5py.File,
    datasets: set[DatasetIdentifier],
    ranges: dict[DatasetIdentifier, tuple[int, int]] | None = None,
) -> StreamBundle:
    """StreamBundle representing HDF5 file created by store_bundle_hdf5

    The purpose is to process full datafiles in a chunked fashion. A second use
    is to read only a restricted range into a memory-based storage.

    Arguments:
        h5f: HDF5 file created by store_bundle_hdf5
        datasets: Which datasets to include in bundle
        ranges: Dictionary optionally overriding individual dataset ranges

    Returns:
        StreamBundle allowing to process the selected datasets.
    """
    if ranges is None:
        ranges = {}
    stb = StreamBundle()
    for dsid in datasets:
        dspth = "/".join(dsid)
        stream, rga = stream_hdf5_dataset(h5f[dspth])
        rg = ranges.get(dsid, rga)
        stb.add(dsid, stream, rg)
    return stb
