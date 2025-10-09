"""The lisainstrument.noisy.noise_gen_numpy module provides numpy-based noise generation

Given a noise definition of type NoiseDefBase, create a NoiseGen instance, which
provides a corresponding noise generation function. This noise generator has internal
state and can be called repeatedly to obtain chunks of noise samples.

Internally, the code is organized around stateless generators that require the state
as explicit parameters. This is suitable for use in the streams package. There is a class
for each elementary noise definition type, implementing the noise generation. Those classes
implement a protocol NoiseGenStateless. By elementary noises we refer to noises that can
be part of noise definitions returned by calls to the elementary() method of any noise.
 """

# pylint: disable = too-few-public-methods

import hashlib
import math
from copy import deepcopy
from functools import singledispatch
from typing import Any, Final, Protocol

import numpy as np

from lisainstrument.sigpro.iir_filters_numpy import IIRChainCoreOp, IIRFilterIC

from .noise_defs import (
    NoiseDefBase,
    NoiseDefCumSum,
    NoiseDefFiltered,
    NoiseDefGradient,
    NoiseDefScaled,
    NoiseDefSum,
    NoiseDefWhite,
    NoiseDefZero,
)


def make_integer_seed(*args) -> int:
    """Create an integer seed from an arbitrary number of arguments

    Anything that can be converted into string can be used, and both the
    string representation and the argument type enter the seed computation.
    """
    h = hashlib.sha256()
    for a in args:
        h.update(f"{type(a)}{a}".encode())
    return int(h.hexdigest(), base=16)


def make_random_seed() -> int:
    """Generate a random integer value from non-deterministic sources

    The sole purpose of this is to seed random number generators.
    """
    return np.random.randint(0, 2**32 - 1)


class NoiseGenStateless(Protocol):
    """Protocol for simple numpy-based noise generators without internal state

    To generate noise in chunks, some state information that changes from one
    chunk to the next must be kept. However, for using the noise generator in the
    framework of the streams package, pure functions are required and the state
    must be passed along externally. This is realized by an additional state
    parameter  to the generator and an additional return value with the new state.
    Finally, the first chunk is marked by passing None as state.
    """

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """Generate an array with noise samples

        Concatenating result of repeated calls should yield identical result to
        a single call with the combined size. For this to work, the state returned
        by one call must be passed on the the next call.

        Arguments:
            size: number of elements to generate
            state: internal state to be passed to next call
        Returns:
            Tuple with noise samples and internal state
        """


@singledispatch
def _noise_generator(noisedef: NoiseDefBase, _seed: int) -> NoiseGenStateless:
    """Helper function for creating a noise generator for the corresponding noise type"""
    msg = f"noise_generator: noise definition type {noisedef.__class__.__name__} not supported"
    raise RuntimeError(msg)


def noise_generator_stateless(
    noisedef: NoiseDefBase, seed: int | str
) -> NoiseGenStateless:
    """Create a NoiseGenStateless noise generator for a given NoiseDefBase noise definition

    See also NoiseGen for usage.

    Arguments:
        noisedef: The noise definition
        seed: master seed value

    Returns:
        A noise generation function adhering to the NoiseGen protocol
    """
    subseed = make_integer_seed(noisedef.name, seed)
    return _noise_generator(noisedef.elementary(), subseed)


class NoiseGenWhite(NoiseGenStateless):
    """NoiseGenStateless implementation for NoiseDefWhite"""

    def __init__(self, noisedef: NoiseDefWhite, seed: int) -> None:
        self._rms: Final = noisedef.sample_rms
        self._seed: Final = seed

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""
        if state is None:
            state = np.random.default_rng(self._seed)
        else:
            state = deepcopy(state)
        noise = state.normal(loc=0.0, scale=self._rms, size=size)
        return noise, state


@_noise_generator.register
def _(noisedef: NoiseDefWhite, seed: int) -> NoiseGenStateless:
    return NoiseGenWhite(noisedef, seed)


class NoiseGenZero(NoiseGenStateless):
    """NoiseGenStateless implementation for NoiseDefZero"""

    def generate(self, size: int, _state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""
        return np.zeros(size), True


@_noise_generator.register
def _(_noisedef: NoiseDefZero, _seed: int) -> NoiseGenStateless:
    return NoiseGenZero()


def is_zero_noise_gen(gen) -> bool:
    """If True, the noise generator would only produce zeros"""
    return isinstance(gen, NoiseGenZero)


class NoiseGenFiltered(NoiseGenStateless):
    """NoiseGen implementation for NoiseDefFiltered"""

    def __init__(self, noisedef: NoiseDefFiltered, seed: int) -> None:
        self._base: Final = noise_generator_stateless(noisedef.base, seed)
        self._filt: Final = IIRChainCoreOp(noisedef.iirfilters, IIRFilterIC.STEADY)
        self._burn_in_size: Final = noisedef.burn_in_size

    def _initial_state(
        self, nstart: int = 5, max_burn_at_once: int = 50000
    ) -> tuple[Any, Any]:
        """Initialize state and perform filter burn-in"""
        start, basestate = self._base.generate(nstart, None)
        locstate = self._filt.initial_state(start[0])
        _, locstate = self._filt.apply(start, locstate)
        state = locstate, basestate

        nburn = self._burn_in_size - nstart
        while nburn > 0:
            bsz = min(nburn, max_burn_at_once)
            _, state = self.generate(bsz, state)
            nburn -= bsz

        return state

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""

        if state is None:
            state = self._initial_state()
        locstate, basestate = state

        noise0, basestate = self._base.generate(size, basestate)
        noise, locstate = self._filt.apply(noise0, locstate)
        newstate = locstate, basestate
        return noise, newstate


@_noise_generator.register
def _(noisedef: NoiseDefFiltered, seed: int) -> NoiseGenStateless:
    return NoiseGenFiltered(noisedef, seed)


class NoiseGenCumSum(NoiseGenStateless):
    """NoiseGen implementation for NoiseDefCumSum"""

    def __init__(self, noisedef: NoiseDefCumSum, seed: int) -> None:
        self._base: Final = noise_generator_stateless(noisedef.base, seed)
        self._normfac: Final = 2 * math.pi / noisedef.f_sample

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""

        if state is None:
            state = 0.0, None
        locstate, basestate = state

        noise0, basestate = self._base.generate(size, basestate)
        noise = locstate + np.cumsum(noise0)
        locstate = float(noise[-1])
        np.multiply(noise, self._normfac, out=noise)

        newstate = locstate, basestate
        return noise, newstate


@_noise_generator.register
def _(noisedef: NoiseDefCumSum, seed: int) -> NoiseGenStateless:
    return NoiseGenCumSum(noisedef, seed)


class NoiseGenGradient(NoiseGenStateless):
    """NoiseGen implementation for NoiseDefGradient"""

    def __init__(self, noisedef: NoiseDefGradient, seed: int) -> None:
        self._base: Final = noise_generator_stateless(noisedef.base, seed)
        self._sample_dt: Final = 1.0 / noisedef.f_sample

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""

        if state is None:
            state = self._base.generate(2, None)

        locstate, basestate = state

        noise0 = np.empty(size + 2, dtype=float)
        noise0[:2] = locstate
        noise0[2:], newbasestate = self._base.generate(size, basestate)
        newlocstate = noise0[-2:]
        newstate = newlocstate, newbasestate
        noise = np.gradient(noise0, self._sample_dt, axis=0)[1:-1] / (2 * math.pi)
        return noise, newstate


@_noise_generator.register
def _(noisedef: NoiseDefGradient, seed: int) -> NoiseGenStateless:
    return NoiseGenGradient(noisedef, seed)


class NoiseGenScaled(NoiseGenStateless):
    """NoiseGen implementation for NoiseDefScaled"""

    def __init__(self, noisedef: NoiseDefScaled, seed: int) -> None:
        self._base: Final = noise_generator_stateless(noisedef.base, seed)
        self._factor: Final = noisedef.factor

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""
        noise, newstate = self._base.generate(size, state)
        np.multiply(noise, self._factor, out=noise)
        return noise, newstate


@_noise_generator.register
def _(noisedef: NoiseDefScaled, seed: int) -> NoiseGenStateless:
    return NoiseGenScaled(noisedef, seed)


class NoiseGenSum(NoiseGenStateless):
    """NoiseGen implementation for NoiseDefSum"""

    def __init__(self, noisedef: NoiseDefSum, seed: int) -> None:
        self._comps = [noise_generator_stateless(c, seed) for c in noisedef.components]

    def generate(self, size: int, state: Any) -> tuple[np.ndarray, Any]:
        """See NoiseGenStateless.generate"""
        if state is None:
            state = [None for c in self._comps]

        noise, cnewstate = self._comps[0].generate(size, state[0])
        newstate = [cnewstate]
        for c, cstate in zip(self._comps[1:], state[1:]):
            cnoise, cnewstate = c.generate(size, cstate)
            newstate.append(cnewstate)
            np.add(noise, cnoise, out=noise)

        return noise, newstate


@_noise_generator.register
def _(noisedef: NoiseDefSum, seed: int) -> NoiseGenStateless:
    return NoiseGenSum(noisedef, seed)


class NoiseGen:
    """Noise generator with internal state for repeated calls

    This is the user-friendly wrapper of the stateless NoiseGenStateless
    noise generator.

    The sequence produced by the generator is fully determined by the combination of the seed
    value, the name of the noise, the type of the noise, and to some extend on the noise parameters.
    The intended use case is for generating uncorrelated noises, providing a master seed to
    all generated noises, each of which has a definition with a unique name. When generating
    two or more realizations of the same noise, create a new noise definition with a unique
    name for each.

    We stress that different parameters alone, with everything else fixed, do not necessarily
    lead to uncorrelated noises. This only happens when the amplitude of a noise or a internally
    generated noise component becomes zero, triggering some optimizations.
    """

    def __init__(self, noisedef: NoiseDefBase, seed: int | str):
        """Constructor

        Arguments:
            noisedef: The noise definition
            seed: master seed value
        """
        self._gen = noise_generator_stateless(noisedef, seed)
        self._state = None

    def generate(self, size: int) -> np.ndarray:
        """Generate an array with noise samples.

        Concatenating the results of repeated calls is guaranteed to be the same
        as the result of a single call with the combined size.

        Arguments:
            size: number of noise samples to generate

        Returns:
            Numpy 1D array with nosie samples
        """
        noise, self._state = self._gen.generate(size, self._state)
        return noise
