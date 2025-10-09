"""Machinery to evaluate a StreamBundle and transfer results to a DataStorage

The store_bundle function takes a StreamBundle and a DataStorage instance as input,
and evaluates the streams in the bundle in chunks and transfers the chunks to the
DataStorage, which might represent a file or memory-based storage.

Internally, the code to figure out what needs to be computed in which order is
separate from the code actually doing it, allowing different engines optimized
for speed or conserving memory. There are two engines: .scheduler_dask.ExecutorDask
for parallel processing and scheduler_serial.ExecutorSerial for serial processing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, TypeAlias

from lisainstrument.streams.graph_util import (
    StreamGraph,
    extract_components,
    extract_layers,
    extract_output_rates,
    get_cumulative_prefix,
    get_required_ranges,
    graph_from_streams,
)
from lisainstrument.streams.scheduler_dask import ExecutorDask
from lisainstrument.streams.scheduler_serial import ExecutorProtocol, ExecutorSerial
from lisainstrument.streams.store import DataStorage, StreamStore
from lisainstrument.streams.streams import StreamBase, StreamBundle, StreamConst

logger = logging.getLogger(__name__)


class StreamPlan:
    """Analyse stream collection for information needed to evaluate streams

    This analyses the graph of stream dependencies, assuming a graph with a single
    connected component. The graph is sorted topoligically into "layers", such that each
    stream depends only on streams in layers above its own. Further, the required ranges
    for each stream are determined, starting at the prescribed ranges of the output streams
    and propagating upwards through the dependency graph, taking into account the domain of
    dependence information stored in the stream dependencies. Similarly to the above ranges,
    this computes the "prefix" ranges for each stream, necessitated by streams with burn-in
    periods. Finally, the downsampling ratios for each dependency are combined to obtain a
    global sampling rate for each stream, normalized such that all rates are integer. If there
    is no solution for consistent sampling rates, an exception is raised.
    """

    def __init__(
        self,
        streams: dict[int, StreamBase],
        graph: StreamGraph,
        out_ranges: dict[int, tuple[int, int]],
    ) -> None:
        """Constructor

        Arguments:
            streams: dictionary with collection of streams, keyed arbitrarily
            graph: Connected dependency graph of the streams
            out_ranges: ranges requested for the output streams
        """
        self._streamgraph: Final = graph
        self._streams: Final = {i: streams[i] for i in graph.src.keys()}
        out_ranges = {i: out_ranges[i] for i in out_ranges if i in graph.src.keys()}
        ranges = get_required_ranges(self._streamgraph, out_ranges)
        self._rg_start: Final = {i: rg[0] for i, rg in ranges.items()}
        self._rg_stop: Final = {i: rg[1] for i, rg in ranges.items()}
        self._rg_prefix: Final = get_cumulative_prefix(streams, out_ranges)
        self._out_rates: Final = extract_output_rates(self._streamgraph)
        self._layers: Final = extract_layers(self._streamgraph)

    @property
    def streams(self) -> dict[int, StreamBase]:
        """Dictionary mapping stream IDs to streams"""
        return self._streams

    @property
    def streamgraph(self) -> StreamGraph:
        """The directed graph descibing the stream dependencies"""
        return self._streamgraph

    @property
    def layers(self) -> list[set[int]]:
        """The dependency layers of the stream graph"""
        return self._layers

    @property
    def rg_start(self) -> dict[int, int]:
        """Dictionary with start index for stream at given ID

        This does not include the accumulated stream prefix sizes
        """
        return self._rg_start

    @property
    def rg_prefix(self) -> dict[int, int]:
        """Dictionary with first required index for stream at given ID

        This does include the accumulated stream prefix sizes, no earlier
        elements are required anywhere.
        """
        return self._rg_prefix

    @property
    def rg_stop(self) -> dict[int, int]:
        """Dictionary with end index for stream at given ID"""
        return self._rg_stop

    @property
    def out_rates(self) -> dict[int, int]:
        """Dictionary with output 'rates' for given stream ID"""
        return self._out_rates

    @property
    def max_out_rate(self) -> int:
        """Maximum output 'rate'"""
        return max(self.out_rates.values())


def storage_stream_plan(
    bundle: StreamBundle,
    store: DataStorage,
) -> list[StreamPlan]:
    """Supplement streams from bundle with storage streams and compute StreamPlan"""
    oids = {bundle.output_from_dsid(dsid) for dsid in store.valid_identifiers}
    streams = bundle.get_needed_streams(oids)
    out_ranges: dict[int, tuple[int, int]] = {}
    for dsid in store.valid_identifiers:
        oid = bundle.output_from_dsid(dsid)
        oistart, oistop = bundle.get_out_range(dsid)
        ostr = bundle.get_stream(oid)
        if isinstance(ostr, StreamConst):
            store.dataset_const(dsid, oistart, oistop, ostr.const)
            if ostr.id in streams:
                del streams[ostr.id]
        else:
            ods = store.dataset(dsid, oistart, oistop, ostr.dtype)
            st = StreamStore(ods, ostr, (oistart, oistop))
            streams[st.id] = st
            out_ranges[st.id] = oistart, oistop

    graph = graph_from_streams(streams)
    comps = extract_components(graph)

    return [StreamPlan(streams, gr, out_ranges) for gr in comps]


def _store_connected_component(
    plan: StreamPlan, *, chunk_size: int, num_chunks: int, build: ExecutorProtocol
) -> None:
    """Evaluate a single connected component of a stream graph

    Based on the num_workers parameter, the serial or parallel engine is used.
    Set num_workers=1 for minimum memory use and no use of dask whatsoever.

    Arguments:
        plan: The StreamPlan storing the component information
        chunk_size: Size of smallest execution unit in terms of global index space
        build: Executor engine
    """

    max_rate = plan.max_out_rate

    k_glob = 0
    for s in plan.layers[0]:
        pre_glob = (
            (plan.rg_start[s] - plan.rg_prefix[s]) * max_rate
        ) // plan.out_rates[s]
        k_glob = min(k_glob, -pre_glob - 1)

    while not build.done():
        logger.info("Computing index %d", k_glob)
        build.load_checkpoint()
        chunk_cnt = 0
        while (chunk_cnt < num_chunks) and (not build.done()):
            chunk_cnt += 1
            k_glob += chunk_size

            for s in plan.layers[0]:
                k_loc = plan.rg_start[s] + (k_glob * plan.out_rates[s]) // max_rate
                k_loc = min(k_loc, plan.rg_stop[s])
                if k_loc > plan.rg_prefix[s]:
                    build.generate_until(s, k_loc)

            for layer in plan.layers[1:]:
                for s in layer:
                    k_dep = []
                    for d in plan.streamgraph.src[s]:
                        dod = plan.streamgraph.dod[(d, s)]
                        k_dep.append((build.i_next(d) - 1 - dod.last) // dod.ratio)
                    k_loc = min(k_dep) + 1
                    k_prv = build.i_next(s)
                    if k_loc > k_prv:
                        build.generate_until(s, k_loc)

            for s in plan.streams:
                k_trim = build.i_next(s)
                for d in plan.streamgraph.dst[s]:
                    dod = plan.streamgraph.dod[(s, d)]
                    k_req = build.i_next(d) * dod.ratio + dod.first
                    k_trim = min(k_trim, k_req)
                build.trim_buffer(s, k_trim)
        build.compute_checkpoint()


@dataclass(frozen=True)
class SchedulerConfigSerial:
    """Parameters for serial execution

    chunk_size: Size of smallest execution unit in terms of global index space
    """

    chunk_size: int

    @property
    def num_chunks(self) -> int:
        """This scheduler parameter is irrelevent for the serial case"""
        return 1

    def __post_init__(self):
        if not (isinstance(self.chunk_size, int) and self.chunk_size > 2):
            msg = f"SchedulerConfigSerial: chunk_size must be integer > 2, got {self.chunk_size}"
            raise RuntimeError(msg)


@dataclass(frozen=True)
class SchedulerConfigParallel:
    """Parameters for parallel execution

    chunk_size: Size of smallest execution unit in terms of global index space
    num_chunks: Number of chunks between checkpoints
    num_workers: Number of tasks to execute in parallel
    """

    chunk_size: int
    num_chunks: int
    num_workers: int

    def __post_init__(self):
        if not (isinstance(self.chunk_size, int) and self.chunk_size > 2):
            msg = f"SchedulerConfigParallel: chunk_size must be integer > 2, got {self.chunk_size}"
            raise RuntimeError(msg)
        if not (isinstance(self.num_chunks, int) and self.num_chunks >= 1):
            msg = f"SchedulerConfigParallel: num_chunks must be integer >= 1, got {self.num_chunks}"
            raise RuntimeError(msg)
        if not (isinstance(self.num_workers, int) and self.num_workers >= 1):
            msg = f"SchedulerConfigParallel: num_workers must be integer >= 1, got {self.num_workers}"
            raise RuntimeError(msg)


SchedulerConfigTypes: TypeAlias = SchedulerConfigParallel | SchedulerConfigSerial


def _get_executor(
    streams: dict[int, StreamBase],
    rg_first: dict[int, int],
    rg_stop: dict[int, int],
    config: SchedulerConfigTypes,
) -> ExecutorProtocol:
    """Set up Executor from config"""
    if isinstance(config, SchedulerConfigParallel):
        logger.info(
            "Using ExecutorDask with %d workers processing %d chunks at a time",
            config.num_workers,
            config.num_chunks,
        )
        return ExecutorDask(streams, rg_first, rg_stop, config.num_workers)
    logger.info("Using ExecutorSerial")
    return ExecutorSerial(streams, rg_first, rg_stop)


def store_bundle(
    bundle: StreamBundle, store: DataStorage, config: SchedulerConfigTypes | None
):
    """Evaluate a StreamBundle instance and store results in a DataStorage instance

    Only the output streams required by the DataStorage are evaluated. The bundle may
    contain other streams which are ignored. The range transferred to DataStorage is
    defined for each output stream when it was added to the bundle.

    Arguments:
        bundle: The StreamBundle to be evaluated
        store: The DataStorage instance were to write results

    """
    if config is None:
        config = SchedulerConfigSerial(chunk_size=1000000)

    plans = storage_stream_plan(bundle, store)

    logger.info("Evaluating streams in chunks of size %d", config.chunk_size)

    for n, plan in enumerate(plans):
        logger.info(
            "Evaluating connected component %d / %d of stream graph", n, len(plans)
        )
        logger.info("Component consists of %d streams", len(plan.streams))

        build = _get_executor(plan.streams, plan.rg_prefix, plan.rg_stop, config)
        _store_connected_component(
            plan,
            chunk_size=config.chunk_size,
            num_chunks=config.num_chunks,
            build=build,
        )

    logger.info("Finished evaluating streams")
