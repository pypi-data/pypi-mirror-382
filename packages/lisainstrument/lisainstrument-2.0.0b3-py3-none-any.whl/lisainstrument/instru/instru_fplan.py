"""Functions for setting up frequency plan source according to Instrument parameter


The init_fplan_source function creates the frequency plan source used in the simulator
"""

import logging
import pathlib

import numpy as np

from lisainstrument.freqplan import FreqPlanFile, FreqPlanSourceFile
from lisainstrument.instru import instru_defaults as defaults
from lisainstrument.orbiting import OrbitSource, OrbitSourceStatic
from lisainstrument.orbiting.constellation_enums import (
    LockTypeID,
    MosaID,
    make_mosa_dict,
    make_mosa_dict_const,
)
from lisainstrument.sigpro import ConstFuncOfTime, FuncOfTimeTypes

logger = logging.getLogger(__name__)


def _init_fplan_from_file(
    path: pathlib.Path | str,
    orbit_file_t0: float,
    lock: dict[str, str],
    lock_config: str | None,
) -> dict[str, FuncOfTimeTypes]:
    """Initialize locking beatnotes from a frequency plan file

    Arguments:
        path: The path of the file
    """

    # Without a standard lock config, there is no dataset
    # in the frequency-plan file and therefore we cannot use it
    if lock_config is None:
        raise ValueError(
            "cannot use frequency-plan for non standard lock configuration"
        )

    with FreqPlanFile(path) as fpf:
        logger.debug("Using frequency-plan file version %s", fpf.format_version)
        if fpf.format_version.is_devrelease:
            logger.warning(
                "You are using an frequency-plan file in a development version"
            )
        logger.debug(
            "Interpolating locking beatnote frequencies with piecewise linear functions"
        )

        locks = {mosa: LockTypeID(lock[mosa.value]) for mosa in MosaID}
        src = FreqPlanSourceFile(fpf, locks, lock_config, orbit_file_t0)

        return {mosa.value: src.beatnote_for_mosa(mosa) for mosa in MosaID}


def _init_fplan_static(values: dict[str, float]) -> dict[str, FuncOfTimeTypes]:
    """Initialize the locking beatnotes to static values"""
    return {mosa: ConstFuncOfTime(values[mosa]) for mosa in MosaID.names()}


def _init_fplan_static_default() -> dict[str, FuncOfTimeTypes]:
    """Initialize the locking beatnotes to static default values"""
    logger.warning(
        "Using default set of locking beatnote frequencies "
        "might cause interferometric beatnote frequencies to fall "
        "outside the requirement range of 5..25 MHz"
    )

    return _init_fplan_static(defaults.LOCKING_BEATNOTES_HZ)


def init_fplan_source(
    fplan: str | float | dict[str, float] | np.ndarray,
    orbsrc: OrbitSource,
    lock: dict[str, str],
    lock_config: str | None,
) -> tuple[dict[str, FuncOfTimeTypes], str | None]:
    """Initialize frequency plan source.

    This returns either static frequency plan sources or sources interpolating
    data loaded from a frequency plan file, depending on the parameters.

    When using a frequency plan file, one needs the standard locking configuration
    name, otherwise the parameter is unsused.

    Args:
        fplan: `fplan` parameter, c.f. `Instrument__init__()`
        orbsrc: Orbit source
        lock: Dictionary with locking configuration
        lock_config: Standard name of locking cofig
    Returns:
        Dictionary with frequency plan sources, and the frequency file path or None
    """

    fplan_file: None | str = None
    fplan_res: dict[str, FuncOfTimeTypes]

    match fplan:
        case np.ndarray():
            msg = "providing numpy arrays as frequency plan temporarily disabled"
            raise RuntimeError(msg)
        case "static":
            logger.info("Using default set of locking beatnote frequencies")
            fplan_res = _init_fplan_static_default()
        case str(fplan_path):
            logger.info("Using frequency-plan file '%s'", fplan_path)
            if isinstance(orbsrc, OrbitSourceStatic):
                msg = "Cannot use frequency-plan for non orbit files"
                raise ValueError(msg)
            fplan_file = fplan_path
            fplan_res = _init_fplan_from_file(fplan_path, orbsrc.t0, lock, lock_config)

        case dict(fplan_dict) if all(
            isinstance(v, np.ndarray) for v in fplan_dict.values()
        ):
            msg = "providing numpy arrays as frequency plan temporarily disabled"
            raise RuntimeError(msg)
        case dict(fplan_dict) if all(isinstance(v, float) for v in fplan_dict.values()):
            logger.info(
                "Using user-provided dictionary with constant scalars for locking beatnote frequencies"
            )
            fplan_res = _init_fplan_static(make_mosa_dict(fplan_dict))
        case float(fplan_scalar):
            logger.info(
                "Using user-provided scalar for all locking beatnote frequencies"
            )
            fplan_res = _init_fplan_static(make_mosa_dict_const(fplan_scalar))
        case _:
            msg = f"Invalid fplan parameter {fplan}"
            raise RuntimeError(msg)

    return fplan_res, fplan_file
