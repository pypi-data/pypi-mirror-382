"""Utilities for analysing stream collections as graphs

This exists to support the streams.scheduler
"""

import math
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from lisainstrument.streams.streams import StreamBase


@dataclass
class Dod:
    """Describes the domain of dependence of one stream on another stream

    Streams computed from other streams require a finite number of elements
    from the dependencies to compute a given index. Further, the stream may
    include downsampling. This class connects the index spaces of a single
    dependency using three parameters. To compute a point i in the output
    stream, the indices required from the input stream at hand are

    i_dep = [i*ratio + first, i*ratio + last]
    """

    first: int
    last: int
    ratio: int

    def __post_init__(self):
        if not isinstance(self.first, int):
            raise TypeError("Dod.first must be int")
        if not isinstance(self.last, int):
            raise TypeError("Dod.last must be int")
        if not isinstance(self.ratio, int):
            raise TypeError("Dod.ratio must be int")
        if self.first > self.last:
            raise ValueError(f"Dod invalid range {self.first}, {self.last}")
        if self.ratio <= 0:
            raise ValueError(f"Dod invalid sample ratio {self.ratio}")

    def first_req(self, i: int) -> int:
        """First dependency index required to compute target index"""
        return i * self.ratio + self.first

    def last_req(self, i: int) -> int:
        """Last dependency index required to compute target index"""
        return i * self.ratio + self.last

    def range_req(self, rg: tuple[int, int]) -> tuple[int, int]:
        """Range of dependency index required to compute target index range"""
        return self.first_req(rg[0]), self.last_req(rg[1])


@dataclass
class StreamGraph:
    """Describes a collection of streams and their interdependencies as a
    directed graph. In addition to the dependencies themselves, this also
    stores the temporal relation between streams via the domain of dependence.
    The streams are not stored, just their IDs.
    """

    dod: dict[tuple[int, int], Dod]
    src: dict[int, set[int]]
    dst: dict[int, set[int]]

    def leaves(self) -> set[int]:
        """IDs of streams that are not dependencies of other streams"""
        return {i for i, e in self.dst.items() if not e}

    def roots(self) -> set[int]:
        """IDs of streams without dependencies"""
        return {i for i, e in self.src.items() if not e}


def graph_from_streams(streams: dict[int, StreamBase]) -> StreamGraph:
    """Assemble StreamGraph from colection of StreamBase"""
    dods: dict[tuple[int, int], Dod] = {}
    for i, s in streams.items():
        for d in s.dependencies:
            j = d.stream.id
            dod = Dod(d.dod_first, d.dod_last, d.sample_ratio)
            dods[(j, i)] = dod
    return stream_graph_from_dods(dods)


def merge_dods(*args: Dod) -> Dod:
    """Compute merged domain of dependence

    This only makes sense for homogeneous downsample ratios, which is required.
    """
    ratios = {a.ratio for a in args}
    if len(ratios) != 1:
        msg = "Merging domains of dependence requires identical downsampling ratios"
        raise RuntimeError(msg)
    ratio = list(ratios)[0]
    first = min(a.first for a in args)
    last = max(a.last for a in args)

    return Dod(first, last, ratio)


def stream_graph_from_dods(dod: dict[tuple[int, int], Dod]) -> StreamGraph:
    """Create StreamGraph from edges"""
    src: dict[int, set[int]] = defaultdict(set)
    dst: dict[int, set[int]] = defaultdict(set)
    for i, j in dod:
        _ = dst[j], src[i]
        dst[i].add(j)
        src[j].add(i)
    return StreamGraph(dod, src, dst)


def subgraph(graph: StreamGraph, keep: set[int]) -> StreamGraph:
    """Return subgraph only contaiing the given set of stream IDs"""
    if not keep <= set(graph.src.keys()):
        msg = "cannot create subgraph with nonexistent nodes"
        raise RuntimeError(msg)

    src: dict[int, set[int]] = {i: set() for i in keep}
    dst: dict[int, set[int]] = {i: set() for i in keep}
    dod: dict[tuple[int, int], Dod] = {}
    for (i, j), d in graph.dod.items():
        if (i in keep) and (j in keep):
            dst[i].add(j)
            src[j].add(i)
            dod[(i, j)] = d

    return StreamGraph(dod, src, dst)


def get_required_ranges(
    graph: StreamGraph, out_ranges: dict[int, tuple[int, int]]
) -> dict[int, tuple[int, int]]:
    """Obtain required range for all streams given range of selected streams

    The resulting range does not include the prefix sizes of any stream, only the domain
    of dependence. Use get_cumulative_prefix to determine instead the absolute smallest index
    ever needed for each stream.
    """
    ranges: dict[int, tuple[int, int]] = {}

    def rec(i, rg):
        if i in ranges:
            rgi = ranges[i]
            ranges[i] = (min(rgi[0], rg[0]), max(rgi[1], rg[1]))
        else:
            ranges[i] = rg
        for j in graph.src[i]:
            dod = graph.dod[(j, i)]
            rec(j, dod.range_req(rg))

    for i, rg in out_ranges.items():
        rec(i, rg)

    return ranges


def get_cumulative_prefix(
    streams: dict[int, StreamBase], out_ranges: dict[int, tuple[int, int]]
) -> dict[int, int]:
    """Obtain required range for streams taking into account also the prefix sizes

    This exists mainly to support throw-away burn-in segments for IIR filters.
    """
    iprefix: dict[int, int] = {}

    def rec(i, istart):
        s = streams[i]
        ipref = istart - s.prefix_size
        if i in iprefix:
            iprefix[i] = min(iprefix[i], ipref)
        else:
            iprefix[i] = ipref

        for d in s.dependencies:
            jstart = ipref * d.sample_ratio + d.dod_first
            rec(d.stream.id, jstart)

    for i, rg in out_ranges.items():
        rec(i, rg[0])

    return iprefix


def extract_layers(graph: StreamGraph) -> list[set[int]]:
    """Rank streams such that each stream only depends on lower ranks

    Returns list starting at rank zero, corresponding to the roots.
    """

    rank: dict[int, int] = {}

    def rec(i: int) -> int:
        if i in rank:
            r = rank[i]
            if r < 0:
                raise RuntimeError("Cyclic dependency")
            return r

        srci = graph.src[i]
        if not srci:
            rank[i] = 0
            return 0

        rank[i] = -1
        nr = max((rec(k) for k in srci)) + 1
        rank[i] = nr
        return nr

    for i in graph.leaves():
        rec(i)

    layers = defaultdict(set)
    for i in graph.src:
        layers[rank[i]].add(i)
    maxrank = max(layers.keys())
    return [layers[i] for i in range(maxrank + 1)]


def extract_output_rates(graph: StreamGraph) -> dict[int, int]:
    """Computes output rate for each stream and ensures consistent downsampling

    The rates are given as integers.
    """

    rates: dict[int, Fraction] = {}

    def rec(i: int, rate: Fraction):
        if i in rates:
            if rate != rates[i]:
                msg = "Inconsistent sample rates in stream dependency graph"
                raise RuntimeError(msg)
            return
        rates[i] = rate
        for j in graph.src[i]:
            f = graph.dod[(j, i)].ratio
            rec(j, Fraction(rate * f))
        for j in graph.dst[i]:
            f = graph.dod[(i, j)].ratio
            rec(j, Fraction(rate / f))

    rec(list(graph.leaves())[0], Fraction(1))
    if len(rates) != len(graph.src):
        msg = "Cannot deduce relative sample rates for disconnected stream graph"
        raise RuntimeError(msg)

    lcm = math.lcm(*(r.denominator for r in rates.values()))
    normrates = {i: int(r * lcm) for i, r in rates.items()}

    return normrates


def extract_components(graph: StreamGraph) -> list[StreamGraph]:
    """Returns a list with subgraphs of the components"""

    def rec(i: int, nodes: set[int]):
        if i in nodes:
            return
        nodes.add(i)
        for j in graph.src[i]:
            rec(j, nodes)
        for j in graph.dst[i]:
            rec(j, nodes)

    comps: list[StreamGraph] = []
    left = list(graph.leaves())
    while left:
        cnd: set[int] = set()
        rec(left[0], cnd)
        comps.append(subgraph(graph, cnd))
        left = [n for n in left if not n in cnd]

    return comps
