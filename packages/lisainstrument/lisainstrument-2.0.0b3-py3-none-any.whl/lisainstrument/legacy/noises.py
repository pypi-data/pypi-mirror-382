#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Noises
======

Implements basic random noise generators and instrumental noise models for the
LISA mission.

LISA noise models
-----------------

.. autofunction:: laser

.. autofunction:: clock

.. autofunction:: modulation

.. autofunction:: backlink

.. autofunction:: ranging

.. autofunction:: testmass

.. autofunction:: oms

.. autofunction:: longitudinal_jitter

.. autofunction:: angular_jitter

.. autofunction:: dws

.. autofunction:: moc_time_correlation

Basic noise generators
----------------------

.. autofunction:: white

.. autofunction:: powerlaw

.. autofunction:: violet

.. autofunction:: pink

.. autofunction:: red

.. autofunction:: infrared

Random noise generators
-----------------------

.. autofunction:: generate_random_seed

.. autofunction:: generate_subseed

"""

import hashlib
import logging

import numpy as np
from lisaconstants import c
from numpy import pi, sqrt

from lisainstrument.legacy.pyplnoise import pyplnoise

logger = logging.getLogger(__name__)


def generate_random_seed() -> int:
    """Generate a random seed for the noise generation.

    Returns:
        A 32-bit unsigned integer seed.
    """
    return np.random.randint(0, 2**32 - 1)


def generate_subseed(seed: int, name: str = "") -> int:
    """Generate a random subseed based on a primary seed and a name.

    Args:
        seed: primary seed
        name: name to identify the subseed

    Returns:
        A random subseed based on the input seed and the name.
    """
    combined_string = f"{seed}_{name}"
    hash_object = hashlib.sha256(combined_string.encode())
    subseed = int(hash_object.hexdigest(), 16) % (2**32)
    return subseed


def white(fs, size, asd, seed: int):
    """Generate a white noise.

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating white noise (fs=%s Hz, size=%s, asd=%s, seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0
    generator = pyplnoise.WhiteNoise(fs, asd**2 / 2, seed=seed)
    return generator.get_series(size)


def powerlaw(fs, size, asd, alpha, seed: int):
    r"""Generate :math:`f^\alpha` noise in amplitude, with :math:`\alpha > -1`.

    Pyplnoise natively accepts alpha values between -1 and 0 (in amplitude).

    We extend the domain of validity to positive :math:`\alpha` values by
    generating noise time series corresponding to the nth-order antiderivative
    of the desired noise (with exponent :math:`\alpha + n` valid for direct
    generation with pyplnoise), and then taking its nth-order numerical
    derivative.

    When :math:`\alpha = -1` (resp. 0), we use internally call the optimized
    :func:`red` function (resp. the :func:`white` function).

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        alpha: frequency exponent in amplitude [`alpha` > -1 and `alpha` != 0]
    """
    logger.debug(
        "Generating power-law noise (fs=%s Hz, size=%s, asd=%s, alpha=%s, seed=%s)",
        fs,
        size,
        asd,
        alpha,
        seed,
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0

    if alpha < -1:
        raise ValueError(f"invalid value for alpha '{alpha}', must be > -1.")
    if alpha == -1:
        return red(fs, size, asd, seed=seed)
    if -1 < alpha < 0:
        generator = pyplnoise.AlphaNoise(fs, fs / size, fs / 2, -2 * alpha, seed=seed)
        return asd / sqrt(2) * generator.get_series(size)
    if alpha == 0:
        return white(fs, size, asd, seed=seed)

    # Else, generate antiderivative and take numerical derivative
    antiderivative = powerlaw(fs, size, asd / (2 * pi), alpha - 1, seed=seed)
    return np.gradient(antiderivative, 1 / fs)


def violet(fs, size, asd, seed: int):
    """Generate a violet noise in :math:`f` in amplitude.

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating violet noise (fs=%s Hz, size=%s, asd=%s, seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0
    white_noise = white(fs, size, asd, seed=seed)
    return np.gradient(white_noise, 1 / fs) / (2 * pi)


def pink(fs, size, asd, seed: int, fmin=None):
    """Generate a pink noise in :math:`f^{-1/2}` in amplitude.

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
        fmin: saturation frequency (default to `fs / size`) [Hz]
    """
    logger.debug(
        "Generating pink noise (fs=%s Hz, size=%s, asd=%s, seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0
    generator = pyplnoise.PinkNoise(fs, fmin or fs / size, fs / 2, seed=seed)
    return asd / sqrt(2) * generator.get_series(size)


def red(fs, size, asd, seed: int):
    """Generate a red (aka Brownian) noise in :math:`f^{-1}` in amplitude.

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating red noise (fs=%s Hz, size=%s, asd=%s, seed=%s)", fs, size, asd, seed
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0
    generator = pyplnoise.RedNoise(fs, fs / size, seed=seed)
    return asd / sqrt(2) * generator.get_series(size)


def infrared(fs, size, asd, seed: int):
    """Generate an infrared noise in :math:`f^{-2}` in amplitude.

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating infrared noise (fs=%s Hz, size=%s, asd=%s, seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    if not asd:
        logger.debug("Vanishing power spectral density, bypassing noise generation")
        return 0
    red_noise = red(fs, size, asd, seed=seed)
    return np.cumsum(red_noise) * (2 * pi / fs)


def laser(fs, size, asd, shape, seed: int):
    r"""Generate laser noise [Hz].

    This is a white noise with an infrared relaxation towards low frequencies,
    following the usual noise shape function,

    .. math::

        S^\text{Hz}_p(f) = A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ]
        = A^2 + A^2 \frac{f_\mathrm{knee}^4}{f^4}.

    The low-frequency part (infrared relaxation) can be disabled, in which
    case the noise shape becomes

    .. math::

        S_p(f) = A^2.

    Args:
        asd: amplitude spectral density [Hz/sqrt(Hz)]
        fknee: cutoff frequency [Hz]
        shape: spectral shape, either ``"white"`` or ``"white+infrared"``
        seed: random seed
    """
    fknee = 2e-3
    logger.debug(
        "Generating laser noise (fs=%s Hz, size=%s, asd=%s "
        "Hz/sqrt(Hz), fknee=%s Hz, shape=%s, seed=%s)",
        fs,
        size,
        asd,
        fknee,
        shape,
        seed,
    )

    if shape == "white":
        return white(fs, size, asd, seed=seed)
    if shape == "white+infrared":
        white_seed = generate_subseed(seed, "white")
        infrared_seed = generate_subseed(seed, "infrared")
        return white(fs, size, asd, seed=white_seed) + infrared(
            fs, size, asd * fknee**2, seed=infrared_seed
        )
    raise ValueError(f"invalid laser noise spectral shape '{shape}'")


def clock(fs, size, asd, seed: int):
    r"""Generate clock noise fluctuations [ffd].

    The power spectral density in fractional frequency deviations is a pink
    noise,

    .. math::

        S^\text{ffd}_q(f) = A^2 f^{-1}.

    Clock noise saturates below 1E-5 Hz, as the low-frequency part is modeled by
    deterministing clock drifts.

    Args:
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating clock noise fluctuations (fs=%s Hz, size=%s, asd=%s /sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return pink(fs, size, asd, fmin=1e-5, seed=seed)


def modulation(fs, size, asd, seed: int):
    r"""Generate modulation noise [ffd].

    The power spectral density as fractional frequency deviations reads

    .. math::

        S^\text{ffd}_M(f) = A^2 f^{2/3}.

    Note that these are fractional frequency deviations wrt. the GHz modulation frequencies.

    Args:
        asd: amplitude spectral density [/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating modulation noise (fs=%s Hz, size=%s, asd=%s /sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return powerlaw(fs, size, asd, 1 / 3, seed=seed)


def backlink(fs, size, asd, fknee, seed: int):
    r"""Generate backlink noise as fractional frequency deviation [ffd].

    The power spectral density in displacement is given by

    .. math::

        S^\text{m}_\mathrm{bl}(f) = A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ].

    Multiplying by :math:`(2 \pi f / c)^2` to express it as fractional frequency
    deviations,

    .. math::

        S^\text{ffd}_\mathrm{bl}(f) = \qty(\frac{2 \pi A}{c})^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]
        = \qty(\frac{2 \pi A}{c})^2 f^2 + \qty(\frac{2 \pi A f_\mathrm{knee}^2}{c})^2 f^{-2}.

    Because this is a optical pathlength noise expressed as fractional frequency deviation, it should
    be multiplied by the beam frequency to obtain the beam frequency fluctuations.

    Args:
        asd: amplitude spectral density [m/sqrt(Hz)]
        fknee: cutoff frequency [Hz]
        seed: random seed
    """
    logger.debug(
        "Generating modulation noise (fs=%s Hz, size=%s, asd=%s m/sqrt(Hz), fknee=%s Hz, seed=%s)",
        fs,
        size,
        asd,
        fknee,
        seed,
    )
    violet_seed = generate_subseed(seed, "violet")
    red_seed = generate_subseed(seed, "red")
    return violet(fs, size, 2 * pi * asd / c, seed=violet_seed) + red(
        fs, size, 2 * pi * asd * fknee**2 / c, seed=red_seed
    )


def ranging(fs, size, asd, seed: int):
    r"""Generate stochastic ranging noise [s].

    This is a white noise as a timing jitter,

    .. math::

        S^\text{s}_R(f) = A^2.

    Args:
        asd: amplitude spectral density [s/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating ranging noise (fs=%s Hz, size=%s, asd=%s s/sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return white(fs, size, asd, seed=seed)


def testmass(fs, size, asd, fknee, fbreak, frelax, shape, seed: int):
    r"""Generate test-mass acceleration noise [m/s].

    Expressed in acceleration, the noise power spectrum reads

    .. math::

        S^\text{acc}_\delta(f) = A^2
        \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^2]
        \qty[ 1 + \qty(\frac{f}{f_\mathrm{break}})^4].

    Multiplying by :math:`1 / (2 \pi f)^2` yields the noise as a velocity,

    .. math::

        S^\text{vel}_\delta(f) &= \qty(\frac{A}{2 \pi})^2
        \qty[ f^{-2} + \frac{f_\mathrm{knee}^2}{f^4}
        + \frac{f^2}{f_\mathrm{break}^4}
        + \frac{f_\mathrm{knee}^2}{f_\mathrm{break}^4} ]

        &= \qty(\frac{A f_\mathrm{knee}}{2 \pi})^2 f^{-4}
        + \qty(\frac{A}{2 \pi})^2 f^{-2}
        + \qty(\frac{A f_\mathrm{knee}}{2 \pi f_\mathrm{break}^2})^2
        + \qty(\frac{A}{2 \pi f_\mathrm{break}^2})^2 f^2,

    which corresponds to the incoherent sum of an infrared, a red, a white,
    and a violet noise.

    A relaxation for more pessimistic models extending below the official LISA
    band of :math`10^{-4}` Hz can be added using the ``"lowfreq-relax"`` shape,
    in which case the noise in acceleration picks up an additional
    :math:`f^{-4}` term,

    .. math::

        S^\text{acc}_\delta(f) = \ldots \times
        \qty[ 1 + \qty(\frac{f_\mathrm{relax}}{f})^4 ].

    In velocity, this corresponds to additional terms,

    .. math::

        S\text{vel}_\delta(f) &= \ldots \times
        \qty[ 1 + \qty(\frac{f_\mathrm{relax}}{f})^4 ]

        &= \ldots + \qty(\frac{A f_\mathrm{knee} f_\mathrm{relax}^2}{2 \pi})^2 f^{-8}
        + \qty(\frac{A f_\mathrm{relax}^2}{2 \pi})^2 f^{-6}

        &\qquad + \qty(\frac{A f_\mathrm{knee} f_\mathrm{relax}^2}{2 \pi f_\mathrm{break}^2})^2 f^{-4}
        + \qty(\frac{A f_\mathrm{relax}^2}{2 \pi f_\mathrm{break}^2})^2 f^{-2}.

    Args:
        asd: amplitude spectral density [ms^(-2)/sqrt(Hz)]
        fknee: low-frequency cutoff frequency [Hz]
        fbreak: high-frequency break frequency [Hz]
        frelax: low-frequency relaxation frequency [Hz]
        shape: spectral shape, either ``"original"`` or ``"lowfreq-relax"``
        seed: random seed
    """
    logger.debug(
        "Generating test-mass noise (fs=%s Hz, size=%s, "
        "asd=%s ms^(-2)/sqrt(Hz), fknee=%s Hz, fbreak=%s Hz, "
        "frelax=%s Hz, shape=%s, seed=%s)",
        fs,
        size,
        asd,
        fknee,
        fbreak,
        frelax,
        shape,
        seed,
    )

    if shape == "original":
        infrared_seed = generate_subseed(seed, "infrared")
        red_seed = generate_subseed(seed, "red")
        white_seed = generate_subseed(seed, "white")
        violet_seed = generate_subseed(seed, "violet")
        return (
            infrared(fs, size, asd * fknee / (2 * pi), seed=infrared_seed)
            + red(fs, size, asd / (2 * pi), seed=red_seed)
            + white(fs, size, asd * fknee / (2 * pi * fbreak**2), seed=white_seed)
            + violet(fs, size, asd / (2 * pi * fbreak**2), seed=violet_seed)
        )
    if shape == "lowfreq-relax":
        # We need to integrate infrared noises to get f^(-6) and f^(-8) noises
        # Start with f^(-4) noises
        relaxation1_seed = generate_subseed(seed, "relaxation1")
        relaxation2_seed = generate_subseed(seed, "relaxation2")
        relaxation1 = infrared(
            fs, size, asd * frelax**2 / (2 * pi), seed=relaxation1_seed
        )
        relaxation2 = infrared(
            fs, size, asd * fknee * frelax**2 / (2 * pi), seed=relaxation2_seed
        )
        # Integrate once for f^(-6)
        relaxation1 = np.cumsum(relaxation1) * (2 * pi / fs)
        relaxation2 = np.cumsum(relaxation2) * (2 * pi / fs)
        # Integrate twice for f^(-8)
        relaxation2 = np.cumsum(relaxation2) * (2 * pi / fs)
        # Add the other components to the original noise
        infrared_asd = asd * fknee * np.sqrt(1 + (frelax / fbreak) ** 4) / (2 * pi)
        red_asd = asd * np.sqrt(1 + (frelax / fbreak) ** 4) / (2 * pi)
        # Generate seeds
        infrared_seed = generate_subseed(seed, "infrared")
        red_seed = generate_subseed(seed, "red")
        white_seed = generate_subseed(seed, "white")
        violet_seed = generate_subseed(seed, "violet")
        return (
            relaxation2  # f^(-8)
            + relaxation1  # f^(-6)
            + infrared(fs, size, infrared_asd, seed=infrared_seed)
            + red(fs, size, red_asd, seed=red_seed)
            + white(fs, size, asd * fknee / (2 * pi * fbreak**2), seed=white_seed)
            + violet(fs, size, asd / (2 * pi * fbreak**2), seed=violet_seed)
        )
    raise ValueError(f"invalid test-mass noise spectral shape '{shape}'")


def oms(fs, size, asd, fknee, seed: int):
    r"""Generate optical metrology system (OMS) noise allocation [ffd].

    The power spectral density in displacement is given by

    .. math::

        S^\text{disp}_\mathrm{oms}(f) = A^2
        \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ].

    Multiplying by :math:`(2 \pi f / c)^2` to express it as fractional frequency
    deviations,

    .. math::

        S^\text{ffd}_\mathrm{oms}(f) &=
        \qty(\frac{2 \pi A}{c})^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]

        &= \qty(\frac{2 \pi A}{c})^2 f^2
        + \qty(\frac{2 \pi A f_\mathrm{knee}^2}{c})^2 f^{-2}.

    Note that the level of this noise depends on the interferometer and the type of beatnote.

    Warning: this corresponds to the overall allocation for the OMS noise from the Performance
    Model. It is a collection of different noises, some of which are duplicates of standalone
    noises we already implement in the simulation (e.g., backlink noise).

    Args:
        asd: amplitude spectral density [m/sqrt(Hz)]
        fknee: cutoff frequency [Hz]
        seed: random seed
    """
    logger.debug(
        "Generating OMS noise (fs=%s Hz, size=%s, asd=%s m/sqrt(Hz), fknee=%s Hz, seed=%s)",
        fs,
        size,
        asd,
        fknee,
        seed,
    )
    violet_seed = generate_subseed(seed, "violet")
    red_seed = generate_subseed(seed, "red")
    return violet(fs, size, 2 * pi * asd / c, seed=violet_seed) + red(
        fs, size, 2 * pi * asd * fknee**2 / c, seed=red_seed
    )


def longitudinal_jitter(fs, size, asd, seed: int):
    r"""Generate MOSA longitudinal jitter noise along sensitive axis [m/s].

    The power spectral density in displacement is given by

    .. math::

        S^\text{disp}_\mathrm{jitter}(f) = A^2,

    which is converted to velocities by multiplying by :math:`(2 \pi f)^2`,

    .. math::

        S^\text{vel}_\mathrm{jitter}(f) = (2 \pi A)^2 f^2.

    Note that this is a ad-hoc model, as no official noise allocation is given
    in the LISA Performance Model (LISA-LCST-INST-TN-003).

    Args:
        fs: sampling frequency [Hz]
        size: number of samples [samples]
        asd: amplitude spectral density [m/sqrt(Hz)]
    """
    logger.debug(
        "Generating longitudinal jitter noise (fs=%s Hz, size=%s, "
        "asd=%s m/sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return violet(fs, size, 2 * pi * asd, seed=seed)


def angular_jitter(fs, size, asd, fknee, seed: int):
    r"""Generate jitter for one angular degree of freedom.

    The power spectral density in angle is given by

    .. math::

        S^\text{rad}_\mathrm{jitter}(f) =
        A^2 \qty[ 1 + \qty(\frac{f_\mathrm{knee}}{f})^4 ],

    which is converted to angular velocity by mutliplying by :math:`(2 \pi f)^2`,

    .. math::

        S^\text{rad/s}_\mathrm{jitter}(f) &=
        (2 \pi A)^2 \qty[ f^2 + \frac{f_\mathrm{knee}^4}{f^2} ]

        &= (2 \pi A)^2 f^2 + (2 \pi A f_\mathrm{knee}^2)^2 f^{-2}.

    Args:
        asd: amplitude spectral density [rad/sqrt(Hz)]
        fknee: cutoff frequency [Hz]
        seed: random seed
    """
    logger.debug(
        "Generating angular jitter (fs=%s Hz, size=%s, asd=%s "
        "rad/sqrt(Hz), fknee=%s Hz, seed=%s)",
        fs,
        size,
        asd,
        fknee,
        seed,
    )
    violet_seed = generate_subseed(seed, "violet")
    red_seed = generate_subseed(seed, "red")
    return violet(fs, size, 2 * pi * asd, seed=violet_seed) + red(
        fs, size, 2 * pi * asd * fknee**2, seed=red_seed
    )


def dws(fs, size, asd, seed: int):
    r"""Generate DWS measurement noise.

    The power spectral density in angle is given by

    .. math::

        S^\text{rad}_\mathrm{dws}(f) = A^2,

    which is converted to angular velocity by mutliplying by :math:`(2 \pi f)^2`,

    .. math::

        S^\text{rad/s}_\mathrm{dws}(f) = (2 \pi A)^2 f^2.

    Args:
        asd: amplitude spectral density [rad/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating DWS measurement (fs=%s Hz, size=%s, asd=%s rad/sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return violet(fs, size, 2 * pi * asd, seed=seed)


def moc_time_correlation(fs, size, asd, seed: int):
    r"""MOC time correlation noise.

    High-level noise model for the uncertainty we have in computing the MOC
    time correlation (or time couples), i.e., the equivalent TCB times for the
    equally-sampled TPS timestamps.

    Assumed to be a white noise in timing,

    .. math::

        S^\text{s}_\mathrm{moc}(f) = A^2.

    Args:
        asd: amplitude spectral density [s/sqrt(Hz)]
        seed: random seed
    """
    logger.debug(
        "Generating MOC time correlation noise (fs=%s Hz, size=%s, "
        "asd=%s s/sqrt(Hz), seed=%s)",
        fs,
        size,
        asd,
        seed,
    )
    return white(fs, size, asd, seed=seed)
