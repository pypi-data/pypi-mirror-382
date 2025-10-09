"""Functions for applying dynamic real-valued shifts to numpy arrays using Lagrange interpolation

The main class in this module is DynamicShiftNumpy. It allows to perform a time-shifting
opration on a numpy array, with time-dependent time shift. A similar functionality is implemented
in the streams.delay module for chunked processing. Both are using the same core
interpolation methods.

The interpolation method to be used is provided by the user in form of an object
implementing the RegularInterpolator protocol defined in the module regular_interpolators.
This interpolation engine is based on numpy arrays. The RegularInterpolator protocol is
not responsible for setting up boundary conditions, which is the responsability of
DynamicShiftNumpy.

The other parameters that determine the DynamicShiftNumpy behavior are collected
in a class DynShiftCfg. It contains the left and right boundary conditions. The available
options are defined by the ShiftBC enum class. DynShiftCfg also contains limits
for the allowable minimum and maximum time shift. Those have to be supplied by the user
because they cannot be determined from the data in DynamicShiftDask and DynamicShiftNumpy
is required to behave exactly like DynamicShiftDask.

The convenience functions make_dynamic_shift_lagrange_numpy() and
make_dynamic_shift_linear_numpy() return a DynamicShiftNumpy instance
employing Lagrange or linear interpolation, respectively. For testing,
there is another Lagrange interpolator based on the legacy dsp.timeshift
code. Use lisainstrument.legacy.dynamic_delay_dsp.make_dynamic_shift_dsp_numpy()
to obtain a corresponding DynamicShiftNumpy instance.

Example use:

>>> op = make_dynamic_shift_lagrange_numpy(
        order=31,
        min_delay=-2., max_delay=21.,
        left_bound=ShiftBC.FLAT, right_bound=ShiftBC.EXCEPTION
    )
>>> delay = np.linspace(-1.2,20.4,100)
>>> data = np.linspace(0,1, len(delay)
>>> shifted_data = op(data, -delay)


Internally, the module works as follows. DynamicShiftNumpy contains a
user-provided RegularInterpolator. The latter can interpolate to points
within the given data, minus a margin size defined by RegularInterpolator
implementations. Before calling RegularInterpolator, DynamicShiftNumpy
extends the data by suitable margins filled according to the selected
boundary conditions. The margin size is computed from the margins needed
by the interpolator as well as the fixed limits specified for the timeshift.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

import numpy as np
from typing_extensions import assert_never

from lisainstrument.sigpro.regular_interpolators import (
    RegularInterpolator,
    make_regular_interpolator_lagrange,
    make_regular_interpolator_linear,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D


class ShiftBC(Enum):
    """Enum for various methods of handling boundaries in dynamic shift

    ZEROPAD: Assume all data outside given range is zero.
    FLAT: Assume all data outside given range is equal to value on nearest boundary
    EXCEPTION: raise exception if data outside range is needed
    """

    EXCEPTION = 1
    ZEROPAD = 2
    FLAT = 3


@dataclass(frozen=True)
class DynShiftCfg:
    """Config class for dynamic shift interpolation

    Attributes:
        min_delay: Assume that any shift > -max_delay
        max_delay: Assume that any shift < -min_delay
        left_bound: Treatment of left boundary
        right_bound: Treatment of right boundary
    """

    min_delay: float
    max_delay: float
    left_bound: ShiftBC
    right_bound: ShiftBC

    @property
    def min_delay_int(self) -> int:
        """Minimum delay in integer index space"""
        return int(np.floor(self.min_delay))

    @property
    def max_delay_int(self) -> int:
        """Maximum delay in integer index space"""
        return int(np.ceil(self.max_delay))

    def __post__init__(self):
        if self.min_delay > self.max_delay:
            msg = f"Invalid delay range for dynamic shift ({self.min_delay}, {self.max_delay})"
            raise ValueError(msg)


class DynamicShiftNumpy:
    """Interpolate to locations given by a non-const shift.

    This allows to interpolate samples in a numpy array to locations specified
    by a shift given by another numpy array of same size. The shift is specified in
    units of the array index, i.e. there is no separate coordinate array.
    A positive shift refers to values right of a given sample, negative shifts
    to values on the left.

    The boundary treatment can be specified for each boundary in terms of
    ShiftBC enums.

    The interpolation method is not fixed but provided via an interpolator
    instance implementing the RegularInterpMethod protocol.

    For technical reasons, the shift values have to be within some bound that
    has to be provided.
    """

    def __init__(
        self,
        cfg: DynShiftCfg,
        interp: RegularInterpolator,
    ):
        """Set up interpolator.

        Arguments:
            cfg: limits of delay and boundary treatment
            interp: interpolation method
        """
        self._cfg: Final = cfg
        self._interp_np: Final = interp

    @property
    def margin_left(self) -> int:
        """Left margin size.

        If positive, specifies how many samples on the left have to be added by boundary conditions.
        If negative, specifies how many samples on the left are unused.
        """
        return self._interp_np.margin_left + self._cfg.max_delay_int

    @property
    def margin_right(self) -> int:
        """Right margin size.

        If positive, specifies how many samples on the right have to be added by boundary conditions.
        If negative, specifies how many samples on the right are unused.
        """
        return self._interp_np.margin_right - self._cfg.min_delay_int

    def __call__(self, samples: np.ndarray, shift: np.ndarray) -> NumpyArray1D:
        """Apply shift given by numpy array to samples in another numpy array.

        The shift and sample arrays need to have the same size, and each shift provides
        the interpolation location relative to the sample with the same index.
        Shifts are floating point values. A shift of +1 refers to the sample on the right,
        -1 the sample on the left, etc. All arrays have to be 1D.


        Arguments:
            samples: 1D numpy array with data samples
            shift: 1D numpy array with shifts

        Returns:
            Numpy array with interpolated samples
        """
        out_size = len(shift)

        npad_left = 0
        padv_left = 0.0
        if self.margin_left > 0:
            match self._cfg.left_bound:
                case ShiftBC.ZEROPAD:
                    npad_left = self.margin_left
                    padv_left = 0.0
                case ShiftBC.FLAT:
                    npad_left = self.margin_left
                    padv_left = samples[0]
                case ShiftBC.EXCEPTION:
                    msg = (
                        f"DynamicShiftNumpy: left edge handling {self._cfg.left_bound.name} not "
                        f"possible for given max delay {self._cfg.max_delay}."
                    )
                    raise RuntimeError(msg)
                case _ as unreachable:
                    assert_never(unreachable)

        npad_right = 0
        padv_right = 0.0
        if self.margin_right > 0:
            match self._cfg.right_bound:
                case ShiftBC.ZEROPAD:
                    npad_right = self.margin_right
                    padv_right = 0.0
                case ShiftBC.FLAT:
                    npad_right = self.margin_right
                    padv_right = samples[-1]
                case ShiftBC.EXCEPTION:
                    msg = (
                        f"DynamicShiftNumpy: right edge handling {self._cfg.right_bound.name} not "
                        f"possible for given min delay {self._cfg.min_delay=}."
                    )
                    raise RuntimeError(msg)
                case _ as unreachable:
                    assert_never(unreachable)

        if npad_left > 0 or npad_right > 0:
            samples = np.pad(
                samples,
                (npad_left, npad_right),
                mode="constant",
                constant_values=(padv_left, padv_right),
            )

        n_size = npad_left + out_size + self.margin_right
        n_first = npad_left - self.margin_left
        samples_needed = samples[n_first : n_first + n_size]
        return self._interp_np.apply_shift(samples_needed, shift, self.margin_left)


def make_dynamic_shift_lagrange_numpy(
    order: int,
    min_delay: float,
    max_delay: float,
    left_bound: ShiftBC,
    right_bound: ShiftBC,
) -> DynamicShiftNumpy:
    """Set up DynamicShiftNumpy instance with Lagrange interpolation method.

    Arguments:
        order: Order of the Lagrange polynomials
        min_delay: Assume that any shift > -max_delay
        max_delay: Assume that any shift < -min_delay
        left_bound: Treatment of left boundary
        right_bound: Treatment of right boundary

    Returns:
        Interpolation function of type DynamicShiftNumpy
    """
    interp = make_regular_interpolator_lagrange(order)
    cfg = DynShiftCfg(min_delay, max_delay, left_bound, right_bound)
    return DynamicShiftNumpy(cfg, interp)


def make_dynamic_shift_linear_numpy(
    min_delay: float,
    max_delay: float,
    left_bound: ShiftBC,
    right_bound: ShiftBC,
) -> DynamicShiftNumpy:
    """Set up DynamicShiftNumpy instance with linear interpolation method.

    Arguments:
        min_delay: Assume that any shift > -max_delay
        max_delay: Assume that any shift < -min_delay
        left_bound: Treatment of left boundary
        right_bound: Treatment of right boundary

    Returns:
        Interpolation function of type DynamicShiftNumpy
    """
    interp = make_regular_interpolator_linear()
    cfg = DynShiftCfg(min_delay, max_delay, left_bound, right_bound)
    return DynamicShiftNumpy(cfg, interp)
