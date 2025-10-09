"""Functions for applying dynamic real-valued shifts to dask arrays using dsp.timeshift

There are two implementations of Lagrange interpolation:

1. dynamic_delay_dsp_dask.make_regular_interpolator_dsp wraps legacy implementation dsp.timeshift
   into new interface
2. dynamic_delay_numpy.make_regular_interpolator_lagrange provides a completely new implementation
   of Lagrange interpolation

Use make_dynamic_shift_dsp_dask to create an interpolator based on dsp.timeshift for dask arrays.
"""

from __future__ import annotations

from typing import Final

import numpy as np

from lisainstrument.legacy import dsp
from lisainstrument.sigpro.dynamic_delay_numpy import (
    DynamicShiftNumpy,
    DynShiftCfg,
    ShiftBC,
)
from lisainstrument.sigpro.regular_interpolators import (
    RegularInterpCore,
    RegularInterpolator,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D


class RegularInterpDSP(RegularInterpCore):
    """Adaptor wrapping dsp.timeshift as RegularInterpCore interface"""

    def __init__(self, order: int):
        if order < 1:
            msg = f"DSPWrapper: order must be greater 0, got {order}"
            raise ValueError(msg)

        if order % 2 == 0:
            msg = "DSPWrapper: even order not supported by dsp timeshift"
            raise ValueError(msg)

        self._order: Final = order
        self._length: Final = order + 1
        self._offset: Final = -(order // 2)

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) on the left boundary

        The interpolator cannot be called with locations within this margin from the leftmost sample.
        """
        return -self._offset

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) on the right boundary

        The interpolator cannot be called with locations within this margin from the rightmost sample.
        """
        return self._length - 1 + self._offset

    def apply(
        self,
        samples: NumpyArray1D,
        locations: NumpyArray1D,
        int_offsets: NumpyArray1D | int = 0,
    ) -> np.ndarray:
        """Interpolate regularly spaced data to location in index-space"""
        doff = int_offsets - np.arange(locations.shape[0])
        shift = locations - doff[0] + doff
        shift_offset = doff[0]

        return self.apply_shift(samples, shift, shift_offset)

    def apply_shift(
        self,
        samples: NumpyArray1D,
        shift: NumpyArray1D,
        shift_offset: int,
    ) -> np.ndarray:
        """Iterpolate to location specified in terms of shifts instead absolute locations"""
        shift_tot = shift + shift_offset

        npad_right = 0

        if shift.shape[0] < samples.shape[0]:
            npad_right = samples.shape[0] - shift.shape[0]
            shift_tot = np.concatenate([shift_tot, np.zeros(npad_right)])
        elif shift.shape[0] > samples.shape[0]:
            msg = "DSPWrapper: insufficient samples for interpolation"
            raise RuntimeError(msg)

        res = dsp.timeshift(samples, shift_tot, self._order)
        if npad_right > 0:
            res = res[:-npad_right]

        return res


def make_regular_interpolator_dsp(order: int) -> RegularInterpolator:
    """Create an interpolator based on dsp.timeshift

    See RegularInterpDSP for details of the method.

    Arguments:
        order: Lagrange interpolation order (must be odd)
    Returns:
        Interpolation function
    """
    return RegularInterpolator(RegularInterpDSP(order))


def make_dynamic_shift_dsp_numpy(
    order: int,
    min_delay: float,
    max_delay: float,
    left_bound: ShiftBC,
    right_bound: ShiftBC,
) -> DynamicShiftNumpy:
    """Set up DynamicShiftNumpy instance using dsp.timeshift.

    Arguments:
        order: Lagrange interpolation order (must be odd)
        min_delay: Assume that any shift > -max_delay
        max_delay: Assume that any shift < -min_delay
        left_bound: Treatment of left boundary
        right_bound: Treatment of right boundary

    Returns:
        Interpolation function of type DynamicShiftNumpy
    """

    interp = make_regular_interpolator_dsp(order)
    cfg = DynShiftCfg(min_delay, max_delay, left_bound, right_bound)
    return DynamicShiftNumpy(cfg, interp)
