#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Containers
==========

Container object for signals.

.. autoclass:: ForEachObject
    :members:

.. autoclass:: ForEachSC
    :members:

.. autoclass:: ForEachMOSA
    :members:

"""

import abc
import logging
from concurrent.futures import ThreadPoolExecutor

import numpy as np

logger = logging.getLogger(__name__)


class ForEachObject(abc.ABC):
    """Abstract class which represents a dictionary holding a value for each object."""

    # Used to bypass Numpy's vectorization and use
    # this class `__rmul__()` method for multiplication from both sides
    __array_priority__ = 10000

    def __init__(self, values, concurrent=False):
        """Initialize an object with a value or a function of the mosa index.

        Args:
            values: a value, a dictionary of values, or a function (mosa -> value)
            concurrent (bool): whether to parallelize using a thread pool
        """
        if isinstance(values, dict):
            self.dict = {mosa: values[mosa] for mosa in self.indices()}
        elif callable(values):
            if concurrent:
                with ThreadPoolExecutor(max_workers=3) as executor:
                    indices = self.indices()
                    computed_values = executor.map(values, indices)
                    self.dict = dict(zip(indices, computed_values))
            else:
                self.dict = {mosa: values(mosa) for mosa in self.indices()}
        else:
            self.dict = {mosa: values for mosa in self.indices()}

    @classmethod
    @abc.abstractmethod
    def indices(cls):
        """Return list of object indices."""
        raise NotImplementedError

    def transformed(self, transformation, concurrent=False):
        """Return a new dictionary from transformed objects.

        Args:
            transformation: function (mosa, value -> new_value)
            concurrent (bool): whether to parallelize using a thread pool
        """
        return self.__class__(lambda mosa: transformation(mosa, self[mosa]), concurrent)

    def collapsed(self):
        """Turn a numpy arrays containing identical elements into a scalar.

        This method can be used to optimize computations when constant time series are involved.
        """
        return self.transformed(
            lambda _, x: x[0] if isinstance(x, np.ndarray) and np.all(x == x[0]) else x
        )

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, item):
        self.dict[key] = item

    def values(self):
        """Return dictionary values."""
        return self.dict.values()

    def keys(self):
        """Return dictionary keys."""
        return self.dict.keys()

    def items(self):
        """Return dictionary items."""
        return self.dict.items()

    def __len__(self):
        """Return maximum size of signals."""
        sizes = [1 if np.isscalar(signal) else len(signal) for signal in self.values()]
        return np.max(sizes)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.dict == other.dict
        if isinstance(other, dict):
            return self.dict == other
        return np.all([self[index] == other for index in self.indices()])

    def __abs__(self):
        return self.transformed(lambda index, value: abs(value))

    def __neg__(self):
        return self.transformed(lambda index, value: -value)

    def __add__(self, other):
        if isinstance(other, ForEachObject):
            if isinstance(other, type(self)):
                return self.transformed(lambda index, value: value + other[index])
            raise TypeError(
                f"unsupported operand type for +: '{type(self)}' and '{type(other)}'"
            )
        return self.transformed(lambda _, value: value + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, ForEachObject):
            if isinstance(other, type(self)):
                return self.transformed(lambda index, value: value - other[index])
            raise TypeError(
                f"unsupported operand type for -: '{type(self)}' and '{type(other)}'"
            )
        return self.transformed(lambda _, value: value - other)

    def __rsub__(self, other):
        return -(self - other)

    def __mul__(self, other):
        if isinstance(other, ForEachObject):
            if isinstance(other, type(self)):
                return self.transformed(lambda index, value: value * other[index])
            raise TypeError(
                f"unsupported operand type for *: '{type(self)}' and '{type(other)}'"
            )
        return self.transformed(lambda _, value: value * other)

    def __rmul__(self, other):
        return self * other

    def __floordiv__(self, other):
        if isinstance(other, ForEachObject):
            if isinstance(other, type(self)):
                return self.transformed(lambda index, value: value // other[index])
            raise TypeError(
                f"unsupported operand type for //: '{type(self)}' and '{type(other)}'"
            )
        return self.transformed(lambda _, value: value // other)

    def __truediv__(self, other):
        if isinstance(other, ForEachObject):
            if isinstance(other, type(self)):
                return self.transformed(lambda index, value: value / other[index])
            raise TypeError(
                f"unsupported operand type for /: '{type(self)}' and '{type(other)}'"
            )
        return self.transformed(lambda _, value: value / other)

    def __rtruediv__(self, other):
        return (self / other) ** (-1)

    def __pow__(self, other):
        return self.transformed(lambda _, value: value**other)

    def __repr__(self):
        return repr(self.dict)


class ForEachSC(ForEachObject):
    """Represents a dictionary of values for each spacecraft."""

    @classmethod
    def indices(cls):
        return ["1", "2", "3"]

    @staticmethod
    def distant_left_sc(sc):
        """Return index of distant rleftspacecraft."""
        if sc not in ForEachSC.indices():
            raise ValueError(f"invalid spacecraft index '{sc}'")
        return f"{int(sc) % 3 + 1}"

    @staticmethod
    def distant_right_sc(sc):
        """Return index of distant right spacecraft."""
        if sc not in ForEachSC.indices():
            raise ValueError(f"invalid spacecraft index '{sc}'")
        return f"{(int(sc) - 2) % 3 + 1}"

    @staticmethod
    def left_mosa(sc):
        """Return index of left MOSA."""
        if sc not in ForEachSC.indices():
            raise ValueError(f"invalid spacecraft index '{sc}'")
        return f"{sc}{ForEachSC.distant_left_sc(sc)}"

    @staticmethod
    def right_mosa(sc):
        """Return index of right MOSA."""
        if sc not in ForEachSC.indices():
            raise ValueError(f"invalid spacecraft index '{sc}'")
        return f"{sc}{ForEachSC.distant_right_sc(sc)}"

    def for_each_mosa(self):
        """Return a ForEachMOSA instance by sharing the spacecraft values on both MOSAs."""
        return ForEachMOSA(lambda mosa: self[ForEachMOSA.sc(mosa)])

    def __add__(self, other):
        if isinstance(other, ForEachMOSA):
            return self.for_each_mosa() + other
        return super().__add__(other)

    def __sub__(self, other):
        if isinstance(other, ForEachMOSA):
            return self.for_each_mosa() - other
        return super().__sub__(other)

    def __mul__(self, other):
        if isinstance(other, ForEachMOSA):
            return self.for_each_mosa() * other
        return super().__mul__(other)

    def __floordiv__(self, other):
        if isinstance(other, ForEachMOSA):
            return self.for_each_mosa() // other
        return super().__floordiv__(other)

    def __truediv__(self, other):
        if isinstance(other, ForEachMOSA):
            return self.for_each_mosa() / other
        return super().__truediv__(other)


class ForEachMOSA(ForEachObject):
    """Represents a dictionary of values for each moveable optical subassembly (MOSA)."""

    @classmethod
    def indices(cls):
        return ["12", "23", "31", "13", "32", "21"]

    @staticmethod
    def sc(mosa):
        """Return index of spacecraft hosting MOSA."""
        return f"{mosa[0]}"

    @staticmethod
    def distant_mosa(mosa):
        """Return index of distant MOSA.

        In practive, we invert the indices to swap emitter and receiver.
        """
        if mosa not in ForEachMOSA.indices():
            raise ValueError(f"invalid MOSA index '{mosa}'")
        return f"{mosa[1]}{mosa[0]}"

    @staticmethod
    def adjacent_mosa(mosa):
        """Return index of adjacent MOSA.

        In practice, we replace the second index by the only unused spacecraft index.
        """
        if mosa not in ForEachMOSA.indices():
            raise ValueError(f"invalid MOSA index '{mosa}'")
        unused = [sc for sc in ForEachSC.indices() if sc not in mosa]
        if len(unused) != 1:
            raise RuntimeError(f"cannot find adjacent MOSA for '{mosa}'")
        return f"{mosa[0]}{unused[0]}"

    def distant(self):
        """Return a ForEachMOSA instance for distant MOSAs."""
        return ForEachMOSA(lambda mosa: self[ForEachMOSA.distant_mosa(mosa)])

    def adjacent(self):
        """Return a ForEachMOSA instance for adjacent MOSAs."""
        return ForEachMOSA(lambda mosa: self[ForEachMOSA.adjacent_mosa(mosa)])

    def __add__(self, other):
        if isinstance(other, ForEachSC):
            return self + other.for_each_mosa()
        return super().__add__(other)

    def __sub__(self, other):
        if isinstance(other, ForEachSC):
            return self - other.for_each_mosa()
        return super().__sub__(other)

    def __mul__(self, other):
        if isinstance(other, ForEachSC):
            return self * other.for_each_mosa()
        return super().__mul__(other)

    def __floordiv__(self, other):
        if isinstance(other, ForEachSC):
            return self // other.for_each_mosa()
        return super().__floordiv__(other)

    def __truediv__(self, other):
        if isinstance(other, ForEachSC):
            return self / other.for_each_mosa()
        return super().__truediv__(other)
