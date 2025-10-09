"""Utilities for defining FIR filters and filtering 1D numpy arrays

This module provides basic definitions for FIR filters and functionality
to apply them to simple 1D numpy arrays. This is used in the streams.firfilter
module to apply FIR filter to streams in chunked data processing.

To define a FIR filter, use the class DefFilterFIR. The filters are specified
by their coefficients and the center location. Instances of DefFilterFIR provide
the required margin sizes (domain of dependence). To set up such a filter where
the center location corresponds to what is called a causal filter, use
make_fir_causal_normal_from_coeffs(). Further, there is a convinience function
make_fir_causal_kaiser() to  set up a FIR definition for a Kaiser window.

The filter definitions can be used to create corresponding functions operating
on numpy arrays. For this, use the `make_filter_fir_numpy` function.

When applying FIR filters, one needs to specify boundary conditions. The
available options are specified using the EdgeHandling enum class.

Example use:

>>> input_data = np.linspace(0, 100, 103)
>>> fir_coeffs = [0.1, 0.7, 0.1, 0.1]
>>> fir_def = DefFilterFIR(filter_coeffs=fir_coeffs, offset=-1)
>>> fir_filt = make_filter_fir_numpy(fir_def, EdgeHandling.ZEROPAD, EdgeHandling.VALID)
>>> filtered_data = fir_filt(input_data)


Internally, the module is organized as follows.
The application of a FIR filter without handling boundary conditions is
implemented in a class FIRCoreOp. It requires that the input arrays
are already suitably padded with margins. This requirement is not exclusive
to FIR filters. It is encoded in the SemiLocalMapType protocol which is
implemented by FIRCoreOp. This generalization is useful when implementing
filters in chunked processing.

Applying a transform of the SemiLocalMapType to a numpy array is the purpose of
the semilocal_map_numpy() function. This also takes care of the boundary
conditions by padding its input accordingly. The special case of applying
a FIR filter is handled by the convenience function filter_fir_numpy().
Finally, the make_filter_fir_numpy() function turns the above into an
unary operator, binding all arguments except the array to be filtered.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, Protocol, TypeAlias

import numpy as np
from attrs import field, frozen
from scipy.signal import convolve, firwin, kaiserord

from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


@frozen
class DefFilterFIR:
    r"""This dataclass defines a FIR filter

    The finite impulse response filter is given by

    .. math::
       y_a = \sum_{i=0}^{L-1} K_i x_{a + i + D}
           = \sum_{k=a+D}^{a+D+L-1} x_{k} K_{k-a-D}


    Note that there are different conventions for the order of coefficients.
    In standard convolution notation, the convolution kernel is given by the
    coefficients above in reversed order.


    Attributes:
        filter_coeffs: Filter coefficients :math:`K_i`
        offset: Offset :math:`D`
    """

    filter_coeffs: list[float] = field(converter=lambda lst: [float(e) for e in lst])

    offset: int = field()

    @filter_coeffs.validator
    def check(self, _, value):
        """Validate filter coefficients"""
        if len(value) < 1:
            msg = "FIR filter coefficients array needs at least one entry"
            raise ValueError(msg)

    @property
    def gain(self) -> float:
        r"""The gain factor for a constant signal

        The gain factor is defined by

        .. math:
           \sum_{i=0}^{L-1} K_i

        """
        return sum(self.filter_coeffs)

    @property
    def length(self) -> int:
        """The length of the domain of dependence of a given output sample
        on the input samples. This does not take into account zeros anywhere
        in the coefficients. Thus the result is simply the number of
        coefficients.
        """
        return len(self.filter_coeffs)

    @property
    def domain_of_dependence(self) -> tuple[int, int]:
        r"""The domain of dependence

        A point with index :math:`a` in the output sequence depends on
        indices :math:`a+D \ldots a+D+L-1`. This property provides the
        domain of dependence for :math:`a=0`.
        """

        return (self.offset, self.length - 1 + self.offset)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} \n"
            f"Length           = {self.length} \n"
            f"Offset           = {self.offset} \n"
            f"Gain             = {self.gain} \n"
            f"Coefficients     = {self.filter_coeffs} \n"
        )


def make_fir_causal_kaiser(
    fsamp: float, attenuation: float, freq1: float, freq2: float
) -> DefFilterFIR:
    """Create FIR filter definition for Kaiser window with given attenuation and transition band

    This creates FIR coefficients from a Kaiser window specified by the
    desired properties of attenuation and transition band. The filter offset
    is set to describe a completely causal filter.

    Arguments:
        fsamp: Sampling rate [Hz]. Must be strictly positive.
        attenuation: Required stop-band attenuation [dB]. Has to be greater zero.
        freq1: Start of transition band [Hz]
        freq2: End of transition band / start of stop band [Hz]. Has to be below Nyquist frequency.

    Returns:
        The FIR definition
    """

    if fsamp <= 0:
        msg = f"make_fir_causal_kaiser: sample rate must be greater zero, got {fsamp=}"
        raise ValueError(msg)

    if freq2 <= freq1:
        msg = f"make_fir_causal_kaiser: end of transition band cannot be below beginning ({freq1=}, {freq2=})"
        raise ValueError(msg)

    if freq1 <= 0:
        msg = f"make_fir_causal_kaiser: start of transition band has to be greater zero, got {freq1=}"
        raise ValueError(msg)

    if freq2 >= fsamp / 2:
        msg = f"make_fir_causal_kaiser: end of transition band has to be below Nyquist, got {freq1=}"
        raise ValueError(msg)

    if attenuation <= 0:
        msg = f"make_fir_causal_kaiser: attenuation must be strictly positive, got {attenuation}"
        raise ValueError(msg)

    nyquist = fsamp / 2
    numtaps, beta = kaiserord(attenuation, (freq2 - freq1) / nyquist)
    taps = firwin(numtaps, (freq1 + freq2) / fsamp, window=("kaiser", beta))

    return DefFilterFIR(filter_coeffs=taps, offset=1 - len(taps))


def make_fir_causal_normal_from_coeffs(coeffs: ArrayLike) -> DefFilterFIR:
    """Create causal, unity-gain FIR filter definition from coefficients.

    This creates FIR coefficients from FIR coefficients. The latter are
    normalized first such that the filter has unity gain. The filter offset
    is set to describe a completely causal filter.

    Arguments:
        coeffs: filter coefficients

    Returns:
        The FIR definition
    """
    coeffs = np.array(coeffs)
    norm = np.sum(coeffs)
    if norm == 0:
        msg = "make_fir_causal_normal_from_coeffs: cannot normalize zero-gain coefficients"
        raise ValueError(msg)
    normed_coeffs = coeffs / norm
    return DefFilterFIR(filter_coeffs=normed_coeffs, offset=1 - len(coeffs))


class SemiLocalMapType(Protocol):
    """Protocol for semi-local maps of 1D numpy arrays

    This is used to describe array operations which require boundary points
    """

    @property
    def margin_left(self) -> int:
        """How many points at the left boundary are missing in the output"""

    @property
    def margin_right(self) -> int:
        """How many points at the right boundary are missing in the output"""

    def __call__(self, data_in: NumpyArray1D) -> NumpyArray1D:
        """Apply the array operation"""


class FIRCoreOp(SemiLocalMapType):
    """Function class applying FIR to numpy array

    This does not include boundary tratment and only returns valid
    points. It does provide the margin sizes corresponding to invalid
    boundary points on each side.

    """

    def __init__(self, fdef: DefFilterFIR):
        self._margin_left = -fdef.domain_of_dependence[0]
        self._margin_right = fdef.domain_of_dependence[1]
        self._convolution_kernel = np.array(fdef.filter_coeffs[::-1], dtype=np.float64)

        if self._margin_left < 0 or self._margin_right < 0:
            msg = f"FilterFirNumpy instantiated with unsupported domain of dependence {fdef.domain_of_dependence}"
            raise ValueError(msg)

    @property
    def margin_left(self) -> int:
        """How many points at the left boundary are missing in the output"""
        return self._margin_left

    @property
    def margin_right(self) -> int:
        """How many points at the right boundary are missing in the output"""
        return self._margin_right

    def __call__(self, data_in: NumpyArray1D) -> NumpyArray1D:
        """Apply FIR filter using convolution

        Only valid points are returned, i.e. points for which the filter stencil fully
        overlaps with the data. No zero padding or similar is applied.

        Arguments:
            data_in: 1D numpy array to be filtered

        Returns:
            Filtered array. Its size is smaller than the input by `m̀argin_left+margin_right`.

        """
        return convolve(data_in, self._convolution_kernel, mode="valid")


class EdgeHandling(Enum):
    """Enum for various methods of handling boundaries in filters.

    VALID:   Use only valid points that can be computed from the given data,
             without zero padding or similar
    ZEROPAD: Compute output for every input point, pad input with suitable
             number of zeros before applying filter.
    """

    VALID = 1
    ZEROPAD = 2


def semilocal_map_numpy(
    op: SemiLocalMapType,
    bound_left: EdgeHandling,
    bound_right: EdgeHandling,
    data: NumpyArray1D,
) -> NumpyArray1D:
    """Apply a semi local map to numpy array and employ boundary conditions.

    Arguments:
        op: the semi local mapping
        bound_left: Boundary treatment on left side
        bound_right: Boundary treatment on right side
        data: the 1D array to be mapped

    Returns:
        The mapped data. The size is the same as the input if both boundary
        conditions are ZEROPAD. A boundary condition VALID reduces the output
        size by the corresponding margin size of the semilocal map.
    """

    if op.margin_left < 0 or op.margin_right < 0:
        msg = (
            f"semilocal_map_numpy: mappings with negative"
            f" margin not supported (got left={op.margin_left}, right={op.margin_right})"
        )
        raise RuntimeError(msg)

    pad_left = op.margin_left if bound_left == EdgeHandling.ZEROPAD else 0
    pad_right = op.margin_right if bound_right == EdgeHandling.ZEROPAD else 0
    if pad_left != 0 or pad_right != 0:
        data = make_numpy_array_1d(
            np.pad(
                data,
                pad_width=(pad_left, pad_right),
                mode="constant",
                constant_values=0,
            )
        )
    return op(data)


FilterFirNumpyType: TypeAlias = Callable[[np.ndarray], NumpyArray1D]


def filter_fir_numpy(
    fdef: DefFilterFIR,
    bound_left: EdgeHandling,
    bound_right: EdgeHandling,
    data: np.ndarray,
) -> NumpyArray1D:
    """Apply FIR filter to 1D numpy array

    Arguments:
        fdef: The definition of the FIR filter
        bound_left: Boundary treatment on left side
        bound_right: Boundary treatment on right side
        data: The 1D numpy array to be filtered

    Returns:
        Filtered 1D numpy array.
    """
    fmap = FIRCoreOp(fdef)
    return semilocal_map_numpy(fmap, bound_left, bound_right, make_numpy_array_1d(data))


def make_filter_fir_numpy(
    fdef: DefFilterFIR, bound_left: EdgeHandling, bound_right: EdgeHandling
) -> FilterFirNumpyType:
    """Create a function that applies a given FIR filter to numpy arrays,
    employing the specified boundary treatment.

    Arguments:
        fdef: The definition of the FIR filter
        bound_left: Boundary treatment on left side
        bound_right: Boundary treatment on right side

    Returns:
        Function which accepts a single 1D numpy array as input and returns
        the filtered array.
    """

    fmap = FIRCoreOp(fdef)

    def op(data: np.ndarray) -> NumpyArray1D:
        return semilocal_map_numpy(
            fmap, bound_left, bound_right, make_numpy_array_1d(data)
        )

    return op
