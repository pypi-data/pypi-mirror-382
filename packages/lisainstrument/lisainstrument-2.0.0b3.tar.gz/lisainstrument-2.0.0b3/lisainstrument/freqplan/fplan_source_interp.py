"""Implementation of FreqPlanSource based on interpolating data from FreqPlanFile

The FreqPlanSourceFile makes data in a FreqPlanFile avaialble via the higher
level FreqPlanSource interface. This includes interpolating the data as needed.
Currently, only linear interpolation is supported.
"""

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from typing_extensions import assert_never

from lisainstrument.freqplan.fplan_file import FreqPlanFile
from lisainstrument.freqplan.fplan_source import FreqPlanSource
from lisainstrument.orbiting.constellation_enums import LockTypeID, MosaID
from lisainstrument.sigpro.types_numpy import (
    ConstFuncOfTime,
    FuncOfTime,
    FuncOfTimeTypes,
)


class FreqPlanSourceFile(FreqPlanSource):  # pylint: disable=too-few-public-methods
    """Provides data in FreqPlanFile via high-level interface FreqPlanSource

    The data in a FreqPlanFile is augmented with further parameters to specify
    locking configuration, the lock types of each MOSA, and a time offset.
    The time coordinate used in the interface is the one in the frequency
    plan file plus the constant time offset.
    To provide the frequency plan as a function of time, the data in the
    file is linearly interpolated.
    """

    @staticmethod
    def _make_interpolator(
        ts: np.ndarray, ys: np.ndarray, time_offset: float
    ) -> FuncOfTime:
        """Create an interpolation function based on samples in numpy arrays

        Currently, just using linear interpolation. We enforce 1D arrays because
        this is intended for simple timeseries.
        """
        s = InterpolatedUnivariateSpline(ts + time_offset, ys, k=1, ext="raise")
        return FuncOfTime(s, dtype=ys.dtype)

    @staticmethod
    def _make_beatnote_func(
        fpf: FreqPlanFile,
        lock_config: str,
        lock: LockTypeID,
        mosa: MosaID,
        time_offset: float,
    ) -> FuncOfTimeTypes:
        """Create lock beatnode interpolation function or constant value on given MOSA

        Arguments:
            fpf: The frequency plan file
            lock_config: the name of the constellation lock configuration
            lock: the lock type for the given MOSA
            mosa: which MOSA
            time_offset: Offset added to the timestamps in the file

        Returns:
            Scalar value or interpolation function accepting numpy arrays
        """

        match lock:
            case LockTypeID.CAVITY:
                # No offset for primary laser
                return ConstFuncOfTime(0.0)
            case LockTypeID.DISTANT:
                lbeat = fpf.load_sci_hz(lock_config, mosa)
            case LockTypeID.ADJACENT:
                lbeat = fpf.load_ref_hz(lock_config, mosa)
            case _ as unreachable:
                assert_never(unreachable)

        return FreqPlanSourceFile._make_interpolator(
            fpf.time_samples, lbeat, time_offset
        )

    def __init__(
        self,
        fpf: FreqPlanFile,
        locks: dict[MosaID, LockTypeID],
        lock_config: str,
        time_offset: float,
    ):
        """Constructor.

        The locking configuration is specified as a string with the name of
        the config as defined in the frquency plan file format.
        [TODO: write down naming scheme]
        The lock types for each MOSA are specified as LockTypeID enums defined
        in lisainstrument.orbiting.constellation_enums. The enum values are the
        same strings used inside Instrument class.

        Arguments:
            fpf: Frequency plan file as FreqPlanFile instance
            locks: The lock type for each MOSA
            lock_config: the locking configuration name
            time_offset: Offset added to the timstamps in the file
        """
        self._interps: dict[MosaID, FuncOfTimeTypes] = {}
        for mosa in MosaID:
            self._interps[mosa] = self._make_beatnote_func(
                fpf, lock_config, locks[mosa], mosa, time_offset
            )

    def beatnote_for_mosa(self, mosa: MosaID) -> FuncOfTimeTypes:
        """Implements abstract method FreqPlanSource.beatnote_for_mosa"""
        return self._interps[mosa]
