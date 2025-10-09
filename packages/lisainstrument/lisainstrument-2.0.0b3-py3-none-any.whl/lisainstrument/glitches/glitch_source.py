"""Module with interface for glitch data source

This provides the glitch information needed in Instrument class.
It does not support chunked data processing directly, but the interface is
written to suit the needs of higher level framworks for this purpose.
The main interface is called GlitchSource. For each glitch injection point,
it provides a method that returns the glitch data for a given link as a
function of time based on numpy arrays.

There are two implementations. The main one glitch_source_interp.GlitchSourceSplines,
interpolates sampled data from glitch files using spline interpolation.  The
GlitchSourceZero in this module implementation provides all-zero glitch data, i.e.
represents the case without any glitches.

The functions providing glitches are of type FuncOfTimeTypes, which allows
representing constant (here: zero) functions as well. See also sigpro package.
"""

from abc import ABC, abstractmethod

from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.types_numpy import ConstFuncOfTime, FuncOfTimeTypes


class GlitchSource(ABC):
    """Abstract interface for obtaining glitch data"""

    @abstractmethod
    def readout_sci_carrier(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_carrier at given MOSA"""

    @abstractmethod
    def readout_sci_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_usbs at given MOSA"""

    @abstractmethod
    def readout_tmi_carriers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_carriers at given MOSA"""

    @abstractmethod
    def readout_tmi_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_usbs at given MOSA"""

    @abstractmethod
    def readout_ref_carriers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_carriers at given MOSA"""

    @abstractmethod
    def readout_ref_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_usbs at given MOSA"""

    @abstractmethod
    def test_mass(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for test mass (tm) at given MOSA"""

    @abstractmethod
    def lasers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for lasers at given MOSA"""


class GlitchSourceZero(GlitchSource):
    """Implementation of GlitchSource interface representing zero glitches"""

    def readout_sci_carrier(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_carrier at given MOSA"""
        return ConstFuncOfTime(0.0)

    def readout_sci_usbs(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_usbs at given MOSA"""
        return ConstFuncOfTime(0.0)

    def readout_tmi_carriers(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_carriers at given MOSA"""
        return ConstFuncOfTime(0.0)

    def readout_tmi_usbs(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_usbs at given MOSA"""
        return ConstFuncOfTime(0.0)

    def readout_ref_carriers(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_carriers at given MOSA"""
        return ConstFuncOfTime(0.0)

    def readout_ref_usbs(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_usbs at given MOSA"""
        return ConstFuncOfTime(0.0)

    def test_mass(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for test mass (tm) at given MOSA"""
        return ConstFuncOfTime(0.0)

    def lasers(self, _: MosaID) -> FuncOfTimeTypes:
        """Glitch function for lasers at given MOSA"""
        return ConstFuncOfTime(0.0)
