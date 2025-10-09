"""This module provides a class for reading frequency plan file data.

The FreqPlanFile class represents a frequency plan file, allowing to load the
raw data (meaning not resampled) for a given locking configuration and MOSA.
"""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d


class FreqPlanFile:
    """Represents a frequency plan file, format version 1.1.*

    The interface allows loading of the sci and ref locking beatnotes and
    the sample times. To get the beatnotes, one has to provide the locking
    configuration and MOSA. The locking is currently specified via a string
    with possible values that are used in the file format. The MOSAs are
    specified using the MosaID enum class from orbiting.constellation_enums.

    Instances can be used as context manager. Further, there is experimental
    support for pickling/unpickling instances in a multiprocessing context.
    """

    def __init__(self, path: Path | str):
        """Constructor

        Arguments:
            path: The path of the frequency plan file
        """
        self._h5: h5py.File | None = None
        self._path = str(path)
        self._open()

    def _open(self) -> None:
        self._h5 = h5py.File(self._path, "r")

        self._version = Version(self._h5.attrs["version"])
        if self._version not in SpecifierSet("== 1.1.*", True):
            msg = f"unsupported frequency-plan file version '{self._version}'"
            raise RuntimeError(msg)

        self._dt = float(self._h5.attrs["dt"])
        if self._dt <= 0:
            msg = f"FreqPlanFile: invalid sample period, dt = {self._dt}"
            raise RuntimeError(msg)

        size = int(self._h5.attrs["size"])
        if size <= 0:
            msg = f"FreqPlanFile: invalid size attribute {size=}"
            raise RuntimeError(msg)

        self._times = np.arange(size) * self._dt

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
    def _open_h5(self) -> h5py.File:
        """Returns the open hdf5 file or raises error if closed already."""
        if self._h5 is None:
            msg = "FreqPlanFile: usage after file was already closed"
            raise RuntimeError(msg)
        return self._h5

    def close(self) -> None:
        """Close file"""
        if self._h5 is not None:
            self._h5.close()
            self._h5 = None

    def __del__(self):
        """Destructor closes file"""
        self.close()

    def __enter__(self) -> "FreqPlanFile":
        """Use this instance as context manager"""
        return self

    def __exit__(self, _type, _value, _traceback):
        """Close file at context exit"""
        self.close()

    @property
    def time_samples(self) -> NumpyArray1D:
        """Sample times as given in file without additional offsets."""
        return make_numpy_array_1d(self._times)

    @property
    def sample_period(self) -> float:
        """Constant sampling period used in the file [s]"""
        return self._dt

    @property
    def sample_rate(self) -> float:
        """Constant sample rate used in the file [Hz]"""
        return 1.0 / self.sample_period

    def _validated(self, data: np.ndarray, name: str) -> NumpyArray1D:
        """Ensure that datasets are 1D and have same size as time samples"""
        d1d = make_numpy_array_1d(data)
        ex_sh = (len(self._times),)
        if tuple(data.shape) != ex_sh:
            msg = (
                f"FreqPlanFile: inconsistent dataset size "
                f"{data.shape} for {name}, expected {ex_sh}"
            )
            raise RuntimeError(msg)
        return d1d

    def load_sci_hz(self, lock_config: str, mosa: MosaID) -> NumpyArray1D:
        """Load ISI beatnotes

        Arguments:
            lock_config: Name of locking configuration
            mosa: Which MOSA to get data for

        Returns:
            beatnote samples [Hz] as 1D numpy array
        """
        flock = self._open_h5[lock_config]
        sci_name = f"isi_{mosa.value}"
        sci_ds_mhz = np.array(flock[sci_name], dtype=np.float64)
        sci_ds_hz = sci_ds_mhz * 1e6

        return self._validated(sci_ds_hz, sci_name)

    def load_ref_hz(self, lock_config: str, mosa: MosaID) -> NumpyArray1D:
        """Load RFI beatnotes

        Although the data is only stored for left MOSAs, this method
        can be called for all MOSAs. For the case of a right MOSA,
        the correct result is obtained from the left MOSA on the same SC,
        which differs only by the sign.

        Arguments:
            lock_config: Name of locking configuration
            mosa: Which MOSA to get data for

        Returns:
            beatnote samples [Hz] as 1D numpy array
        """

        flock = self._open_h5[lock_config]
        left_mosa = mosa.sat.left_mosa
        ref_name = f"rfi_{left_mosa.value}"

        sign = +1 if left_mosa == mosa else -1

        ref_ds_mhz = sign * np.array(flock[ref_name], dtype=np.float64)
        ref_hz = ref_ds_mhz * 1e6

        return self._validated(ref_hz, ref_name)

    @property
    def format_version(self) -> Version:
        """The version of the file format"""
        return self._version
