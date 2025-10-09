"""Module with interface for GW link responses

This provides the GW response information needed in Instrument class. The interface
is based on numpy arrays, written to support chunked processing needs handled on a
higher level. The main GW interface is named GWSource. It provides a method that
returns the GW response of a given link as a function of time, which accepts and
returns numpy arrays.

There are several implementations. The main one GWSourceSplines, interpolates
sampled data using spline interpolation. The sampled data needs to be provided
by a callback function that returns time series for a requested time window. The
methods from the gw_file.GWFile interface can be used as such a source.
GWSourceSplines has an option to construct interpolators on the fly for the time
range it is evaluated on. This is to support chunked evaluation without the need to
read all GW data at once, allowing to be used during chunked data processing.
The GWSourceSplines implementation is used in the Instrument class to set up the
GW data from GW files.

Another implementation is GWSourceNumpyArrays. Here, spline interpolators are set up
once from samples provided as numpy arrays. This is intended to support the user-supplied
GW data in the Instrument class, for GW data that fits into memory.

Finally, there is a trivial implementation GWSourceZero that returns all zero
GW response.

The GW functions are of type ArrayFuncOrScalar, which is either a scalar or a function
of time, accepting and returning a 1D numpy array. The scalar option exists to represents
constant functions more efficiently.
"""

import functools
from abc import ABC, abstractmethod
from typing import Callable, Final

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.chunked_splines import make_spline_interpolator
from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTime,
    FuncOfTimeTypes,
    TimeSeriesNumpy,
    make_numpy_array_1d,
)


class GWSource(ABC):  # pylint: disable=too-few-public-methods
    """Abstract interface for obtaining GW data for links

    This does not return GW data for a given link directly, but in form
    of a univariate function of time that can be sampled in turn.
    """

    @abstractmethod
    def link_gw(self, mosa: MosaID) -> FuncOfTimeTypes:
        """GW data as function of time for given link

        For the case of constant data, a scalar can be returned instead of a
        function.

        Arguments:
            mosa: Return GW for the link belonging to this MOSA

        Returns:
            GW as scalar or function accepting numpy array
        """


class GWSourceSplines(GWSource):  # pylint: disable=too-few-public-methods
    """Implementation of GWSource based on spline interpolating time series

    This constructs interpolation splines using a user-provided callable function
    which returns time series covering a given time interval.
    There are two options for interpolation, global and chunked.

    Chunked interpolation splines are constructed each time GW on a time interval are
    computed, using only points covering the interval plus an additional margin. This
    causes interpolation errors dependent on the chunk size. The magnitude of those
    compared to the usual interpolation error decays exponentially with margin size.
    For 5th order splines and regularly spaced data, the contribution from a sample
    20 points away from a given location is around 10^-8 lower than for an adjacent
    sample.

    Global spline interpolation is constructed once during instance creation, covering
    a user-provided time interval.

    Evaluating times not covered by the data source results in zeros.
    """

    def __init__(
        self,
        src: Callable[[float, float, MosaID, int], TimeSeriesNumpy | None],
        tmin: float,
        tmax: float,
        chunked: bool = True,
        margin_size: int = 100,
        spline_order: int = 5,
    ):
        """Constructor based on a callable providing GW timeseries.

        The callable must behave as the load_segment_tpsppr and load_segment_tcbltt
        methods of the gw_file.GWFile interface.

        One has to specify the time interval that this GW source needs to correctly
        represent. Note that evaluating time samples outside that range is undefined
        behavior even in case the data source covers such samples.

        Arguments:
            src: function for obtaining time series
            tmin: Start of time interval to cover
            tmax: End of time interval to cover
            chunked: Wether to used chunked or global interpolation
            margin_size: number of margin points on each side
            spline_order: order of the interpolation splines
        """

        def wrpsrc(t0: float, t1: float, mosa: MosaID) -> TimeSeriesNumpy | None:
            return src(t0, t1, mosa, int(margin_size))

        mosa_interps: dict[MosaID, FuncOfTimeTypes] = {}
        for mosa in MosaID:
            gw = functools.partial(wrpsrc, mosa=mosa)
            mosa_interps[mosa] = make_spline_interpolator(
                gw, tmin, tmax, int(spline_order), chunked
            )

        self._mosa_interps: Final = mosa_interps

    def link_gw(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See GWSource"""
        return self._mosa_interps[mosa]


class GWSourceNumpyArrays(GWSource):  # pylint: disable=too-few-public-methods
    """Implementation of GWSource based on gw data in numpy arrays

    This sets up global interpolation splines from time series provided as numpy arrays.
    """

    def __init__(
        self,
        times: np.ndarray,
        data: dict[MosaID, np.ndarray],
        spline_order: int = 5,
    ):
        """Constructor based on samples as arrays.

        The times are shared between the samples.

        Arguments:
            times: 1D array sample times [s]
            data: Dictionary with data samples for each MOSA
            spline_order: Order of the interpolation spline
        """

        mosa_interps: dict[MosaID, InterpolatedUnivariateSpline] = {}
        for mosa in MosaID:
            datm = make_numpy_array_1d(data[mosa])
            if len(datm) != len(times):
                msg = (
                    "GWSourceNumpyArrays: inconsistent time and data array ",
                    f" length (data:{len(datm)}, times:{len(times)})",
                )
                raise RuntimeError(msg)
            spl = InterpolatedUnivariateSpline(
                times, datm, k=int(spline_order), ext="raise"
            )
            mosa_interps[mosa] = FuncOfTime(spl, dtype=data[mosa].dtype)
        self._mosa_interps: Final = mosa_interps

    def link_gw(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See GWSource"""
        return self._mosa_interps[mosa]


class GWSourceZero(GWSource):  # pylint: disable=too-few-public-methods
    """Implementation of trivial GWSource that is always zero

    The use-case is to unify the trivial case with others to avoid special logic.
    """

    def link_gw(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See GWSource"""
        return ConstFuncOfTime(0.0)
