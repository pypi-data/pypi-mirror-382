"""Module with entrypoints for commandline interface

The function `run` is called when the module is started as a script, via
`python -m lisainstrument`.
"""

import argparse
import logging

import yaml

from lisainstrument.instrument import Instrument
from lisainstrument.streams import (
    SchedulerConfigParallel,
    SchedulerConfigSerial,
    SchedulerConfigTypes,
)
from lisainstrument.version import __version__


def run() -> None:
    """Perform a LISA simulation using parameters specified in yaml file.

    This takes a YAML file with the simulation parameters and produces a HDF5 file with
    the results of a LISA simulation. The parameters are passed unchanged to the
    `lisainstrument.Instrument` class (see user manual).
    The simulations can make use of multithreading but using more than O(10) threads
    will yield diminishing returns. Specifying 1 thread will employ a purely serial
    task execution, which is recommended when debugging.
    The chunksize parameter affects directly the peak memory usage. Specifying lower
    values than the default will reduce memory but increase runtime, while larger
    values typically do not result in further speedup. The value is in samples per
    stream, and a typical simulation uses O(1000) streams.
    """

    def positive_int(a):
        i = int(a)
        if i <= 0:
            msg = "Expected strictly positive integer"
            raise argparse.ArgumentTypeError(msg)
        return i

    parser = argparse.ArgumentParser(prog="lisainstrument", description=run.__doc__)
    parser.add_argument(
        "parfile",
        default="sim_params.yaml",
        help="YAML file with simulation parameters",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="sim_results.h5",
        help="Path of result file (must not exist)",
    )
    parser.add_argument(
        "-l",
        "--log",
        default="sim_logs.txt",
        help="Path of log file (will be overwritten)",
    )
    parser.add_argument(
        "--threads",
        type=positive_int,
        default=4,
        help="Maximum number of threads to use",
    )
    parser.add_argument(
        "--chunksize",
        type=positive_int,
        default=200000,
        help="Segment size for chunked processing",
    )

    version_info = f"lisainstrument version {__version__}"
    parser.add_argument("--version", action="version", version=version_info)

    args = parser.parse_args()

    logger = logging.getLogger("lisainstrument")
    logfh = logging.FileHandler(args.log, mode="w")
    logfh.setLevel(logging.DEBUG)
    logger.addHandler(logfh)
    logger.setLevel(logging.DEBUG)

    with open(args.parfile, "r", encoding="utf-8") as parfile:
        sim_param = yaml.safe_load(parfile)

    for k, v in sim_param.items():
        print(f"{k}, {type(v)}, {v}")

    instru = Instrument(**sim_param)

    scfg: SchedulerConfigTypes
    if args.threads == 1:
        scfg = SchedulerConfigSerial(chunk_size=args.chunksize)
    else:
        scfg = SchedulerConfigParallel(
            chunk_size=args.chunksize, num_chunks=2, num_workers=args.threads
        )

    instru.export_hdf5(path=args.out, cfgscheduler=scfg)
