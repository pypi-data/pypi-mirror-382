"""Utilities for defining IIR filters and filtering 1D numpy arrays

This module provides basic definitions for IIR filters and functionality
to apply them to 1D numpy arrays. The streams.iirfilter module uses
this module for applying IIR filter to streams, i.e. chunked sata processing.

To define an IIR filter, use the class DefFilterIIR. The filters are specified
by their coefficients. There are convinience functions for setting up various
iir filter types: make_iir_def_derivative(), make_iir_def_cumsum(), and
make_iir_def_trapezoidal().

The filter definitions can be used to create corresponding functions operating
on numpy arrays. For this, use the `make_filter_iir_numpy` function.

When applying IIR filters, one needs to specify initial conditions to handle
the left boundary. The available options are specified using the IIRFilterIC
enum class.

Example use:

>>> input_data = np.linspace(0, 100, 103)
>>> iir_def = make_iir_def_cumsum()
>>> iir_filt = make_filter_iir_numpy(iir_def, IIRFilterIC.ZEROPAD)
>>> filtered_data = iir_filt(input_data)


Internally, the module is organized as follows.
The main engine is the IIRCoreOp class. It implements a protocol
SequentialNumpyMapType which describes an operation that can be applied
repeatedly to numpy arrays and has an internal state that can change
on each call. An important constraint is the convention that the result
of applying a SequentialNumpyMapType operation sequentially on chunks of
a larger array does not depend on the chunk sizes, but only on the array
and the initial internal state. Another aspect of the SequentialNumpyMapType is
to provide an internal state for use with the first array, i.e. the initial
condition.

The IIRCoreOp implements the SequentialNumpyMapType for IIR filters, using
scipy's IIR filter functions. The internal state is the initial condition
for the iir filter. This generalization SequentialNumpyMapType is useful when
implementing such operations for chunked processing.

The filter_iir_numpy() function uses IIRCoreOp to apply a DefFilterIIR filter
definition to a whole numpy array, setting up initial conditions according
to boundary condition specified using the IIRFilterIC enum. Finally, the
make_filter_iir_numpy() function turns the above into an unary operator,
binding all arguments except the array to be filtered.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Iterable, Protocol

import numpy as np
from attrs import field, frozen
from scipy import signal

from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


@frozen
class DefFilterIIR:
    r"""This dataclass defines a IIR filter

    The infinite impulse response filter is given by

    .. math::
       y_n = \frac{1}{a_0} \left(
                      b_0 x_n + b_1 x_{n-1} + \ldots + b_M x_{n-M}
                      - a_1 y_{n-1} - \ldots - a_N y_{n-N}
                      \right)


    Attributes:
        coeffs_a: Filter coefficients :math:`a_i`
        coeffs_b: Filter coefficients :math:`b_i`

    """

    coeffs_a: list[float] = field(converter=lambda lst: [float(e) for e in lst])
    coeffs_b: list[float] = field(converter=lambda lst: [float(e) for e in lst])

    @coeffs_a.validator
    def check(self, _, value):
        """Validate filter coefficients a"""
        if len(value) < 1:
            msg = "IIR filter coeff_a needs at least one entry"
            raise ValueError(msg)
        if value[0] == 0:
            msg = "IIR filter coeff_a[0] cannot be zero"
            raise ValueError(msg)


def make_iir_def_derivative(dx: float) -> DefFilterIIR:
    """Return IIR filter definition for time derivative as first order finite differences

    Arguments:
        dx: constant grid spacing
    """
    coeffs_a = [1.0]
    coeffs_b = [1 / dx, -1 / dx]
    return DefFilterIIR(coeffs_b=coeffs_b, coeffs_a=coeffs_a)


def make_iir_def_cumsum() -> DefFilterIIR:
    """Return IIR filter definition equivalent to cumulative sum"""
    coeffs_a = [1.0, -1.0]
    coeffs_b = [1.0]
    return DefFilterIIR(coeffs_b=coeffs_b, coeffs_a=coeffs_a)


def make_iir_def_trapezoidal(dx: float) -> DefFilterIIR:
    """Return IIR filter definition equivalent to integration with trapezoidal rule

    Arguments:
        dx: constant grid spacing
    """
    coeffs_a = [1.0, -1.0]
    h = 0.5 * dx
    coeffs_b = [h, h]
    return DefFilterIIR(coeffs_b=coeffs_b, coeffs_a=coeffs_a)


class IIRFilterIC(Enum):
    """Enum for various methods of constructing initial state in IIR filters

    STEADY:  Initial conditions chosen such that, given some constant,
    applying the filter to a constant sequence of the same value will
    result in a constant output. Note this is not possible for all filters.
    It will fail for a cumsum filter. For the 1st order finite difference
    filter on the other hand, filtering the constant sequence will result
    in a sequence of zeroes.

    ZEROPAD: Initial conditions chosen as if preceeding data is all zero
    """

    STEADY = 1
    ZEROPAD = 2


class SequentialNumpyMapType(Protocol):  # pylint: disable = too-few-public-methods
    """This protocol represents a transformation of arrays that can be applied to consecutive segments.

    The transformation is computed by calling the `apply` method in ascending order
    on contiguous segments of the whole array. The transformation exposes an internal
    state that is obtained from the `initial state` and `apply` methods and needs
    to be passed along in each call to `apply`. The convention is that the transform
    result does not depend on the choice of segments boundaries. The internal state
    should not be used or manipulated in any way by the caller. The transformation
    is not allowed to have any internal state in addition to the exposed one, and
    is not allowed to have side effects (except for testing and debugging purposes).
    """

    def initial_state(self, first: float) -> Any:
        """Compute initial conditions

        Arguments:
            first: first element of data to be filtered
        """

    def apply(self, chunk: NumpyArray1D, fstate: Any) -> tuple[NumpyArray1D, Any]:
        """The filter function

        Arguments:
            chunk: Segment of larger 1D array, either the first one or the one following the
                   segment from the previous call.
            fstate: filter state
        Returns:
            Tuple with transformed array and new filter state
        """


class IIRCoreOp(SequentialNumpyMapType):  # pylint: disable = too-few-public-methods
    """Function class for applying IIR filter to numpy array

    The object can be called either on a whole array or sequentially
    on smaller, contiguous, non-overlapping segments in strictly ascending
    order. For the first case, use the `__call__` method. for the latter,
    first call the `initial state` method to get initial conditions for the
    first segment. Then use the `apply` method to process each segment and
    obtain initial conditions for processing the next segment.
    """

    def __init__(self, fdef: DefFilterIIR, ic: IIRFilterIC):
        """Constructor

        Arguments:
            fdef: The definition of the IIR filter to be employed
            ic: Which prescription to use for initial filter state
        """
        self._fdef = fdef
        self._ic = ic
        self._a = np.array(fdef.coeffs_a)
        self._b = np.array(fdef.coeffs_b)

    def _initial_state_zero(self) -> np.ndarray:
        """Initial IIR filter state according to ZEROPAD prescription"""
        return np.zeros(max(len(self._a), len(self._b)) - 1)

    def _initial_state_steady(self, x0: float) -> np.ndarray:
        """Initial IIR filter state according to STEADY prescription

        Arguments:
            x0: value for which input constant sequence will yield constant output
        """
        return signal.lfilter_zi(self._b, self._a) * x0

    def initial_state(self, first: float) -> Any:
        """Set up initial state for IIR filter.

        Arguments:
            first: First element of data to be filtered

        Returns:
            Filter initial conditions
        """

        match self._ic:
            case IIRFilterIC.STEADY:
                fstate = self._initial_state_steady(first)
            case IIRFilterIC.ZEROPAD:
                fstate = self._initial_state_zero()
            case _:
                msg = f"Initial filter state {self._ic} not implemented"
                raise RuntimeError(msg)
        return fstate

    def apply(self, chunk: NumpyArray1D, fstate: Any) -> tuple[NumpyArray1D, Any]:
        """Apply IIR filter to a segment of a 1D numpy array.

        The filtered data has the same length as the input.

        Arguments:
            chunk: 1D array segment to be filtered
            fstate: filter initial conditions for this segment

        Returns:
            Tuple with filtered data and initial conditions for next segment
        """

        y, fstate = signal.lfilter(self._b, self._a, chunk, zi=fstate)

        return make_numpy_array_1d(y), fstate

    def __call__(self, data: NumpyArray1D) -> NumpyArray1D:
        """Apply filter to whole 1D numpy array at once.

        Arguments:
            data: The array to be filtered

        Returns:
            The filtered data, with same length as input
        """
        fstate = self.initial_state(data[0])
        y, _ = self.apply(data, fstate)
        return y


class IIRChainCoreOp(
    SequentialNumpyMapType
):  # pylint: disable = too-few-public-methods
    """Function class for applying a chain of IIR filters to a numpy array

    The object can be called either on a whole array or sequentially
    on smaller, contiguous, non-overlapping segments in strictly ascending
    order. For the first case, use the `__call__` method. for the latter,
    first call the `initial state` method to get initial conditions for the
    first segment. Then use the `apply` method to process each segment and
    obtain initial conditions for processing the next segment.
    """

    def __init__(self, fdef: Iterable[DefFilterIIR], ic: IIRFilterIC):
        """Constructor.

        The initial condition type is the same for all filters. An empty list of
        filters is legal and correponds to not applying any filter, i.e. the identity.

        Arguments:
            fdef: The definition of the IIR filter to be employed
            ic: Which prescription to use for initial filter state
        """
        self._filters = [IIRCoreOp(d, ic) for d in fdef]

    def initial_state(self, first: float) -> Any:
        """Set up initial state for IIR filter chain.

        Arguments:
            first: First element for first filter in the chain.

        Returns:
            Filter chain initial conditions
        """
        fstate = []
        for filti in self._filters:
            fsi = filti.initial_state(first)
            first = filti.apply(make_numpy_array_1d(np.array([first])), fsi)[0][0]
            fstate.append(fsi)
        return np.array(fstate)

    def apply(self, chunk: NumpyArray1D, fstate: Any) -> tuple[NumpyArray1D, Any]:
        """Apply IIR filter chain to a segment of a 1D numpy array.

        The filtered data has the same length as the input.

        Arguments:
            chunk: 1D array segment to be filtered
            fstate: filter initial conditions for this segment

        Returns:
            Tuple with filtered data and initial conditions for next segment
        """

        fstate_new = []
        y = chunk
        for filti, fsi in zip(self._filters, fstate):
            y, nfsi = filti.apply(y, fsi)
            fstate_new.append(nfsi)

        return make_numpy_array_1d(y), np.array(fstate_new)

    def __call__(self, data: NumpyArray1D) -> NumpyArray1D:
        """Apply filter to whole 1D numpy array at once.

        Arguments:
            data: The array to be filtered

        Returns:
            The filtered data, with same length as input
        """
        fstate = self.initial_state(data[0])
        y, _ = self.apply(data, fstate)
        return y


def filter_iir_numpy(
    fdef: DefFilterIIR, ic: IIRFilterIC, data: np.ndarray
) -> NumpyArray1D:
    """Filter a 1D numpy array using an IIR filter.

    Arguments:
        fdef: The definition of the IIR filter
        ic: Which prescription to use for initial filter state
        data: The numpy array to be filtered

    Returns:
        Filtered numpy array
    """
    fmap = IIRCoreOp(fdef, ic)
    return fmap(make_numpy_array_1d(data))


def make_filter_iir_numpy(
    fdef: DefFilterIIR, ic: IIRFilterIC
) -> Callable[[np.ndarray], NumpyArray1D]:
    """Create a filter function that accepts a 1D numpy array and returns
    the array filtered according to the given filter definition.


    Arguments:
        fdef: The definition of the IIR filter
        ic: Which prescription to use for initial filter state

    Returns:
        Filter function
    """

    def op(data: np.ndarray) -> NumpyArray1D:
        """Apply IIR filter to 1D numpy array"""
        return filter_iir_numpy(fdef, ic, make_numpy_array_1d(data))

    return op


def get_iir_steady_state(fdef: DefFilterIIR, const: float) -> float:
    """Compute constant output when applying IIR filter to infinite constant sequence

    Not all filter coefficients have a steady state, this raises an exception if not.

    Arguments:
        fdef: The IIR filter definition to get steady state for
        const: the constant value of the assumed input sequence

    Returns:
        The constant value of the output sequence
    """
    op = IIRCoreOp(fdef, IIRFilterIC.STEADY)
    state = op.initial_state(const)
    ca = np.empty(2)
    ca[:] = const
    return op.apply(ca, state)[0][-1]


def get_iir_chain_steady_state(fdef: Iterable[DefFilterIIR], const: float) -> float:
    """Like get_iir_steady_state but for filter chains

    Not all filter coefficients have a steady state, this raises an exception if not.

    Arguments:
        fdef: IIR filters of the chain in order of application
        const: the constant value of the assumed input sequence

    Returns:
        The constant value of the output sequence
    """
    for d in fdef:
        const = get_iir_steady_state(d, const)
    return const
