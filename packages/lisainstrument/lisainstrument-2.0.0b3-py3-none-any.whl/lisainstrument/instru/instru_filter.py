"""Tools for setting up delay operators according to Instrument parameters

The InstruDelays class provides the various delay and shift inversion operators
used in the simulator.
"""

import logging
from typing import Callable

import numpy as np

from lisainstrument.sigpro import (
    DefFilterFIR,
    make_fir_causal_kaiser,
    make_fir_causal_normal_from_coeffs,
)
from lisainstrument.streams import (
    StreamBase,
    stream_delay_lagrange,
    stream_filter_fir,
    stream_shift_inv_lagrange,
)


def stream_filter_none(s: StreamBase) -> StreamBase:
    """Identity operator for streams to represent filter that does nothing"""
    return s


def init_aafilter(
    aafilter: tuple[str, float, float, float] | list[float] | np.ndarray | None,
    fsample: float,
) -> tuple[Callable[[StreamBase], StreamBase], list[float] | None, float]:
    r"""Initialize antialiasing filter.

    The aafilter parameter can be one of the following:

    None: this disables filtering
    A tuple of the form ("kaiser", attenuation, freq1, freq2): Set up Kaiser
    window, see make_fir_causal_kaiser for details
    A list or 1D numpy array: FIR filter coefficients. Those will be normalized.
    FIR filter coefficients for the antialiasing filter have to be symmetric.

    The constructed AA filter has unity gain and is causal. i.e. an element
    with index k in the output array is constructed from elements i=k-L+1..k
    where L is the number of FIR coefficients.

    The group delay for the above choice is given by


    .. math::

       \tau = \Delta t_\mathrm{phys} \frac{N-1}{2}

    where :math:`N` is the number of FIR filter coefficients and :math:`\Delta t_\mathrm{phys}`


    Args:
        aafilter: Instrument aafilter parameter
        fsample: sample rate [Hz] of data that filter will be applied to

    Returns:
        Filter operator, FIR coefficients or None, and group delay of filter
    """

    logger = logging.getLogger(__name__)
    filt_def: DefFilterFIR | None = None
    match aafilter:
        case None:
            filt_def = None
        case ("kaiser", 0, _freq1, _freq2):
            msg = "Kaiser filter with zero attenuation no longer allowed, use aafilter=None to disable filtering"
            raise RuntimeError(msg)
        case ("kaiser", attenuation, freq1, freq2):
            filt_def = make_fir_causal_kaiser(
                fsample,
                float(attenuation),
                float(freq1),
                float(freq2),
            )
            logger.debug("Designing finite-impulse response filter from Kaiser window")
            logger.debug("Filter attenuation is %s dB", attenuation)
            logger.debug("Filter transition band is [%s Hz, %s Hz]", freq1, freq2)
            # ~ logger.debug("Filter details: {%s}", filt_def)
        case list() | np.ndarray():
            filt_def = make_fir_causal_normal_from_coeffs(aafilter)
            if not np.all(filt_def.filter_coeffs == np.flip(filt_def.filter_coeffs)):
                msg = "AA filter coefficients must be symmetric"
        case func if callable(func):
            msg = "Custom callables as AA filters forbidden since change to chunked processing"
            raise RuntimeError(msg)
        case _:
            msg = f"Invalid aafilter parameters {aafilter}"
            raise RuntimeError(msg)

    aafilter_op: Callable[[StreamBase], StreamBase]
    if filt_def is None:
        aafilter_op = stream_filter_none
        fir_coeffs = None
        group_delay = 0.0
    else:
        aafilter_op = stream_filter_fir(filt_def)
        fir_coeffs = filt_def.filter_coeffs
        group_delay = (filt_def.length - 1) / (2 * fsample)

    return aafilter_op, fir_coeffs, group_delay


class InstruDelays:
    """This class provides the delay and shift inversion operators used in the simulator"""

    def __init__(
        self,
        interpolation: None | tuple[str, int],
        delay_isc_min: float,
        delay_isc_max: float,
        delay_clock_max: float,
        clockinv_tolerance: float,
        clockinv_maxiter: int,
        fsample: float,
    ) -> None:
        """Initialize or design the interpolation functions for the delays

        We support no interpolation or Lagrange interpolation.
        This sets up two interpolation methods, one for dynamic delays and one
        for constant delays.
        This also sets up the time frame inversion methods, using the same
        interpolator in the internal inversion algorithm. The delay_clock_max
        parameter is also used there during the internal interpolation.

        The user has to provide a minimum and maximum delay for any timeshift
        the interpolator has to handle. This is a technical constraint from
        working with chunked processing. Note: making the limits too wide causes
        unnecessarily large margins in internal computations.

        Note: There are no boundary conditions anymore. The streaming framework
        evaluates any stream on a suitably enlarged range automatically.

        Args:
            interpolation: see `interpolation` docstring in `__init__()`
            delay_isc_min: Minimum allowed interspacecraft delay [s]
            delay_isc_max: Maximum allowed interspacecraft delay [s]
            delay_clock_max: Maximum allowed absolute delay [s] between clocks/tpc/tcp
            clockinv_tolerance: Tolerance [s] for inverting time coordinate transforms
            clockinv_maxiter: Maximum iterations for time frame inversion scheme
            fsample: Sample rate [Hz] of data which operators will be applied to
        """

        match clockinv_tolerance:
            case float() | int() if clockinv_tolerance > 0:
                self._clockinv_tolerance = float(clockinv_tolerance)
            case _:
                msg = f"Invalid clockinv_tolerance parameter {clockinv_tolerance}"
                raise ValueError(msg)

        match clockinv_maxiter:
            case int() if clockinv_maxiter > 0:
                self._clockinv_maxiter = clockinv_maxiter
            case _:
                msg = f"Invalid clockinv_maxiter parameter {clockinv_maxiter}"
                raise ValueError(msg)

        match delay_clock_max:
            case float() | int() if delay_clock_max >= 0:
                self._delay_clock_max = float(delay_clock_max)
            case _:
                msg = f"Invalid delay_clock_max parameter {delay_clock_max}"
                raise ValueError(msg)

        match delay_isc_min:
            case float() | int() if delay_isc_min >= 0:
                self._delay_isc_min = float(delay_isc_min)
            case _:
                msg = f"Invalid delay_isc_min parameter {delay_isc_min}"
                raise ValueError(msg)

        match delay_isc_max:
            case float() | int() if delay_isc_max >= 0:
                self._delay_isc_max = float(delay_isc_max)
            case _:
                msg = f"Invalid delay_isc_max parameter {delay_isc_max}"
                raise ValueError(msg)

        if delay_isc_max < delay_isc_min:
            msg = f"Maximum interspacecraft delay {delay_isc_min} below minimum delay {delay_isc_min} specified"
            raise ValueError(msg)

        match interpolation:
            case None:
                self._delay_isc = lambda x, _: x
                self._delay_clock = self._delay_isc
            case (
                "lagrange",
                int(order),
            ):
                self._delay_isc = stream_delay_lagrange(
                    delay_isc_min, delay_isc_max, 1 / fsample, order
                )

                self._delay_clock = stream_delay_lagrange(
                    -delay_clock_max, delay_clock_max, 1 / fsample, order
                )

                self._shift_inversion = stream_shift_inv_lagrange(
                    order=order,
                    sample_dt=1.0 / fsample,
                    max_abs_shift=delay_clock_max,
                    max_iter=self._clockinv_maxiter,
                    tolerance=self._clockinv_tolerance,
                )

                self._interpolation_order = order

            case (
                "lagrange_dsp",
                int(order),
            ):
                msg = "Legacy dsp interpolator option temporarily disabled"
                raise RuntimeError(msg)

            case func if callable(func):
                msg = "Custom callables as interpolation method forbidden since switch to chunked processing"
                raise RuntimeError(msg)
            case _:
                msg = f"Invalid interpolation parameters {interpolation}"
                raise RuntimeError(msg)

        self._delay_electro = self._delay_isc

    @property
    def clockinv_tolerance(self) -> float:
        """Tolerance [s] for inverting time coordinate transforms"""
        return self._clockinv_tolerance

    @property
    def clockinv_maxiter(self) -> float:
        """clockinv_maxiter: Maximum iterations for time frame inversion scheme"""
        return self._clockinv_maxiter

    @property
    def interpolation_order(self) -> int:
        """Interpolation order"""
        return self._interpolation_order

    @property
    def delay_isc_min(self) -> float:
        """Minimum allowed interspacecraft delay [s]"""
        return self._delay_isc_min

    @property
    def delay_isc_max(self) -> float:
        """Maximum allowed interspacecraft delay [s]"""
        return self._delay_isc_max

    @property
    def delay_clock_max(self) -> float:
        """Maximum allowed absolute delay [s] between clocks/tpc/tcp"""
        return self._delay_clock_max

    @property
    def delay_isc(self) -> Callable[[StreamBase, StreamBase], StreamBase]:
        """Delay operator for interspacecraft propagation"""
        return self._delay_isc

    @property
    def delay_clock(self) -> Callable[[StreamBase, StreamBase], StreamBase]:
        """Delay operator for time frame transformations"""
        return self._delay_clock

    @property
    def delay_electro(
        self,
    ) -> Callable[[StreamBase, StreamBase], StreamBase]:
        """Delay operator for electronic delays"""
        return self._delay_electro

    @property
    def shift_inversion(self) -> Callable[[StreamBase], StreamBase]:
        """Operator for time frame transform inversion"""
        return self._shift_inversion
