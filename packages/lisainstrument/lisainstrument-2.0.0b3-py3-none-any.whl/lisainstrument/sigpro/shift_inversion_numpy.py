"""
Time coordinate inversion
=========================

Functions for inverting a 1D (time)coordinate transform given as numpy array

The inversion function internally requires an interpolation operator implementing the
RegularInterpolator interface, and which is provided by the user. Use
make_shift_inverse_lagrange_numpy to create an inversion operator employing Lagrange
interpolation.
"""

from __future__ import annotations

from typing import Callable, Final

import numpy as np

from lisainstrument.sigpro.regular_interpolators import (
    RegularInterpolator,
    make_regular_interpolator_lagrange,
)
from lisainstrument.sigpro.types_numpy import NumpyArray1D, make_numpy_array_1d


def fixed_point_iter(
    f: Callable[[NumpyArray1D], NumpyArray1D],
    ferr: Callable[[NumpyArray1D, NumpyArray1D], float],
    x: NumpyArray1D,
    tolerance: float,
    max_iter: int,
) -> NumpyArray1D:
    r"""Perform a fixed point iteration for functions operating on a 1D array.

    This uses fixed-point iteration to find a solution for

    .. math::
       x = f(x)

    where :math:`x` is a 1D array and :math:`f` returns an array of the same size.

    The convergence criterion is provided by the user
    via a function :math:`r(x)` that returns a scalar error measure. The iteration
    is performed until :math:`r(x) < \epsilon`. If convergence is not achieved
    after a given number of iterations, an exception is raised.

    Arguments:
        f: The function :math:`f(x)`
        ferr: The error measure :math:`r(x)`
        x: The initial data for the iteration.
        tolerance: The tolerance :math:`\epsilon`
        max_iter: Maximum number of iterations

    Returns:
        Array with solution
    """
    for _ in range(max_iter):
        x_next = f(x)
        err = ferr(x, x_next)
        if err < tolerance:
            return x_next
        x = x_next
    msg = (
        f"ShiftInverseNumpy: iteration did not converge (error={err}, "
        f"tolerance={tolerance}), iterations={max_iter}"
    )
    raise RuntimeError(msg)


class ShiftInverseNumpy:  # pylint: disable=too-few-public-methods
    r"""Invert time coordinate transformation given as numpy array

    The purpose of this class is the inversion of a 1D coordinate transform
    :math:`v \rightarrow U(v)` between some coordinates :math:`u` and :math:`v`.
    The inverse is denoted :math:`u \rightarrow V(u)`, i.e. :math:`V(U(v)) = v`.

    The transform is expressed as a
    shift
    :math:`\delta U(v) = U(v) - v`.
    It will be provided as samples
    :math:`\delta U_k = \delta U(v_k)`
    at regularly spaced sample locations
    :math:`v_k = v_0 + k \Delta v`.

    The inverse will be expressed as
    :math:`\delta V(u) = u - V(u)`.
    It will be computed for locations
    :math:`u_l = u_0 + l \Delta u` regularly spaced with respect to the
    :math:`u`-coordinate, i.e. the output will be the sequence
    :math:`\delta V_l = u_l - V(u_l)`.

    Currently, we restrict to the special case where :math:`u_k = v_k`,
    i.e. identical offsets :math:`v_0 = u_0` and spacings :math:`\Delta u = \Delta v`.

    By convention, the coordinates refer to times, and coordinate shift,
    tolerance, and sample rate are all given in SI units.
    """

    def __init__(
        self,
        fsample: float,
        max_abs_shift: float,
        interp: RegularInterpolator,
        max_iter: int,
        tolerance: float,
    ):
        r"""Set up the coordinate inversion operator.

        One needs to provide the sample rate :math:`f_s` used
        both for input and output sequences. All calls to the operator will
        assume regularly sampled sequences with :math:`\Delta u = \Delta v = 1 / f_s`.

        For technical reasons, one also needs to provide a limit for the maximum
        shift between the coordinates, i.e. :math:`|\delta U(v)| < S_\mathrm{max}`.

        Another parameter is an interpolation operator to be used in the internal
        fixed-point iteration algorithm. One also needs to provide the desired
        accuracy of the resulting coordinate shift, as well as a limit for the
        allowed number of iterations before aborting with an exception.

        Arguments:
            fsample: Sample rate :math:`f_s > 0` [s]
            max_abs_shift: Upper limit :math:`S_\mathrm{max} \ge 0` [s] for coordinate shift
            interp: Interpolation operator
            max_iter: Maximum iterations before fail
            tolerance: Maximum absolute error [s] of result
        """

        self._fsample: Final = float(fsample)
        self._max_abs_shift_idx: Final = int(np.ceil(max_abs_shift * self._fsample))

        self._interp_np: Final = interp
        self._max_iter = int(max_iter)
        self._tolerance_idx = float(tolerance * self._fsample)

        if self._fsample <= 0:
            msg = f"ShiftInverseNumpy: fsample must be strictly positive, got {fsample}"
            raise ValueError(msg)

        if max_abs_shift < 0:
            msg = f"ShiftInverseNumpy: max_abs_shift must be positive, got {max_abs_shift}"
            raise ValueError(msg)

        if self._max_iter <= 0:
            msg = f"ShiftInverseNumpy: max_iter must be strictly positive integer, got {max_iter}"
            raise ValueError(msg)

    @property
    def margin_left(self) -> int:
        """Left margin size.

        Specifies how many samples on the left have to be added by boundary conditions.
        """
        return self._interp_np.margin_left + self._max_abs_shift_idx

    @property
    def margin_right(self) -> int:
        """Right margin size.

        Specifies how many samples on the right have to be added by boundary conditions.
        """
        return self._interp_np.margin_right + self._max_abs_shift_idx

    def __call__(self, shift: np.ndarray) -> NumpyArray1D:
        r"""Compute the inverse coordinate transform

        The coordinate transform is given an array with the sequence
        :math:`\delta U_k = \delta U(v_k)`. The sample locations :math:`v_k` do not have to be provided
        but are assumed to be regularly spaced, i.e.
        :math:`v_k = v_0 + k \Delta v`, and the first array element corresponds to
        :math:`k=0`.
        The output is given as an array with the sequence
        :math:`\delta V_l = u_l - V(u_l)` providing the shift
        at sample locations regularly spaced in the transformed coordinate
        :math:`u`, that is, at points :math:`u_l = u_0 + l \Delta u`. The first
        element of the output corresponds to :math:`l=0`.
        The output sample locations are not returned, but are implicitly
        equal to the input ones, meaning :math:`v_l = u_l`.


        The algorithm works using fixed point iteration
        :math:`\delta V_l^{n+1} = f(l,\delta V_l^{n})`,
        where
        :math:`f(l,d) = I[v_k, \delta U_k](v_l - d)`, and :math:`I[v_k, \delta U_k]` is a
        function obtained by interpolating the samples :math:`v_k, \delta U_k`,
        approximating  :math:`I[v_k, \delta U_k](v) \approx \delta U(v)`.
        On the technical level, the interpolation operator is implemented
        using shifts directly, with an interface of the form
        :math:`I[\delta U_k](d_l) \approx \delta U(v_l + d_l)`.
        Hence, :math:`f(l,d_l) = I[\delta U_k](-d_l) \approx \delta U(v_l - d_l)`.

        If the iteration converges, it converges to a solution
        :math:`\delta \bar{V}_l = f(l,\delta \bar{V}_l)
        \approx \delta U(v_l - \delta\bar{V}_l) =  \delta U(u_l - \delta\bar{V}_l)`,
        where we used the implicit convention that :math:`u_l = v_l`.
        This equation fulfilled for :math:`\delta\bar{V}_l` is indeed the one that
        needs to be fulfilled for the desired quantity :math:`\delta V_l`, which
        can be shown as follows:
        :math:`u_l = U(V(u_l)) = \delta U(V(u_l)) + V(u_l)` and hence
        :math:`\delta V_l = u_l - V(u_l) = \delta U(V(u_l)) = \delta U(u_l - \delta V_l)`.
        This shows that the iteration converges to the correct solution if
        it converges.

        The initial value is :math:`\delta V_l^0 = \delta U_l`.
        The iteration is repeated until
        :math:`\max_l |\delta V_l^{n+1} - \delta V_l^{n} | < \epsilon`,
        where :math:`\epsilon` is the tolerance specified when constructing
        the operator.

        During the interpolation, we use flat boundary conditions, meaning that
        any time shift sample required outside the provided range will be replaced
        by the value of the nearest available sample. The number of points potentially
        affected by boundary conditions is given by the margin_left and margin_right
        properties.


        Arguments:
            shift: 1D numpy array with shifts :math:`\delta U_k` [s]

        Returns:
            1D numpy array with shifts :math:`\delta V_l` [s]
        """

        shift_idx = shift * self._fsample
        dx = make_numpy_array_1d(shift_idx)

        dx_pad = np.pad(
            dx,
            (self.margin_left, self.margin_right),
            mode="constant",
            constant_values=(shift_idx[0], shift_idx[-1]),
        )

        def f_iter(x: NumpyArray1D) -> NumpyArray1D:
            return self._interp_np.apply_shift(dx_pad, -x, self.margin_left)

        def f_err(x1: NumpyArray1D, x2: NumpyArray1D) -> float:
            return np.max(np.abs(x1 - x2))

        shift_idx_inv = fixed_point_iter(
            f_iter, f_err, dx, self._tolerance_idx, self._max_iter
        )
        shift_inv = shift_idx_inv / self._fsample

        return make_numpy_array_1d(shift_inv)


def make_shift_inverse_lagrange_numpy(
    order: int,
    fsample: float,
    max_abs_shift: float,
    max_iter: int,
    tolerance: float,
) -> ShiftInverseNumpy:
    r"""Set up ShiftInverseNumpy instance with Lagrange interpolation method.

    Arguments:
        order: Order of the Lagrange polynomials
        fsample: Sample rate :math:`f_s > 0` [s]
        max_abs_shift: Upper limit :math:`S_\mathrm{max} \ge 0` [s] for coordinate shift
        max_iter: Maximum iterations before fail
        tolerance: Maximum absolute error of result

    Returns:
        Inversion function of type ShiftInverseNumpy
    """
    interp = make_regular_interpolator_lagrange(order)
    return ShiftInverseNumpy(
        fsample=fsample,
        max_abs_shift=max_abs_shift,
        interp=interp,
        max_iter=max_iter,
        tolerance=tolerance,
    )
