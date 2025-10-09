"""Module with an implementation of GlitchSource interpolating data from GlitchFile


GlitchSourceSplines interpolates sampled data from glitch files using spline
interpolation. The files are not read directly, but provided as via the
glitch_file.GlitchFile interface.

GlitchSourceSplines has an option to construct interpolators on the fly for the time
range it is evaluated on. This is to support chunked evaluation without the need to
read all glitch data at once, allowing to be used with chunked data processing. The
GlitchSourceSplines implementation is used by the Instrument class to set up the
glitch data from glitch files.
"""

from typing import Callable, Final

from lisainstrument.glitches.glitch_file import GlitchFile
from lisainstrument.glitches.glitch_source import GlitchSource
from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.chunked_splines import make_spline_interpolator
from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTimeTypes,
    TimeSeriesNumpy,
)


class GlitchSourceSplines(GlitchSource):
    """Implementation of GlitchSource interface based on spline interpolation

    This implementation extracts glitch data samples from a GlitchFile instance,
    and sets up interpolation functions to provide the GlitchSource interface.
    The interpolation can be done globally or in a chunked fashion, using splines.
    The interpolation order can be chosen.
    """

    def _make_func_mosa(
        self,
        src: Callable[[float, float, MosaID, int], TimeSeriesNumpy | None],
        mosa: MosaID,
    ) -> FuncOfTimeTypes:
        """Helper function to create interpolation function for given MOSA

        Arguments:
            src: Function providing time series for given MOSA and time interval
            mosa: Which MOSA to evaluate

        Returns:
            Interpolation function
        """

        def op(tbegin: float, tend: float) -> TimeSeriesNumpy | None:
            return src(tbegin, tend, mosa, self._margin_size)

        return make_spline_interpolator(
            op, self._tmin, self._tmax, self._order, self._chunked
        )

    def _make_funcs(
        self,
        src: Callable[[float, float, MosaID, int], TimeSeriesNumpy | None],
        has_src: Callable[[MosaID], bool],
    ) -> dict[MosaID, FuncOfTimeTypes]:
        """Helper function to create dictionary mapping mosa to interpolation functions

        Arguments:
            src: Function providing time series for given MOSA and time interval
            has_src: Function to query if time series are available for given MOSA

        Returns:
            Interpolation function or zero
        """

        return {
            mosa: (
                self._make_func_mosa(src, mosa)
                if has_src(mosa)
                else ConstFuncOfTime(0.0)
            )
            for mosa in MosaID
        }

    def __init__(
        self,
        glfile: GlitchFile,
        tmin: float,
        tmax: float,
        margin_size: int = 100,
        spline_order: int = 5,
        chunked: bool = True,
    ):
        """Constructor

        When chosing global interpoation, one has to provide the time interval that
        has to be covered in advance. For chunked interpolation, this is not required and
        the parameters are ignored.
        For both options, one has to specify how many margin points to add around data samples
        covering a given time interval on which to interpolate. For the global interpolation, the
        margin is only used for the global boundary. For chunked interpolation, it is used for each
        segment the interpolation is called on. The size controls the impact of the chunk size on
        the interpolation error. See module chunked_splines.


        Arguments:
            glfile: Instance providing GlitchFile interface
            tmin: Start of time interval to be covered by interpolation
            tmin: End of time interval to be covered by interpolation
            margin_size: Number of margin points for chunked interpolation
            spline order: Order of spline interpolation
            chunked: Whether to use chunked or global interpolation
        """
        self._order: Final = int(spline_order)
        self._chunked: Final = bool(chunked)
        self._margin_size: Final = int(margin_size)
        self._tmin: Final = float(tmin)
        self._tmax: Final = float(tmax)

        self._readout_sci_carrier: Final = self._make_funcs(
            glfile.load_segment_readout_sci_carrier, glfile.has_readout_sci_carrier
        )
        self._readout_sci_usbs: Final = self._make_funcs(
            glfile.load_segment_readout_sci_usbs, glfile.has_readout_sci_usbs
        )
        self._readout_tmi_carriers: Final = self._make_funcs(
            glfile.load_segment_readout_tmi_carriers, glfile.has_readout_tmi_carriers
        )
        self._readout_tmi_usbs: Final = self._make_funcs(
            glfile.load_segment_readout_tmi_usbs, glfile.has_readout_tmi_usbs
        )
        self._readout_ref_carriers: Final = self._make_funcs(
            glfile.load_segment_readout_ref_carriers, glfile.has_readout_ref_carriers
        )
        self._readout_ref_usbs: Final = self._make_funcs(
            glfile.load_segment_readout_ref_usbs, glfile.has_readout_ref_usbs
        )
        self._test_mass: Final = self._make_funcs(
            glfile.load_segment_test_mass, glfile.has_test_mass
        )
        self._lasers: Final = self._make_funcs(
            glfile.load_segment_lasers, glfile.has_lasers
        )

    def readout_sci_carrier(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_carrier at given MOSA"""
        return self._readout_sci_carrier[mosa]

    def readout_sci_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_sci_usbs at given MOSA"""
        return self._readout_sci_usbs[mosa]

    def readout_tmi_carriers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_carriers at given MOSA"""
        return self._readout_tmi_carriers[mosa]

    def readout_tmi_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_tmi_usbs at given MOSA"""
        return self._readout_tmi_usbs[mosa]

    def readout_ref_carriers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_carriers at given MOSA"""
        return self._readout_ref_carriers[mosa]

    def readout_ref_usbs(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for readout_ref_usbs at given MOSA"""
        return self._readout_ref_usbs[mosa]

    def test_mass(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for test mass (tm) at given MOSA"""
        return self._test_mass[mosa]

    def lasers(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Glitch function for lasers at given MOSA"""
        return self._lasers[mosa]
