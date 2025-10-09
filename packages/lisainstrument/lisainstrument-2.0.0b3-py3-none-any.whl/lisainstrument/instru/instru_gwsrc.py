"""Functions for setting up GW source according to Instrument parameter


The init_gw_source function creates the GW data source used in the simulator
"""

import logging

import numpy as np

from lisainstrument.gwsource import GWSource, GWSourceSplines, GWSourceZero, gw_file

logger = logging.getLogger(__name__)


def _gw_source_from_file(
    path: str, orbit_dataset: str | None, chunk_gw_files: bool, tmin: float, tmax: float
) -> tuple[GWSource, str]:
    """Create GWSource from GW file.

    The type of dataset to use from the gw file is selected based upon what
    was used for orbits ("tps/ppr"|"tcb/ltt" for orbit files, None otherwise).
    If the orbit dataset is "tps/ppr" but the gw file does not have it,
    we fall back to use tcb. The reason is backward-compatibility. The other
    way around is an error, however.


    There are two options for interpolating the GW data. For global interpolation,
    a fixed interpolation spline is constructed from the portion of the data covering
    the entire simulation time grid plus a large margin.
    For chunked interpolation, data is read when required and interpolated locally.
    The latter is using the same spline interpolation, but using only the data covering
    the requested interval plus a large margin.
    Beware: this leads to interpolation errors which depend weakly on the chunk sizes.

    If the required time window extends beyond the available data, zero-padding is
    employed by the GWFile instance.

    Arguments:
        path: path of the gw file
        orbit_dataset: which dataset type was used for orbits
        chunk_gw_files: whether to use chunked or global interpolation
        tmin: Start of time interval that needs to be be covered
        tmax: End of time interval that needs to be be covered

    Returns:
        Tuple with GWSource and the dataset type that was used from the gw file.
    """
    gwf = gw_file(path)
    if gwf.format_version.is_devrelease:
        logger.warning("You are using a GW file in a development version")

    match orbit_dataset:
        case "tps/ppr":
            if gwf.has_tpsppr_dataset:
                logger.debug("Using link responses in TPS (following orbit dataset)")
                gw_group = "tps"
                gws = gwf.load_segment_tpsppr
            else:
                logger.warning(
                    "TPS link responses not found on '%s', fall back to TCB responses",
                    path,
                )
                logger.debug(
                    "Using link responses in TCB (inconsistent with orbit dataset)"
                )
                gw_group = "tcb"
                gws = gwf.load_segment_tcbltt
        case "tcb/ltt" | None:
            logger.debug("Using link responses in TCB (following orbit dataset)")
            gw_group = "tcb"
            gws = gwf.load_segment_tcbltt
        case _:
            msg = f"Invalid orbit dataset {orbit_dataset}"
            raise RuntimeError(msg)

    src = GWSourceSplines(
        gws,
        tmin=tmin,
        tmax=tmax,
        chunked=chunk_gw_files,
    )

    return src, gw_group


def init_gw_source(
    gws: str | None | dict[str, np.ndarray],
    orbit_dataset: str | None,
    chunk_gw_files: bool,
    tmin: float,
    tmax: float,
) -> tuple[GWSource, str | None, str | None]:
    """Parser gws parameter and set up a corresponding GWSource

    The orbit dataset parameter only has effect when using gw files,
    where it is used to select the dataset type (see _gw_source_from_file).

    Besides the GW data source, this also returns related metadata entries
    for the simulator

    Arguments:
        gws: see Instrument.__init__()
        orbit_dataset: orbit dataset type ("tps/ppr" | "tcb/ltt" | None)
        chunk_gw_files: Whether to use global or chunked interpolation for GW files
        tmin: Start of time interval that needs to be be covered
        tmax: End of time interval that needs to be be covered

    Returns:
        GWSource instance, GW file name or None, GW dataset group or None
    """
    res_gw_source: GWSource
    res_gw_file: str | None = None
    res_gw_group: str | None = None

    match gws:
        case str(gw_path):
            res_gw_file = gw_path
            res_gw_source, res_gw_group = _gw_source_from_file(
                gw_path, orbit_dataset, chunk_gw_files, tmin, tmax
            )
        case None:
            res_gw_source = GWSourceZero()
        case dict(gw_dict) if all(isinstance(v, np.ndarray) for v in gw_dict.values()):
            msg = "Passing time series for GWs forbidden since switch to chunked processing"
            raise RuntimeError(msg)
        case _:
            msg = f"Invalid GW parameter {gws=} for selected orbits {orbit_dataset}"
            raise RuntimeError(msg)

    return res_gw_source, res_gw_file, res_gw_group
