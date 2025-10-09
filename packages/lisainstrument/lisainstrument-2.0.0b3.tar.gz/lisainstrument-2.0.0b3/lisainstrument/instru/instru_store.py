"""Adapters connecting Instrument-specific data and more generic DataSource

SimResultsNumpyCore and SimResultsNumpyFull collect simulation results stored in numpy
arrays for simulations that fit into memory. They contain exactly the same data that
is also written to HDF5 files when exporting the simulation to HDF5 (Core and Full
correspond to the keep_all=False and True variants). Those classes take over the
role of the Instrument class in older versions, where the data could be accessed
by scripts via instance attributes. Those attributes no longer exist since the
switch to chunked processing data flow. To obtain SimResultsNumpyCore/Full instances,
the Instrument class has methods export_numpy_core and export_numpy_full.

Per-MOSA data, per-spacecraft data, and meta-data is kept in separate substructures
mosa_data, sat_data, and meta_data, respectively. Per-MOSA/SC data is kept in
ordinary Python dictionaries keyed by the MOSA or spacecraft names.
Data is organized into groups represented by a dataclasses SimCoreDatasetsMOSA,
SimFullDatasetsMOSA, SimCoreDatasetsSat, SimFullDatasetsSat, and SimMetaData.
Those are used as members in SimResultsNumpy*. In addition, the index range of
each dataset is available under moa_ranges and sat_ranges attributes. The index
ranges depend only on the quantity but not the MOSA/SC.

The store_instru_hdf5 function is used to create HDF5 files with simulation results.
It is not intended for direct use, however. Users should use Instrument.export_hdf5
to evaluate simulation directly to disk, or SimResultsNumpy*.export_hdf5 to export
data already evaluated to memory (using Instrument.export_hdf5 in that case should be
avoided since all computations would be repeated).

"""

import importlib
import json
import pathlib
from dataclasses import dataclass, field, fields, make_dataclass
from enum import Enum
from typing import Any, Final, Generic, Type, TypeAlias, TypeVar

import numpy as np

from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.streams import (
    DatasetIdentifier,
    SchedulerConfigSerial,
    SchedulerConfigTypes,
    StreamBundle,
    ValidMetaDataTypes,
    array_dict_as_stream_bundle,
    store_bundle_hdf5,
)
from lisainstrument.streams.hdf5_store import H5AttrValidTypes

SamplesType: TypeAlias = np.ndarray
SamplesMosasType: TypeAlias = dict[str, SamplesType]
SamplesSatsType: TypeAlias = dict[str, SamplesType]


def _dataclass_attr_set(cls: type) -> frozenset[str]:
    """Return the set of all field names of a dataclass"""
    return frozenset((f.name for f in fields(cls)))


def _make_range_dataclass(name: str, cls: type) -> type:
    """Transform dataclass to store index ranges insteas datasets"""
    cfields = [(f.name, tuple[int, int]) for f in fields(cls)]
    return make_dataclass(name, cfields)


def _asdict_shallow(obj) -> dict[str, Any]:
    """Convert data class instance to dictionary

    This differs from dataclasses.asdict, which makes deep copies of the data
    """
    return {f.name: getattr(obj, f.name) for f in fields(obj)}


class IdxSpace(Enum):
    """Categories of index spaces belonging to the simulator datasets

    REGULAR: Data sampled at SimMetaData.dt starting at SimMetaData.t0
    PHYSICS: Data sampled at SimMetaData.physics_dt starting at SimMetaData.t0
    PHYSICS_EXT: Like PHYSICS but range extended to include TELEMETRY range
    TELEMETRY: Sampled at SimMetaData.telemetry_dt starting at SimMetaData.telemetry_t0.
    """

    REGULAR = 1
    PHYSICS = 2
    PHYSICS_EXT = 3
    TELEMETRY = 4


@dataclass(frozen=True)
class DataCategories:
    """Categorization of datasets"""

    actual: bool
    basic: bool
    idxspace: IdxSpace


def _dataset(actual: bool, basic: bool, ispace: IdxSpace) -> Any:
    """Dataclass field with custom metadata for dataset properties"""
    md = {"actual": actual, "basic": basic, "ispace": ispace}
    return field(metadata=md)  # pylint: disable = invalid-field-call


def _dataclass_meta_dict(cls: type) -> dict[str, DataCategories]:
    """Extract custom metadata from dataclass attributes"""
    return {
        f.name: DataCategories(
            f.metadata["actual"], f.metadata["basic"], f.metadata["ispace"]
        )
        for f in fields(cls)
    }


def make_dataset_id(actual: bool, name: str, idx: str) -> tuple[str, ...]:
    """Defines DatasetID for instrument data

    Arguments:
        actual: True for data that will be available in reality
        name: dataset name
        idx: MOSA or SC name

    Returns:
        DatasetID to be used fro instrument data
    """
    dsid = [] if actual else ["debug"]
    dsid = dsid + [name, idx]
    return tuple(dsid)


@dataclass(kw_only=True, frozen=True)
class SimCoreDatasetsMOSA:
    """Data class to store core set of per-MOSA simulation results.

    This stores the MOSA-specific time series that are saved to the keep_all=False
    version of the instrument HDF5 files (internally, the list of attributes of this class
    now actually defines the set written to file).

    Data is stored as dictionaries mapping MOSA names to numpy arrays. Arrays are allowed
    to be scalar, which is to be interpreted as constant time series.
    """

    # All sampled at dt
    sci_carrier_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    sci_carrier_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    sci_usb_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    sci_usb_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    sci_dws_phis: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    sci_dws_etas: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    tmi_carrier_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    tmi_carrier_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    tmi_usb_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    tmi_usb_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    ref_carrier_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    ref_carrier_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    ref_usb_offsets: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    ref_usb_fluctuations: SamplesMosasType = _dataset(False, True, IdxSpace.REGULAR)
    sci_carriers: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    sci_usbs: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    tmi_carriers: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    tmi_usbs: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    ref_carriers: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    ref_usbs: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)
    mprs: SamplesMosasType = _dataset(True, True, IdxSpace.REGULAR)

    @classmethod
    def dataset_names(cls) -> frozenset[str]:
        """Set of dataset names available in this class"""
        return _dataclass_attr_set(cls)

    @classmethod
    def dataset_metadata(cls) -> dict[str, DataCategories]:
        """Get dictionary with dataset properties for each dataset name"""
        return _dataclass_meta_dict(cls)

    @classmethod
    def index_range_class(cls) -> type:
        """Create a dataclass for storing index ranges for each dataset"""
        return _make_range_dataclass("SimCoreRangesMOSA", cls)

    def asdict(self) -> dict[str, Any]:
        """Export as dictionary (data not copied but referenced)"""
        return _asdict_shallow(self)

    @property
    def mosa_names(self) -> frozenset[str]:
        """Set of MOSA names used for the dictionary keys"""
        return frozenset((m.value for m in MosaID))


@dataclass(kw_only=True, frozen=True)
class SimMoreDatasetsMOSA:
    """Data class to store per-MOSA simulation results not in the core set

    This stores the MOSA-specific time series that are saved to the keep_all=True
    version of the instrument HDF5 files, but that are not already part of SimCoreDatasetsMOSA

    There are a few datasets that were not part of the original file format:
    mosa_jitter_etas, mosa_jitter_xs, dws_phi_noises, and dws_eta_noises.
    """

    pprs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    d_pprs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    gws: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    glitch_tms: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    glitch_lasers: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tdir_modulations_tseries: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    laser_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    modulation_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    backlink_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    testmass_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    ranging_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_sci_carrier_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_sci_usb_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_tmi_carrier_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_tmi_usb_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_ref_carrier_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    oms_ref_usb_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    mosa_jitter_phis: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    # This was not part of the files before
    mosa_jitter_etas: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    mosa_jitter_xs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    dws_phi_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    dws_eta_noises: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    fplan_ts: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    #
    mosa_total_jitter_phis: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    mosa_total_jitter_etas: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_carrier_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_usb_fluctuations: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_ttls: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    distant_ttls: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    distant_carrier_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    distant_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    distant_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    distant_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    adjacent_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_sci_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_sci_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    distant_sci_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    distant_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    distant_sci_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    distant_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_sci_carrier_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_sci_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_sci_dws_phis: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_sci_dws_etas: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_tmi_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_tmi_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_tmi_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_tmi_usb_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_tmi_carrier_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_tmi_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_ref_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    local_ref_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    local_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_ref_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_ref_usb_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    adjacent_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_ref_carrier_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    tps_ref_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_sci_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_sci_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_sci_dws_phis: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_sci_dws_etas: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_tmi_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_tmi_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_ref_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_ref_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_sci_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_sci_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    electro_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_tmi_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_tmi_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    electro_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_ref_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    electro_ref_usb_offsets: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    electro_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_sci_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_sci_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_sci_usb_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_sci_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_sci_dws_phis: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    filtered_sci_dws_etas: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    filtered_tmi_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_tmi_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_tmi_usb_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_tmi_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_ref_carrier_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_ref_carrier_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_ref_usb_offsets: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    filtered_ref_usb_fluctuations: SamplesMosasType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    scet_mprs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    mprs_unambiguous: SamplesMosasType = _dataset(False, False, IdxSpace.REGULAR)
    tps_mprs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    filtered_mprs: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_wrt_tps_distant: SamplesMosasType = _dataset(False, False, IdxSpace.PHYSICS)


@dataclass(kw_only=True, frozen=True)
class SimCoreDatasetsSat:
    """Data class to store core set of per-spacecraft simulation results

    This stores the spacecraft-specific time series that are saved to the keep_all=False
    version of the instrument HDF5 files, which is currently just moc_time_correlations.
    See also SimCoreDatasetsSat
    """

    moc_time_correlations: SamplesSatsType = _dataset(True, True, IdxSpace.TELEMETRY)

    @classmethod
    def dataset_names(cls) -> frozenset[str]:
        """Set of dataset names available in this class"""
        return _dataclass_attr_set(cls)

    @classmethod
    def dataset_metadata(cls) -> dict[str, DataCategories]:
        """Get dictionary with dataset properties for each dataset name"""
        return _dataclass_meta_dict(cls)

    @classmethod
    def index_range_class(cls) -> type:
        """Create a dataclass for storing index ranges for each dataset"""
        return _make_range_dataclass("SimCoreRangesSat", cls)

    def asdict(self) -> dict[str, Any]:
        """Export as dictionary (data not copied but referenced)"""
        return _asdict_shallow(self)

    @property
    def sat_names(self) -> frozenset[str]:
        """Set of spacecraft names used for the dictionary keys"""
        return frozenset((s.value for s in SatID))


@dataclass(kw_only=True, frozen=True)
class SimMoreDatasetsSat:
    """Data class to store per-spacecraft simulation results not in the core set

    This stores the spacecraft-specific time series that are saved to the keep_all=True
    version of the instrument HDF5 files, but that are not already part of SimCoreDatasetsSat.
    """

    clock_noise_offsets: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    clock_noise_fluctuations: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    clock_noise_fluctuations_withinitial: SamplesSatsType = _dataset(
        False, False, IdxSpace.PHYSICS_EXT
    )
    integrated_clock_noise_fluctuations_withinitial: SamplesSatsType = _dataset(
        False, False, IdxSpace.PHYSICS_EXT
    )
    integrated_clock_noise_fluctuations: SamplesSatsType = _dataset(
        False, False, IdxSpace.PHYSICS
    )
    sc_jitter_phis: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    sc_jitter_etas: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    sc_jitter_thetas: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_wrt_scet: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    tps_wrt_tcb: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    moc_time_correlation_noises: SamplesSatsType = _dataset(
        False, False, IdxSpace.TELEMETRY
    )
    scet_wrt_tps_local: SamplesSatsType = _dataset(False, False, IdxSpace.PHYSICS)
    scet_wrt_tcb_withinitial: SamplesSatsType = _dataset(
        False, False, IdxSpace.PHYSICS_EXT
    )


@dataclass(kw_only=True, frozen=True)
class SimFullDatasetsMOSA(SimCoreDatasetsMOSA, SimMoreDatasetsMOSA):
    """Data class to store full set of per-MOSA simulation results"""

    @classmethod
    def dataset_names(cls) -> frozenset[str]:
        """Set of dataset names available in this class"""
        return _dataclass_attr_set(cls)

    @classmethod
    def dataset_metadata(cls) -> dict[str, DataCategories]:
        """Get dictionary with dataset properties for each dataset name"""
        return _dataclass_meta_dict(cls)

    @classmethod
    def index_range_class(cls) -> type:
        """Create a dataclass for storing index ranges for each dataset"""
        return _make_range_dataclass("SimFullRangesMOSA", cls)

    def asdict(self) -> dict[str, Any]:
        """Export as dictionary (data not copied but referenced)"""
        return _asdict_shallow(self)


@dataclass(kw_only=True, frozen=True)
class SimFullDatasetsSat(SimCoreDatasetsSat, SimMoreDatasetsSat):
    """Data class to store full set of per-spacecraft simulation results"""

    @classmethod
    def dataset_names(cls) -> frozenset[str]:
        """Set of dataset names available in this class"""
        return _dataclass_attr_set(cls)

    @classmethod
    def dataset_metadata(cls) -> dict[str, DataCategories]:
        """Get dictionary with dataset properties for each dataset name"""
        return _dataclass_meta_dict(cls)

    @classmethod
    def index_range_class(cls) -> type:
        """Create a dataclass for storing index ranges for each dataset"""
        return _make_range_dataclass("SimFullRangesSat", cls)

    def asdict(self) -> dict[str, Any]:
        """Export as dictionary (data not copied but referenced)"""
        return _asdict_shallow(self)


@dataclass(kw_only=True, frozen=True)
class SimMetaData:
    """Data class to store simulation metadata

    This contains the metadata of the simulation from the Instrument class that also gets
    stored to HDF5 files (this class now defines what gets stored into files). There are some
    differences to the corresponding attributes of the Instrument class for historic reasons.
    SimMetaData only contains plain and short data parameters while some of the Instrument
    "metadata" attributes contain time series or functions. If this is the case, the
    corresponding attribute in SimMetaData contains None instead.

    This affects fplan and tdir_modulations attributes. Originally, Instrument.ranging_biases
    could also contain time series, but this is now forbidden.
    In the original set of metadata saved to file, mosa_jitter_eta_asds was missing, but it
    is now part of SimMetaData and saved to file.

    SimMetaData instance are available as attribute meta_data of the SimResultsNumpyCore/Full
    dataclasses that are created by Instrument.export_numpy_full/core. If only the metadata
    is needed, one can also use Instrument.export_metadata.

    The data SimMetaData does not equal the data stored to HDF5 attributes in the hdf5 files,
    which is further mangled to the valid data types. Most notably, SimMetaData contains
    dictionaries which are written as strings in the file attributres.
    See metadata_value_as_hdf5_type for details of this mapping.
    """

    seed: int
    dt: float
    t0: float
    size: int
    fs: float
    duration: float
    initial_telemetry_size: int
    telemetry_downsampling: int
    telemetry_fs: float
    telemetry_dt: float
    telemetry_size: int
    telemetry_t0: float
    physics_upsampling: int
    physics_size: int
    physics_dt: float
    physics_fs: float
    aafilter_coeffs: list[float] | None
    aafilter_group_delay: float
    central_freq: float
    lock_config: str | None
    lock: dict[str, str]
    fplan_file: str | None
    # This used to potentially contain time series. Having time series in metadata
    # was always a problematic choice but after the switch to chunked processing it becomes
    # completely unfeasible. As a transitional solution, any time series are replaced by None.
    fplan: dict[str, float | None] | None
    #
    laser_asds: dict[str, float]
    modulation_asds: dict[str, float]
    modulation_freqs: dict[str, float]
    # Note this is None or a dict of lambda functions in Instrument class
    # Was saved as str in file, we also store it as str in this metadata data class
    tdir_modulations: str
    #
    clock_asds: dict[str, float]
    clock_offsets: dict[str, float]
    clock_freqoffsets: dict[str, float]
    clock_freqlindrifts: dict[str, float]
    clock_freqquaddrifts: dict[str, float]
    clockinv_tolerance: float
    clockinv_maxiter: int
    # This was allowed to be time series, but now only floats
    ranging_biases: dict[str, float]
    #
    ranging_asds: dict[str, float]
    prn_ambiguity: float | None
    backlink_asds: dict[str, float]
    backlink_fknees: dict[str, float]
    testmass_asds: dict[str, float]
    testmass_fknees: dict[str, float]
    testmass_fbreak: dict[str, float]
    testmass_frelax: dict[str, float]
    testmass_shape: str
    oms_sci_carrier_asds: dict[str, float]
    oms_sci_usb_asds: dict[str, float]
    oms_tmi_carrier_asds: dict[str, float]
    oms_tmi_usb_asds: dict[str, float]
    oms_ref_carrier_asds: dict[str, float]
    oms_ref_usb_asds: dict[str, float]
    oms_fknees: dict[str, float]
    ttl_coeffs_local_phis: dict[str, float]
    ttl_coeffs_distant_phis: dict[str, float]
    ttl_coeffs_local_etas: dict[str, float]
    ttl_coeffs_distant_etas: dict[str, float]
    sc_jitter_phi_asds: dict[str, float]
    sc_jitter_eta_asds: dict[str, float]
    sc_jitter_theta_asds: dict[str, float]
    mosa_jitter_x_asds: dict[str, float]
    mosa_jitter_phi_asds: dict[str, float]
    mosa_jitter_eta_asds: dict[str, float]
    dws_asds: dict[str, float]
    # This was not saved originally
    laser_shape: str
    moc_time_correlation_asds: dict[str, float]
    sc_jitter_phi_fknees: dict[str, float]
    sc_jitter_eta_fknees: dict[str, float]
    sc_jitter_theta_fknees: dict[str, float]
    mosa_jitter_phi_fknees: dict[str, float]
    mosa_jitter_eta_fknees: dict[str, float]
    delay_isc_min: float
    delay_isc_max: float
    delay_clock_max: float
    #
    mosa_angles: dict[str, float]
    orbit_file: str | None
    orbit_dataset: str | None
    orbit_t0: float
    gw_file: str | None
    gw_group: str | None
    glitch_file: str | None
    interpolation_order: int
    electro_delays_scis: dict[str, float]
    electro_delays_tmis: dict[str, float]
    electro_delays_refs: dict[str, float]

    @classmethod
    def dataset_names(cls) -> frozenset[str]:
        """Set of dataset names available in this class"""
        return _dataclass_attr_set(cls)

    def asdict(self) -> dict[str, Any]:
        """Export as dictionary (data not copied but referenced)"""
        return _asdict_shallow(self)


_MosaT = TypeVar("_MosaT", SimCoreDatasetsMOSA, SimFullDatasetsMOSA)
_SatT = TypeVar("_SatT", SimCoreDatasetsSat, SimFullDatasetsSat)


class SimResultsNumpy(Generic[_MosaT, _SatT]):
    """Collect simulation results exported to numpy arrays in dataclasses

    The purpose of this class is to contain simulation results and simulation
    metadata. The data is organized into per-MOSA datasets, per-spacecraft
    datasets, and metadata.

    The per-MOSA data is available via the mosa_data property, the per-spacecraft
    data through the sat_data property, and the metadata throught the meta_data
    property.

    This is a generic class that comes in two variants, one that contains
    the full set of simulation results, and one that only contains a core
    selection of datasets. It is not intended to be created directly. Instead,
    users should instanciate the concrete subclasses SimResultsNumpyFull or
    SimResultsNumpyCore. The motivation for this roundabout scheme is to
    allow static type checking of attribute names when accessing results.

    There are special data sets for the different time grids to which the
    datasets belong. Those are not saved when writing in HDF5 files, but the
    metadata contains all information needed to reconstruct them. The
    properties "t", "physics_t", and "telemetry_t" provide the reconstructed
    time arrays.

    Finally, there is a method export_hdf5 to save the results to a HDF5 file.
    """

    metadata_names: frozenset[str] = SimMetaData.dataset_names()

    def __init__(
        self,
        data: dict[DatasetIdentifier, np.ndarray],
        ranges: dict[IdxSpace, tuple[int, int]],
        meta_data: dict[str, Any],
        cls_dat_mosa: type[_MosaT],
        cls_dat_sat: type[_SatT],
    ):
        """Constructor. Not intended for direct use, see SimResultsNumpyFull/Core"""
        meta = SimMetaData(**meta_data)

        propm = cls_dat_mosa.dataset_metadata()
        istart_dsid: dict[DatasetIdentifier, int] = {}
        dsmosa: dict[str, dict[str, np.ndarray]] = {}
        rgmosa: dict[str, tuple[int, int]] = {}
        for n in cls_dat_mosa.dataset_names():
            cat = propm[n]
            rg = ranges[cat.idxspace]
            rgmosa[n] = rg
            dsmosan = {}
            for mosa in MosaID.names():
                dsid = make_dataset_id(cat.actual, n, mosa)
                dsmosan[mosa] = data[dsid]
                istart_dsid[dsid] = rg[0]
            dsmosa[n] = dsmosan

        props = cls_dat_sat.dataset_metadata()
        dssat: dict[str, dict[str, np.ndarray]] = {}
        rgsat: dict[str, tuple[int, int]] = {}
        for n in cls_dat_sat.dataset_names():
            cat = props[n]
            rg = ranges[cat.idxspace]
            rgsat[n] = rg
            dssatn = {}
            for sc in SatID.names():
                dsid = make_dataset_id(cat.actual, n, sc)
                dssatn[sc] = data[dsid]
                istart_dsid[dsid] = rg[0]
            dssat[n] = dssatn

        cls_rg_mosa = cls_dat_mosa.index_range_class()
        cls_rg_sat = cls_dat_sat.index_range_class()

        self._generic_data = data
        self._metadata: Final[SimMetaData] = meta
        self._mosadata: Final[_MosaT] = cls_dat_mosa(**dsmosa)
        self._mosaranges: Final = cls_rg_mosa(**rgmosa)
        self._satdata: Final[_SatT] = cls_dat_sat(**dssat)
        self._satranges: Final = cls_rg_sat(**rgsat)
        self._idxsp_ranges: Final = ranges
        self._istart_dsid: Final = istart_dsid

    @property
    def meta_data(self) -> SimMetaData:
        """The simulation metadata"""
        return self._metadata

    @property
    def mosa_data(self) -> _MosaT:
        """Per-MOSA datasets

        Returns an object which has an attribute for each dataset. Each such
        attribute is a dictionary mapping MOSA index strings to numpy arrays.
        """
        return self._mosadata

    @property
    def mosa_ranges(self):
        """Index ranges for per-MOSA datasets

        Returns an object which has an attribute for each dataset. Each such
        attribute is a tuple (istart, istop) with the index range of the data
        in the stream it came from.
        """
        return self._mosaranges

    @property
    def sat_data(self) -> _SatT:
        """Per-spacecraft datasets

        Returns an object which has attributes for each dataset. Each such
        attribute is a dictionary mapping spacecraft index strings to numpy arrays.
        """
        return self._satdata

    @property
    def sat_ranges(self):
        """Index ranges for per-spacecraft datasets

        Returns an object which has an attribute for each dataset. Each such
        attribute is a tuple (istart, istop) with the index range of the data
        in the stream it came from.
        """
        return self._satranges

    def export_hdf5(
        self,
        path="measurements.h5",
        *,
        description: str | None = None,
        overwrite=False,
        cfgscheduler: SchedulerConfigTypes | None = None,
    ) -> None:
        """Store the results in a HDF5 file.

        This will create an HDF5 file with the time series and metadata
        of the simulation. This is equivalent to using Instrument.export_hdf5
        directly.

        Note: Instrument.export_hdf5 has a keep_all parameter. In contrast,
        InstruDataNumpy.export_hdf5 just saves the available data.
        The choice of core vs full set of data is made when creating InstruDataNumpy,
        e.g. setting the Instrument.export_numpy keep_all parameter.

        Arguments:
        path: Path of the file to use
        overwrite: If True, any existing file will be overwritten.
        cfgscheduler: Parameters for the scheduling
        """
        if cfgscheduler is None:
            cfgscheduler = SchedulerConfigSerial(chunk_size=50000)

        source = array_dict_as_stream_bundle(self._generic_data, self._istart_dsid)
        store_instru_hdf5(
            path,
            source,
            self.meta_data.asdict(),
            datasets=source.output_ids,
            description=description,
            overwrite=overwrite,
            cfgscheduler=cfgscheduler,
        )

    @property
    def t(self) -> np.ndarray:
        """Sample times for regular time series"""
        rg = self._idxsp_ranges[IdxSpace.REGULAR]
        m = self.meta_data
        return m.t0 + np.arange(rg[0], rg[1]) * m.dt

    @property
    def telemetry_t(self) -> np.ndarray:
        """Sample times for upsampled time series"""
        rg = self._idxsp_ranges[IdxSpace.TELEMETRY]
        m = self.meta_data
        return m.t0 + np.arange(rg[0], rg[1]) * m.telemetry_dt


class SimResultsNumpyFull(SimResultsNumpy[SimFullDatasetsMOSA, SimFullDatasetsSat]):
    """Collect full set of simulation results stored in numpy arrays

    See SimResultsNumpy for details.
    """

    mosa_dataset_names: frozenset[str] = SimFullDatasetsMOSA.dataset_names()
    sat_dataset_names: frozenset[str] = SimFullDatasetsSat.dataset_names()
    all_dataset_names: frozenset[str] = mosa_dataset_names | sat_dataset_names

    @classmethod
    def dataset_identifier_set(cls) -> set[DatasetIdentifier]:
        """Set of all dataset identifiers for this class"""
        return _get_dataset_identifiers(SimFullDatasetsMOSA, SimFullDatasetsSat)

    def __init__(
        self,
        data: dict[DatasetIdentifier, np.ndarray],
        ranges: dict[IdxSpace, tuple[int, int]],
        meta_data: dict[str, Any],
    ):
        """Constructor

        The data is passed as dictionaries mapping dataset names
        to dictionaries mapping MOSA/spacecraft indices to numpy arrays.

        Arguments:
            data: Flat dictionary with results keyed by DatasetIdentifier
            ranges: Original stream index range for each data entry
            metadata: Dictionary with metadata
        """
        super().__init__(
            data, ranges, meta_data, SimFullDatasetsMOSA, SimFullDatasetsSat
        )

    @property
    def physics_t(self) -> np.ndarray:
        """Sample times for upsampled time series"""
        rg = self._idxsp_ranges[IdxSpace.PHYSICS]
        m = self.meta_data
        return m.t0 + np.arange(rg[0], rg[1]) * m.physics_dt

    @property
    def physics_ext_t(self) -> np.ndarray:
        """Sample times for upsampled time series"""
        rg = self._idxsp_ranges[IdxSpace.PHYSICS_EXT]
        m = self.meta_data
        return m.t0 + np.arange(rg[0], rg[1]) * m.physics_dt


class SimResultsNumpyCore(SimResultsNumpy[SimCoreDatasetsMOSA, SimCoreDatasetsSat]):
    """Collect core set of simulation results stored in numpy arrays"""

    mosa_dataset_names: frozenset[str] = SimCoreDatasetsMOSA.dataset_names()
    sat_dataset_names: frozenset[str] = SimCoreDatasetsSat.dataset_names()
    all_dataset_names: frozenset[str] = mosa_dataset_names | sat_dataset_names

    @classmethod
    def dataset_identifier_set(cls) -> set[DatasetIdentifier]:
        """Set of all dataset identifiers for this class"""
        return _get_dataset_identifiers(SimCoreDatasetsMOSA, SimCoreDatasetsSat)

    def __init__(
        self,
        data: dict[DatasetIdentifier, np.ndarray],
        ranges: dict[IdxSpace, tuple[int, int]],
        meta_data: dict[str, Any],
    ):
        """Constructor

        The data is passed as dictionaries mapping dataset names
        to dictionaries mapping MOSA/spacecraft indices to numpy arrays.

        Arguments:
            data: Flat dictionary with results keyed by DatasetIdentifier
            ranges: Original stream index range for each data entry
            metadata: Dictionary with metadata
        """
        super().__init__(
            data, ranges, meta_data, SimCoreDatasetsMOSA, SimCoreDatasetsSat
        )


SimResultsNumpyAny: TypeAlias = SimResultsNumpyCore | SimResultsNumpyFull


def _get_dataset_identifiers(
    cls_mosa: Type[SimCoreDatasetsMOSA] | Type[SimFullDatasetsMOSA],
    cls_sat: Type[SimCoreDatasetsSat] | Type[SimFullDatasetsSat],
) -> set[DatasetIdentifier]:
    """Set of all dataset identifiers for given dataclass"""
    sources: set[DatasetIdentifier] = set()
    for mname, cat in cls_mosa.dataset_metadata().items():
        for mosa in MosaID:
            sources.add(make_dataset_id(cat.actual, mname, mosa.value))
    for sname, cat in cls_sat.dataset_metadata().items():
        for sc in SatID:
            sources.add(make_dataset_id(cat.actual, sname, sc.value))
    return sources


def names_actual_datasets() -> set[str]:
    """Names of all actual data quantities"""
    mv = {n for n, cat in SimFullDatasetsMOSA.dataset_metadata().items() if cat.actual}
    sv = {n for n, cat in SimFullDatasetsSat.dataset_metadata().items() if cat.actual}
    return mv | sv


def names_debug_datasets() -> set[str]:
    """Names of all actual data quantities"""
    mv = {
        n for n, cat in SimFullDatasetsMOSA.dataset_metadata().items() if not cat.actual
    }
    sv = {
        n for n, cat in SimFullDatasetsSat.dataset_metadata().items() if not cat.actual
    }
    return mv | sv


def datasets_metadata_dict() -> dict[str, DataCategories]:
    """Dictionary with metadata for all dataset names"""
    mprops = SimFullDatasetsMOSA.dataset_metadata()
    sprops = SimFullDatasetsSat.dataset_metadata()
    return mprops | sprops


def metadata_as_json(metadata: dict[str, ValidMetaDataTypes]) -> str:
    """Convert metadata dictionary to JSON string"""
    return json.dumps(metadata, indent=4, sort_keys=True)


def store_instru_hdf5(
    path: pathlib.Path | str,
    source: StreamBundle,
    meta: dict[str, ValidMetaDataTypes],
    *,
    datasets: set[DatasetIdentifier],
    description: str | None = None,
    overwrite: bool = False,
    cfgscheduler: SchedulerConfigTypes | None = None,
) -> None:
    """Write instrument datasets to hdf5 and creates alias for backward compatibility

    This is mainly identical to the generic store_source_hdf5, but specialized for
    storing instrument data.

    Arguments:
        path: Path where to create the HDF5 file
        source: Streams as StreamBundle
        keep_all: Save all if True, else save only core datasets
        metadata: Dictionary with metadata
        overwrite: If True Truncate already existing file, else fail
        cfgscheduler: Parameters for the scheduling
    """
    meta_json = metadata_as_json(meta)

    package_version = importlib.metadata.version("lisainstrument")
    git_url = "https://gitlab.in2p3.fr/lisa-simulation/instrument"

    meta_hdf5: dict[str, H5AttrValidTypes] = {
        "metadata_json": meta_json,
        "version": package_version,
        "version_format": package_version,
        "git_url": git_url,
    }
    if description:
        meta_hdf5["description"] = description

    store_bundle_hdf5(
        path,
        source,
        meta_hdf5,
        datasets=datasets,
        overwrite=overwrite,
        cfgscheduler=cfgscheduler,
    )
