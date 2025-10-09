"""This module provides PSD estimation and comparison to support unit testing


For testing and debugging, this module provides a function
estimate_psd_twosided() that estimates the PSD for generated noise
samples and computes confidence bounds for the estimate. The results
are bundled in a data class PSDEstimate.
"""

from dataclasses import dataclass

import numpy as np
from scipy import signal, stats


@dataclass
class PSDEstimate:
    """Dataclass collecting PSD estimate results

    Attributes:
        freq: The frequency bins
        psd_twosided: Estimated PSD for each bin
        conf_lower: Confidence interval lower bound for given bin
        conf_upper: Confidence interval upper bound for given bin
        conf_prob: Probability confidence interval refers to
    """

    freq: np.ndarray
    psd_twosided: np.ndarray
    conf_lower: float
    conf_upper: float
    conf_prob: float

    def is_compatible(self, psd_expected: np.ndarray, false_pos_prob: float) -> bool:
        """Test if PSD estimate is compatible with expected PSD.

        Compares the number of bins where the PSD estimate is outside the
        confidence interval around the expected PSD to an admissable number.
        The latter is chosen such that the probabilty to find more than this
        number of outliers is the user-provided false positive probability.

        Arguments:
            psd_expected: The expected PSD evaluated for the same frequencies as the estimate
            false_pos_prob: False positive probability

        Returns:
            Whether the PSD estimate is compatible with the expected one

        Note: we make the simplifying (read: incorrect) assumption
        that the estimated PSD values for different frequency bins are
        completely independent. For this case, the number of outliers is
        described by the binomial distribution. Lower values of false_pos_prob
        result in fewer false incompatible outcomes, but increase the number
        of false compatible outcomes.
        """

        if false_pos_prob <= 0:
            msg = f"false_pos_prob must be > 0, got {false_pos_prob}"
            raise ValueError(msg)

        num_allow = stats.binom.isf(
            false_pos_prob, len(psd_expected), 1 - self.conf_prob
        )

        outliers = np.logical_or(
            self.psd_twosided > psd_expected * self.conf_upper,
            self.psd_twosided < psd_expected * self.conf_lower,
        )

        return np.count_nonzero(outliers) < num_allow


def estimate_psd_twosided(
    noise: np.ndarray,
    fsamp: float,
    nseg: int = 5000,
    conf_prob: float = 0.95,
    detrend="constant",
) -> PSDEstimate:
    """Computes an estimate of the PSD from noise samples using Welch method

    Only frequencies large enough for a meaningful estimate are returned,
    based on the sample rate, the number of samples per segment.

    Beside the PSD estimate, this also computes a confidence band such that
    the frequency bins are withing the band with a given probability.

    Note this only accepts numpy arrays since it is intended mainly for testing
    and debugging.

    Arguments:
        noise: 1D array with the noise samples
        fsamp: Sample rate of the noise [Hz]
        nseg: Number of segments to use in Welch's method
        conf_prob: Probability for which to compute the confidence intervals
        detrend: Prescription for detrending, 'constant' or 'linear'

    Returns:
        PSD and confidence bound as PSDEstimate data class
    """

    if conf_prob <= 0:
        msg = f"conf_prob must be > 0, got {conf_prob}"
        raise ValueError(msg)

    size = len(noise)
    nmin = size // nseg
    fmin = fsamp / nmin

    f, psd_s1 = signal.welch(
        noise, fs=fsamp, nperseg=nmin, return_onesided=True, detrend=detrend
    )
    psd_s2 = psd_s1 / 2
    valid = np.logical_and(f > fmin, f < fsamp / 2)

    alfa = 1 - conf_prob
    v = 2 * nseg
    c0 = float(v / stats.chi2.ppf(1 - alfa / 2, v))
    c1 = float(v / stats.chi2.ppf(alfa / 2, v))

    return PSDEstimate(
        freq=f[valid],
        psd_twosided=psd_s2[valid],
        conf_lower=c0,
        conf_upper=c1,
        conf_prob=conf_prob,
    )
