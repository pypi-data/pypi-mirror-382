"""Package for signal processing based on numpy arrays

This contains tools for
- FIR filtering
- IIR filtering
- Interpolation and delay
  - Lagrange interpolation for non-const shift
  - Lagrange interpolation for const shift
  - Global and chunked spline interpolation
- Inversion of time coordinate transforms

This package contains low-level utilities operating on numpy arrays that fit in memory.
The core algorithms provided here are used in the streams package to provide similar
functionality for chunked data processing.

Besides signal processing tools, this package defines types for concepts commonly
used throughout the simulator package:
- FuncOfTime: Contiuous function of time, operating on 1D numpy arrays
- ConstFuncOfTime: Represents constant functions for optimization
"""

from lisainstrument.sigpro.dynamic_delay_numpy import ShiftBC
from lisainstrument.sigpro.fir_filters_numpy import (
    DefFilterFIR,
    EdgeHandling,
    make_fir_causal_kaiser,
    make_fir_causal_normal_from_coeffs,
)
from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTime,
    FuncOfTimeTypes,
)
