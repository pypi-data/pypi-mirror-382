"""Module with interface and implementations for reading Glitch files

The main interface is named GlitchFile. It provides glitch data as time series
represented by the TimeSeriesNumpy class. The interface only returns
time series covering a specified time interval, to allow reading large
data sets chunk by chunk. Implementations should be optimized for the case
that all data is read sequentially in chunks.

For each injection point, there is a method to load data segments for a given
MOSA. Data may be unavailable for any combination of injection point and MOSA,
and there are methods to query availability.

The GlitchFile interface can be directly used by the
glitch_source_interp.GlitchSourceSplines class, turning the low level
file reader interface GlitchFile into a high level GlitchSource interface
suitable for sampling.

There is an GlitchFile implementation for each supported file format. The
function glitch_file returns the appropriate implementation for a file with any
supported format. Currently, only format version 1.4.dev is supported. The
corresponding implementation is GlitchFileV14.
"""

import pathlib
from abc import ABC, abstractmethod
from typing import Final

import h5py
import numpy as np
from packaging.version import Version

from lisainstrument.gwsource.hdf5util import HDF5Source
from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.types_numpy import TimeSeriesNumpy, make_numpy_array_1d


class GlitchFile(ABC):
    """Abstract interface for reading glitch files.

    Thie GlitchFile interface is a low-level numpy-based representation of
    the glitch files. It allows reading subsets of the data directly from file,
    where the subsets are specified as time intervals.

    The purpose is for use in chunked processing of glitch data. In particular,
    the methods provided by GlitchFile are suitable for usage together with
    interpolation functions in sigpro.chunked_splines module.
    """

    @property
    @abstractmethod
    def format_version(self) -> Version:
        """Version number of the file format"""

    @property
    @abstractmethod
    def start_time(self) -> float:
        """Start time of available data [s]"""

    @property
    @abstractmethod
    def end_time(self) -> float:
        """End time of available data [s]"""

    @abstractmethod
    def has_readout_sci_carrier(self, mosa: MosaID) -> bool:
        """Whether the file has readout_sci_carrier datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_sci_carrier(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_sci_carrier glitch data covering a given time interval

        If the dataset is unavailable, an exception is raised.

        The data to be read is selected using a time interval, including the minimum
        range of samples such that the time interval is fully covered.
        One can optionally ask to include additional data points left and right of the
        specified interval. The margin size is specified in terms of the number of samples.

        If the requested time interval (not including the margins) has no overlap with
        the available data, None is returned.

        If the requested time interval has some overlap, at least the available data
        points are returned. In addition, as many of the margin points as available
        are also included. If the total number of available points is less than the
        margin size, an exception is raised.


        Arguments:
            tbegin: Start of interval to be covered [s]
            tend: End of interval to be covered [s]
            mosa: For which link to obtain response
            margin_points: How many additional margin points to provide

        Returns:
            Time series that covers entire requested interval or None
        """

    @abstractmethod
    def has_readout_sci_usbs(self, mosa: MosaID) -> bool:
        """Whether the file has readout_sci_usbs datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_sci_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_sci_usbs glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_readout_tmi_carriers(self, mosa: MosaID) -> bool:
        """Whether the file has readout_tmi_carriers datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_tmi_carriers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_tmi_carriers glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_readout_tmi_usbs(self, mosa: MosaID) -> bool:
        """Whether the file has readout_tmi_usbs  datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_tmi_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_tmi_usbs glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_readout_ref_carriers(self, mosa: MosaID) -> bool:
        """Whether the file has readout_ref_carriers  datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_ref_carriers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_ref_carriers glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_readout_ref_usbs(self, mosa: MosaID) -> bool:
        """Whether the file has readout_ref_usbs datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_readout_ref_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of readout_ref_usbs glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_test_mass(self, mosa: MosaID) -> bool:
        """Whether the file has test mass (tm) datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_test_mass(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of test mass (tm) glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """

    @abstractmethod
    def has_lasers(self, mosa: MosaID) -> bool:
        """Whether the file has lasers datasets for given MOSA

        Arguments:
            mosa: which MOSA dataset to query
        """

    @abstractmethod
    def load_segment_lasers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load a segment of lasers glitch data covering a given time interval

        Arguments and behavior are as described for load_segment_readout_sci_carrier.
        """


class GlitchFileV14(GlitchFile):
    """Implements GlitchFile interface for file format versions 1.4"""

    def _dataset_mosa_name(self, name: str, mosa: MosaID) -> str:
        return f"{name}_{mosa.value}"

    def _has_datasets(self, name: str, mosa: MosaID) -> bool:
        return self._dataset_mosa_name(name, mosa) in self._h5.file

    def _load_dataset(self, i0: int, i1: int, dataset: str, mosa: MosaID) -> np.ndarray:
        """Load range of dataset for one MOSA"""
        if not self._has_datasets(dataset, mosa):
            msg = f"GlitchFileV14: dataset {dataset} for MOSA {mosa.value} not present"
            raise RuntimeError(msg)
        dsname = self._dataset_mosa_name(dataset, mosa)
        return self._h5.file[dsname][i0:i1]

    def _load_segment_dataset(
        self, name: str, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """Load segment of a dataset covering time interval plus margin points"""

        if tbegin > tend:
            msg = f"GlitchFileV14: invalid time interval ({tbegin},{tend}) requested"
            raise RuntimeError(msg)
        if margin_points < 0:
            msg = f"GlitchFileV14: invalid number of margin points ({margin_points}) requested"
            raise RuntimeError(msg)

        ibegin = int(np.floor((tbegin - self._t0) / self._dt))
        iend = int(np.ceil((tend - self._t0) / self._dt))

        if (iend < 0) or (ibegin >= self._size):
            return None

        k0 = max(0, ibegin - margin_points)
        k1 = min(self._size, iend + margin_points + 1)

        if k1 - k0 < margin_points:
            msg = f"GlitchFileV14: data too short ({self._size}) for requested margin size ({margin_points})"
            raise RuntimeError(msg)

        times = self._t0 + np.arange(k0, k1) * self._dt
        data = self._load_dataset(k0, k1, name, mosa)

        return TimeSeriesNumpy(make_numpy_array_1d(times), make_numpy_array_1d(data))

    def __init__(self, path: str | pathlib.Path, chunk_size=None):
        self._h5: Final = HDF5Source(path, chunk_size)
        self._version: Final = Version(self._h5.file.attrs["version"])

        self._size = int(self._h5.file.attrs["size"])
        self._dt = float(self._h5.file.attrs["dt"])
        self._t0 = float(self._h5.file.attrs["t0"])

    @property
    def format_version(self) -> Version:
        """Version number of the file format"""
        return self._version

    @property
    def start_time(self) -> float:
        """See GlitchFile interface description"""
        return self._t0

    @property
    def end_time(self) -> float:
        """See GlitchFile interface description"""
        return self._t0 + (self._size - 1) * self._dt

    def has_readout_sci_carrier(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("readout_isi_carrier", mosa)

    def load_segment_readout_sci_carrier(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_isi_carrier", tbegin, tend, mosa, margin_points
        )

    def has_readout_sci_usbs(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("readout_isi_usb", mosa)

    def load_segment_readout_sci_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_isi_usb", tbegin, tend, mosa, margin_points
        )

    def has_readout_tmi_carriers(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("readout_tmi_carrier", mosa)

    def load_segment_readout_tmi_carriers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_tmi_carrier", tbegin, tend, mosa, margin_points
        )

    def has_readout_tmi_usbs(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("readout_tmi_usb", mosa)

    def load_segment_readout_tmi_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_tmi_usb", tbegin, tend, mosa, margin_points
        )

    def has_readout_ref_carriers(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("readout_rfi_carrier", mosa)

    def load_segment_readout_ref_carriers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_rfi_carrier", tbegin, tend, mosa, margin_points
        )

    def has_readout_ref_usbs(self, mosa: MosaID) -> bool:
        """Whether the file has readout_ref_usbs datasets"""
        return self._has_datasets("readout_rfi_usb", mosa)

    def load_segment_readout_ref_usbs(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset(
            "readout_rfi_usb", tbegin, tend, mosa, margin_points
        )

    def has_test_mass(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("tm", mosa)

    def load_segment_test_mass(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset("tm", tbegin, tend, mosa, margin_points)

    def has_lasers(self, mosa: MosaID) -> bool:
        """See GlitchFile interface description"""
        return self._has_datasets("laser", mosa)

    def load_segment_lasers(
        self, tbegin: float, tend: float, mosa: MosaID, margin_points: int
    ) -> TimeSeriesNumpy | None:
        """See GlitchFile interface description"""
        return self._load_segment_dataset("laser", tbegin, tend, mosa, margin_points)


def glitch_file(path: str | pathlib.Path) -> GlitchFile:
    """Open Glitch file of any supported version

    Arguments:
        path: Path of the file

    Returns:
        Instance providing GlitchFile interface
    """
    with h5py.File(path, "r") as gwf:
        version = Version(gwf.attrs["version"])
        if version >= Version("1.4.dev"):
            return GlitchFileV14(path)
        if version >= Version("1.3.dev"):
            msg = "Glitch file format < 1.4 currently not supported"
            raise RuntimeError(msg)
        if version >= Version("1.0"):
            msg = "Glitch file format < 1.4 currently not supported"
            raise RuntimeError(msg)

    msg = f"unsupported GW file version '{version}'"
    raise RuntimeError(msg)
