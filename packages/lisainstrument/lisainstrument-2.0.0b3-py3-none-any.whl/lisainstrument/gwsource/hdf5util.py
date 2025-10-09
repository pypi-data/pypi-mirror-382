"""Wrapper for H5 file objects with adjusted internal chunk size and serialization support

For use in multiprocessing scenarios, we include an experimental solution that allows
the wrapper to be pickled, which normally does not work with h5py file objects.
"""

import pathlib

import h5py
import numpy as np


class HDF5Source:
    """Wrap HDF5 file for reading with adjusted cache size

    Provides read-only hdf5 file with option adjusting cache size.
    For files intended to be read sequentially in overlapping chunks, the internal
    dataset cache size should be adjusted to fit several chunks

    The file is guaranteed to be open while instance exists, file is closed
    automatically when instance is garbage collected.
    """

    def __init__(
        self,
        path: str | pathlib.Path,
        chunk_size: int | None = None,
        num_chunks: int = 4,
    ):
        """Constructor

        Arguments:
            path: Path of the hdf5 file
            chunk_size: maximum length of dataset segments to be read in one go
            num_chunks: number of segments per dataset to fit in cache

        Returns:
            Opened file object with adjusted internal cache.
        """
        rdcc_nbytes_hdf5_default = 1024**2
        cache_length_limit = 10000000
        rdcc_nbytes = rdcc_nbytes_hdf5_default
        if chunk_size is not None:
            cache_length = min(int(num_chunks * chunk_size), cache_length_limit)
            rdcc_nbytes = max(rdcc_nbytes, cache_length * np.float64().itemsize)

        self._file: None | h5py.File
        self._state: tuple[str, int] = (str(path), rdcc_nbytes)
        self._open()

    def _open(self) -> None:
        path, rdcc_nbytes = self._state
        self._file = h5py.File(path, "r", rdcc_nbytes=rdcc_nbytes)

    def __setstate__(self, state: tuple[str, int]) -> None:
        """Restore from unpickled state

        This just opens the same file, assuming the file never changes.
        """
        self._state = state
        self._open()

    def __getstate__(self) -> tuple[str, int]:
        """Compute state needed for pickling.

        This is just the file path,  assuming the file never changes.
        """
        return self._state

    @property
    def file(self) -> h5py.File:
        """Provide the open HDF5 file"""
        return self._file

    def __del__(self):
        """Close file when instance is garbage collected"""
        if self._file is not None:
            self._file.close()
            self._file = None
