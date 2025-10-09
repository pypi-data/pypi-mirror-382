"""This module allows to perform spline interpolation in a chunked fashion.

The main use case is interpolation of arbitrary large data read from file in the context of
chunked data processing. This module has no chunking functionality itself but provides
useful low level infrastructure.
The source of data is abstracted as a function that provides data samples covering
a given time interval. For example, it could read a partial dataset from file.
The idea is that this function will be called sequentially for consequtive time intervals.
Time series are represented by the TimeSeriesNumpy class, and the above callable by the
type alias TimeSeriesSource.
The function make_chunked_spline_interpolator and make_global_spline_interpolator turn a
TimeSeriesSource into an interpolation function. The difference is that the first
constructs spline interpolators on the fly for each segment, while the other uses a fixed
interpolation spline covering a fixed time interval.

The resulting interpolating functions are returned as FuncOfTime instances which can be used
by stream_func_of_time from the streams.sampling module to create streams of sampled data.
"""

from typing import Callable, TypeAlias

import numpy as np
from scipy.interpolate import make_interp_spline

from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTime,
    FuncOfTimeTypes,
    TimeSeriesNumpy,
)

TimeSeriesSource: TypeAlias = Callable[[float, float], TimeSeriesNumpy | None]


def make_chunked_spline_interpolator(func: TimeSeriesSource, order: int) -> FuncOfTime:
    """Turns a source of time series into a chunked spline interpolation function

    The input is a function that returns a timeseries covering a time interval given as
    arguments. The timeseries is assumed to include a margin sufficient to be used for
    spline interpolation on the requested interval.
    The output is a function of time based on interpolating the time series on the fly.
    Given an array with sample times, the input function is used to get a time series covering
    the same interval. This time series is used to construct a spline interpolator,
    which is evaluated at the sample times. The resulting interpolation function can be evaluated
    anywhere and zero-pads data outside the range of the available data.

    Arguments:
        func: Callable providing time series for a given interval
        order: The order of the spline interpolation

    Returns:
        Interpolation function
    """

    def op(t: np.ndarray) -> np.ndarray:
        seg = func(np.min(t), np.max(t))
        res = np.zeros_like(t)

        if seg is None:
            return res

        # ~ spl = InterpolatedUnivariateSpline(seg.times, seg.values, k=order, ext="zeros")
        spl = make_interp_spline(seg.times, seg.values, k=order)

        msk = np.logical_and(t >= seg.times[0], t <= seg.times[-1])
        res[msk] = spl(t[msk])
        return res

    return FuncOfTime(op, dtype=np.float64)


def make_global_spline_interpolator(
    func: TimeSeriesSource, tmin: float, tmax: float, order: int
) -> FuncOfTimeTypes:
    """Turns a source of time series into a global spline interpolation function

    The input is a function that returns a timeseries covering a time interval given as
    arguments. The timeseries is assumed to include a margin sufficient to be used for
    spline interpolation on the requested interval.
    The output is a fixed interpolation function covering the specified interval.

    Arguments:
        func: Callable providing time series for a given interval
        tmin: Start of interval to be covered by interpolation function
        tmax: End of interval to be covered by interpolation function
        order: The order of the spline interpolation

    Returns:
        Interpolation function
    """

    seg = func(tmin, tmax)

    if seg is None:
        return ConstFuncOfTime(0.0)

    # ~ spl = InterpolatedUnivariateSpline(seg.times, seg.values, k=order, ext="zeros")
    spl = make_interp_spline(seg.times, seg.values, k=order)

    def op(t: np.ndarray) -> np.ndarray:
        msk = np.logical_and(t >= seg.times[0], t <= seg.times[-1])
        res = np.zeros_like(t)
        res[msk] = spl(t[msk])
        return res

    return FuncOfTime(op, dtype=np.float64)


def make_spline_interpolator(
    func: TimeSeriesSource | float,
    tmin: float,
    tmax: float,
    order: int,
    chunked: bool,
) -> FuncOfTimeTypes:
    """Wrapper presenting spline-interpolated or const function as FuncOfTime or ConstFuncOfTime.

    This sets up a spline interplator based on a data source, with option to chose between
    chunked and global interpolation. Further, providing a scalar float instead of a data source
    is interpreted as constant data without need for interpolation, and a ConstFuncOfTime is
    returned instead of an interpolation function.

    Arguments:
        func: Scalar or callable source for time series
        tmin: Start of interval that has to be covered (used only when chunked==False)
        tmax: End of interval that has to be covered (used only when chunked==False)
        order: Order of the interpolation splines
        chunked: Wether to used chunked or global interpolation

    Returns:
        Interpolation function as FuncOfTime or ConstFuncOfTime
    """

    if isinstance(func, float):
        return ConstFuncOfTime(func)

    if chunked:
        return make_chunked_spline_interpolator(func, order)

    return make_global_spline_interpolator(func, tmin, tmax, order)
