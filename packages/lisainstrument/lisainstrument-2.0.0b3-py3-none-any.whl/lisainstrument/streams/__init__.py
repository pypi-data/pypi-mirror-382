"""Package for chunked data processing of large datasets


The design is outlined below.


The central concept is a "stream" , implemented in the StreamBase class.
Streams represent the abstract concept of a sequence in time that depends on other sequences

A stream stores

- A function to compute a new chunk from chunks of the streams it depends on
- A list of streams it depends on
- The relative index range needed from each other stream for a given index
- Optionally, a downsampling ratio for streams it depends on


The package provides functions operating on streams for the following tasks

- FIR and IIR filtering
- Sampling of continuous functions (used for orbits, GW, glitches, freqplan)
- Delaying one stream by a time shift given in another stream
- Inversion of the above coordinate transformation
- Time integration and derivatives
- Applying functions given in terms of numpy arrays chunk-wise to streams

There are "input" stream types without dependencies

- Generating noise for given noise definition
- Generating regularly spaced timestamps

To save the computed streams data, there are "output" Stream types

- Saving chunks to dataset in file
- Copy chunks into large in-memory numpy array

A difference to working with arrays is that streams are conceptually infinite. One specifies
the ranges of streams that should be stored, and the required ranges for the dependencies are
computed automatically. As a bonus, the generated data is now completely valid, interpolation and
filtering do not need boundary conditions anymore.

To collect and label streams that are to be saved, there is a class StreamBundle. This container
uses tuples of strings as identifiers for output streams. The motivation for this choice is so that
identifiers can be easily used to create hirarchical storage formats, such as nested groups in HDF5
files.

Collections of streams in StreamBundle just describe the computational task. The actual computation
is the responsability of the "scheduler". The current scheduler works roughly as follows.
First, it extracts the dependency graph and performs a topoligical sort into layers, such that streams in each
layer depend only on streams in layers above. This is used to make a work plan.

- Compute a chunk of each streams in the topmost layer
- Compute each stream in the next layer as far as possible with the already computed data
- Do the same in each layer successively.
- Determine which is the last index needed from the dependencies to compute one more element of each stream
- Split off the data still needed for each stream, to be joined with chunk in next cycle

The work plan above is implemented in the scheduler code by calls to an engine. There are two engines, serial
and parallel. The serial one just immediately executes the tasks, while the parallel one creates a dask.delayed
for the task. For the benefit of parallel engines, the engine interface also has the concept of a checkpoint.
At a checkpoint, all delayed tasks are executed and the data needed in the next cycle is stored as regular data,
which is read back in the next cycle as initial data. The tasks that can be executed in parallel are thus
strictly confined between two checkpoints. A checkpoint happens every few chunk-cycles (default is 3 chunks)
to allow some degree of parallelism also in the time direction.

The numpy-based core routines for filtering, noise definitions, interpolations, among others, are contained
in the sigpro package. For noise generation, there are two designs: One consists of a single stream per
noise, doing all computations for a noise chunk internally. This is delegated to the numpy-based
noisy.noise_gen_numpy module. This version leads to a simpler stream graph because a sum of two noises is
just one stream. The second variant, which is now the default, assembles compound noises as several streams.
For example, a sum of noises is the sum of two noise streams, and a filtered noise is a noise stream chained
to a filtering stream. This leads to a more complex graph, but potentially better parallelism.

The work of actually storing data somewhere is delegated to a DataStorage interface. There are DataStorage
implementations for HDF5 output, and plain dictionaries of in-memory numpy arrays. Conversely, the streams
package does not just allow computing data on the fly, but provides tools to make existing data avaialble as
stream. Currently, there is only StreamNumpyArray for reading plain in-memory arrays, but a HDF5 dataset input
stream is planned.
"""

from lisainstrument.streams.array import array_dict_as_stream_bundle
from lisainstrument.streams.delay import stream_delay_lagrange
from lisainstrument.streams.derivative import stream_gradient
from lisainstrument.streams.expression import stream_expression
from lisainstrument.streams.firfilter import stream_filter_fir
from lisainstrument.streams.hdf5_store import (
    H5AttrValidTypes,
    hdf5_file_as_stream_bundle,
    store_bundle_hdf5,
)
from lisainstrument.streams.iirfilter import stream_filter_iir, stream_filter_iir_chain
from lisainstrument.streams.integrate import stream_int_cumsum, stream_int_trapz
from lisainstrument.streams.noise_alt import stream_noise
from lisainstrument.streams.numpy_store import (
    eval_stream_list_numpy,
    store_bundle_numpy,
)
from lisainstrument.streams.sampling import stream_func_of_time
from lisainstrument.streams.scheduler import (
    SchedulerConfigParallel,
    SchedulerConfigSerial,
    SchedulerConfigTypes,
    store_bundle,
)
from lisainstrument.streams.shift_inv import stream_shift_inv_lagrange
from lisainstrument.streams.store import DatasetIdentifier, ValidMetaDataTypes
from lisainstrument.streams.streams import (
    StreamBase,
    StreamBundle,
    StreamConst,
    StreamIndices,
    describe_streams_dict,
)
from lisainstrument.streams.time import (
    StreamTimeGrid,
    stream_downsample,
    timestamp_stream,
)
