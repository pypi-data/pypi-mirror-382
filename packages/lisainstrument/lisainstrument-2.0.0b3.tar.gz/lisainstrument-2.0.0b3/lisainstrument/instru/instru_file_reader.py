"""The instru.instru_file_reader module allows reading data from simulation result files.


This module is not required by the simulator but supports using simulation
results in post-processing. The SimResultFile is a low-level representation of
a simulation result file, allowing direct access to datasets without having to
know the internal file format. It also provides a view of the simulation data
as a StreamBundle, allowing chunked processing of saved simulation results.

Besides chunked processing, it also allows reading all data into memory at once,
collected in a SimResultsNumpyCore or SimResultsNumpyFull instance.
"""

import json
import pathlib
from collections import defaultdict
from typing import Final, TypeVar

import h5py
import numpy as np

from lisainstrument.instru.instru_store import (
    IdxSpace,
    SimFullDatasetsMOSA,
    SimFullDatasetsSat,
    SimMetaData,
    SimResultsNumpyCore,
    SimResultsNumpyFull,
    datasets_metadata_dict,
    make_dataset_id,
)
from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.streams import DatasetIdentifier, StreamBundle
from lisainstrument.streams.hdf5_store import (
    DataStorageHDF5,
    hdf5_file_as_stream_bundle,
)
from lisainstrument.streams.numpy_store import store_bundle_numpy

_T = TypeVar("_T", SimResultsNumpyFull, SimResultsNumpyCore)


def _unique_index_range(ranges: list[tuple[int, int]]) -> tuple[int, int]:
    """Ensure index ranges in list are identical and return that range"""
    s = set(ranges)
    if len(s) != 1:
        msg = f"unique_index_range: ranges not identical ({ranges=})"
        raise RuntimeError(msg)
    (uni,) = list(s)
    return uni


class SimResultFile:
    """Represents a simulation result file in HDF5 format.

    There are low-level methods for direct reading of datasets identified either
    by name and MOSA or SC index, or by a DatasetIdentifier. For use cases where the
    results fit into memory, there are methods to create a SimResultsNumpyCore or
    SimResultsNumpyFull instance with the data and metadata.

    For use cases dealing with large data sets, there is a method representing
    the datasets as streams in a StreamBundle for use with chunked processing.
    For all those methods, it is possible to restrict the data to a given time
    interval.
    """

    def __init__(self, path: pathlib.Path | str):
        """Constructor

        Arguments:
            path: Path of the a HDF5 file created by store_instru_hdf5
        """
        self._h5f = h5py.File(str(path), "r")

        ds_actual = set(self._h5f.keys()) - {"debug"}
        ds_debug = set(self._h5f["debug"].keys())
        ds_all = ds_actual | ds_debug

        if ds_all == SimResultsNumpyFull.all_dataset_names:
            self._extended = True
        elif ds_all == SimResultsNumpyCore.all_dataset_names:
            self._extended = False
        else:
            msg = f"File {path} contains invalid set of quantities"
            raise RuntimeError(msg)

        md = json.loads(self._h5f.attrs["metadata_json"])
        self._metadata = SimMetaData(**md)

        self._description = str(self._h5f.attrs.get("description", None))

        self._t0 = self._metadata.t0
        self._sample_periods = {
            IdxSpace.PHYSICS: self._metadata.physics_dt,
            IdxSpace.PHYSICS_EXT: self._metadata.physics_dt,
            IdxSpace.REGULAR: self._metadata.dt,
            IdxSpace.TELEMETRY: self._metadata.telemetry_dt,
        }

        categories = datasets_metadata_dict()

        isps: dict[DatasetIdentifier, IdxSpace] = {}
        ranges: dict[IdxSpace, list[tuple[int, int]]] = defaultdict(list)
        for dsid in self.dataset_identifier_set():
            n = dsid[-2]
            cat = categories[n]
            rg = self._read_range(dsid)
            ranges[cat.idxspace].append(rg)
            isps[dsid] = cat.idxspace
        self._isp_by_dsid: Final = isps
        self._range_by_isp: Final = {
            i: _unique_index_range(r) for i, r in ranges.items()
        }

    def __del__(self):
        """File is automatically closed"""
        self._h5f.close()

    @property
    def is_extended(self) -> bool:
        """Whether file contains extended set of quantities"""
        return self._extended

    @property
    def metadata(self) -> SimMetaData:
        """Simulation metadata"""
        return self._metadata

    @property
    def description(self) -> str | None:
        """Description text"""
        return self._description

    def dataset_identifier_set(self) -> set[DatasetIdentifier]:
        """Set of all available dataset identifiers"""
        if self.is_extended:
            return SimResultsNumpyFull.dataset_identifier_set()
        return SimResultsNumpyCore.dataset_identifier_set()

    def idxspace_by_dataset_id(self, dsid: DatasetIdentifier) -> IdxSpace:
        """Get index space for dataset"""
        return self._isp_by_dsid[dsid]

    def range_by_idxspace(self, isp: IdxSpace) -> tuple[int, int]:
        """Get range for given index space"""
        return self._range_by_isp[isp]

    def range_by_dataset_id(self, dsid: DatasetIdentifier) -> tuple[int, int]:
        """Get range for given index space"""
        return self.range_by_idxspace(self.idxspace_by_dataset_id(dsid))

    def dt_by_idxspace(self, isp: IdxSpace) -> float:
        """Get range for given index space"""
        return self._sample_periods[isp]

    def dt_by_dataset_id(self, dsid: DatasetIdentifier) -> float:
        """Get range for given index space"""
        return self.dt_by_idxspace(self.idxspace_by_dataset_id(dsid))

    def read_by_datset_id(
        self, dsid: DatasetIdentifier, istart: int | None, istop: int | None
    ) -> np.ndarray:
        """Read data identified by a `DatasetIdentifier`

        Optionally, one can restrict the index range. This refers to the logical
        index range given returned `range_by_dataset_id()`, not necessarily starting
        at zero. The returned data will contain indices `istart <= i < istop`

        Arguments:
            dsid: `DatasetIdentifier` specifying dataset
            istart: Optionally, exclude lower indices
            istop: Optionally, first index to exclude

        Returns:
            1D numpy array with data
        """
        dspth = "/".join(dsid)
        ds: h5py.Dataset = self._h5f[dspth]
        aistart, aistop = self.range_by_dataset_id(dsid)
        istart = aistart if istart is None else int(istart)
        istop = aistop if istop is None else int(istop)
        if not aistart <= istart <= istop <= aistop:
            msg = (
                f"SimResultFile: index range {istart}, {istop} not "
                f"available for dataset {dspth}"
            )
            raise RuntimeError(msg)
        if len(ds.shape) == 0:  # pylint: disable = no-member
            dat = np.empty(
                istop - istart, dtype=ds.dtype  # pylint: disable = no-member
            )
            dat[:] = ds[()]
            return dat
        return ds[istart - aistart, istop - aistart]

    def read_by_name_and_mosa(
        self, name: str, mosa: MosaID | str, istart: int | None, istop: int | None
    ) -> np.ndarray:
        """Like `read_by_datset_id` but dataset is specified by name and `MosaID`

        Arguments:
            name: Dataset name
            mosa: Read dataset for MOSA specified by `MosaID` or MOSA name
            istart: Optionally, exclude lower indices
            istop: Optionally, first index to exclude

        Returns:
            1D numpy array with data
        """

        if name not in SimFullDatasetsMOSA.dataset_names():
            msg = f"SimResultFile: invalid per-MOSA dataset {name}"
            raise RuntimeError(msg)
        cat = SimFullDatasetsMOSA.dataset_metadata()[name]
        dsid = make_dataset_id(cat.actual, name, MosaID(mosa).value)
        return self.read_by_datset_id(dsid, istart, istop)

    def read_by_name_and_sat(
        self, name: str, sc: SatID | str, istart: int | None, istop: int | None
    ) -> np.ndarray:
        """Like `read_by_datset_id` but dataset is specified by name and `SatID`

        Arguments:
            name: Dataset name
            sc: Read dataset for spacecraft specified by `SatID` or spacecraft name
            istart: Optionally, exclude lower indices
            istop: Optionally, first index to exclude

        Returns:
            1D numpy array with data
        """
        if name not in SimFullDatasetsSat.dataset_names():
            msg = f"SimResultFile: invalid per-spacecraft dataset {name}"
            raise RuntimeError(msg)
        cat = SimFullDatasetsSat.dataset_metadata()[name]
        dsid = make_dataset_id(cat.actual, name, SatID(sc).value)
        return self.read_by_datset_id(dsid, istart, istop)

    def _read_range(self, dsid: DatasetIdentifier) -> tuple[int, int]:
        """Get the index range available for a given dataset

        The available indices `i` are in the range `istart <= i < istop`.

        Arguments:
            dsid: `DatasetIdentifier` specifying the dataset

        Returns:
            Tuple `(istart, istop)`
        """
        dspth = "/".join(dsid)
        ds: h5py.Dataset = self._h5f[dspth]
        istart = int(ds.attrs[DataStorageHDF5.attr_name_index_start])
        istop = int(ds.attrs[DataStorageHDF5.attr_name_index_stop])
        return (istart, istop)

    def _restrict_range_isp(
        self,
        isp: IdxSpace,
        t_min: float | None = None,
        t_max: float | None = None,
    ) -> tuple[int, int]:
        """Compute index range within given time interval for a given dataset"""
        dt = self.dt_by_idxspace(isp)
        istart, istop = self.range_by_idxspace(isp)
        if t_min is None:
            i0 = istart
        else:
            i0 = int(np.ceil((t_min - self._t0) / dt))

        if t_max is None:
            i1 = istop
        else:
            i1 = int(np.ceil((t_max - self._t0) / dt))

        return i0, i1

    def _restrict_ranges(
        self,
        t_min: float | None = None,
        t_max: float | None = None,
    ) -> dict[IdxSpace, tuple[int, int]]:
        """Compute index ranges within given time interval for datasets"""
        return {
            isp: self._restrict_range_isp(isp, t_min, t_max)
            for isp in self._range_by_isp
        }

    def _read_datasets(
        self,
        cls: type[_T],
        t_min: float | None = None,
        t_max: float | None = None,
    ) -> _T:
        """Read datasets into a `DataStorageNumpy` instance"""
        datasets = cls.dataset_identifier_set()
        ranges_isp = self._restrict_ranges(t_min, t_max)
        ranges_dsid = {
            dsid: ranges_isp[self.idxspace_by_dataset_id(dsid)] for dsid in datasets
        }

        stb = self.as_stream_bundle(datasets, ranges_dsid)
        store = store_bundle_numpy(stb)
        return cls(store.as_dict(), ranges_isp, self.metadata.asdict())

    def read_full(
        self, t_min: float | None = None, t_max: float | None = None
    ) -> SimResultsNumpyFull:
        """Read extended set of quantities into memory as `SimResultsNumpyFull` instance

        If the file does not contain the extended set, an RuntimeError is raised.

        Optionally, on can restrict the time range for which the data samples are
        read. This does not change the index space, i.e. which indices refer to which
        times. It only changes the index range of the datasets, available through
        the `sat_ranges` and `mosa_ranges` attributes of `SimResultsNumpyFull`.

        Arguments:
            t_min: Optionally, only read samples at later times
            t_max: Optionally, only read samples at earlier times

        Returns:
            `SimResultsNumpyFull` instance with data.
        """

        if not self.is_extended:
            msg = "SimResultFile: cannot read extended results from basic result file"
            raise RuntimeError(msg)
        return self._read_datasets(SimResultsNumpyFull, t_min, t_max)

    def read_core(
        self, t_min: float | None = None, t_max: float | None = None
    ) -> SimResultsNumpyCore:
        """Same as `read_full` but restricted to basic set of quantities

        Arguments:
            t_min: Optionally, only read samples at later times
            t_max: Optionally, only read samples at earlier times

        Returns:
            `SimResultsNumpyCore` instance with data.
        """
        return self._read_datasets(SimResultsNumpyCore, t_min, t_max)

    def as_stream_bundle(
        self,
        datasets: set[DatasetIdentifier] | None = None,
        ranges: dict[DatasetIdentifier, tuple[int, int]] | None = None,
    ) -> StreamBundle:
        """Represent datasets in the file as `StreamBundle`

        Arguments:
            datasets: Set of quantities to include
            ranges: Dictionary with optional entris restricting dataset index range

        Returns:
            StreamBundle with specified datasets as outputs.
        """
        if datasets is None:
            datasets = self.dataset_identifier_set()
        return hdf5_file_as_stream_bundle(self._h5f, datasets, ranges=ranges)
