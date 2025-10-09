"""This module provides enums for spacecrafts, MOSAs, and locking types.

The enum values are the same strings used in the instrument and container modules,
and the enums can be created from such strings. The enums can be used to validate
string arguments that are supposed to be MOSA or spacecraft names. Another use
is to mark arguments in newly written code as SC or MOSA identifiers instead of
arbitrary strings, increasing the strictness of static type checking.


This module also contains some helper functions related to working with dictionaries
of MOSAs or spacecrafts
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, TypeAlias, TypeVar


class SatID(Enum):
    """Enumerate spacecrafts"""

    SAT_1 = "1"
    SAT_2 = "2"
    SAT_3 = "3"

    @property
    def left(self) -> SatID:
        """The spacecraft which is to the left (naming convention)"""
        return {
            SatID.SAT_1: SatID.SAT_2,
            SatID.SAT_2: SatID.SAT_3,
            SatID.SAT_3: SatID.SAT_1,
        }[self]

    @property
    def right(self) -> SatID:
        """The spacecraft which is to the right  (naming convention)"""
        return {
            SatID.SAT_1: SatID.SAT_3,
            SatID.SAT_2: SatID.SAT_1,
            SatID.SAT_3: SatID.SAT_2,
        }[self]

    @property
    def left_mosa(self) -> "MosaID":
        """The left MOSA of the spacecraft (naming convention)"""
        return {
            SatID.SAT_1: MosaID.MOSA_12,
            SatID.SAT_2: MosaID.MOSA_23,
            SatID.SAT_3: MosaID.MOSA_31,
        }[self]

    @staticmethod
    def names() -> frozenset[str]:
        """Set of all enum values"""
        return frozenset((s.value for s in SatID))


class MosaID(Enum):
    """Enumerate all MOSAs on all spacecrafts"""

    MOSA_12 = "12"
    MOSA_21 = "21"
    MOSA_13 = "13"
    MOSA_31 = "31"
    MOSA_23 = "23"
    MOSA_32 = "32"

    @property
    def distant(self) -> "MosaID":
        """The MOSA on the distant SC a given MOSA is pointed at"""
        return {
            MosaID.MOSA_12: MosaID.MOSA_21,
            MosaID.MOSA_21: MosaID.MOSA_12,
            MosaID.MOSA_13: MosaID.MOSA_31,
            MosaID.MOSA_31: MosaID.MOSA_13,
            MosaID.MOSA_23: MosaID.MOSA_32,
            MosaID.MOSA_32: MosaID.MOSA_23,
        }[self]

    @property
    def adjacent(self) -> "MosaID":
        """The other MOSA on the same spacecraft"""
        return {
            MosaID.MOSA_12: MosaID.MOSA_13,
            MosaID.MOSA_21: MosaID.MOSA_23,
            MosaID.MOSA_13: MosaID.MOSA_12,
            MosaID.MOSA_31: MosaID.MOSA_32,
            MosaID.MOSA_23: MosaID.MOSA_21,
            MosaID.MOSA_32: MosaID.MOSA_31,
        }[self]

    @property
    def sat(self) -> SatID:
        """The spacecraft a MOSA is located on"""
        return {
            MosaID.MOSA_12: SatID.SAT_1,
            MosaID.MOSA_21: SatID.SAT_2,
            MosaID.MOSA_13: SatID.SAT_1,
            MosaID.MOSA_31: SatID.SAT_3,
            MosaID.MOSA_23: SatID.SAT_2,
            MosaID.MOSA_32: SatID.SAT_3,
        }[self]

    @staticmethod
    def names() -> frozenset[str]:
        """Set of all enum values"""
        return frozenset((m.value for m in MosaID))


class LockTypeID(Enum):
    """Enumerate types of laser locking"""

    CAVITY = "cavity"
    DISTANT = "distant"
    ADJACENT = "adjacent"


_Tdict = TypeVar("_Tdict")
_Ttrdict = TypeVar("_Ttrdict")


MosaDictFloat: TypeAlias = dict[str, float]
MosaIdDictFloat: TypeAlias = dict[MosaID, float]
SatDictFloat: TypeAlias = dict[str, float]
SatIdDictFloat: TypeAlias = dict[SatID, float]


def make_mosa_id_dict(
    source: dict[str, _Tdict] | dict[MosaID, _Tdict]
) -> dict[MosaID, _Tdict]:
    """Convert and validate dictionary for MOSA-specific variables keyed by MosaID

    This creates a dictionary mapping MOSA names to arbitrary data,
    ensuring that there is an entry for every MOSA. The source is a generic
    dictionary with MOSA name strings or MosaID as keys. All keys need to
    have the same type. The source dictionary must contain an entry for every
    MOSA and nothing else. No constrains are applied to the value type.
    This function also serves to allow static type checking of the dict keys.

    Arguments:
        source: Dictionary with MOSA variables

    Returns:
        Validated dictionary.

    """

    match source:
        case {
            MosaID.MOSA_12: m12,
            MosaID.MOSA_13: m13,
            MosaID.MOSA_21: m21,
            MosaID.MOSA_23: m23,
            MosaID.MOSA_31: m31,
            MosaID.MOSA_32: m32,
            **other,
        } if not other:
            res = {
                MosaID.MOSA_12: m12,
                MosaID.MOSA_13: m13,
                MosaID.MOSA_21: m21,
                MosaID.MOSA_23: m23,
                MosaID.MOSA_31: m31,
                MosaID.MOSA_32: m32,
            }
        case {
            MosaID.MOSA_12.value: m12,
            MosaID.MOSA_13.value: m13,
            MosaID.MOSA_21.value: m21,
            MosaID.MOSA_23.value: m23,
            MosaID.MOSA_31.value: m31,
            MosaID.MOSA_32.value: m32,
            **other,
        } if not other:
            res = {
                MosaID.MOSA_12: m12,
                MosaID.MOSA_13: m13,
                MosaID.MOSA_21: m21,
                MosaID.MOSA_23: m23,
                MosaID.MOSA_31: m31,
                MosaID.MOSA_32: m32,
            }
        case _:
            msg = "make_mosa_dict: invalid input"
            raise RuntimeError(msg)

    return res


def make_mosa_dict(
    source: dict[str, _Tdict] | dict[MosaID, _Tdict]
) -> dict[str, _Tdict]:
    """Convert and validate dictionary for MOSA-specific variables keyed by MOSA names

    Like make_mosa_id_dict, but using MOSA names instead MosaID as keys.
    """
    res = make_mosa_id_dict(source)
    return {r.value: v for r, v in res.items()}


def make_mosa_dict_const(scalar: _Tdict) -> dict[str, _Tdict]:
    """Create dictionary mapping all MOSA names to the same value"""
    return {m.value: scalar for m in MosaID}


def make_mosa_id_dict_const(scalar: _Tdict) -> dict[MosaID, _Tdict]:
    """Create dictionary mapping all MosaIDs to the same value"""
    return {m: scalar for m in MosaID}


# ~ def make_mosa_dict_float_const(scalar: int|float) -> dict[MosaID, float]:
# ~ """Create dictionary for MOSA-specific variables with equal float-valued entries"""
# ~ return make_mosa_dict_const(float(scalar))

# ~ def make_mosa_dict_int_const(scalar: int) -> dict[MosaID, int]:
# ~ """Create dictionary for MOSA-specific variables with equal int-valued entries"""
# ~ return make_mosa_dict_const(int(scalar))


def transform_mosa_dict(
    mdict: dict[str, _Tdict], func: Callable[[_Tdict], _Ttrdict]
) -> dict[str, _Ttrdict]:
    """Transform MOSA-specific variables dict by mapping each value with a function"""
    return {mosa.value: func(mdict[mosa.value]) for mosa in MosaID}


def make_sat_id_dict(
    source: dict[str, _Tdict] | dict[SatID, _Tdict]
) -> dict[SatID, _Tdict]:
    """Convert and validate dictionary for spacecraft-specific variables keyed by SatID

    This creates a dictionary mapping spacecraft names to arbitrary data,
    ensuring that there is an entry for every spacecraft. The source is a generic
    dictionary with spacecraft name strings or SatID as keys. All keys need to
    have the same type. The source dictionary must contain an entry for every
    spacecraft and nothing else. No constrains are applied to the value type.
    This function also serves to allow static type checking of the dict.

    Arguments:
        source: Dictionary with spacecraft variables

    Returns:
        Validated dictionary
    """

    match source:
        case {SatID.SAT_1: s1, SatID.SAT_2: s2, SatID.SAT_3: s3, **other} if not other:
            res = {SatID.SAT_1: s1, SatID.SAT_2: s2, SatID.SAT_3: s3}
        case {
            SatID.SAT_1.value: s1,
            SatID.SAT_2.value: s2,
            SatID.SAT_3.value: s3,
            **other,
        } if not other:
            res = {SatID.SAT_1: s1, SatID.SAT_2: s2, SatID.SAT_3: s3}
        case _:
            msg = "make_sat_dict: invalid input"
            raise RuntimeError(msg)
    return res


def make_sat_dict(source: dict[str, _Tdict] | dict[SatID, _Tdict]) -> dict[str, _Tdict]:
    """Convert and validate dictionary for spacecraft-specific variables keyed by SC name

    Like make_sat_id_dict, but result uses spacecraft names instead SatID as keys.
    """
    res = make_sat_id_dict(source)
    return {r.value: v for r, v in res.items()}


def make_sat_dict_const(scalar: _Tdict) -> dict[str, _Tdict]:
    """Create dictionary mapping all spaccraft names to the same value"""
    return {s.value: scalar for s in SatID}


def make_sat_id_dict_const(scalar: _Tdict) -> dict[SatID, _Tdict]:
    """Create dictionary mapping all SatID to the same value"""
    return {s: scalar for s in SatID}


def transform_sat_dict(
    sdict: dict[str, _Tdict], func: Callable[[_Tdict], _Ttrdict]
) -> dict[str, _Ttrdict]:
    """Transform spacecraft-specific variables dict by mapping each value with a function"""
    return {sc.value: func(sdict[sc.value]) for sc in SatID}


def for_each_key(keys):
    """Decorator to apply function to given keys in dictionary arguemnts

    The resulting function returns a dictionary with the given keys. For each
    key, the result contains the original function called with each dictionary
    arguments replaced by the element with the same key and each non-dictionary
    argument passed unchanged.
    """

    def decorate(func):
        def wrapped(*args, **kwargs):
            res = {}
            for m in keys:
                iargs = [(a[m] if isinstance(a, dict) else a) for a in args]
                ikwargs = {
                    n: (a[m] if isinstance(a, dict) else a) for n, a in kwargs.items()
                }
                res[m] = func(*iargs, **ikwargs)
            return res

        return wrapped

    return decorate


def for_each_mosa(func):
    """Decorator to apply function to dictionary arguments with MOSA keys"""
    return for_each_key(MosaID.names())(func)


def for_each_sat(func):
    """Decorator to apply function to dictionary arguments with spacecraft keys"""
    return for_each_key(SatID.names())(func)
