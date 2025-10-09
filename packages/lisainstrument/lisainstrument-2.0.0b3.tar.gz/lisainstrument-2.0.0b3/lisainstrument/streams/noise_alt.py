"""Module for creating noise streams

This is one of two alternative approaches to noise generation, the other module
is `noise`. Both provide the same function stream_noise, differing
only in the implementation of the returned stream. The version in this module
is the default when using from .streams import stream_noise.

Use stream_noise to create a stream for a given NoiseDefBase noise definition
and master seed value.

Internally, compound noises in this module are realized by combining streams,
e.g. applying a IIR filter to a white noise stream, or adding two noise streams.
Thus, the internals of the noise computation are visible to the scheduler, with
some potential for improving parallelism.
"""

from __future__ import annotations

import math
from copy import deepcopy
from functools import singledispatch
from typing import Any, Final

import numpy as np

from lisainstrument.noisy.noise_defs import (
    NoiseDefBase,
    NoiseDefCumSum,
    NoiseDefFiltered,
    NoiseDefGradient,
    NoiseDefScaled,
    NoiseDefSum,
    NoiseDefWhite,
    NoiseDefZero,
)
from lisainstrument.noisy.noise_gen_numpy import make_integer_seed
from lisainstrument.streams.derivative import stream_gradient
from lisainstrument.streams.expression import stream_expression
from lisainstrument.streams.iirfilter import IIRFilterIC, stream_filter_iir_chain
from lisainstrument.streams.integrate import stream_int_cumsum
from lisainstrument.streams.segments import Segment, SegmentArray, segment_empty
from lisainstrument.streams.streams import StreamBase, StreamConst


class StreamNoiseWhite(StreamBase):
    """Stream providing white noise samples"""

    def __init__(self, noisedef: NoiseDefWhite, seed: int):
        """Not part of API, use stream_noise instead

        Arguments:
            noisedef: White noise parameters
        """
        super().__init__([], True, float)
        self._rms: Final = noisedef.sample_rms
        self._seed: Final = seed

    def generate(
        self, state: Any, deps: list[Segment], istart: int, istop: int
    ) -> tuple[Segment, Any]:
        """Generate segment, see StreamBase documentation"""

        if istart == istop:
            return segment_empty(istart, self.dtype), state

        if state is None:
            state = np.random.default_rng(self._seed)
        else:
            state = deepcopy(state)
        noise = state.normal(loc=0.0, scale=self._rms, size=istop - istart)
        res = SegmentArray(noise, istart)

        return res, state


@singledispatch
def _noise_stream(noisedef: NoiseDefBase, _seed: int) -> StreamBase:
    """Helper function for creating a noise stream for the corresponding noise type"""
    msg = f"noise_generator: noise definition type {noisedef.__class__.__name__} not supported"
    raise RuntimeError(msg)


@_noise_stream.register
def _(_noisedef: NoiseDefZero, _seed: int) -> StreamBase:
    return StreamConst(0.0)


@_noise_stream.register
def _(noisedef: NoiseDefWhite, seed: int) -> StreamBase:
    return StreamNoiseWhite(noisedef, seed)


@_noise_stream.register
def _(noisedef: NoiseDefFiltered, seed: int) -> StreamBase:
    base = stream_noise(noisedef.base, seed)
    op = stream_filter_iir_chain(
        noisedef.iirfilters, IIRFilterIC.STEADY, noisedef.burn_in_size
    )
    return op(base)


@_noise_stream.register
def _(noisedef: NoiseDefCumSum, seed: int) -> StreamBase:
    base = stream_noise(noisedef.base, seed)
    dt_times_norm = 2 * math.pi / noisedef.f_sample
    op = stream_int_cumsum(dt_times_norm)
    return op(base)


@_noise_stream.register
def _(noisedef: NoiseDefGradient, seed: int) -> StreamBase:
    base = stream_noise(noisedef.base, seed)
    dt_times_norm = 2 * math.pi / noisedef.f_sample
    op = stream_gradient(dt_times_norm)
    return op(base)


@_noise_stream.register
def _(noisedef: NoiseDefScaled, seed: int) -> StreamBase:

    @stream_expression(dtype=float)
    def strans(y: np.ndarray) -> np.ndarray:
        return y * noisedef.factor

    base = stream_noise(noisedef.base, seed)
    return strans(base)


@_noise_stream.register
def _(noisedef: NoiseDefSum, seed: int) -> StreamBase:
    @stream_expression(dtype=float)
    def strans(first: np.ndarray, *args: np.ndarray) -> np.ndarray:
        res = np.copy(first)
        for s in args:
            np.add(res, s, out=res)
        return res

    comps = [stream_noise(c, seed) for c in noisedef.components]
    return strans(*comps)


def stream_noise(noisedef: NoiseDefBase, seed: int) -> StreamBase:
    """Create a stream for given noise definition and master seed


    If the noise generator would produce zeros only, a StreamConst(0) is
    returned, allowing to optimize the important case of zero noise amplitudes.

    See noisy.noise_gen_numpy.NoiseGen for details on seed handling.

    Arguments:
        noisedef: Noise definition
        seed: Master seed value
    """

    subseed = make_integer_seed(noisedef.name, seed)
    return _noise_stream(noisedef.elementary(), subseed)
