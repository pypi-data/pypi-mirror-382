"""Functions for applying fixed real-valued shifts to dask arrays using dsp.timeshift

There are two implementations of fixed-shift Lagrange interpolation:

1. fixed_shift_dsp.make_fixed_shift_dsp wraps legacy implementation dsp.timeshift
   into new interface
2. fixed_shift_numpy.make_fixed_shift_lagrange provides a completely new implementation
   of Lagrange interpolation

Use make_fixed_shift_dsp_dask to create an interpolator based on dsp.timeshift for dask arrays.
"""

from __future__ import annotations

from typing import Final

import numpy as np

from lisainstrument.legacy import dsp
from lisainstrument.sigpro.fixed_shift_numpy import (
    FixedShiftCore,
    FixedShiftFactory,
    make_numpy_array_1d_float,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d


class FixedShiftWrapDSP(FixedShiftCore):
    r"""Class implementing fixed shift of regularly spaced 1D data using dsp.timeshift().

    This class is an adaptor making dsp.timeshift function available through a
    FixedShiftCore interface.

    See FixedShiftCore for general properties not specific to the interpolation method.
    """

    def __init__(self, order: int, shift: float):
        """Set up interpolation parameters.

        The order parameter specifies the order of the interpolation polynomials. The
        number of samples used for each interpolation point is order + 1. The order of
        the interpolating polynomials is also the order of plynomials that are interpolated
        with zero error.

        The shift sign is defined such that positive values refer to locations
        to the right of the output sample at hand.

        Arguments:
            order: The order of the interpolation polynomials
            shift: The constant shift
        """

        if order < 1:
            msg = f"FixedShiftWrapDSP: order must be >= 1, got {order}"
            raise ValueError(msg)

        if order % 2 == 0:
            msg = "FixedShiftWrapDSP: even Lagrange polynomial order not supported by dsp.timeshift"
            raise ValueError(msg)

        loc = float(shift)
        loc_int = int(np.floor(loc))
        # ~ loc_frac = loc - loc_int

        margin_lagr_left = order // 2
        margin_lagr_right = order - margin_lagr_left

        self._margin_left: Final = max(0, margin_lagr_left - loc_int)
        self._margin_right: Final = max(0, margin_lagr_right + loc_int)
        self._shift: Final = shift
        self._order: Final = order

    @property
    def margin_left(self) -> int:
        """Margin size (>= 0) needed on the left boundary"""
        return self._margin_left

    @property
    def margin_right(self) -> int:
        """Margin size (>= 0) needed on the right boundary"""
        return self._margin_right

    @property
    def shift(self) -> float:
        """The shift"""
        return self._shift

    def apply(self, samples: np.ndarray) -> NumpyArray1D:
        """Apply shift, see FixedShiftCore.apply()

        Arguments:
            samples: 1D numpy array with sampled data

        Returns:
            Shifted input excluding margins
        """
        a = make_numpy_array_1d_float(samples)
        res = dsp.timeshift(a, self.shift, self._order)

        if self.margin_left > 0:
            res = res[self.margin_left :]
        if self.margin_right > 0:
            res = res[: -self.margin_right]

        return make_numpy_array_1d(res)

    @staticmethod
    def factory(order: int) -> FixedShiftFactory:
        """Factory for making FixedShiftWrapDSP instances

        Arguments:
            order: Order of the Lagrange polynomials to use

        Returns:
            Factory function for making FixedShiftWrapDSP instances from shift
        """

        def factory(shift: float) -> FixedShiftCore:
            """FixedShiftWrapDSP instances from shift using preselected order
            Arguments:
                shift: The fixed shift
            """
            return FixedShiftWrapDSP(order, shift)

        return factory
