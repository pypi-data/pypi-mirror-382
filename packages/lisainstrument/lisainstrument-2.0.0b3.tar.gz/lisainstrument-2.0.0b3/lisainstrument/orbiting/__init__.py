"""Tools for obtaining orbit file data and enum classes for indexing MOSA and spacecrafts

The orbit_source module provides an abstract interface representing orbit data as continuous
functions. An implementation based on spline interpolation can be found in module
orbit_source_interp. The orbit_file module provides an abstract interface for reading
generic orbit files, and implementations for the formats currently used in the simulator.

The constellation_enums module provides enums for indexing MOSAs, spacecrafts, and locking
types, as well as related helper functions. This is used extensively by many modules in the
lisainstrument package.
"""

from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.orbiting.orbit_file import orbit_file
from lisainstrument.orbiting.orbit_source import (
    OrbitSource,
    OrbitSourceStatic,
    make_orbit_source_static,
)
from lisainstrument.orbiting.orbit_source_interp import (
    OrbitSourceSplines,
    make_orbit_source_from_tcbltt,
    make_orbit_source_from_tpsppr,
)
