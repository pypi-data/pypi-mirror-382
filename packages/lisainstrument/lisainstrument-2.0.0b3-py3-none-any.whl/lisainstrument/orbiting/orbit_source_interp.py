"""Implementation of OrbitSource that interpolates data from OrbitFile

OrbitSourceSplines interpolates TimeSeriesNumpy using splines in a global
fashion, using data provided as TimeSeriesNumpy.

The function make_orbit_source_from_tpsppr() sets up a OrbitSourceSplines
instance from an OrbitFile, using the TPS/PPR dataset. Similarly,
make_orbit_source_from_tcbltt() uses the TCB/LTT dataset.
"""

import functools

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.orbiting.orbit_file import OrbitFile
from lisainstrument.orbiting.orbit_source import OrbitSource
from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTime,
    FuncOfTimeTypes,
    TimeSeriesNumpy,
)


class OrbitSourceSplines(OrbitSource):
    """Implementation of OrbitSource based on interpolating time series

    This is used in make_orbit_source_from_tpsppr and make_orbit_source_from_tcbltt
    to represent orbit file data.
    """

    def _make_spl(self, ts: TimeSeriesNumpy) -> InterpolatedUnivariateSpline:
        """Helper funtion to create spline from time series"""
        return InterpolatedUnivariateSpline(
            ts.times, ts.values, k=self._order, ext="raise"
        )

    def __init__(
        self,
        ppr0: dict[MosaID, float],
        dppr: dict[MosaID, TimeSeriesNumpy],
        tps_wrt_tcb: dict[SatID, TimeSeriesNumpy | float],
        interp_order: int = 5,
    ) -> None:
        """Constructor.

        The PPR is provided in terms of a time series for its time derivative
        together with the PPR value at the start of the time series. The
        PPR is computed via numerical integration.

        The TPS/TCB time shifts can optionally be given as a scalar instead
        of a time series for the case of constant data.

        Arguments:
            ppr0: Dictionary with start values of PPR for each MOSA
            dppr: Dictionary with time series of dPPR/dt for each MOSA
            tps_wrt_tcb: Dictionary with time shift for each space craft, as time series or const scalar
            interp_order: Order of spline interpolation to use
        """

        self._order = int(interp_order)
        self._t0 = max(dppr[mosa].times[0] for mosa in MosaID)

        self._spls_dppr: dict[MosaID, FuncOfTime] = {}
        self._spls_ppr: dict[MosaID, FuncOfTime] = {}

        def eval_offs_spl(
            t: np.ndarray, *, spl: InterpolatedUnivariateSpline, offs: float
        ) -> np.ndarray:
            """Helper function used below"""
            return spl(t) + offs

        for mosa in MosaID:
            spl_dppr = self._make_spl(dppr[mosa])
            int_dppr = spl_dppr.antiderivative()
            offs = ppr0[mosa] - int_dppr(dppr[mosa].times[0])
            # do not simplify this, it wards off the late binding closure curse
            spl_ppr = functools.partial(eval_offs_spl, spl=int_dppr, offs=offs)

            self._spls_dppr[mosa] = FuncOfTime(spl_dppr, dtype=np.float64)
            self._spls_ppr[mosa] = FuncOfTime(spl_ppr, dtype=np.float64)

        self._spls_tps_wrt_tcb: dict[SatID, FuncOfTimeTypes] = {}
        for sc in SatID:
            ts = tps_wrt_tcb[sc]
            if isinstance(ts, TimeSeriesNumpy):
                self._spls_tps_wrt_tcb[sc] = FuncOfTime(
                    self._make_spl(ts), dtype=np.float64
                )
            else:
                self._spls_tps_wrt_tcb[sc] = ConstFuncOfTime(ts)

    @property
    def t0(self) -> float:
        """See OrbitSource interface"""
        return self._t0

    def pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return self._spls_ppr[mosa]

    def d_pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return self._spls_dppr[mosa]

    def tps_wrt_tcb(self, sc: SatID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return self._spls_tps_wrt_tcb[sc]


def make_orbit_source_from_tpsppr(orbitf: OrbitFile) -> OrbitSourceSplines:
    """Create orbit data source from orbit file using TPS/PPR dataset

    Arguments:
        orbitf: OrbitFile instance
    Returns:
        OrbitSource implmentation using spline interpolation
    """
    ppr0 = {mosa: orbitf.ppr0_type_tpsppr(mosa) for mosa in MosaID}
    dppr = {mosa: orbitf.d_ppr_type_tpsppr(mosa) for mosa in MosaID}
    tps_wrt_tcb: dict[SatID, TimeSeriesNumpy | float] = {
        sc: orbitf.tps_wrt_tcb_type_tpsppr(sc) for sc in SatID
    }

    return OrbitSourceSplines(ppr0, dppr, tps_wrt_tcb)


def make_orbit_source_from_tcbltt(orbitf: OrbitFile) -> OrbitSourceSplines:
    """Create orbit data source from orbit file using TCB/LTT dataset

    Arguments:
        orbitf: OrbitFile instance
    Returns:
        OrbitSource implmentation using spline interpolation
    """
    ppr0 = {mosa: orbitf.ppr0_type_tcbltt(mosa) for mosa in MosaID}
    dppr = {mosa: orbitf.d_ppr_type_tcbltt(mosa) for mosa in MosaID}
    tps_wrt_tcb: dict[SatID, TimeSeriesNumpy | float] = {sc: 0.0 for sc in SatID}

    return OrbitSourceSplines(ppr0, dppr, tps_wrt_tcb)
