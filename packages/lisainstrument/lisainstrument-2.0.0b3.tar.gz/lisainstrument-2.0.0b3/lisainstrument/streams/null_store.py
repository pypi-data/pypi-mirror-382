"""Function for mock DataStorage that discards all data immediately

This is for testing and debugging.
"""

from typing import Final

import numpy as np

from lisainstrument.streams.segments import ArrayTarget
from lisainstrument.streams.store import DatasetIdentifier, DataStorage


class DatasetDiscarder(ArrayTarget):  # pylint: disable = too-few-public-methods
    """Mock target for data transfer that just discards the data"""

    def __setitem__(self, rg: slice, data: np.ndarray):
        """Write portion of data to oblivion"""


class DataStorageDiscard(DataStorage):  # pylint: disable = too-few-public-methods
    """Provide DataStorage based on immediate discarding of the data"""

    def __init__(self, identifiers: set[DatasetIdentifier]):
        self._identifiers: Final = set(identifiers)
        self._store: set[DatasetIdentifier] = set()

    @property
    def valid_identifiers(self) -> set[DatasetIdentifier]:
        """Set with identifiers of all required datasets"""
        return self._identifiers.copy()

    def _check_ident(self, ident: DatasetIdentifier) -> None:
        """Ensure that identifier can be added"""
        if not ident in self.valid_identifiers:
            msg = f"DataStorageDiscard: attempt to create dataset with invalid indentifier {ident}"
            raise RuntimeError(msg)
        if ident in self._store:
            msg = f"DataStorageDiscard: attempt to create already existing dataset {ident}"
            raise RuntimeError(msg)
        self._store.add(ident)

    def dataset(
        self, ident: DatasetIdentifier, _istart: int, _istop: int, _dtype: np.dtype
    ) -> ArrayTarget:
        """Create a target for a dataset identifier.

        See DataStorage for general description.
        """

        self._check_ident(ident)

        return DatasetDiscarder()

    def dataset_const(
        self,
        ident: DatasetIdentifier,
        _istart: int,
        _istop: int,
        _const: int | float | complex,
    ) -> None:
        """Create a dataset that is constant

        See DataStorage for general description.
        """
        self._check_ident(ident)
