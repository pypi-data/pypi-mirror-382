"""Functions for setting up orbit source according to Instrument parameter

The init_orbit_source function creates the orbit source used in the simulator
"""

import logging

from lisainstrument.instru import instru_defaults as defaults
from lisainstrument.orbiting import (
    OrbitSource,
    OrbitSourceSplines,
    make_orbit_source_from_tcbltt,
    make_orbit_source_from_tpsppr,
    make_orbit_source_static,
    orbit_file,
)


def _make_orbit_from_file(path, dataset) -> OrbitSourceSplines:
    """Create OrbitSource based on interpolation splines from orbit file

    Arguments:
        path: Path of the orbits file
        dataset: Which type of dataset to use ("tps/ppr" or "tcb/ltt")
    Returns:
        OrbitSource implementation of type OrbitSourceSplines
    """

    with orbit_file(path) as orbf:
        match dataset:
            case "tps/ppr":
                return make_orbit_source_from_tpsppr(orbf)
            case "tcb/ltt":
                return make_orbit_source_from_tcbltt(orbf)
            case _:
                msg = f"Invalid orbit_dataset parameter {dataset}"
                raise RuntimeError(msg)


def init_orbit_source(
    orbits: str | dict[str, float], orbit_dataset: str
) -> tuple[OrbitSource, str | None, str | None]:
    """Parse orbit parameters and set up orbit data source accordingly

    Arguments:
        orbits: Specifies orbit file, dictionary with static values, or use of default values
        orbit_dataset: In case of orbit file, which dataset type to use

    Returns:
        Generic OrbitSource instance, orbit file name or None, orbit dataset or None
    """
    logger = logging.getLogger(__name__)

    res_orbit_file: str | None = None
    res_orbit_dataset: str | None = None
    res_orbit_source: OrbitSource

    match (orbits, orbit_dataset):
        # Changing dataset default makes no sense for static case and is forbidden
        # Note: this used to be legal
        case ("static", "tps/ppr"):
            logger.info("Using default set of static proper pseudo-ranges")
            res_orbit_source = make_orbit_source_static(defaults.STATIC_PPRS_S, t0=0.0)
        case (str(path), str(dataset)):
            logger.info("Using orbit file '%s' with dataset '%s'", orbits, dataset)
            res_orbit_file = path
            res_orbit_dataset = dataset
            res_orbit_source = _make_orbit_from_file(path, dataset)
        # Changing dataset default would make no sense here either
        # Note: this used to be legal
        case (dict(orb_dict), "tps/ppr") if all(
            isinstance(v, float) for v in orb_dict.values()
        ):
            logger.info("Using static proper pseudo-ranges provided by user")
            res_orbit_source = make_orbit_source_static(orb_dict, t0=0.0)
        # Note: providing numpy arrays used to be legal
        case (dict(), str()):
            msg = "Only float is allowed in dicts providing orbits, since the switch to chunked processing"
            raise RuntimeError(msg)
        case _:
            msg = f"Invalid orbit parameters {orbits=}, {orbit_dataset=}"
            raise RuntimeError(msg)

    return res_orbit_source, res_orbit_file, res_orbit_dataset
