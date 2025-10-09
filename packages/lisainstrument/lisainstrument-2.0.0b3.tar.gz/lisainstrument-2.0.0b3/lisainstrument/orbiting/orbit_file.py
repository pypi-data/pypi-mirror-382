"""Interface and implementations for reading orbit files

There is an abstract interface class OrbitFile to extract the information needed
in the Instrument class from orbit files of any format. For each orbit file
format, there is an implementation, OrbitFileV1 and OrbitFileV2. Those classes
return orbit data as time series each represented by a TimeSeriesNumpy instance.
The function orbit_file() opens an orbit file of any supported format, returning
the generic OrbitFile interface.

"""

import pathlib
from abc import ABC, abstractmethod

import h5py
import numpy as np
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.sigpro.types_numpy import TimeSeriesNumpy, make_numpy_array_1d


class OrbitFile(ABC):
    """Abstract base for reading orbit files"""

    def __init__(self, path: str | pathlib.Path) -> None:
        """Open HDF5 file with given path"""
        self._h5_: None | h5py.File = None
        self._path = str(path)
        self._open()

    def _open(self) -> None:
        """Open the file for reading and get version"""
        self._h5_ = h5py.File(self._path, "r")
        self._version = Version(self._h5_.attrs["version"])

    def __setstate__(self, state: str) -> None:
        """Restore from unpickled state

        This just opens the same file, assuming the file never changes.
        """
        self._path = state
        self._open()

    def __getstate__(self) -> str:
        """Compute state needed for pickling.

        This is just the file path,  assuming the file never changes.
        """
        return self._path

    @property
    def _h5(self) -> h5py.File:
        """Provide the HDF5 file for implementations of the interface

        Makes sure file is not used after closing.
        """
        if self._h5_ is None:
            msg = "Attempt to use already closed orbit file"
            raise RuntimeError(msg)
        return self._h5_

    def close(self) -> None:
        """Close file"""
        if self._h5_ is not None:
            self._h5_.close()
            self._h5_ = None

    def __enter__(self):
        """Enter context"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        self.close()

    def __del__(self):
        """Close file when instance is garbage collected"""
        self.close()

    @property
    def format_version(self) -> Version:
        """Version number of the file format"""
        return self._version

    @property
    @abstractmethod
    def t0_type_tcbltt(self) -> float:
        """Orbit t0 for TCB/LTT dataset"""

    @property
    @abstractmethod
    def t0_type_tpsppr(self) -> float:
        """Orbit t0 for TPS/PPR dataset"""

    @abstractmethod
    def ppr0_type_tcbltt(self, mosa: MosaID) -> float:
        """PPR for given MOSA at time t0 for TCB/LTT dataset"""

    @abstractmethod
    def ppr0_type_tpsppr(self, mosa: MosaID) -> float:
        """PPR for given MOSA at time t0 for TPS/PPR dataset"""

    @abstractmethod
    def d_ppr_type_tcbltt(self, mosa: MosaID) -> TimeSeriesNumpy:
        """Time deriative of PPR for given MOSA for TCB/LTT dataset"""

    @abstractmethod
    def d_ppr_type_tpsppr(self, mosa: MosaID) -> TimeSeriesNumpy:
        """Time deriative of PPR for given MOSA for TPS/PPR dataset"""

    @abstractmethod
    def tps_wrt_tcb_type_tpsppr(self, sc: SatID) -> TimeSeriesNumpy:
        """TPS w.r.t. PPR for given spacecraft"""


class OrbitFileV1(OrbitFile):
    """Implementation of OrbitFile for orbit files with format version 1.*"""

    @property
    def t0_type_tcbltt(self) -> float:
        """See OrbitFile interface description"""
        return self._h5["tcb"]["t"][0]

    @property
    def t0_type_tpsppr(self) -> float:
        """See OrbitFile interface description"""
        return self._h5["tps"]["tau"][0]

    def ppr0_type_tcbltt(self, mosa: MosaID) -> float:
        """See OrbitFile interface description"""
        return self._h5[f"tcb/l_{mosa.value}"]["tt"][0]

    def ppr0_type_tpsppr(self, mosa: MosaID) -> float:
        """See OrbitFile interface description"""
        return self._h5[f"tps/l_{mosa.value}"]["ppr"][0]

    def d_ppr_type_tcbltt(self, mosa: MosaID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        times = self._h5["tcb"]["t"][:]
        values = self._h5[f"tcb/l_{mosa.value}"]["d_tt"][:]
        return TimeSeriesNumpy(times, values)

    def d_ppr_type_tpsppr(self, mosa: MosaID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        times = self._h5["tps"]["tau"][:]
        values = self._h5[f"tps/l_{mosa.value}"]["d_ppr"][:]
        return TimeSeriesNumpy(times, values)

    def tps_wrt_tcb_type_tpsppr(self, sc: SatID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        times = self._h5["tcb"]["t"][:]
        values = self._h5[f"tcb/sc_{sc.value}"]["tau"][:]
        return TimeSeriesNumpy(times, values)


class OrbitFileV2(OrbitFile):
    """Implementation of OrbitFile for orbit files with format version 2.*"""

    def _open(self) -> None:
        super()._open()
        size = int(self._h5.attrs["size"])
        dt = float(self._h5.attrs["dt"])
        self._t0 = float(self._h5.attrs["t0"])
        self._times = self._t0 + np.arange(size) * dt

    @staticmethod
    def _link_index(mosa: MosaID) -> int:
        """Map lisainstrument.Instrument mosa names to indexing in orbit file"""
        link_index = {"12": 0, "23": 1, "31": 2, "13": 3, "32": 4, "21": 5}
        return link_index[mosa.value]

    @staticmethod
    def _sc_index(sc: SatID) -> int:
        """Map lisainstrument.Instrument spacecraft names to indexing in orbit file"""
        sc_index = {"1": 0, "2": 1, "3": 2}
        return sc_index[sc.value]

    def _make_ts(self, values: np.ndarray) -> TimeSeriesNumpy:
        """Combine data with timestamps ito time series"""
        return TimeSeriesNumpy(
            make_numpy_array_1d(self._times), make_numpy_array_1d(np.array(values))
        )

    @property
    def t0_type_tcbltt(self) -> float:
        """See OrbitFile interface description"""
        return self._t0

    @property
    def t0_type_tpsppr(self) -> float:
        """See OrbitFile interface description"""
        return self._t0

    def ppr0_type_tcbltt(self, mosa: MosaID) -> float:
        """See OrbitFile interface description"""
        return self._h5["tcb/ltt"][0, OrbitFileV2._link_index(mosa)]

    def ppr0_type_tpsppr(self, mosa: MosaID) -> float:
        """See OrbitFile interface description"""
        return self._h5["tps/ppr"][0, OrbitFileV2._link_index(mosa)]

    def d_ppr_type_tcbltt(self, mosa: MosaID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        values = self._h5["tcb/d_ltt"][:, OrbitFileV2._link_index(mosa)][:]
        return self._make_ts(values)

    def d_ppr_type_tpsppr(self, mosa: MosaID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        values = self._h5["tps/d_ppr"][:, OrbitFileV2._link_index(mosa)][:]
        return self._make_ts(values)

    def tps_wrt_tcb_type_tpsppr(self, sc: SatID) -> TimeSeriesNumpy:
        """See OrbitFile interface description"""
        values = self._h5["tcb/delta_tau"][:, self._sc_index(sc)][:]
        return self._make_ts(values)


OrbitFileV3 = OrbitFileV2


def orbit_file(path: str | pathlib.Path) -> OrbitFile:
    """Open generic orbit file

    Arguments:
        path: location of the orbit file

    Returns:
        Object implementing OrbitFile interface
    """
    with h5py.File(path, "r") as orbitf:
        version = Version(orbitf.attrs["version"])

    if version in SpecifierSet("== 1.*", True):
        return OrbitFileV1(path)
    if version in SpecifierSet("== 2.*", True):
        return OrbitFileV2(path)
    if version in SpecifierSet("== 3.*", True):
        return OrbitFileV3(path)

    msg = f"unsupported orbit file version '{version}'"
    raise RuntimeError(msg)
