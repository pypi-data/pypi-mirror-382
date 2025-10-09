"""The noisy.noise_defs module contains classes for parameters of each noise type and its PSD.

The module module does not generate noise, but provides the definitions used in
the modules dedicated to noise generation. See noise_gen_numpy for a numpy-based
noise stream generator, and streams.noise_alt for a generator based on the
streams package.

The noise definitions can be divided in two categories: elementary noises that the
noise generator can generate directly, and noises that first have to be expressed in
terms of elementary noises. All noise classes have a method elementary() that returns
an equivalent elementary noise. For example, the non-elementary NoiseDefRed describes
filtered white noise that can be represented in terms of the elementary noises
NoiseDefFiltered and NoiseDefWhite. In addition, the elementary method can apply
optimizations. This is used to convert noises with zero amplitude into an
NoiseDefZero, allowing noise generators to optimize away zero-amplitude noises.

All noises have a sample rate and a name, stored in the base class NoiseDefBase.
The name is used when deriving random seeds from a master seed. Naming noises
differently makes them uncorrelated. Noise classes used within a non-elementary noise
instance are generated with a seed that also incorporates the names of all
parent classes. For example, several noise classes create a NoiseDefWhite instance
named "white" within their elementary() method. Yet those will be generated with
different seeds, unless the names of the parent class also agree.

By design, the names of noises and the master seed of the generator fully determine
the seed. The order of instance creation does not matter, neither the amount of
instances. There is also no random element. The noise parameters can also enter
the seed generation via optimizations. For example if a sum involving only one noise
with non-zero amplitude is replaced by the nonzero component.

The intended usage is to name each noise definition
uniquely (with the exception of noises used internally within other noises) to
obtain uncorrelated noises when passing the definition to the generator.
Computing correlated noises is not within the scope of this module. Using
the same name for two noise definitions can lead to unintended results
and should be avoided.

The noise classes provide a method discrete_psd_twosided() which computes the
two-sided PSD of the discrete noise samples that would be generated (defined in
the limit of infinite signal length). Those methods do not generate noises but rely
on analytically computed PSDs. Note that the discrete PSD is a continuous function
of frequency, but differs from the continuous signal PSDs that the various noises
aim to approximate. In particular, the discrete PSD is periodic in frequency,
with period given by the sample rate.

Instances of noise definitions can be added together. Generating noise samples
from the resulting noise definition will result in a noise with PSD that is the
sum of the individual PSDs. The noise is uncorrelated with the noises that
would be generated for the individual noise definitions, since the seed of
the sum contains the name of the sum, which is computed from the names of the
summed noises.
Noise definitions can also be multiplied by constant scalars. This results in
a noise definition with ASD scaled by the factor. As with sums, generating noise
from a scaled noise defintion is uncorrelated with noise generated for the unscaled
definition.

If arithmetic combinations of the same noise realization are needed, one should instead
first generate the individual noises, and then directly operate on the resulting arrays
with noise samples.

The noises described by the definitions in this module refer to quantities with
different units as defined in the documentation of each noise class. Some noise
definitions do not refer to specific physical quantities, but represent general
purpose spectral shapes. On their own, those general purpose noises are formally
dimensionless, but dimensions will be re-interpreted when used in the context
of implementing other dimensionful models.


Frequency parameters such as sample rates are all in [Hz]. Also the PSD methods employ
frequencies in units [Hz]. Thus, PSDs of dimensionless quantities are all in units
[1/Hz] and ASDs in units [1/sqrt(Hz)]. For noises of a dimensionful quantity with
unit [u], the ASD unit is [u/sqrt(Hz)] and the PSD unit [u^2/Hz].

All noises in this module follow a Gaussian distribution for any individual noise
sample, with zero mean.
"""

from __future__ import annotations

import math
import operator
import textwrap
from abc import ABC, abstractmethod
from functools import reduce
from typing import TYPE_CHECKING

import numpy as np
from scipy import signal

from lisainstrument.sigpro.iir_filters_numpy import DefFilterIIR, make_iir_def_cumsum

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


def psd_onesided_from_psd_twosided(psd2):
    """Compute the one-sided power spectral density (PSD) from a two-sided PSD

    Arguments:
        psd2: Two-sided PSD [1/Hz]

    Returns:
        One-sided PSD [1/Hz]

    """
    return 2.0 * psd2


def psd_twosided_from_psd_onesided(psd1):
    """Compute the two-sided PSD from a one-sided PSD

    Arguments:
        psd1: One-sided PSD [1/Hz]

    Returns:
        Two-sided PSD [1/Hz]

    """
    return psd1 / 2.0


def asd_onesided_from_psd_twosided(psd2):
    """Compute the one-sided amplitude spectral density (ASD) from a two-sided PSD

    Arguments:
        psd2: Two-sided PSD [1/Hz]

    Returns:
        One-sided ASD [1/sqrt(Hz)]
    """
    return np.sqrt(psd_onesided_from_psd_twosided(psd2))


def psd_onesided_from_asd_onesided(asd1):
    """Compute the one-sided PSD from the one-sided ASD

    Arguments:
        asd1: One-sided ASD [1/sqrt(Hz)]

    Returns:
        One-sided PSD [1/Hz]
    """
    return asd1**2


def psd_twosided_from_asd_onesided(asd1):
    """Compute two-sided PSD from one-sided ASD

    Arguments:
        asd1: One-sided ASD [1/sqrt(Hz)]

    Returns:
        Two-sided PSD [1/Hz]
    """
    psd1 = psd_onesided_from_asd_onesided(asd1)
    return psd_twosided_from_psd_onesided(psd1)


def iir_freq_resp(iir_filt: DefFilterIIR, f: ArrayLike, f_samp: float) -> np.ndarray:
    """Compute the frequency response of a IIR filter

    Arguments:
        iir_filt: The filter definition containing the coefficients
        f: Array with frequencies for which to compute response [Hz]
        f_samp: Sampling rate [Hz]

    Returns:
        Array with frequency response

    Note: in principle the frequency units are arbitrary (but the same for f
    and f_samp) but the general convention in this module is that frequencies
    are in Hz.
    """
    f = np.array(f, dtype=np.float64)
    _, h = signal.freqz(iir_filt.coeffs_b, iir_filt.coeffs_a, worN=f, fs=f_samp)
    return h.reshape(f.shape)


class NoiseDefBase(ABC):
    """Base class for all noise definitions

    This stores the sample rate and a name. The name will be used while generating
    noise from the definition to derive a seed for the random number generator
    used. It is up to the user to specify unique names to ensure uncorrelated
    noises. Note that defining correlations between noises is not in the scope of
    this noise definition class.

    The sample rate is used when generating noises from the definition, and to
    compute the corresponding discrete PSD.

    All noises definitions must implement the discrete_psd_twosided() method,
    providing the exact discrete PSD of the generated noise.

    The class defines summation and multiplication operators. Summation of two
    noise definitions results in a noise definition for the sum of two uncorrelated
    noises. Multiplication of a noise definition with a scalar value results in a
    noise definition with ASD scaled by that factor.
    """

    def __init__(self, f_sample: float, name: str):
        """Constructor

        Arguments:
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """

        self._f_sample = float(f_sample)
        self._name = str(name)

        if not (self.f_sample > 0 and np.isfinite(self.f_sample)):
            msg = f"Attempt to create noise with invalid sample rate {self.f_sample}"
            raise ValueError(msg)

    @abstractmethod
    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""

    @property
    def f_sample(self) -> float:
        """Sampling rate at which noise will be generated [Hz]"""
        return self._f_sample

    @property
    def name(self) -> str:
        """Noise name used in generation of random seeds"""
        return self._name

    def __add__(self, other: NoiseDefBase) -> NoiseDefBase:
        """The sum of two noise definitions

        The sum is a noise definition with discrete PSD given by sum of the individual PSDs.
        One can only add noise definitions with identical sample rates.
        """
        if not isinstance(other, NoiseDefBase):
            msg = "Can only add another NoiseDefBase to NoiseDefBase"
            raise TypeError(msg)
        name = f"{self.name} + {other.name}"
        return NoiseDefSum([self, other], name)

    def __mul__(self, other: float) -> NoiseDefScaled:
        """A noise definition multiplied by a constant

        This results in a noise definition with ASD given by original ASD (not PSD)
        scaled by the factor.
        """
        factor = float(other)
        name = f"{factor} * {self.name}"
        return NoiseDefScaled(base=self, factor=factor, name=name)

    def __rmul__(self, other: float) -> NoiseDefScaled:
        """A constant multiplied by a noise definition

        Same as noise definition multiplied by the constant.
        """
        return self.__mul__(other)

    def __str__(self) -> str:
        return (
            f"Noise type {self.__class__.__name__}\n"
            f"name = {self.name}\n"
            f"f_sample [Hz] = {self.f_sample}\n"
        )

    @abstractmethod
    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""


def common_sample_rate(noises: list[NoiseDefBase]) -> float:
    """Return common sample rate of noises or raise ValueError

    Arguments:
        noises: list of noise definitions with identical sample rate

    Returns:
        Common sample rate
    """
    rates = np.unique([n.f_sample for n in noises])
    if len(rates) > 1:
        msg = "Attempt to combine noises with different sample rates"
        raise ValueError(msg)
    if len(rates) == 0:
        msg = "Cannot obtain common sample rate for empty list of noises"
        raise RuntimeError(msg)
    return rates[0]


class NoiseDefZero(NoiseDefBase):
    r"""Defines zero noise

    The one-sided ASD of this noise is zero. Noise generated for this
    definition will simply be samples that are all zero. However, the
    purpose of this noise definition is to simplify logistics, not to
    generate zeros.
    """

    def __init__(self, f_sample: float = 1.0, name: str = "ZERO"):
        """Constructor

        Note: unlike for other noise types, the name field has no purpose since no
        seeds for random number generation are needed in this case.

        Arguments:
            f_sample: Sample rate to generate noise with [Hz]
            name: arbitrary name.
        """
        super().__init__(f_sample, name)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        return self

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return np.zeros_like(f, dtype=np.float64)


class NoiseDefWhite(NoiseDefBase):
    r"""Defines a Gaussian white noise

    The one-sided ASD of this noise is a constant :math:`A`.

    This is a general-purpose noise formally defined for dimensionless
    quantities. The ASD has units [1/sqrt(Hz)].

    Individual samples of noise series generated for this definition are
    uncorrelated with each other and follow a Gaussian normal distribution
    with zero mean and standard deviation of :math:`\sigma = \sqrt{f_s S}`,
    where :math:`f_s` is the sample rate and :math:`S=A^2/2` is the constant
    two-sided PSD.
    """

    def __init__(self, asd_onesided_const: float, f_sample: float, name: str):
        """Constructor

        Arguments:
            asd_onesided_const: The coefficient :math:`A` [1/sqrt(Hz)]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_const = float(asd_onesided_const)
        if self._asd_onesided_const < 0:
            msg = f"NoiseDefWhite: negative ASD not allowed, got {asd_onesided_const=}"
            raise RuntimeError(msg)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        if self._asd_onesided_const == 0:
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        return self

    @property
    def asd_onesided_const(self) -> float:
        """The one-sided constant ASD [1/sqrt(Hz)]"""
        return self._asd_onesided_const

    @property
    def psd_twosided_const(self) -> float:
        """The two-sided constant PSD [1/Hz]"""
        return psd_twosided_from_asd_onesided(self.asd_onesided_const)

    @property
    def sample_rms(self) -> float:
        """The RMS for the Gaussian distribution of a single noise sample"""
        return math.sqrt(self.f_sample * self.psd_twosided_const)

    def sample_distribution(self, x: np.ndarray) -> np.ndarray:
        """Evaluate the zero-mean Gaussian distribution for single noise samples"""
        sigma = self.sample_rms
        return np.exp(-((x / sigma) ** 2) / 2) / (np.sqrt(2 * np.pi) * sigma)

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        psd = np.empty_like(f, dtype=np.float64)
        psd[:] = psd_twosided_from_asd_onesided(self.asd_onesided_const)
        return psd

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_const [1/sqrt(Hz)] = {self.asd_onesided_const} \n"
        )


class NoiseDefFiltered(NoiseDefBase):
    """Defines a noise obtained by applying one or more IIR filters to another noise

    The discrete PSD of this noise is the one of the base noise times
    the squared frequency response of each IIR filter.

    When generating  finite amount of samples for filtered noise using
    infinite response filters, all samples are in principle affected by the
    impact of the left boundary. Depending on the filter coefficients, the
    impact decreases to insignificance after a certain amount of samples,
    denoted here as the burn-in size. This amount needs to be specified by
    the user together with the filter. The noise generator will generate
    the same amount of extra samples at the beginning, which are then discarded.

    Note: not all IIR filters can be used to generate stationary noise. It is
    up to the user to ensure the filters are meaningful.

    """

    def __init__(
        self,
        base: NoiseDefBase,
        iirfilters: list[DefFilterIIR],
        burn_in_size: int,
        name: str,
    ):
        """Constructor

        The sample rate taken from the base noise definition.

        Arguments:
            base: The definition of the noise to be filtered
            iirfilters: List of IIR filter definitions to apply in order
            burn_in_size: number of throw-away samples
            name: Unique name used to generate seeds
        """
        super().__init__(base.f_sample, name)
        self._base = base
        self._iirfilters = list(iirfilters)
        self._burn_in_size = int(burn_in_size)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        ebase = self.base.elementary()
        if isinstance(ebase, NoiseDefZero):
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        return NoiseDefFiltered(ebase, self.iirfilters, self.burn_in_size, self.name)

    @property
    def base(self) -> NoiseDefBase:
        """The definition of the base noise to be filtered"""
        return self._base

    @property
    def iirfilters(self) -> list[DefFilterIIR]:
        """The list of IIR filters to apply to the base noise"""
        return self._iirfilters

    @property
    def burn_in_size(self) -> int:
        """Number of extra samples that should be discarded to avoid edge effects"""
        return self._burn_in_size

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        base_psd = self.base.discrete_psd_twosided(f)
        if self.iirfilters:
            responses = (
                iir_freq_resp(filt, f, self.f_sample) for filt in self.iirfilters
            )
            fresp = reduce(operator.mul, responses)
            return base_psd * np.abs(fresp) ** 2
        return base_psd

    def __str__(self) -> str:
        sfilt = "\n".join(str(f) for f in self.iirfilters)

        return (
            f"{super().__str__()}"
            f"burn-in size = {self.burn_in_size} \n"
            f"IIR filters: \n"
            f"{textwrap.indent(sfilt, '  ')} \n"
            f"Base noise: \n"
            f"{textwrap.indent(str(self.base), '  ')}"
        )


class NoiseDefGradient(NoiseDefBase):
    """Defines a noise obtained by finite differencing of another noise

    Noise samples will be generated by applying a second order central finite
    difference operator to noise samples generated from the base noise definition.
    The result is also scaled. The discrete PSD in the limit of low frequencies
    is the base PSD times the frequency squared.

    Note: when approaching the Nyquist frequency, the discrete PSD
    deviates from this simple scaling. The exact PSD can be obtained using
    the discrete_psd_twosided() method.
    """

    def __init__(self, base: NoiseDefBase, name: str):
        """Constructor

        The sample rate taken from the base noise definition.

        Arguments:
            base: The definition of the noise to be filtered
            name: Unique name used to generate seeds
        """
        super().__init__(base.f_sample, name)
        self._base = base

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        ebase = self.base.elementary()
        if isinstance(ebase, NoiseDefZero):
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        return NoiseDefGradient(ebase, self.name)

    @property
    def base(self) -> NoiseDefBase:
        """The base noise to which the finite difference should be applied"""
        return self._base

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data

        The formula used was obtained by direct calculation from the PSD
        definition applied to central finite differences, in the limit of
        infinitly long signals.
        """
        base_psd = self.base.discrete_psd_twosided(f)
        fresp = np.sin(2 * np.pi * f / self.f_sample) * self.f_sample / (2 * np.pi)
        return base_psd * fresp**2

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"Base noise: \n"
            f"{textwrap.indent(str(self.base), '  ')}"
        )


class NoiseDefCumSum(NoiseDefBase):
    """Defines a noise obtained by taking the cumulative sum of another noise

    Noise samples will be generated by computing the cumulative sum of noise
    samples generated from the base noise definition. The result is also scaled.

    The discrete PSD in the limit of low frequencies is the base PSD divided by
    frequency squared.

    Warning: depending on the base noise, this might not lead to a valid stationary
    noise with defined PSD.
    """

    def __init__(self, base: NoiseDefBase, name: str):
        """Constructor

        The sample rate taken from the base noise definition.

        Arguments:
            base: The definition of the noise to be filtered
            name: Unique name used to generate seeds
        """
        super().__init__(base.f_sample, name)
        self._base = base

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        ebase = self.base.elementary()
        if isinstance(ebase, NoiseDefZero):
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        return NoiseDefCumSum(ebase, self.name)

    @property
    def base(self) -> NoiseDefBase:
        """The base noise for which to compute the cumulative sum"""
        return self._base

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data

        Note: we compute the PSD by using the frequncy response of an IIR filter
        equivalent to the cumulative sum.
        """
        base_psd = self.base.discrete_psd_twosided(f)
        filt = make_iir_def_cumsum()
        fresp = iir_freq_resp(filt, f, self.f_sample)
        scale = 2 * math.pi / self.f_sample
        return base_psd * np.abs(fresp * scale) ** 2

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"Base noise: \n"
            f"{textwrap.indent(str(self.base), '  ')}"
        )


class NoiseDefSum(NoiseDefBase):
    """Defines a noise that is the sum of two or more uncorrelated noises.

    This describes a noise definition with a PSD given by the sum of the
    individual noise definitions. Such a PSD describes the PSD of a noise
    obtained by generating uncorrelated noises with the PSDs of the individual
    zero-mean noise definitions and adding the noise samples.
    All valid noise definitions described in this module have zero mean.

    The unit of the summed noise ASD is the same as the individual ASD units,
    which have to be all the same. The latter is not enforced, it is up to the
    user to make sure not to add noises with mismatched units.

    Warning: when one ore more of the added noises are ill-defined, e.g.
    NoiseDefCumSum with an ill-suited base noise, the mean value is not
    zero or even defined, due to low-frequency divergence. Summing might
    thus worsen such problems.
    """

    def __init__(self, components: list[NoiseDefBase], name: str):
        """Constructor

        The sample rate taken from the base noise definitions. One can
        only add noises with identical sample rates.

        Arguments:
            components: List of noise definitions to add up
            name: Unique name used to generate seeds
        """
        self._components = list(components)
        if not self._components:
            msg = "NoiseDefSum needs at least one component"
            raise RuntimeError(msg)

        fsamp = common_sample_rate(self.components)

        super().__init__(fsamp, name)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        ecomps = [c.elementary() for c in self.components]
        nonzero = [c for c in ecomps if not isinstance(c, NoiseDefZero)]
        if not nonzero:
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        if len(nonzero) == 1:
            return nonzero[0]
        return NoiseDefSum(ecomps, self.name)

    @property
    def components(self) -> list[NoiseDefBase]:
        """The definitions of the noises to be added"""
        return self._components

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        psds = (c.discrete_psd_twosided(f) for c in self.components)
        return reduce(operator.add, psds)

    def __str__(self) -> str:
        comps = [
            f"Component {i} \n{textwrap.indent(str(c),'  ')}"
            for i, c in enumerate(self.components)
        ]
        scomp = "\n".join(comps)
        return f"{super().__str__()} {scomp} \n"


class NoiseDefScaled(NoiseDefBase):
    """Defines a noise obtained by scaling another noise by a constant

    Generating this noise is equivalent (in the statistical sense) to
    generating the base noise and multiply the samples by the scaling factor.
    Note however that a different seed value will by used, such that generating
    noise samples from the base definition and the scaled definition will
    yield uncorrelated noises.

    The discrete PSD is the original one times the scaling factor squared,
    the ASD is the original one time the scaling factor.
    The ASD of the scaled noise definition depends pn the unit of the
    base ASD and the unit of the scaling factor. The latter is up to the
    user and might be dimensionless or not.
    """

    def __init__(self, base: NoiseDefBase, factor: float, name: str):
        """Constructor

        The sample rate taken from the base noise definition.

        Arguments:
            base: The definition of the noise to be filtered
            factor: The scaling factor for the ASD
            name: Unique name used to generate seeds
        """
        super().__init__(base.f_sample, name)
        self._base = base
        self._factor = float(factor)
        if self._factor < 0:
            msg = f"NoiseDefScaled: negative noise amplitudes not allowed, got {factor=}. Stay positive!"
            raise RuntimeError(msg)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent definition in terms of elementary noises"""
        ebase = self.base.elementary()
        if isinstance(ebase, NoiseDefZero) or self.factor == 0:
            return NoiseDefZero(f_sample=self.f_sample, name=self.name)
        if isinstance(ebase, NoiseDefScaled):
            return NoiseDefScaled(
                ebase.base, factor=self.factor * ebase.factor, name=self.name
            )
        return NoiseDefScaled(ebase, factor=self.factor, name=self.name)

    @property
    def base(self) -> NoiseDefBase:
        """The definition of the noise to be scaled"""
        return self._base

    @property
    def factor(self) -> float:
        """The scale factor to apply to the noise samples"""
        return self._factor

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        psdbase = self.base.discrete_psd_twosided(f)
        return psdbase * self.factor**2

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"ASD scale factor = {self.factor} \n"
            f"Base noise: \n"
            f"{textwrap.indent(str(self.base), '  ')}"
        )


class NoiseDefRed(NoiseDefBase):
    """Defines red (aka Brownian) noise with ASD approximating :math:`f^{-1}` falloff.

    In the limit of frequencies small compared to the sample rate, the
    PSD scales with :math:`f^{-2}` (the ASD with :math:`f^{-1}`), but only
    until a cutoff frequency, below which the PSD approaches a constant.
    The cutoff frequency needs to be strictly positive.
    The exact discrete PSD can be obtained from discrete_psd_twosided().

    The noise amplitude is specified in terms of the amplitude of the
    above idealized scaling law at a fiducal frequency of 1 Hz. Note however
    that the actual discrete ASD of the noise samples at the same
    frequency differs from this value, depending on the sample rate.
    The two agree only in the limit where the sample rate is much bigger
    than the fiducial frequency of 1 Hz.

    This is a general-purpose noise formally defined for dimensionless
    quantities. The ASD has units [1/sqrt(Hz)].
    """

    def __init__(
        self, asd_onesided_at_1hz: float, f_min_hz: float, f_sample: float, name: str
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: The one-sided ASD amplitude coefficient [1/sqrt(Hz)]
            f_min_hz: The cutoff frequency below which PSD approaches a constant [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._f_min_hz = float(f_min_hz)

        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefRed got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz <= 0:
            msg = f"NoiseDefRed requires f_min_hz > 0, got {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    @property
    def f_min_hz(self) -> float:
        """Cutoff frequency below which PSD approaches a constant [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises

        The red noise is equivalent to white noise filtered by a particular
        IIR filter
        """

        scaling_filter = 1.0 / (self.f_sample * self.f_min_hz)
        asd1s = self.asd_onesided_at_1hz * scaling_filter
        base = NoiseDefWhite(
            asd_onesided_const=asd1s, f_sample=self.f_sample, name="White"
        )

        coeff_b = [2.0 * math.pi * self.f_min_hz]
        coeff_a = [1.0, -1.0 * math.exp(-2.0 * math.pi * self.f_min_hz / self.f_sample)]
        burn_in = int(math.ceil(2.0 * self.f_sample / self.f_min_hz))
        filt = DefFilterIIR(coeff_a, coeff_b)

        ndef = NoiseDefFiltered(
            base=base,
            iirfilters=[filt],
            burn_in_size=burn_in,
            name=self.name,
        )
        return ndef.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefAlpha(NoiseDefBase):
    r"""Defines colored noise with PSD approximating :math:`1/f^\alpha` power law.

    In the limit of frequencies small compared to the sample rate, the
    PSD scales according to a power law :math:`f^{-\alpha}`, but only
    within a given frequency range, outside of which the PSD approaches a constant.
    The exact discrete PSD can be obtained from discrete_psd_twosided().
    The power law exponent is restricted to the range :math:`0.01 \le \alpha \le 2`.

    For compatibility with previous noise generation code, the amplitude is
    specified in a very roundabout way: The alpha noise is defined as white noise
    filtered by a chain of IIR filters, each of which has a frequency response
    approximating the desired global power law within a small frequency segment,
    while approaching constant values above and below the segment.
    The amplitude of the noise obtained after applying all filters is scaled
    with a factor based on the last segment only, such that the power law
    model that the last filter would approximate by itself has the specified
    amplitude at a fiducial frequency of 1 Hz.

    This definition is not very useful, in particular since the choice of segments
    is computed internally and thus hidden from the user. However, the exact discrete
    PSD can be obtained from the discrete_psd_twosided() method.

    This is a general-purpose noise formally defined for dimensionless
    quantities. The ASD has units [1/sqrt(Hz)].
    """

    def __init__(
        self,
        asd_onesided_at_1hz: float,
        f_min_hz: float,
        f_max_hz: float,
        alpha: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: The incomprehensibly defined amplitude [1/sqrt(Hz)]
            f_min_hz: The frequency below which PSD approaches a constant [Hz]
            f_max_hz: The frequency above which PSD approaches another constant [Hz]
            alpha: The PSD falloff exponent
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._f_min_hz = float(f_min_hz)
        self._f_max_hz = float(f_max_hz)
        self._alpha = float(alpha)

        if self.alpha > 2.0 or self.alpha < 0.01:
            msg = f"NoiseDefAlpha: exponent must be in the range 0.01 <= alpha <= 2., got {self.alpha}"
            raise ValueError(msg)

        if self.f_sample < 2.0 * self.f_max_hz:
            msg = f"The sampling rate must be at least 2 x f_max_hz (= {2. * self.f_max_hz} Hz)."
            raise ValueError(msg)

        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefAlpha got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz <= 0:
            msg = f"NoiseDefAlpha requires f_min_hz > 0, got {f_min_hz=}"
            raise RuntimeError(msg)

        if self._f_max_hz <= 0:
            msg = f"NoiseDefAlpha requires f_max_hz > 0, got {f_max_hz=}"
            raise RuntimeError(msg)

        if self._f_max_hz <= self._f_min_hz:
            msg = f"NoiseDefAlpha requires f_max_hz > f_min_hz, got {f_min_hz=}, {f_max_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """The incomprehensibly defined amplitude [1/sqrt(Hz)]"""
        return self._asd_onesided_at_1hz

    @property
    def f_min_hz(self) -> float:
        """Frequency below which PSD approaches a constant [Hz]"""
        return self._f_min_hz

    @property
    def f_max_hz(self) -> float:
        """Frequency above which PSD approaches another constant [Hz]"""
        return self._f_max_hz

    @property
    def alpha(self) -> float:
        """Exponent of the power-law falloff for the PSD"""
        return self._alpha

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def _calc_filter(self, f_min: float, f_max: float) -> DefFilterIIR:
        """Computes the filter responsible for a single frequency segment"""
        pi = math.pi
        fs = self.f_sample
        b0 = (fs + f_max * pi) / (fs + f_min * pi)
        b1 = -(fs - f_max * pi) / (fs + f_min * pi)
        a1 = -(fs - f_min * pi) / (fs + f_min * pi)
        return DefFilterIIR([1.0, a1], [b0, b1])

    def _segments(self) -> list[tuple[float, float]]:
        """Divide the frequency range into suitable smaller segments"""
        log_w_min = math.log10(2.0 * math.pi * self.f_min_hz)
        log_w_max = math.log10(2.0 * math.pi * self.f_max_hz)
        num_spectra = int(math.ceil(4.5 * (log_w_max - log_w_min)))
        dp = (log_w_max - log_w_min) / num_spectra

        segs: list[tuple[float, float]] = []
        for i in range(0, num_spectra):
            log_p_i = log_w_min + dp * 0.5 * ((2.0 * i + 1.0) - self.alpha / 2.0)
            filter_f_min = 10.0**log_p_i / (2.0 * math.pi)
            filter_f_max = 10.0 ** (log_p_i + (dp * self.alpha / 2.0)) / (2.0 * math.pi)
            segs.append((filter_f_min, filter_f_max))
        return segs

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises

        The alpha noise is equivalent to white noise filtered by a chain
        of suitable IIR filters.
        """
        segments = self._segments()

        filters = [self._calc_filter(*seg) for seg in segments]

        filt_fmax_last = segments[-1][1]
        scaling_filter = 1.0 / (filt_fmax_last) ** (self.alpha / 2.0)

        asd1s = self.asd_onesided_at_1hz * scaling_filter
        base = NoiseDefWhite(
            asd_onesided_const=asd1s, f_sample=self.f_sample, name="White"
        )

        filt_fmin_first = segments[0][0]
        burn_in = int(math.ceil(2.0 * self.f_sample / filt_fmin_first))

        ndef = NoiseDefFiltered(
            base=base,
            iirfilters=filters,
            burn_in_size=burn_in,
            name=self.name,
        )
        return ndef.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_max_hz [Hz] = {self.f_max_hz} \n"
            f"alpha = {self.alpha} \n"
        )


class NoiseDefPowerLaw(NoiseDefBase):
    r"""Defines noise with ASD approximating :math:`f^\gamma` power law.

    The exact discrete noise PSD depends on the power law exponent, based on
    which different noise models are chosen as follows.
    For :math:`\gamma = -1`, NoiseDefPowerLaw is equivalent to
    NoiseDefRed. In the range :math:`-1 < \gamma < 0`, it is equivalent to
    NoiseDefAlpha with :math:`\alpha = -2 \gamma`. For :math:`\gamma = 0`,
    it is equivalent to NoiseDefWhite. Finally, for :math:`\gamma > 0`,
    NoiseDefPowerLaw is equivalent to NoiseDefGradient based on another
    NoiseDefPowerLaw definition with exponent :math:`\gamma - 1`.

    For the case where NoiseDefAlpha is used, the upper frequency cutoff
    (f_max_hz) is set to the Nyquist frequency.

    For the cases where NoiseDefAlpha or NoiseDefRed are used, the lower
    frequency cutoff parameter of these is set to the f_min_hz parameter
    of the NoiseDefPowerLaw. For the cases where NoiseDefWhite is used,
    this parameter is ignored.

    The amplitude is specified by the asd_onesided_at_1hz parameter, which
    is used for the asd_onesided_at_1hz parameter of NoiseDefAlpha or NoiseDefRed,
    and the asd_onesided_const parameter of NoiseDefWhite.

    Note that due to the different models used for different parameter ranges,
    the PSD does not depend on the exponent :math:`\gamma` in a continuous fashion.
    """

    def __init__(
        self,
        asd_onesided_at_1hz: float,
        asd_exp: float,
        f_min_hz: float,
        f_sample: float,
        name: str,
    ):
        r"""Constructor

        Arguments:
            asd_onesided_at_1hz: The ASD amplitude [1/sqrt(Hz)]
            f_min_hz: The lower frequency cutoff, if used by the noise model for the given exponent [Hz]
            asd_exp: The ASD exponent :math:`f^\gamma`
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._asd_exp = float(asd_exp)
        self._f_min_hz = float(f_min_hz)
        if self.asd_exp < -1:
            msg = f"NoiseDefPowerLaw: invalid value for ASD exponent '{self.asd_exp}', must be > -1."
            raise ValueError(msg)
        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefPowerLaw got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)
        if self._f_min_hz < 0:
            msg = f"NoiseDefPowerLaw got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    @property
    def asd_exp(self) -> float:
        r"""The PSD power law exponent  :math:`\gamma`."""
        return self._asd_exp

    @property
    def f_min_hz(self) -> float:
        """Lower cutoff frequency (see above) [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        if self.asd_exp == -1:
            red = NoiseDefRed(
                f_sample=self.f_sample,
                asd_onesided_at_1hz=self.asd_onesided_at_1hz,
                f_min_hz=self.f_min_hz,
                name=self.name,
            )
            return red.elementary()
        if -1 < self.asd_exp < 0:
            fnyquist = self.f_sample / 2.0
            psd_falloff = -2 * self.asd_exp
            alpha = NoiseDefAlpha(
                f_sample=self.f_sample,
                asd_onesided_at_1hz=self.asd_onesided_at_1hz,
                f_min_hz=self.f_min_hz,
                f_max_hz=fnyquist,
                alpha=psd_falloff,
                name=self.name,
            )
            return alpha.elementary()
        if self.asd_exp == 0:
            white = NoiseDefWhite(
                f_sample=self.f_sample,
                asd_onesided_const=self.asd_onesided_at_1hz,
                name=self.name,
            )
            return white.elementary()
        if self.asd_exp > 0:
            base = NoiseDefPowerLaw(
                f_sample=self.f_sample,
                asd_onesided_at_1hz=self.asd_onesided_at_1hz,
                f_min_hz=self.f_min_hz,
                asd_exp=self.asd_exp - 1,
                name="Power",
            )
            grad = NoiseDefGradient(base=base, name=self.name)
            return grad.elementary()

        msg = "NoiseDefPowerLaw: something went very wrong"
        raise RuntimeError(msg)

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"asd_exp = {self.asd_exp} \n"
        )


class NoiseDefViolet(NoiseDefBase):
    r"""Defines violet noise with ASD approximating :math:`\propto f`

    The amplitude is specified such that in the limit of infinite sample rate,
    the discrete ASD at a fiducial frequency of 1 Hz is the given value.
    Note that the actual discrete PSD deviates from the ideal (continous)
    model PSD. The exact PSD can be obtained using the discrete_psd_twosided()
    method.
    """

    def __init__(self, asd_onesided_at_1hz: float, f_sample: float, name: str):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: ASD amplitude coefficient [1/sqrt(Hz)]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefViolet got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises

        NoiseDefViolet is equivalent to NoiseDefGradient based on
        NoiseDefWhite.
        """

        base = NoiseDefWhite(
            asd_onesided_const=self.asd_onesided_at_1hz,
            f_sample=self.f_sample,
            name="White",
        )
        grad = NoiseDefGradient(base=base, name=self.name)
        return grad.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
        )


class NoiseDefInfraRed(NoiseDefBase):
    """Defines infrared noise with ASD approximating :math:`f^{-2}` falloff

    Below a cutoff frequency, the ASD falloff changes to a powerlaw :math:`f^{-1}`.
    NoiseDefInfraRed is equivalent to NoiseDefCumSum based on NoiseDefRed.
    The amplitude parameter asd_onesided_at_1hz and the frequency cutoff f_min_Hz
    are passed on to NoiseDefRed.
    """

    def __init__(
        self, asd_onesided_at_1hz: float, f_min_hz: float, f_sample: float, name: str
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: ASD amplitude coefficient [1/sqrt(Hz)]
            f_min_hz: The frequency where the PSD falloff changes [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._f_min_hz = float(f_min_hz)

        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefInfrared got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefInfrared got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        base = NoiseDefRed(
            asd_onesided_at_1hz=self.asd_onesided_at_1hz,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="Red",
        )
        cumsum = NoiseDefCumSum(base=base, name=self.name)
        return cumsum.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefFalloff6(NoiseDefBase):
    """Defines noise with PSD approximating :math:`f^{-6}` falloff

    Below a cutoff frequency, the PSD falloff changes to a powerlaw :math:`f^{-4}`.
    NoiseDefFalloff6 is equivalent to NoiseDefCumSum based on NoiseDefInfrared.
    The amplitude parameter asd_onesided_at_1hz and the frequency cutoff f_min_Hz
    are passed on to NoiseDefInfrared.


    Warning: it is currently unclear if NoiseDefInfrared is a valid base for
    NoiseDefCumSum. This definition might not result in stationary noise with
    well-defined PSD. In any case, the low-frequency divergence can lead to
    huge dynamic range even for finite length noise signals. Estimates of the
    PSD using Welch method might also become biased and won't converge with
    increasing signal length.
    """

    def __init__(
        self, asd_onesided_at_1hz: float, f_min_hz: float, f_sample: float, name: str
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: ASD amplitude coefficient [1/sqrt(Hz)]
            f_min_hz: The frequency where the PSD falloff changes [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._f_min_hz = float(f_min_hz)

        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefFalloff6 got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefFalloff6 got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        base = NoiseDefInfraRed(
            asd_onesided_at_1hz=self.asd_onesided_at_1hz,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="Infrared",
        )
        cumsum = NoiseDefCumSum(base=base, name=self.name)
        return cumsum.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefFalloff8(NoiseDefBase):
    """Defines noise with PSD approximating :math:`f^{-8}` falloff

    Below a cutoff frequency, the PSD falloff changes to a powerlaw :math:`f^{-6}`.
    NoiseDefFalloff8 is equivalent to NoiseDefCumSum based on NoiseDefFalloff6.
    The amplitude parameter asd_onesided_at_1hz and the frequency cutoff f_min_Hz
    are passed on to NoiseDefFalloff6.

    Warning: it is currently unclear if NoiseDefFalloff6 is a valid noise or at
    least a valid base for NoiseDefCumSum. This definition might not result in
    stationary noise with well-defined PSD. In any case, the low-frequency
    divergence can lead to huge dynamic range even for finite length noise signals.
    Estimates of the PSD using Welch method might also become biased and won't
    converge with increasing signal length.
    """

    def __init__(
        self, asd_onesided_at_1hz: float, f_min_hz: float, f_sample: float, name: str
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: ASD amplitude coefficient [1/sqrt(Hz)]
            f_min_hz: The frequency where the PSD falloff changes [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        super().__init__(f_sample, name)
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        self._f_min_hz = float(f_min_hz)

        if self._asd_onesided_at_1hz < 0:
            msg = f"NoiseDefFalloff8 got negative ASD parameter {asd_onesided_at_1hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefFalloff8 got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """Noise amplitude [1/sqrt(Hz)], see class documentation"""
        return self._asd_onesided_at_1hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        base = NoiseDefFalloff6(
            asd_onesided_at_1hz=self.asd_onesided_at_1hz,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="falloff6",
        )
        cumsum = NoiseDefCumSum(base=base, name=self.name)
        return cumsum.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefPink(NoiseDefAlpha):
    r"""Pink noise with PSD falloff :math:`1/f`

    This is just an alias for alpha noise with alpha=1 and f_max_hz = f_sample / 2
    see NoiseDefAlpha for details.
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
            f_min_hz: The frequency below which PSD approaches a constant [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """

        super().__init__(
            asd_onesided_at_1hz=asd_onesided_at_1hz,
            f_min_hz=f_min_hz,
            f_max_hz=f_sample / 2,
            alpha=1,
            f_sample=f_sample,
            name=name,
        )

    def __str__(self) -> str:
        return (
            f"{NoiseDefBase.__str__(self)}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
        )


class NoiseDefRedAndViolet(NoiseDefBase):
    r"""Defines a sum of red and violet noise components

    This is used as base for the definitions of several LISA instrument noises.


    This noise approximates a model PSD given by

    .. math::

        S^\text{ffd}_\mathrm{bl}(f) = A^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]
        = A^2 f^2 + \qty(A f_\mathrm{knee}^2)^2 f^{-2}.


    The :math:`f^2` component is implemented using NoiseDefViolet, and the
    :math:`f^{-2}` using NoiseDefRed. Note that the latter has a low frequency
    cutoff. The exact resulting discrete PSD can be obtained using the discrete_psd_twosided()
    method.
    """

    def __init__(
        self,
        asd_onesided_at_1hz: float,
        f_min_hz: float,
        f_knee_hz: float,
        f_sample: float,
        name: str,
    ):
        """Constructor

        Arguments:
            asd_onesided_at_1hz: ASD amplitude coefficient A [1/sqrt(Hz)]
            f_min_hz: frequency cutoff for red noise component [Hz]
            f_knee_hz: transition frequency between violet and red components [Hz]
            f_sample: Sample rate to generate noise with [Hz]
            name: Unique name used to generate seeds
        """
        self._asd_onesided_at_1hz = float(asd_onesided_at_1hz)
        super().__init__(f_sample, name)
        self._f_min_hz = float(f_min_hz)
        self._f_knee_hz = float(f_knee_hz)

        if self._asd_onesided_at_1hz < 0:
            msg = (
                f"NoiseDefRedAndViolet got negative ASD parameter {asd_onesided_at_1hz}"
            )
            raise RuntimeError(msg)

        if self._f_knee_hz < 0:
            msg = f"NoiseDefRedAndViolet got negative transition frequency {f_knee_hz=}"
            raise RuntimeError(msg)

        if self._f_min_hz < 0:
            msg = f"NoiseDefRedAndViolet got negative cutoff frequency {f_min_hz=}"
            raise RuntimeError(msg)

    @property
    def asd_onesided_at_1hz(self) -> float:
        """ASD amplitude coefficient :math:`A` [1/sqrt(Hz)]"""
        return self._asd_onesided_at_1hz

    @property
    def f_knee_hz(self) -> float:
        """Transition frequency to red part [Hz]"""
        return self._f_knee_hz

    @property
    def f_min_hz(self) -> float:
        """Low frequency cutoff [Hz]"""
        return self._f_min_hz

    def discrete_psd_twosided(self, f: np.ndarray) -> np.ndarray:
        """Compute twosided PSD of discrete sampled data"""
        return self.elementary().discrete_psd_twosided(f)

    def elementary(self) -> NoiseDefBase:
        """Return equivalent noise definition using elementary noises"""

        violet = NoiseDefViolet(
            asd_onesided_at_1hz=self.asd_onesided_at_1hz,
            f_sample=self.f_sample,
            name="violet",
        )
        asd_red = self.asd_onesided_at_1hz * self.f_knee_hz**2
        red = NoiseDefRed(
            asd_onesided_at_1hz=asd_red,
            f_min_hz=self.f_min_hz,
            f_sample=self.f_sample,
            name="red",
        )
        ndef = NoiseDefSum([violet, red], self.name)
        return ndef.elementary()

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"asd_onesided_at_1hz [1/sqrt(Hz)] = {self.asd_onesided_at_1hz} \n"
            f"f_min_hz [Hz] = {self.f_min_hz} \n"
            f"f_knee_hz [Hz] = {self.f_knee_hz} \n"
        )
