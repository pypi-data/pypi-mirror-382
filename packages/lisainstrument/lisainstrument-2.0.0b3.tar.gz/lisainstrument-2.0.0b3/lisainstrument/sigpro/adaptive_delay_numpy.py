"""Time shift operator employing dynamic or fixed shift to numpy arrays

AdaptiveShiftNumpy is a wrapper that stores a fixed and a dynamic time shift
operators and uses the appropriate one when called.
"""

from typing import Callable

import numpy as np


class AdaptiveShiftNumpy:  # pylint: disable=too-few-public-methods
    """Time shifting that accepts fixed or dynamic shifts as well as constant data

    Instances  act as interpolator function, which delegates to interpolation
    methods for fixed or dynamic time shifting. The specialised interpolation
    functions are provided during construction.

    In addition, instances store a fixed sample rate that is assumed for any
    interpolated data, allowing time shifts to be given in time units.
    """

    def __init__(
        self,
        delay_const: Callable[[np.ndarray, float], np.ndarray],
        delay_dynamic: Callable[[np.ndarray, np.ndarray], np.ndarray],
        fsample: float,
    ):
        """Construct from fixed and dynamic interpolator functions and sample rate

        Arguments:
            delay_const: Interpolator function with same interface as FixedShiftNumpy
            delay_dynamic: Interpolator function with same interface as DynamicShiftNumpy
            fsample: Sample rate [Hz]
        """
        self._delay_const = delay_const
        self._delay_dynamic = delay_dynamic
        self._fsample = float(fsample)

    def fixed(self, x: np.ndarray | float, shift_time: float) -> np.ndarray | float:
        """Apply fixed timeshift

        Arguments:
            x: the data to be shifted, as scalar or 1D array
            shift_time: scalar time shift [s]
        """
        if isinstance(x, np.ndarray):
            shift_samps = float(shift_time * self._fsample)
            if shift_samps == 0:
                return x
            return self._delay_const(x, shift_samps)
        return float(x)

    def dynamic(
        self, x: np.ndarray | float, shift_time: np.ndarray
    ) -> np.ndarray | float:
        """Apply dynamic time shift

        The shift is given in time units, and the data is assumed to be sampled
        with rate fsample given in the constructor.

        Both data and time shift can be scalar or 1D numpy arrays. Scalars
        are interpreted as constant arrays. In case of scalar data, the same
        scalar is returned. In case of scalar shift, a more efficient algorithm
        is used, which should yield identical results as for a const shift array.

        Args:
            x: the data to be shifted, as scalar or 1D array
            shift_time: time shift [s], as 1D array

        Returns:
            The shifted data
        """
        if isinstance(x, np.ndarray):
            return self._delay_dynamic(x, shift_time * self._fsample)
        return float(x)

    def _apply(
        self,
        x: np.ndarray | float,
        shift_time: np.ndarray | float,
        shift_is_delay: bool,
    ) -> np.ndarray | float:
        """Apply time shift with option to specify sign of shift definition

        Args:
            x: the data to be shifted, as scalar or 1D array
            shift_time: time shift [s], as scalar or 1D array
            shift_is_delay: If True, flip sign of shift_time

        Returns:
            The shifted data
        """
        if shift_is_delay:
            shift_time = -shift_time

        if isinstance(shift_time, np.ndarray):
            return self.dynamic(x, shift_time)
        return self.fixed(x, shift_time)

    def shift(
        self, x: np.ndarray | float, shift_time: np.ndarray | float
    ) -> np.ndarray | float:
        """Apply adaptive time shift to sequence, chosing most efficient method

        The shift is given in time units, and the data is assumed to be sampled
        with rate fsample given in the constructor.
        A positive shift means the result depends on data to the right.

        Both data and time shift can be constant or non-constant sequences,
        represented by 1d numpy arrays or float values, respectively.
        Shifting a constant sequence results in the same constant sequence, as
        constant sequences are interpreted as infinite (no boundaries).
        Shifting a non-constant sequence applies the most efficient method depending
        if the shift is variable, constant, or zero.

        Args:
            x: the data to be shifted
            shift_time: time shift [s]

        Returns:
            The shifted data
        """
        return self._apply(x, shift_time=shift_time, shift_is_delay=False)

    def delay(
        self, x: np.ndarray | float, delay_time: np.ndarray | float
    ) -> np.ndarray | float:
        """Like shift, but specified in terms of a delay, with opposite sign

        A positive delay means the result depends on data to the left (aka the past).

        Args:
            x: the data to be shifted
            delay_time: time delay (= -shift_time) [s]

        Returns:
            The delayed data
        """
        return self._apply(x, shift_time=delay_time, shift_is_delay=True)
