"""Locking related constants and parameter parsing for internal use in the simulator"""

import logging
import re
from dataclasses import dataclass, field
from typing import Final

from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.streams import StreamBase

LOCK_TOPOLOGIES: Final[dict[str, dict[str, str]]] = {
    "N1": {
        "12": "cavity",
        "23": "adjacent",
        "31": "distant",
        "13": "adjacent",
        "32": "adjacent",
        "21": "distant",
    },
    "N2": {
        "12": "cavity",
        "23": "adjacent",
        "31": "distant",
        "13": "adjacent",
        "32": "distant",
        "21": "distant",
    },
    "N3": {
        "12": "cavity",
        "23": "adjacent",
        "31": "adjacent",
        "13": "adjacent",
        "32": "distant",
        "21": "distant",
    },
    "N4": {
        "12": "cavity",
        "23": "distant",
        "31": "distant",
        "13": "adjacent",
        "32": "adjacent",
        "21": "distant",
    },
    "N5": {
        "12": "cavity",
        "23": "distant",
        "31": "distant",
        "13": "adjacent",
        "32": "adjacent",
        "21": "adjacent",
    },
    "N6": {
        "12": "cavity",
        "23": "adjacent",
        "31": "adjacent",
        "13": "distant",
        "32": "distant",
        "21": "distant",
    },
}
"""Supported laser locking topologies.

Definitions are given for 12 as the primary laser. Other configurations are
obtained by cycling the indices.
"""

INDEX_CYCLES: Final[dict[str, dict[str, str]]] = {
    "12": {"12": "12", "23": "23", "31": "31", "13": "13", "32": "32", "21": "21"},
    "21": {"12": "21", "23": "13", "31": "32", "13": "23", "32": "31", "21": "12"},
    "31": {"12": "23", "23": "31", "31": "12", "13": "21", "32": "13", "21": "32"},
    "32": {"12": "32", "23": "21", "31": "13", "13": "31", "32": "12", "21": "23"},
    "23": {"12": "31", "23": "12", "31": "23", "13": "32", "32": "21", "21": "13"},
    "13": {"12": "13", "23": "32", "31": "21", "13": "12", "32": "23", "21": "31"},
}
"""Index cycles for laser locking topologies."""


@dataclass
class LockingResults:
    """Dataclass for internal use by Instrument.simulate_locking method"""

    local_carrier_offsets: dict[MosaID, StreamBase] = field(default_factory=dict)
    distant_carrier_offsets: dict[MosaID, StreamBase] = field(default_factory=dict)
    local_carrier_fluctuations: dict[MosaID, StreamBase] = field(default_factory=dict)
    distant_carrier_fluctuations: dict[MosaID, StreamBase] = field(default_factory=dict)
    adjacent_carrier_fluctuations: dict[MosaID, StreamBase] = field(
        default_factory=dict
    )
    laser_noises: dict[MosaID, StreamBase] = field(default_factory=dict)


def init_lock(lock: str | dict[str, str]) -> tuple[dict[str, str], str | None]:
    """Initialize laser locking configuration."""

    logger = logging.getLogger(__name__)
    allowed_lock_types = {"cavity", "distant", "adjacent"}

    match lock:
        case "six":
            logger.info("Using pre-defined locking configuration 'six'")
            res_lock_config = None  # not a standard lock config
            res_lock = {
                "12": "cavity",
                "23": "cavity",
                "31": "cavity",
                "13": "cavity",
                "32": "cavity",
                "21": "cavity",
            }
        case "three":
            logger.info("Using pre-defined locking configuration 'three'")
            res_lock_config = None  # not a standard lock config
            res_lock = {
                "12": "cavity",
                "13": "adjacent",
                "23": "cavity",
                "21": "adjacent",
                "31": "cavity",
                "32": "adjacent",
            }
        case str(lock_str):
            logger.info("Using pre-defined locking configuration '%s'", lock)
            res_lock_config = lock_str
            match = re.match(r"^(N[1-6])-(12|23|31|13|32|21)$", lock_str)
            if match:
                topology, primary = match.group(1), match.group(2)
                lock_12 = LOCK_TOPOLOGIES[topology]  # with 12 as primary
                cycle = INDEX_CYCLES[primary]  # correspondance to lock_12
                res_lock = {mosa: lock_12[cycle[mosa]] for mosa in MosaID.names()}
            else:
                msg = f"unsupported pre-defined locking configuration '{lock_str}'"
                raise ValueError(msg)
        case dict(lock_dict):
            logger.info("Using explicit locking configuration '%s'", lock)
            if set(lock_dict.keys()) != MosaID.names():
                msg = f"invalid MOSA name in locking configuration '{lock}'"
                raise ValueError(msg)
            if not set(lock_dict.values()) <= allowed_lock_types:
                msg = f"invalid type specifiers in locking configuration '{lock}'"
                raise ValueError(msg)
            res_lock_config = None
            res_lock = lock
        case _:
            msg = f"invalid locking configuration '{lock}'"
            raise ValueError(msg)

    return res_lock, res_lock_config
