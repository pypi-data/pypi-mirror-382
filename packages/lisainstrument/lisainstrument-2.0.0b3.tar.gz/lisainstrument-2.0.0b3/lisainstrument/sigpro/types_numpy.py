"""Assorted type definitions related to functions of numpy arrays"""

from dataclasses import dataclass
from typing import Callable, TypeAlias

import numpy as np

NumpyArray1D: TypeAlias = np.ndarray[  # pylint: disable=invalid-name
    tuple[int], np.dtype[np.number]
]


def make_numpy_array_1d(x: np.ndarray) -> NumpyArray1D:
    """Check that numpy array is 1D or raise exception

    This improves static type checking by promoting array dimensionality to a type.
    """
    if (dims := len(x.shape)) != 1:
        msg = f"Expected numpy array with one dimension, got {dims}"
        raise ValueError(msg)
    return x


@dataclass(frozen=True)
class TimeSeriesNumpy:
    """Dataclass representing a segment of timeseries"""

    times: NumpyArray1D
    values: NumpyArray1D


class SeqChunk:
    """Container for a 1D numpy array representing a chunk of samples

    The purpose is for static type checking and self-documentation,
    providing a type specifically representing a chunk of a sequence,
    which is stored in memory. It also ensures that stored raw arrays
    are one-dimensional.

    """

    def __init__(self, samples: np.ndarray) -> None:
        """Constructor.

        Args:
            samples: One-dimensional numpy array with the samples
        """
        if len(samples.shape) != 1:
            msg = f"SeqChunk: expected 1D numpy array, got shape {samples.shape}"
            raise TypeError(msg)

        self._samples = samples

    @property
    def samples(self) -> np.ndarray:
        """One-dimensional numpy array with the samples"""
        return self._samples

    @property
    def dtype(self):
        """The data type of the chunk elements, as numpy dtype"""
        return self.samples.dtype

    @property
    def size(self) -> int:
        """Length of the chunk"""
        return self.samples.shape[0]


class ConstSeqChunk:
    """Class representing a constant chunk of samples

    This represents a constant chunk equipped with a length.
    """

    def __init__(self, const: float, size: int) -> None:
        if size < 0:
            msg = f"ConstSeqChunk: got negative size {size}"
            raise ValueError(msg)
        self._const = float(const)
        self._size = int(size)

    @property
    def const(self):
        """The constant value of the chunk"""
        return self._const

    @property
    def dtype(self):
        """The data type of the chunk elements, as numpy dtype"""
        return np.dtype(type(self.const))

    @property
    def size(self) -> int:
        """Length of the chunk"""
        return self._size


class FuncOfTime:
    """class representing a function of time for use in simulation

    The purpose is for static type checking and self-documentation,
    providing a type for functions of time that accept times as SeqChunk
    with dtype being float, and return samples as another SeqChunk.
    It also ensures that the shape of the sampled array equals the shape
    of the sample time array.
    """

    def __init__(
        self, func: Callable[[np.ndarray], np.ndarray], dtype=np.float64
    ) -> None:
        self._func = func
        self._dtype = dtype

    def __call__(self, t: SeqChunk) -> SeqChunk:
        """Evaluate function and ensure correct shape"""
        if t.dtype != float:
            msg = f"FuncOfTime: times must be float, got {t.dtype}"
            raise TypeError(msg)

        res = self._func(t.samples)

        if res.dtype != self.dtype:
            msg = f"FuncOfTime: wrapped function returned invalid type {res.dtype}"
            raise TypeError(msg)

        if res.shape != t.samples.shape:
            msg = (
                "FuncOfTime: wrapped function returned invalid "
                f"shape {res.shape}, expected {t.samples.shape}"
            )
            raise RuntimeError(msg)
        return SeqChunk(res)

    @property
    def dtype(self):
        """The data type of returned chunks"""
        return self._dtype

    def rawfunc(self, t: np.ndarray) -> np.ndarray:
        """Bare-metal interface to function using numpy arrays"""
        return self(SeqChunk(t)).samples


class ConstFuncOfTime:
    """class representing a constant function of time for use in simulation

    The purpose is for static type checking and self-documentation,
    providing a type for functions of time that are constant. ConstFuncOfTime
    can be called like FuncOfTime, but returns a ConstChunk
    of same size as the time array.
    """

    def __init__(self, const: float) -> None:
        self._const = float(const)

    @property
    def const(self):
        """The constant return value of the function"""
        return self._const

    def __call__(self, t: SeqChunk) -> ConstSeqChunk:
        if t.dtype != float:
            msg = f"ConstFuncOfTime: times must be float, got {t.dtype}"
            raise TypeError(msg)
        return ConstSeqChunk(self._const, t.size)

    @property
    def dtype(self):
        """The data type of returned chunks"""
        return np.dtype(type(self.const))


FuncOfTimeTypes: TypeAlias = FuncOfTime | ConstFuncOfTime
