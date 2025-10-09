"""This module collects all physical noise models for the LISA Instrument

The noise definitions are based on the general-purpose noise definitions in
lisainstrument.noise_defs module. This only provides definitions, to generate
noise samples, see module noisy.noise_gen_numpy and stream.noise_alt
"""

from __future__ import annotations

import math
from enum import Enum

import numpy as np
from lisaconstants import SPEED_OF_LIGHT as C_SI
from typing_extensions import assert_never

from .noise_defs import (
    NoiseDefBase,
    NoiseDefFalloff6,
    NoiseDefFalloff8,
    NoiseDefInfraRed,
    NoiseDefPink,
    NoiseDefPowerLaw,
    NoiseDefRed,
    NoiseDefRedAndViolet,
    NoiseDefSum,
    NoiseDefViolet,
    NoiseDefWhite,
)


class NoiseDefClock(NoiseDefPink):
    r"""LISA instrument clock noise

    The power spectral density in fractional frequency deviations is a pink
    noise,

    .. math::

        S^\text{ffd}_q(f) = A^2 f^{-1}.

    Clock noise saturates below 1E-5 Hz, as the low-frequency part is modeled by
    deterministing clock drifts.

    This model is just an alias for pink noise with f_min_hz=1e-5,
    see NoiseDefPink for details.
    """

    def __init__(
        self,
        asd_onesided_at_1hz: float,
        f_sample: float,
        name: str,
        f_min_hz: float = 1e-5,
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: The ASD amplitude [1/sqrt(Hz)]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
            f_min_hz: Low frequency cutoff [Hz]
        """

        super().__init__(
            asd_onesided_at_1hz=asd_onesided_at_1hz,
            f_min_hz=f_min_hz,
            f_sample=f_sample,
            name=name,
        )

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class LaserNoiseShape(Enum):
    """Enum class listing the choices for the spectral shape in NoiseDefLaser"""

    WHITE = "white"
    WHITE_PLUS_INFRARED = "white+infrared"


class NoiseDefLaser(NoiseDefBase):
    r"""Defines LISA instrument laser noise

    This is a white noise with an infrared relaxation towards low frequencies,
    approximating the continuous PSD model

    .. math::

        S^\text{Hz}_p(f) = A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ]
        = A^2 + A^2 \frac{f_\mathrm{knee}^4}{f^4}.

    The low-frequency part (infrared relaxation) can be disabled, in which
    case the PSD model becomes

    .. math::

        S_p(f) = A^2.

    The laser noise is defined as noise of the frequency. The ASD therefore
    has units of [Hz/sqrt(Hz)].

    """

    def __init__(
        self,
        asd_onesided_const: float,
        shape: LaserNoiseShape | str,
        f_min_hz: float,
        f_sample: float,
        name: str,
        f_knee_hz: float = 2e-3,
    ):
        """Constructor

        Arguments:
            asd_onesided_const: The one-sided ASD amplitude [Hz/sqrt(Hz)]
            shape: Which of the two noise models to use
            f_min_hz: cutoff frequency of infrared noise model, if used [Hz]
            f_knee_hz: transition frequency to relaxiation term [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_const = float(asd_onesided_const)
        self._f_min_hz = float(f_min_hz)
        self._f_knee_hz = float(f_knee_hz)
        self._shape = LaserNoiseShape(shape)

        if self._asd_onesided_const < 0:
            msg = f"NoiseDefLaser got negative ASD parameter {asd_onesided_const}"
            raise RuntimeError(msg)

        if self._f_knee_hz < 0:
            msg = f"NoiseDefLaser got negative transition frequency {f_knee_hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefLaser got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_const(self) -> float:
        """ASD amplitude coefficient :math:`A` [1/sqrt(Hz)]"""
        return self._asd_onesided_const

    @property
    def f_knee_hz(self) -> float:
        """Transition frequency to infrared part [Hz]"""
        return self._f_knee_hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    @property
    def shape(self) -> LaserNoiseShape:
        """Which spectral shape option to use"""
        return self._shape

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        ndef: NoiseDefBase
        match self.shape:
            case LaserNoiseShape.WHITE:
                ndef = NoiseDefWhite(
                    asd_onesided_const=self.asd_onesided_const,
                    f_sample=self.f_sample,
                    name=self.name,
                )
            case LaserNoiseShape.WHITE_PLUS_INFRARED:
                white = NoiseDefWhite(
                    asd_onesided_const=self.asd_onesided_const,
                    f_sample=self.f_sample,
                    name="white",
                )
                asd_infr = self.asd_onesided_const * self.f_knee_hz**2
                infrared = NoiseDefInfraRed(
                    asd_onesided_at_1hz=asd_infr,
                    f_min_hz=self.f_min_hz,
                    f_sample=self.f_sample,
                    name="infrared",
                )
                ndef = NoiseDefSum(components=[white, infrared], name=self.name)
            case _ as unreachable:
                assert_never(unreachable)
        return ndef.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"shape = {self.shape.value}\n"
            f"asd_onesided_const [Hz/sqrt(Hz)] = {self.asd_onesided_const} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_knee_hz [Hz] = {self.f_knee_hz} \n"
        )


class NoiseDefModulation(NoiseDefPowerLaw):
    r"""Defines LISA instrument modulation noise

    The PSD model for the fractional frequency deviations reads

    .. math::

        S^\text{ffd}_M(f) = A^2 f^{2/3}.

    Note that these are fractional frequency deviations wrt. the GHz modulation frequencies.

    The model is approximated using NoiseDefPowerLaw noise with asd_exp = 1/3.
    See NoiseDefPowerLaw for details.
    """

    def __init__(
        self,
        asd_onesided_at_1hz: float,
        f_min_hz: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: The ASD amplitude [1/sqrt(Hz)]
            f_min_hz: The low frequency cutoff [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(
            asd_onesided_at_1hz=asd_onesided_at_1hz,
            asd_exp=1 / 3,
            f_min_hz=f_min_hz,
            f_sample=f_sample,
            name=name,
        )

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefBacklink(NoiseDefRedAndViolet):
    r"""Defines LISA instrument backlink noise


    This noise approximates a model PSD for fractional frequency
    deviations given by

    .. math::

        S^\text{ffd}_\mathrm{bl}(f) = \qty(\frac{2 \pi A}{c})^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]
        = \qty(\frac{2 \pi A}{c})^2 f^2 + \qty(\frac{2 \pi A f_\mathrm{knee}^2}{c})^2 f^{-2}.

    The exact discrete PSD can be obtained using the discrete_psd_twosided()
    method.

    Note that the amplitude coefficient refers to the displacement amplitude and not
    the fractional frequency amplitude. The displacemnt amplitude is also the parameter
    used to create NoiseDefBacklink instances. The amplitude coefficient in terms of
    fractional frequency deviation will be available as a property asd_onesided_at_1hz.

    The PSD in terms of the displacement is given by

    .. math::

        S^\text{m}_\mathrm{bl}(f) = A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ].

    Multiplying by :math:`(2 \pi f / c)^2` yields the fractional frequency
    deviations PSD.

    Because this is a optical pathlength noise expressed as fractional frequency deviation, it
    should be multiplied by the beam frequency to obtain the beam frequency fluctuations.

    The noise is implemented using NoiseDefRedAndViolet as a base, see class
    documentation for further details.
    """

    def __init__(
        self,
        displacement_asd_onesided: float,
        f_min_hz: float,
        f_knee_hz: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            displacement_asd_onesided: Displacement ASD amplitude A [m/sqrt(Hz)]
            f_min_hz: frequency cutoff for red noise component [Hz]
            f_knee_hz: transition frequency between violet and red components [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        self._displacement_asd_onesided = float(displacement_asd_onesided)
        asd1s = 2 * math.pi * self._displacement_asd_onesided / C_SI
        super().__init__(
            asd_onesided_at_1hz=asd1s,
            f_min_hz=f_min_hz,
            f_knee_hz=f_knee_hz,
            f_sample=f_sample,
            name=name,
        )

    @property
    def displacement_asd_onesided(self) -> float:
        """ASD amplitude of displacement :math:`A` [m/sqrt(Hz)]"""
        return self._displacement_asd_onesided

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"displacement_asd_onesided [m/sqrt(Hz)] = {self.displacement_asd_onesided} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_knee_hz [Hz] = {self.f_knee_hz} \n"
        )


class NoiseDefRanging(NoiseDefWhite):
    """Defines LISA instrument stochastic ranging noise

    This models timing jitter as white noise

    .. math::

        S^\text{s}_R(f) = A^2.

    The noise is implemented as an alias for NoiseDefWhite. However,
    the latter is to be interpreted as noise for a dimensionful quantity
    with unit [s], such that the ASD amplitude has unit [s/sqrt(Hz)].
    """

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"asd_onesided_const [s/sqrt(Hz)] = {self.asd_onesided_const} \n"
        )


class TestMassNoiseShape(Enum):
    """Enum class listing the choices for the spectral shape in NoiseDefTestMass"""

    ORIGINAL = "original"
    LOWFREQ_RELAX = "lowfreq-relax"


class NoiseDefTestMass(NoiseDefBase):
    r"""Defines LISA instrument testmass noise

    This models the noise caused by test-mass acceleration, more precisely,
    it describes the correponding noise of the testmass velocity.
    Generated noise samples have unit [m/s], and the ASD has unit [(m/s)/sqrt(Hz)].

    There are two different choices for the spectral shape, specified via
    the TestMassNoiseShape enum class.

    The first model, named "original", models the PSD of the test mass
    acceleration as

    .. math::

        S^\text{acc}_\delta(f) = A^2
        \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^2]
        \qty[ 1 + \qty(\frac{f}{f_\mathrm{break}})^4].

    Multiplying by :math:`1 / (2 \pi f)^2` yields the PSD of the velocity,

    .. math::

        S^\text{vel}_\delta(f) &= \qty(\frac{A}{2 \pi})^2
        \qty[ f^{-2} + \frac{f_\mathrm{knee}^2}{f^4}
        + \frac{f^2}{f_\mathrm{break}^4}
        + \frac{f_\mathrm{knee}^2}{f_\mathrm{break}^4} ]

        &= \qty(\frac{A f_\mathrm{knee}}{2 \pi})^2 f^{-4}
        + \qty(\frac{A}{2 \pi})^2 f^{-2}
        + \qty(\frac{A f_\mathrm{knee}}{2 \pi f_\mathrm{break}^2})^2
        + \qty(\frac{A}{2 \pi f_\mathrm{break}^2})^2 f^2,

    Note that we parametrize the velocity ASD amplitude using the acceleration amplitude
    coefficient :math:`A`, which has units [(m/s^2)/sqrt(Hz)].


    The PSD model corresponds to the incoherent sum of an infrared, a red, a white,
    and a violet noise. Noise generated for NoiseDefTestMass is equivalent to
    the incoherent sum of noises generated for the NoiseDefInfrared, NoiseDefRed,
    NoiseDefWhite, and NoiseDefViolet noise definitions.
    The resulting actual PSD for NoiseDefTestMass approximates the above model
    PSD. Note however that NoiseDefInfrared and NoiseDefRed have an additional
    low frequency cutoff parameter `f_min_hz`, which has to be specified for
    NoiseDefTestMass as well. Below the cutoff, the PSD deviates from the model
    above. See NoiseDefRed for details. The resulting exact discrete PSD of noise
    generated for NoiseDefTestMass can be computed using  the discrete_psd_twosided() method.

    The second PSD model, named "lowfreq-relax", multiplies the "original"
    model PSD by a factor modifying the low-frequency behavior.
    The PSD of the acceleration becomes

    .. math::

        S^\text{acc}_\delta(f) = \ldots \times
        \qty[ 1 + \qty(\frac{f_\mathrm{relax}}{f})^4 ].

    This corresponds to additional terms in the PSD of the testmass velocity noise

    .. math::

        S\text{vel}_\delta(f) &= \ldots \times
        \qty[ 1 + \qty(\frac{f_\mathrm{relax}}{f})^4 ]

        &= \ldots + \qty(\frac{A f_\mathrm{knee} f_\mathrm{relax}^2}{2 \pi})^2 f^{-8}
        + \qty(\frac{A f_\mathrm{relax}^2}{2 \pi})^2 f^{-6}

        &\qquad + \qty(\frac{A f_\mathrm{knee} f_\mathrm{relax}^2}{2 \pi f_\mathrm{break}^2})^2 f^{-4}
        + \qty(\frac{A f_\mathrm{relax}^2}{2 \pi f_\mathrm{break}^2})^2 f^{-2}.


    .. warning::

       This PSD strongly diverges for low frequencies, adding terms with falloff
       :math:`f^{-6}` and :math:`f^{-8}`. The latter are represented by the noise definitions
       NoiseDefFalloff6 and NoiseDefFalloff8. Although both have a low frequency cutoff
       parameter `f_min_hz`, they still diverge below that cutoff. See NoiseDefFalloff6 for details.
       For both, it is unclear if they represent a valid PSD for stationary noise. In any case,
       including low frequencies causes huge dynamic range of the PSD. This makes it difficult
       to measure the PSD using the Welch method. It may also result in unphysically large test
       mass displacements (for which the PSD picks up another factor :math:`f^{-2}`).
       Results obtained with the "lowfreq-relax" model should be treated with care.

    """

    def __init__(
        self,
        accel_asd_onesided: float,
        shape: TestMassNoiseShape | str,
        f_knee_hz: float,
        f_break_hz: float,
        f_relax_hz: float,
        f_min_hz: float,
        f_sample: float,
        name: str,
    ):
        r"""Constructor

        Arguments:
            accel_asd_onesided: Coefficient :math:`A` [(m/s^2)/sqrt(Hz)]
            shape: Which spectral shape model to use
            f_knee_hz: Coefficient :math:`f_\mathrm{knee}` [Hz]
            f_break_hz: Coefficient :math:`f_\mathrm{break}` [Hz]
            f_relax_hz: Coefficient :math:`f_\mathrm{relax}` [Hz]
            f_min_hz: Low frequency cutoff parameter passed to the definitions of the noise components [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._accel_asd_onesided = float(accel_asd_onesided)
        self._f_min_hz = float(f_min_hz)
        self._f_knee_hz = float(f_knee_hz)
        self._f_break_hz = float(f_break_hz)
        self._f_relax_hz = float(f_relax_hz)
        self._shape = TestMassNoiseShape(shape)

        if self._accel_asd_onesided < 0:
            msg = f"NoiseDefTestMass got negative ASD amplitude {accel_asd_onesided}"
            raise RuntimeError(msg)

        if self._f_knee_hz < 0:
            msg = f"NoiseDefTestMass got negative transition frequency {f_knee_hz=}"
            raise RuntimeError(msg)

        if self._f_break_hz < 0:
            msg = f"NoiseDefTestMass got negative transition frequency {f_break_hz=}"
            raise RuntimeError(msg)

        if self._f_relax_hz < 0:
            msg = f"NoiseDefTestMass got negative transition frequency {f_relax_hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefTestMass got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def accel_asd_onesided(self) -> float:
        """Acceleration ASD amplitude coefficient :math:`A` [(m/s^2)/sqrt(Hz)]"""
        return self._accel_asd_onesided

    @property
    def f_knee_hz(self) -> float:
        """Transition frequency to TODO [Hz]"""
        return self._f_knee_hz

    @property
    def f_break_hz(self) -> float:
        """Transition frequency to TODO [Hz]"""
        return self._f_break_hz

    @property
    def f_relax_hz(self) -> float:
        """Transition frequency to TODO [Hz]"""
        return self._f_relax_hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    @property
    def shape(self) -> TestMassNoiseShape:
        """Which spectral shape option to use"""
        return self._shape

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def _elementary_original(self) -> list[NoiseDefBase]:
        """Return elementary noise components for spectral shape original"""

        asd_infrared = self.accel_asd_onesided * self.f_knee_hz / (2 * math.pi)
        infrared = NoiseDefInfraRed(
            asd_onesided_at_1hz=asd_infrared,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="original_infrared",
        )

        asd_red = self.accel_asd_onesided / (2 * math.pi)
        red = NoiseDefRed(
            asd_onesided_at_1hz=asd_red,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="original_red",
        )

        asd_white = (
            self.accel_asd_onesided
            * self.f_knee_hz
            / (2 * math.pi * self.f_break_hz**2)
        )
        white = NoiseDefWhite(
            asd_onesided_const=asd_white, f_sample=self.f_sample, name="original_white"
        )

        asd_violet = self.accel_asd_onesided / (2 * math.pi * self.f_break_hz**2)
        violet = NoiseDefViolet(
            asd_onesided_at_1hz=asd_violet,
            f_sample=self.f_sample,
            name="original_violet",
        )

        return [infrared, red, white, violet]

    def _elementary_lowfreq_relax(self) -> list[NoiseDefBase]:
        """Return elementary noise components for spectral shape lowfreq-relax"""

        asd_falloff6 = self.accel_asd_onesided * self.f_relax_hz**2 / (2 * math.pi)

        falloff6 = NoiseDefFalloff6(
            asd_onesided_at_1hz=asd_falloff6,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="relax_falloff6",
        )

        asd_falloff8 = (
            self.accel_asd_onesided
            * self.f_knee_hz
            * self.f_relax_hz**2
            / (2 * math.pi)
        )
        falloff8 = NoiseDefFalloff8(
            asd_onesided_at_1hz=asd_falloff8,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="relax_falloff8",
        )

        asd_infrared = (
            self.accel_asd_onesided
            * self.f_knee_hz
            * math.sqrt(1 + (self.f_relax_hz / self.f_break_hz) ** 4)
            / (2 * math.pi)
        )
        infrared = NoiseDefInfraRed(
            asd_onesided_at_1hz=asd_infrared,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="relax_infrared",
        )

        asd_red = (
            self.accel_asd_onesided
            * math.sqrt(1 + (self.f_relax_hz / self.f_break_hz) ** 4)
            / (2 * math.pi)
        )
        red = NoiseDefRed(
            asd_onesided_at_1hz=asd_red,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="relax_red",
        )

        asd_white = (
            self.accel_asd_onesided
            * self.f_knee_hz
            / (2 * math.pi * self.f_break_hz**2)
        )
        white = NoiseDefWhite(
            asd_onesided_const=asd_white, f_sample=self.f_sample, name="relax_white"
        )

        asd_violet = self.accel_asd_onesided / (2 * math.pi * self.f_break_hz**2)
        violet = NoiseDefViolet(
            asd_onesided_at_1hz=asd_violet, f_sample=self.f_sample, name="relax_violet"
        )

        return [
            falloff8,
            falloff6,
            infrared,
            red,
            white,
            violet,
        ]

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        noise_components: list[NoiseDefBase]

        match self.shape:
            case TestMassNoiseShape.ORIGINAL:
                noise_components = self._elementary_original()
            case TestMassNoiseShape.LOWFREQ_RELAX:
                noise_components = self._elementary_lowfreq_relax()
            case _ as unreachable:
                assert_never(unreachable)

        ndef = NoiseDefSum(noise_components, self.name)
        return ndef.elementary()

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"shape = {self.shape.value} \n"
            f"accel_asd_onesided [(m/s^2)/sqrt(Hz)] = {self.accel_asd_onesided} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_knee_hz [Hz] = {self.f_knee_hz} \n"
            f"f_break_hz [Hz] = {self.f_break_hz} \n"
            f"f_relax_hz [Hz] = {self.f_relax_hz} \n"
        )


class NoiseDefOMS(NoiseDefBacklink):
    r"""Defines LISA instrument optical metrology system (OMS) noise allocation

    This noise approximates a model PSD for fractional frequency
    deviations given by

    .. math::

        S^\text{ffd}_\mathrm{bl}(f) = \qty(\frac{2 \pi A}{c})^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]
        = \qty(\frac{2 \pi A}{c})^2 f^2 + \qty(\frac{2 \pi A f_\mathrm{knee}^2}{c})^2 f^{-2}.

    Note that the amplitude coefficient refers to the displacement amplitude and not
    the fractional frequency amplitude. The corresponding PSD for the displacement is
    given by

    .. math::

        S^\text{m}_\mathrm{bl}(f) = A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ].

    Multiplying by :math:`(2 \pi f / c)^2` yields the fractional frequency
    deviations PSD.

    Note that the level of this noise depends on the interferometer and the type of beatnote.

    .. warning::

       This corresponds to the overall allocation for the OMS noise from the Performance
       Model. It is a collection of different noises, some of which are duplicates of standalone
       noises we already implement in the simulation (e.g., backlink noise).

    This noise is implemented as an alias for NoiseDefBacklink which is currently using
    the exact same PSD model.
    """


class NoiseDefLongitudinalJitter(NoiseDefViolet):
    r"""Defines LISA instrument MOSA longitudinal jitter noise

    This computes the jitter in terms of the velocity jitter given by
    the continous one-sided PSD

    .. math::

        S^\text{vel}_\mathrm{jitter}(f) = (2 \pi A)^2 f^2.

    This noise is not dimensionless. Generated noise samples have unit
    of velocity, and the PSD has units of [(m/s)^2 / Hz)].

    The corresponding onse-sided PSD in terms of displacement is given by
    white noise

    .. math::

        S^\text{disp}_\mathrm{jitter}(f) = A^2,

    which is converted to velocities by multiplying by :math:`(2 \pi f)^2`.

    Note we specify the amplitude of the velocity jitter in terms of the
    coefficient :math:`A` that is is the amplitude of the one-sided ASD of
    the displacement jitter. The unit of :math:`A` is thus [m/sqrt(Hz)].

    Technical note: this noise class is implemented as a subclass of
    NoiseDefViolet, which is a dimensionless general-purpose noise. In the
    context of NoiseDefLongitudinalJitter, the NoiseDefViolet noise is to be
    considered dimensionful with same units as NoiseDefLongitudinalJitter. The
    amplitude parameter asd_onesided_at_1hz of NoiseDefViolet is set to
    :math:`(2 \pi A)`
    """

    def __init__(
        self,
        displacement_asd_onesided: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            displacement_asd_onesided: The coefficient :math:`A` [m/sqrt(Hz)]
            f_sample: The sampling rate [Hz]
            name: Unique name used to derive seeds
        """
        self._displacement_asd_onesided = float(displacement_asd_onesided)
        asd_violet = 2 * math.pi * self._displacement_asd_onesided
        super().__init__(
            asd_onesided_at_1hz=asd_violet,
            f_sample=f_sample,
            name=name,
        )

    @property
    def displacement_asd_onesided(self) -> float:
        """The amplitude coefficient :math:`A` [m/sqrt(Hz)]"""
        return self._displacement_asd_onesided

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"displacement_asd_onesided [m/sqrt(Hz)] = {self.displacement_asd_onesided} \n"
        )


class NoiseDefAngularJitter(NoiseDefRedAndViolet):
    r"""Defines LISA instrument jitter for one angular degree of freedom


    This defines the angular jitter in terms of angular velocity,
    approximating a model PSD given by

    .. math::

        S^\text{rad/s}_\mathrm{jitter}(f) &=
        (2 \pi A)^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]

        &= (2 \pi A)^2 f^2 + (2 \pi A f_\mathrm{knee}^2)^2 f^{-2}.

    Generated noise samples have unit [Rad/s], and the ASD has units
    [(Rad/s)/sqrt(Hz)].

    Note that the amplitude coefficient is given in terms of the jitter
    of the angle, not the angular velocity. The power spectral density in
    angle is given by

    .. math::

        S^\text{rad}_\mathrm{jitter}(f) =
        A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ],

    which is converted to angular velocity by mutliplying by :math:`(2 \pi f)^2`,


    The noise is implemented using NoiseDefRedAndViolet as a base, see class
    documentation for further details.
    """

    def __init__(
        self,
        angle_asd_onesided: float,
        f_min_hz: float,
        f_knee_hz: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            angle_asd_onesided: amplitude coefficient :math:`A` for ASD of angle [Rad/sqrt(Hz)]
            f_min_hz: frequency cutoff for red noise component [Hz]
            f_knee_hz: transition frequency between violet and red components [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        self._angle_asd_onesided = float(angle_asd_onesided)
        asd1s = 2 * math.pi * self._angle_asd_onesided
        super().__init__(
            asd_onesided_at_1hz=asd1s,
            f_min_hz=f_min_hz,
            f_knee_hz=f_knee_hz,
            f_sample=f_sample,
            name=name,
        )

    @property
    def angle_asd_onesided(self) -> float:
        """Amplitude coefficient :math:`A` for ASD of angle [Rad/sqrt(Hz)]"""
        return self._angle_asd_onesided

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"angle_asd_onesided [Rad/sqrt(Hz)] = {self.angle_asd_onesided} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_knee_hz [Hz] = {self.f_knee_hz} \n"
        )


class NoiseDefDWS(NoiseDefViolet):
    r"""Defines LISA instrument DWS measurement noise.

    This defines the DWS measurement noise in terms of angular velocity,
    approximating a model PSD given by

    .. math::

        S^\text{rad/s}_\mathrm{dws}(f) = (2 \pi A)^2 f^2.

    Generated noise samples have unit [Rad/s], and the ASD has units
    [(Rad/s) / sqrt(Hz)].

    Note that the amplitude coefficient :math:`A` refers to the ASD of
    angles, not angular velocity. The PSD in angle is given by

    .. math::

        S^\text{rad}_\mathrm{dws}(f) = A^2,

    which is converted to the angular velocity PSD by mutliplying by
    :math:`(2 \pi f)^2`,


    Technical note: this noise class is implemented as a subclass of
    NoiseDefViolet, which is a dimensionless general-purpose noise. In the
    context of NoiseDefLongitudinalJitter, the NoiseDefViolet noise is to be
    considered dimensionful with same units as NoiseDefDWS. The
    amplitude parameter asd_onesided_at_1hz of NoiseDefViolet is set to
    :math:`(2 \pi A)` and has units of [Rad/sqrt(Hz)].
    """

    def __init__(
        self,
        angle_asd_onesided: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            angle_asd_onesided: amplitude coefficient :math:`A` for ASD of angle [Rad/sqrt(Hz)]
            f_sample: The sampling rate [Hz]
            name: Unique name used to derive seeds
        """
        self._angle_asd_onesided = float(angle_asd_onesided)
        asd_violet = 2 * math.pi * self._angle_asd_onesided
        super().__init__(
            asd_onesided_at_1hz=asd_violet,
            f_sample=f_sample,
            name=name,
        )

    @property
    def angle_asd_onesided(self) -> float:
        """The amplitude coefficient :math:`A` for ASD of angle [Rad/sqrt(Hz)]"""
        return self._angle_asd_onesided

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"angle_asd_onesided [Rad/sqrt(Hz)] = {self.angle_asd_onesided} \n"
        )


class NoiseDefMocTimeCorrelation(NoiseDefWhite):
    r"""Defines LISA instrument MOC time correlation noise

    High-level noise model for the uncertainty we have in computing the MOC
    time correlation (or time couples), i.e., the equivalent TCB times for the
    equally-sampled TPS timestamps.

    Assumed to be a white noise in timing,

    .. math::

        S^\text{s}_\mathrm{moc}(f) = A^2.

    The generated noise has units of [s], and the ASD units of [s/sqrt(Hz)].


    The noise is implemented as an alias for the formally dimensionless
    NoiseDefWhite. However, the latter is to be interpreted here as noise
    for a dimensionful quantity with unit [s], such that the ASD
    amplitude has unit [s/sqrt(Hz)].
    """

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"asd_onesided_const [s/sqrt(Hz)] = {self.asd_onesided_const} \n"
        )
