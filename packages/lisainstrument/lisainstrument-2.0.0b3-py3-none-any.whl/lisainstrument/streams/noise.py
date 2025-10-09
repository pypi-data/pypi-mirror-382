"""Module for creating noise streams

This is one of two alternative approaches to noise generation, the other module
is noise_alt. Both provide the same function stream_noise, differing
only in the implementation of the returned stream. The version in the other module
is the default when using from .streams import stream_noise. Use
`from streams.noise import stream_noise` to get this one.

Use stream_noise to create a stream for a given NoiseDefBase noise definition
and master seed value. See noisy.noise_gen_numpy.NoiseGen for details.

Internally, the StreamNoise stream just wraps a stateless numpy-based noise
generator of type NoiseGenStateless from noisy.noise_gen_numpy. Since all computations
happens inside a single stream, even for compund noises, the gneration of a single
noise stream has no potential for parallelism inside the scheduler.
"""

from __future__ import annotations

from typing import Any, Final

from lisainstrument.noisy.noise_defs import NoiseDefBase
from lisainstrument.noisy.noise_gen_numpy import (
    NoiseGenStateless,
    is_zero_noise_gen,
    noise_generator_stateless,
)
from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst


class StreamNoise(StreamBase):
    """Stream generating noise samples using a provided stateless noise generator

    Note that the noise is not just determined by the noise definition and seed.
    When selecting different output variables or ranges while storing a StreamBundle,
    the starting index of the noise stream can shift, and thus the whole noise sequence.
    The statistical properties should not be affected for well-defined noises, e.g.
    the expectation values.

    It is up to the user to ensure that the sample rate specified in the noise model
    agrees with the sample rate attributed to the stream. Otherwise, the resulting PSD
    as function of log-freq would be shifted.
    """

    def __init__(self, noisegen: NoiseGenStateless):
        """Not part of API, use stream_noise instead

        Arguments:
            noisegen: Stateless noise generator
        """
        super().__init__([], True, float)
        self._gen: Final = noisegen

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        noise, state = self._gen.generate(istop - istart, state)

        res = SegmentArray(noise, istart)
        return res, state


def stream_noise(noisedef: NoiseDefBase, seed: int) -> StreamBase:
    """Create a stream for given noise definition and master seed


    If the noise generator would produce zeros only, a StreamConst(0) is
    returned, allowing to optimize the important case of zero noise amplitudes.

    See noisy.noise_gen_numpy.NoiseGen for details on seed handling. The most
    impoertant thing to know is that streams for noise definitions with different
    names are uncorrelated.

    Arguments:
        noisedef: Noise definition
        seed: Master seed value
    """
    gen = noise_generator_stateless(noisedef, seed)
    if is_zero_noise_gen(gen):
        return StreamConst(0.0)
    return StreamNoise(gen)
