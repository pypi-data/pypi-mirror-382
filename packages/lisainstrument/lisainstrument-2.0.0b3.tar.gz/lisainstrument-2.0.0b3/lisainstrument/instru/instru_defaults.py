"""Various constants that define default values used in the Instrument class"""

from typing import Final

import numpy as np

from lisainstrument.orbiting.constellation_enums import MosaID

OFFSET_FREQS: Final[dict[str, float]] = {
    "12": 0.0,
    "23": 11e6,
    "31": 7.5e6,
    "13": 16e6,
    "32": -12e6,
    "21": -7e6,
}
"""Values to use if offset_freqs=="default"

Default set yields valid beatnote frequencies for all lasers ('six')
with default 'static' set of MPRs
"""


MODULATION_ASDS: Final[dict[str, float]] = {
    "12": 5.2e-14,
    "23": 5.2e-14,
    "31": 5.2e-14,
    "13": 5.2e-13,
    "32": 5.2e-13,
    "21": 5.2e-13,
}
"""Values to use if modulation_asds == "default"

Default based on the performance model, with 10x amplification for right-sided
 MOSAs, to account for errors in the frequency distribution system
"""

MODULATION_FREQS: Final[dict[str, float]] = {
    "12": 2.4e9,
    "23": 2.4e9,
    "31": 2.4e9,
    "13": 2.401e9,
    "32": 2.401e9,
    "21": 2.401e9,
}
"""Values to use if modulation_freqs == "default"

Default based on mission baseline 2.4 MHz/2.401 MHz for left and right MOSAs
"""


CLOCK_FREQOFFSETS: Final[dict[str, float]] = {"1": 5e-8, "2": 6.25e-7, "3": -3.75e-7}
"""Values to use if clock_freqoffsets == "default"

Default based on LISANode
"""

CLOCK_FREQLINDRIFTS: Final[dict[str, float]] = {"1": 1.6e-15, "2": 2e-14, "3": -1.2e-14}
"""Value to use if clock_freqlindrifts == "default"

Default based on LISANode
"""

CLOCK_FREQQUADDRIFTS: Final[dict[str, float]] = {
    "1": 9e-24,
    "2": 6.75e-23,
    "3": -1.125e-22,
}
"""Value to use if clock_freqquaddrifts == "default"

Default based on LISANode
"""


TTL_COEFFS_LOCAL_PHIS: Final[dict[str, float]] = {
    "12": 2.005835e-03,
    "23": 2.105403e-04,
    "31": -1.815399e-03,
    "13": -2.865050e-04,
    "32": -1.986657e-03,
    "21": 9.368319e-04,
}
"""Value to use if  ttl_coeffs == "default"

Default values were drawn from the same distributions used for ttl_coeffs == "random"
"""


TTL_COEFFS_DISTANT_PHIS: Final[dict[str, float]] = {
    "12": 1.623910e-03,
    "23": 1.522873e-04,
    "31": -1.842871e-03,
    "13": -2.091585e-03,
    "32": 1.300866e-03,
    "21": -8.445374e-04,
}
"""Value to use if  ttl_coeffs == "default"

Default values were drawn from the same distributions used for ttl_coeffs == "random"
"""

TTL_COEFFS_LOCAL_ETAS: Final[dict[str, float]] = {
    "12": -1.670389e-03,
    "23": 1.460681e-03,
    "31": -1.039064e-03,
    "13": 1.640473e-04,
    "32": 1.205353e-03,
    "21": -9.205764e-04,
}
"""Value to use if  ttl_coeffs == "default"

Default values were drawn from the same distributions used for ttl_coeffs == "random"
"""

TTL_COEFFS_DISTANT_ETAS: Final[dict[str, float]] = {
    "12": -1.076470e-03,
    "23": 5.228848e-04,
    "31": -5.662766e-05,
    "13": 1.960050e-03,
    "32": 9.021890e-04,
    "21": 1.908239e-03,
}
"""Value to use if  ttl_coeffs == "default"

Default values were drawn from the same distributions used for ttl_coeffs == "random"
"""


MOSA_ANGLES: Final[dict[str, float]] = {
    "12": 30,
    "23": 30,
    "31": 30,
    "13": -30,
    "32": -30,
    "21": -30,
}
"""Value to use if  mosa_angles == "default"

Default MOSA at +/- 30 deg
"""


LOCKING_BEATNOTES_HZ: Final[dict[str, float]] = {
    "12": 8e6,
    "23": 9e6,
    "31": 10e6,
    "13": -8.2e6,
    "32": -8.5e6,
    "21": -8.7e6,
}
"""Static default values for locking beatnotes [Hz]"""


STATIC_PPRS_S: Final[dict[str, float]] = {
    "12": 8.33242295,
    "23": 8.30282196,
    "31": 8.33242298,
    "13": 8.33159404,
    "32": 8.30446786,
    "21": 8.33159402,
}
"""Static default values for PPRs [s]

Those default PPRs are based on first samples of Keplerian orbits (v2.0.dev)
"""


def random_ttl_coeffs_local_phis(low=-2.2e-3, high=2.2e-3) -> dict[str, float]:
    """Generate random value to use if ttl_coeffs == "random" """
    return {m.value: np.random.uniform(low, high) for m in MosaID}


def random_ttl_coeffs_distant_phis(low=-2.4e-3, high=2.4e-3) -> dict[str, float]:
    """Generate random value to use if ttl_coeffs == "random" """
    return {m.value: np.random.uniform(low, high) for m in MosaID}


def random_ttl_coeffs_local_etas(low=-2.2e-3, high=2.2e-3) -> dict[str, float]:
    """Generate random value to use if ttl_coeffs == "random" """
    return {m.value: np.random.uniform(low, high) for m in MosaID}


def random_ttl_coeffs_distant_etas(low=-2.4e-3, high=2.4e-3) -> dict[str, float]:
    """Generate random value to use if ttl_coeffs == "random" """
    return {m.value: np.random.uniform(low, high) for m in MosaID}
