"""Abstract interface for providing frequency plans.

The FreqPlanSource abstract base class provides the interface for getting
the frequency plans for the different MOSAa as function of time. The
interface is based on numpy arrays.


An implementation providing data from frequency plan files can be found in
the lisainstrument.freqplan.fplan_source_interp module.
"""

from abc import ABC, abstractmethod

from lisainstrument.orbiting.constellation_enums import MosaID
from lisainstrument.sigpro.types_numpy import FuncOfTimeTypes


class FreqPlanSource(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for providing frequency plan data.

    The interface consists of a single method beatnote_for_mosa() computing
    locking beatnodes as function of time for a given MOSA.

    MOSAs are identified by enum class MosaID from the module
    orbiting.constellations_enums.
    """

    @abstractmethod
    def beatnote_for_mosa(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Get locking beatnotes as function of time for given MOSA

        This returns a function that accepts 1D numpy arrays with times
        and returns a 1D numpy array with the locking beatnotes at the
        given times. Times refer to the [TODO: CHECK] time frame.

        In case of constant beatnotes, the constant is returned as a
        ConstFuncOfTime instance, else as FuncOfTime.

        Arguments:
            mosa: which mosa to get locking for

        Returns:
            Locking beatnotes as function of time
        """
