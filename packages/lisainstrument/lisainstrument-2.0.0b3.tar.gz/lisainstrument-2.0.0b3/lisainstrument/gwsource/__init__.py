"""The gwsource package contains tools for reading GW data required by the instrument simulator

The gw_source module provides an abstract interface representing the GW data as continuous
functions of time, and implementations allowing spline interpolation. The gw_file module provides
an abstract interface for reading any gw file data and implementations for the format currently
used in the simulator. The hdf5util contains some utilities for internal use by gw_file.
"""

from .gw_file import gw_file
from .gw_source import GWSource, GWSourceSplines, GWSourceZero
