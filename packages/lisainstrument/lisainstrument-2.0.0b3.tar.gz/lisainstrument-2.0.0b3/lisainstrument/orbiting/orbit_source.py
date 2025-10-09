"""Interface representing orbits as continuous functions

This module defines an abstract interface class OrbitSource which provides the
orbit information needed by the Instrument class as functions of time, operating
on 1D numpy arrays. Functions are represented by FuncOfTime instances or
ConstFuncOfTime instances for the case of constant data.

This module also provides a trivial implementation OrbitSourceStatic representing
static values. Use make_orbit_source_static() to creates an OrbitSourceStatic from
a dictionary. See orbit_source_interp module for the most important implementation
based on interpolation.
"""

from abc import ABC, abstractmethod
from typing import Final

from lisainstrument.orbiting.constellation_enums import MosaID, SatID
from lisainstrument.sigpro.types_numpy import ConstFuncOfTime, FuncOfTimeTypes


class OrbitSource(ABC):
    """Abstract interface to orbit data

    This represents an interface to the specific data needed in the Instrument
    class. The quantites are provided as callable functions wrapped in FuncOfTime
    instances. Constant functions are to be represented by ConstFuncOfTime instances.
    """

    @property
    @abstractmethod
    def t0(self) -> float:
        """Start of valid time window [s]"""

    @abstractmethod
    def pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """PPRS for a given MOSA as function of time [s].

        Arguments:
            mosa: Which MOSA
        Returns:
            Function accepting 1D numpy array with times  [s]
        """

    @abstractmethod
    def d_pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Time derivative of PPRS for a given MOSA as function of time  [s].

        Arguments:
            mosa: Which MOSA
        Returns:
            Function accepting 1D numpy array with times [s]
        """

    @abstractmethod
    def tps_wrt_tcb(self, sc: SatID) -> FuncOfTimeTypes:
        """Time shift of TPS w.r.t TCB for a given spacecraft as function of time [s].

        Arguments:
            sc: Which spacecraft
        Returns:
            Function accepting 1D numpy array with times [s]
        """


class OrbitSourceStatic(OrbitSource):
    """Implementation of OrbitSource for case of static PPRs

    The TPS/TCB time shift is assumed zero for this orbit source.
    Note: even though not meaningful for the static case, one still needs
    to specify the start time because it is part of the generic interface.
    """

    def __init__(self, t0: float, ppr: dict[MosaID, float]) -> None:
        """Constructor

        Arguments:
            t0: start of valid time window
            ppr: dictionary with constant PPR for each MOSA
        """
        self._t0: Final[float] = t0
        self._ppr: Final[dict[MosaID, float]] = ppr

    @property
    def t0(self) -> float:
        """See OrbitSource interface"""
        return self._t0

    def pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return ConstFuncOfTime(self._ppr[mosa])

    def d_pprs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return ConstFuncOfTime(0.0)

    def tps_wrt_tcb(self, sc: SatID) -> FuncOfTimeTypes:
        """See OrbitSource interface"""
        return ConstFuncOfTime(0.0)


def make_orbit_source_static(
    ppr: dict[str, float], t0: float = 0.0
) -> OrbitSourceStatic:
    """Create orbit data source for static PPR case

    Arguments:
        ppr: dictionary with constant PPR for each MOSA
        t0: start of valid time window
    Returns:
        OrbitSource implmentation for static case
    """
    pprdict = {mosa: float(ppr[mosa.value]) for mosa in MosaID}
    return OrbitSourceStatic(t0, pprdict)
