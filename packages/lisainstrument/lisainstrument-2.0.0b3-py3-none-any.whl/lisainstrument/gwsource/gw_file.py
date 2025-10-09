"""Module with interface and implementations for reading GW files

The main interface is named GWFile. It provides GW data as time series
represented by the TimeSeriesNumpy class. The interface only returns
time series covering a specified time interval, to allow reading large
data sets chunk by chunk. Implementations should be optimized for the case
that all data is read sequentially in chunks.

There are two sets of methods, one referring to TCP time and the other to TPS.
Data may be available for both or only one, and there are methods to query
availability.

The methods for loading a dataset of a given type can be directly used by the
gw_source.GWSourceSplines class, turning the low level file reader interface
GWFile into a high level GWSource interface suitable for sampling.

There is an GWFile implementation for each supported file format. The function
gw_file returns the appropriate implementation for a file with any
supported format. Currently, only format version 2.* is supported. The
corresponding implementation is GWFileV2.
"""

import pathlib
from abc import ABC, abstractmethod
from typing import Final

import h5py
import numpy as np
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from lisainstrument.gwsource.hdf5util import HDF5Source
from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.types_numpy import TimeSeriesNumpy, make_numpy_array_1d


class GWFile(ABC):
    """Abstract interface for reading GW response files.

    The interface allows reading subsets of the data directly from file,
    where the subsets are specified as time intervals.
    The purpose is to support interpolation of GW data use chunked processing
    The chunked processing is handled on a higher level, this interface is a low-level
    numpy-based representation of the files.
    """

    @property
    @abstractmethod
    def format_version(self) -> Version:
        """Version number of the file format"""

    @property
    @abstractmethod
    def start_time_tps(self) -> float:
        """Start time (TPS) of available data [s]"""

    @property
    @abstractmethod
    def start_time_tcb(self) -> float:
        """Start time (TCB) of available data [s]"""

    @property
    @abstractmethod
    def end_time_tps(self) -> float:
        """End time (TPS) of available data [s]"""

    @property
    @abstractmethod
    def end_time_tcb(self) -> float:
        """End time (TCB) of available data [s]"""

    @property
    @abstractmethod
    def has_tpsppr_dataset(self) -> bool:
        """Whether the file has a dataset sampled w.r.t. TPS"""

    @property
    @abstractmethod
    def has_tcbltt_dataset(self) -> bool:
        """Whether the file has a dataset sampled w.r.t. TCB"""

    @abstractmethod
    def load_segment_tpsppr(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of GW data covering a given TPS time interval

        The data is sampled with respect to TPS. If the dataset is unavailable,
        an exception is raised.

        The data to be read is selected using a time interval, including the minimum
        range of samples such that the time interval is fully covered.
        One can optionally ask to include additional data points left and right of the
        specified interval. The margin size is specified in terms of the number of samples.

        If the requested time interval (not including the margins) has no overlap with
        the available data, None is returned.

        If the requested time interval has any overlap, at least the available data
        points are returned. In addition, as many of the margin points as available
        are also included. If the total number of available points is less than the
        margin size, an exception is raised.


        Arguments:
            tbegin: Start of interval to be covered [s]
            tend: End of interval to be covered [s]
            mosa: For which link to obtain response
            margin_points: Number of margin points (>=0)

        Returns:
            Time series with data points or None
        """

    @abstractmethod
    def load_segment_tcbltt(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of GW data covering a given TCB time interval

        This is the same as load_segment_tpsppr but with respect to TCB times.
        """


class GWFileV2(GWFile):
    """Implements GWFile interface for file format versions 2.*"""

    def __init__(self, path: str | pathlib.Path, chunk_size=None):
        """Constructor

        This implementation allows to specify the expected approximate
        chunk size it will be evaluated with. This is used to tune the HDF5 cache
        settings.

        Arguments:
            path: Path of the HDF5 file with GW data
            chunk_size: Optionally, evaluation chunk size to optimize for
        """
        self._h5 = HDF5Source(path, chunk_size)
        self._version: Final = Version(self._h5.file.attrs["version"])

        f5 = self._h5.file
        self._size = int(f5.attrs["size"])
        self._dt = float(f5.attrs["dt"])
        self._t0 = float(f5.attrs["t0"])
        self._has_tps = "tps/y" in f5
        self._has_tcb = "tcb/y" in f5
        if not (self._has_tps or self._has_tcb):
            msg = "GWFileV2: corrupt file has neither TPS nor TCB dataset"
            raise RuntimeError(msg)

    @property
    def format_version(self) -> Version:
        """See GWFile interface"""
        return self._version

    @property
    def start_time_tps(self) -> float:
        """See GWFile interface"""
        return self._t0

    @property
    def start_time_tcb(self) -> float:
        """See GWFile interface"""
        return self.start_time_tps

    @property
    def end_time_tps(self) -> float:
        """See GWFile interface"""
        return self._t0 + (self._size - 1) * self._dt

    @property
    def end_time_tcb(self) -> float:
        """See GWFile interface"""
        return self.end_time_tps

    @property
    def has_tpsppr_dataset(self) -> bool:
        """See GWFile interface"""
        return self._has_tps

    @property
    def has_tcbltt_dataset(self) -> bool:
        """See GWFile interface"""
        return self._has_tcb

    @staticmethod
    def _link_index(mosa: MosaID) -> int:
        """Indexing used in file for link belonging to given MOSA"""
        return {"12": 0, "23": 1, "31": 2, "13": 3, "32": 4, "21": 5}[mosa.value]

    def _load_dataset(self, i0: int, i1: int, dataset: str, mosa: MosaID) -> np.ndarray:
        """Load range of dataset for one link"""
        link_idx = GWFileV2._link_index(mosa)
        return self._h5.file[dataset][i0:i1, link_idx]

    def load_segment(
        self, dataset: str, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load segment of dataset covering given time interval

        This is the same as the load_segment_tpsppr and load_segment_tcbltt
        methods of the GWFile interface, only that the dataset type is selected
        with an additional first parameter.

        Arguments:
            dataset: Name of dataset name to load from file
            tbegin: Start of time interval to cover
            tend: End of time interval to cover
            mosa: Load link belonging to this MOSA

        Returns:
            Time series with segment data or None
        """
        if tbegin > tend:
            msg = f"GWFileV2: invalid time interval ({tbegin},{tend}) requested"
            raise RuntimeError(msg)
        if margin_points < 0:
            msg = (
                f"GWFileV2: invalid number of margin points ({margin_points}) requested"
            )
            raise RuntimeError(msg)

        ibegin = int(np.floor((tbegin - self._t0) / self._dt))
        iend = int(np.ceil((tend - self._t0) / self._dt))

        if (iend < 0) or (ibegin >= self._size):
            return None

        k0 = max(0, ibegin - margin_points)
        k1 = min(self._size, iend + margin_points + 1)

        if k1 - k0 < margin_points:
            msg = f"GWFileV2: data too short ({self._size}) for requested margin size ({margin_points})"
            raise RuntimeError(msg)

        times = self._t0 + np.arange(k0, k1) * self._dt
        data = self._load_dataset(k0, k1, dataset, mosa)

        return TimeSeriesNumpy(make_numpy_array_1d(times), make_numpy_array_1d(data))

    def load_segment_tpsppr(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GWFile interface"""
        if not self.has_tpsppr_dataset:
            msg = "GWFileV2: file doeas not contain data sampled w.r.t TPS"
            raise RuntimeError(msg)
        return self.load_segment("tps/y", tbegin, tend, mosa, margin_points)

    def load_segment_tcbltt(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GWFile interface"""
        if not self.has_tcbltt_dataset:
            msg = "GWFileV2: file doeas not contain data sampled w.r.t TCB"
            raise RuntimeError(msg)
        return self.load_segment("tcb/y", tbegin, tend, mosa, margin_points)


GWFileV3 = GWFileV2


def gw_file(path: str | pathlib.Path) -> GWFile:
    """Open GW file of any supported version

    Arguments:
        path: Path of the file

    Returns:
        Instance providing GWFile interface
    """
    with h5py.File(path, "r") as gwf:
        version = Version(gwf.attrs["version"])

    if version in SpecifierSet("< 1.1", True):
        msg = "Reading GW file format version < 1.1 currently not implemented"
        raise RuntimeError(msg)
        # return GWFileVPre11(path)
    if version in SpecifierSet("== 1.1", True):
        msg = "Reading GW file format version = 1.1 currently not implemented"
        raise RuntimeError(msg)
        # return GWFileV11(path)
    if version in SpecifierSet("== 2.*", True):
        return GWFileV2(path)
    if version in SpecifierSet("== 3.*", True):
        return GWFileV3(path)

    msg = f"unsupported GW file version '{version}'"
    raise RuntimeError(msg)
