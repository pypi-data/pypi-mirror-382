"""This module defines the physical model of the simulator.


The class ModelConstellation is the core of the simulator. It is responsible
for assembling a network of streams that can be evaluated to produce simulation
data. Its direct parameters are collected in a configuration class named
ModelConstellationCfg. Further, it requires ready to use objects representing
sources for orbits, GW, glitches, frequency plan, and signal processing.
"""

import logging
import math
from dataclasses import dataclass
from typing import Callable, Final

from typing_extensions import assert_never

from lisainstrument.glitches.glitch_source import GlitchSource
from lisainstrument.gwsource.gw_source import GWSource
from lisainstrument.instru import instru_formulas as compute
from lisainstrument.instru.instru_filter import InstruDelays
from lisainstrument.instru.instru_locking import LockingResults
from lisainstrument.instru.instru_noises import InstruNoises
from lisainstrument.instru.instru_store import (
    IdxSpace,
    SimFullDatasetsMOSA,
    SimFullDatasetsSat,
    SimResultsNumpyFull,
    make_dataset_id,
)
from lisainstrument.noisy import NoiseDefBase
from lisainstrument.orbiting.constellation_enums import (
    LockTypeID,
    MosaDictFloat,
    MosaID,
    SatDictFloat,
    SatID,
    for_each_mosa,
    make_mosa_dict,
    make_mosa_dict_const,
)
from lisainstrument.orbiting.orbit_source import OrbitSource
from lisainstrument.sigpro import FuncOfTimeTypes
from lisainstrument.streams import (
    StreamBase,
    StreamBundle,
    StreamConst,
    StreamTimeGrid,
    describe_streams_dict,
    stream_downsample,
    stream_func_of_time,
    stream_int_trapz,
    stream_noise,
    timestamp_stream,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelConstellationCfg:
    """Physical parameters of the constellation model

    This does not include parameters of orbits, glitches, frequency plan,
    GW, and signal processing parameters. Those aspects are passed as generic
    interfaces.
    """

    size: int
    t0: float
    dt: float
    physics_upsampling: int
    telemetry_downsampling: int
    initial_telemetry_size: int

    lock: dict[str, str]

    clock_offsets: SatDictFloat
    clock_freqoffsets: SatDictFloat
    clock_freqlindrifts: SatDictFloat
    clock_freqquaddrifts: SatDictFloat

    central_freq: float
    offset_freqs: MosaDictFloat
    modulation_freqs: MosaDictFloat
    dopplers_disable: bool
    prn_ambiguity: None | float
    ranging_biases: MosaDictFloat

    mosa_angles: MosaDictFloat
    ttl_coeffs_local_phis: MosaDictFloat
    ttl_coeffs_distant_phis: MosaDictFloat
    ttl_coeffs_local_etas: MosaDictFloat
    ttl_coeffs_distant_etas: MosaDictFloat

    electro_delays_scis: MosaDictFloat
    electro_delays_tmis: MosaDictFloat
    electro_delays_refs: MosaDictFloat

    @property
    def physics_size(self) -> int:
        """Number of samples to create for regular data send to earth"""
        return self.size * self.physics_upsampling

    @property
    def physics_dt(self) -> float:
        """Sampling period for quantities representing continuous physical signals"""
        return self.dt / self.physics_upsampling

    @property
    def physics_fs(self) -> float:
        """Sampling rate for quantities representing continuous physical signals"""
        return 1 / self.physics_dt

    @property
    def fs(self) -> float:
        """Sampling rate for regular data send to earth by the actual instrument"""
        return 1 / self.dt

    @property
    def telemetry_dt(self) -> float:
        """Sampling rate for telemetry data"""
        return self.dt * self.telemetry_downsampling

    @property
    def telemetry_to_physics_dt(self) -> int:
        """Ratio of sampling rates for physics and telemetry"""
        return self.telemetry_downsampling * self.physics_upsampling

    @property
    def telemetry_size(self) -> int:
        """Number of samples in telemetry data"""
        return (
            self.initial_telemetry_size
            + 1
            + int(math.ceil(self.size / self.telemetry_downsampling))
        )

    @property
    def physics_size_covering_telemetry(self) -> int:
        """Number of samples at pysics rate when also covering initial telemetry samples"""
        return self.telemetry_size * self.telemetry_to_physics_dt


class ModelConstellation:  # pylint: disable = too-few-public-methods
    """Represents constellation physical model as network of streams

    This class is the core of the simulator, responsible for defining how all
    timeseries are computed from each other. To this end, a network of streams
    is assembled. The actual evaluation of those streams happens elsewhere,
    the scope of this class is to return a StreamBundle representing the model.
    """

    # pylint: disable=attribute-defined-outside-init
    def __init__(
        self,
        noises: InstruNoises,
        orbitsrc: OrbitSource,
        fplansrc: dict[str, FuncOfTimeTypes],
        gwsrc: GWSource,
        glitchsrc: GlitchSource,
        tdirmod: dict[str, Callable | None],
        delays: InstruDelays,
        aafilter: Callable[[StreamBase], StreamBase],
        cfg: ModelConstellationCfg,
    ) -> None:
        self.noises: Final = noises
        self.orbit_source: Final = orbitsrc
        self.fplansrc: Final = fplansrc
        self.gwsrc: Final = gwsrc
        self.glitchsrc: Final = glitchsrc
        self.tdir_modulations: Final = tdirmod
        self.delays: Final = delays
        self.aafilter: Final = aafilter
        self.config: Final = cfg

        self._assemble_all()

    def _assemble_all(self) -> None:
        """Build physical model of instrument as interrelated streams

        This sets up streams for all intermediate and final results. Nothing is actually
        computed here, computations will be triggered when evaluating a selection of the
        streams for storage.
        """

        logger.info("Assembling constellation model")

        self._assemble_time_samples()
        self._assemble_orbits()
        self._assemble_gw()
        self._assemble_glitches()
        self._assemble_freq_plan()

        self._simulate_noises()

        self._assemble_moc_time_correlations()
        self._assemble_tdir_modulation()

        self._assemble_locking()

        self._assemble_sidebands()
        self._assemble_scet_distant()
        self._assemble_propagation_adjacent()
        self._assemble_sci_local_beams()
        self._assemble_sci_beatnotes()
        self._assemble_dws_tps()
        self._assemble_pseudo_ranging_tps()
        self._assemble_tmi_local_beams()
        self._assemble_tmi_adjacent_beams()
        self._assemble_tmi_beatnotes()
        self._assemble_ref_local_beams()
        self._assemble_ref_adjacent_beams()
        self._assemble_ref_beatnotes()
        self._assemble_scet_resampling()
        self._assemble_electro_delays()
        self._assemble_antialiasing()
        self._assemble_downsampling()
        self._assemble_total_freqs()

    def _assemble_time_samples(self) -> None:
        """Assemble streams for time samples"""
        cfg = self.config

        self.physics_et = timestamp_stream(dt=cfg.physics_dt, t0=0.0)
        self.physics_et.set_description("Elapsed time at physics sample rate")

        self.physics_t = timestamp_stream(dt=cfg.physics_dt, t0=cfg.t0)
        self.physics_t.set_description("Time at physics sample rate")

        # Time grids that only differed in range and are the same now
        # that they are infinite streams instead arrays:
        # self.physics_et_covering_telemetry == self.physics_et
        # self.physics_t_covering_telemetry == self.physics_t

        # Time streams self.t and self.telemetry_t not used anywhere explicitly
        #
        # self.t = timestamp_stream(dt=self.dt, t0=self.t0)
        # self.t.set_description("Time at normal sample rate")
        # self.telemetry_t = timestamp_stream(dt=self.telemetry_dt, t0=self.t0)
        # self.telemetry_t.set_description("Time at telemetry sample rate")

    def _assemble_gw(self) -> None:
        """Assemble stream for GW response"""
        self.gws = self._sample_func_mosas(self.gwsrc.link_gw, self.physics_t)
        describe_streams_dict(self.gws, "GW [MOSA_%s]")

    def _assemble_freq_plan(self) -> None:
        """Assemble stream for frequency plan"""
        self.fplan_ts = {
            mosa: stream_func_of_time(self.fplansrc[mosa])(self.physics_t)
            for mosa in MosaID.names()
        }
        describe_streams_dict(self.fplan_ts, "Frequency plan [MOSA_%s]")

    def _assemble_moc_time_correlations(self) -> None:
        """Assemble streams for MOC time correlations"""
        cfg = self.config

        self.scet_wrt_tps_local = compute.scet_wrt_tps_local(
            self.physics_et,
            self.integrated_clock_noise_fluctuations,
            clock_offsets=cfg.clock_offsets,
            clock_freqoffsets=cfg.clock_freqoffsets,
            clock_freqlindrifts=cfg.clock_freqlindrifts,
            clock_freqquaddrifts=cfg.clock_freqquaddrifts,
        )

        describe_streams_dict(
            self.scet_wrt_tps_local, "local SCET with respect to TPS [SC_%s]"
        )

        self.scet_wrt_tcb_withinitial = compute.scet_wrt_tcb_withinitial(
            self.physics_et,
            self.tps_wrt_tcb,
            self.clock_noise_fluctuations_covering_telemetry,
            self.integrated_clock_noise_fluctuations_covering_telemetry,
            clock_offsets=cfg.clock_offsets,
            clock_freqoffsets=cfg.clock_freqoffsets,
            clock_freqlindrifts=cfg.clock_freqlindrifts,
            clock_freqquaddrifts=cfg.clock_freqquaddrifts,
        )

        describe_streams_dict(
            self.scet_wrt_tcb_withinitial,
            "SCET with respect to TCB at physics rate [SC_%s]",
        )

        downsample_physics_to_telem = stream_downsample(
            ratio=cfg.telemetry_to_physics_dt, offset=0
        )

        scet_wrt_tcb_telemetry = {
            sc: downsample_physics_to_telem(self.scet_wrt_tcb_withinitial[sc])
            for sc in SatID.names()
        }
        describe_streams_dict(
            scet_wrt_tcb_telemetry, "SCET with respect to TCB at telemetry rate [SC_%s]"
        )

        self.moc_time_correlations = compute.moc_time_correlations(
            self.moc_time_correlation_noises, scet_wrt_tcb_telemetry
        )
        describe_streams_dict(
            self.moc_time_correlations, "MOC time correlations [SC_%s]"
        )

    def _assemble_tdir_modulation(self) -> None:
        """Assemble streams for TDIR modulations"""

        self.tdir_modulations_tseries = {
            mosa.value: compute.tdir_modulations_tseries(
                self.physics_et,
                self.scet_wrt_tps_local[mosa.sat.value],
                tdir_modulations=self.tdir_modulations[mosa.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.tdir_modulations_tseries, "TDIR assistance modulations [MOSA_%s]"
        )

    def _assemble_sidebands(self) -> None:
        """Assemble streams for sidebands"""
        cfg = self.config

        self.local_usb_offsets = {
            mosa.value: compute.local_usb_offsets(
                self.local_carrier_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                modulation_freqs=cfg.modulation_freqs[mosa.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.local_usb_offsets,
            "upper sideband offsets for primary local beam [MOSA_%s]",
        )

        self.local_usb_fluctuations = {
            mosa.value: compute.local_usb_fluctuations(
                self.local_carrier_fluctuations[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
                self.modulation_noises[mosa.value],
                modulation_freqs=cfg.modulation_freqs[mosa.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.local_usb_fluctuations,
            "upper sideband fluctuations for primary local beam [MOSA_%s]",
        )

        delayed_distant_usb_offsets = {
            mosa.value: self.delays.delay_isc(
                self.local_usb_offsets[mosa.distant.value], self.pprs[mosa.value]
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            delayed_distant_usb_offsets,
            "upper sideband offsets delayed to distant MOSAs [MOSA_%s]",
        )

        self.distant_usb_offsets = compute.distant_usb_offsets(
            self.d_pprs,
            delayed_distant_usb_offsets,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.distant_usb_offsets,
            "propagating upper sideband offsets to distant MOSA [MOSA_%s]",
        )

        usb_fluctuations = compute.usb_fluctuations(
            self.local_usb_fluctuations,
            self.local_usb_offsets,
            self.distant_ttls,
            self.mosa_jitter_xs,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(usb_fluctuations, "computing usb fluctuations [MOSA_%s]")

        delayed_distant_usb_fluctuations = {
            mosa.value: self.delays.delay_isc(
                usb_fluctuations[mosa.distant.value], self.pprs[mosa.value]
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            delayed_distant_usb_fluctuations,
            "upper sideband fluctuations delayed to distant MOSA [MOSA_%s]",
        )

        propagated_usb_fluctuations = compute.propagated_usb_fluctuations(
            self.d_pprs, delayed_distant_usb_fluctuations
        )
        describe_streams_dict(
            propagated_usb_fluctuations, "compute propagated_usb_fluctuations [MOSA_%s]"
        )

        self.distant_usb_fluctuations = compute.distant_usb_fluctuations(
            propagated_usb_fluctuations,
            delayed_distant_usb_offsets,
            self.gws,
            self.local_ttls,
            self.mosa_jitter_xs,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.distant_usb_fluctuations, "compute distant_usb_fluctuations [MOSA_%s]"
        )

    def _assemble_scet_distant(self) -> None:
        """Assemble streams for SCET w.r.t. distant TPS"""

        delayed_distant_scet_wrt_tps = {
            mosa.value: (
                self.delays.delay_isc(
                    self.scet_wrt_tps_local[mosa.distant.sat.value],
                    self.pprs[mosa.value],
                )
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            delayed_distant_scet_wrt_tps,
            "local SCETs with respect to TPS delayed to distant MOSAs [MOSA_%s]",
        )

        self.scet_wrt_tps_distant = compute.scet_wrt_tps_distant(
            delayed_distant_scet_wrt_tps, self.pprs
        )
        describe_streams_dict(
            self.scet_wrt_tps_distant, "compute scet_wrt_tps_distant [MOSA_%s]"
        )

    def _assemble_propagation_adjacent(self) -> None:
        """Assemble streams for propagation to adjacent MOSA

        Note adjacent carrier and usb offsets just refer to the corresponding streams
        under a different name (hence we cannot set stream description).
        """
        cfg = self.config

        self.adjacent_carrier_offsets = {
            mosa.value: (self.local_carrier_offsets[mosa.adjacent.value])
            for mosa in MosaID
        }

        self.adjacent_usb_offsets = {
            mosa.value: (self.local_usb_offsets[mosa.adjacent.value]) for mosa in MosaID
        }

        self.adjacent_usb_fluctuations = {
            mosa.value: compute.adjacent_usb_fluctuations(
                self.local_usb_fluctuations[mosa.adjacent.value],
                self.backlink_noises[mosa.value],
                central_freq=cfg.central_freq,
            )
            for mosa in MosaID
        }

        describe_streams_dict(
            self.adjacent_usb_fluctuations,
            "propagating upper sideband fluctuations to adjacent MOSA [MOSA_%s]",
        )

    def _assemble_sci_local_beams(self) -> None:
        """Assemble streams for inter-spacecraft interferometer local beams

        This just creates alias names. Note: we cannot set a new stream description
        as it would overwrite the previous description for the same stream.
        """

        # Propagating local carrier offsets to inter-spacecraft interferometer
        self.local_sci_carrier_offsets = self.local_carrier_offsets

        # Propagating local carrier fluctuations to inter-spacecraft interferometer
        self.local_sci_carrier_fluctuations = self.local_carrier_fluctuations

        # Propagating local upper sideband offsets to inter-spacecraft interferometer
        self.local_sci_usb_offsets = self.local_usb_offsets

        # Propagating local upper sideband fluctuations to inter-spacecraft interferometer
        self.local_sci_usb_fluctuations = self.local_usb_fluctuations

        # Inter-spacecraft interferometer distant beams

        # Propagating distant carrier offsets to inter-spacecraft interferometer
        self.distant_sci_carrier_offsets = self.distant_carrier_offsets

        # Propagating distant carrier fluctuations to inter-spacecraft interferometer
        self.distant_sci_carrier_fluctuations = self.distant_carrier_fluctuations

        # Propagating distant upper sideband offsets to inter-spacecraft interferometer
        self.distant_sci_usb_offsets = self.distant_usb_offsets

        # Propagating distant upper sideband fluctuations to inter-spacecraft interferometer
        self.distant_sci_usb_fluctuations = self.distant_usb_fluctuations

    def _assemble_sci_beatnotes(self) -> None:
        """Assemble streams for inter-spacecraft interferometer beatnotes on TPS"""
        cfg = self.config

        self.tps_sci_carrier_offsets = compute.tps_sci_carrier_offsets(
            self.distant_sci_carrier_offsets,
            self.local_sci_carrier_offsets,
        )
        describe_streams_dict(
            self.tps_sci_carrier_offsets,
            "computing inter-spacecraft carrier beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_sci_carrier_fluctuations = compute.tps_sci_carrier_fluctuations(
            self.distant_sci_carrier_fluctuations,
            self.local_sci_carrier_fluctuations,
            self.oms_sci_carrier_noises,
            self.glitch_readout_sci_carriers,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_sci_carrier_fluctuations,
            "computing inter-spacecraft carrier beatnote fluctuations on TPS [MOSA_%s]",
        )

        self.tps_sci_usb_offsets = compute.tps_sci_usb_offsets(
            self.distant_sci_usb_offsets, self.local_sci_usb_offsets
        )
        describe_streams_dict(
            self.tps_sci_usb_offsets,
            "computing inter-spacecraft upper sideband beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_sci_usb_fluctuations = compute.tps_sci_usb_fluctuations(
            self.distant_sci_usb_fluctuations,
            self.local_sci_usb_fluctuations,
            self.oms_sci_usb_noises,
            self.glitch_readout_sci_usbs,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_sci_usb_fluctuations,
            "computing inter-spacecraft upper sideband beatnote fluctuations on TPS [MOSA_%s]",
        )

    def _assemble_dws_tps(self) -> None:
        """Assemble streams for inter-spacecraft DWS measurements on TPS"""

        self.tps_sci_dws_phis = compute.tps_sci_dws_phis(
            self.mosa_total_jitter_phis, self.dws_phi_noises
        )
        describe_streams_dict(
            self.tps_sci_dws_phis, "compute tps_sci_dws_phis [MOSA_%s]"
        )

        self.tps_sci_dws_etas = compute.tps_sci_dws_etas(
            self.mosa_total_jitter_etas, self.dws_eta_noises
        )
        describe_streams_dict(
            self.tps_sci_dws_etas, "compute tps_sci_dws_etas [MOSA_%s]"
        )

    def _assemble_pseudo_ranging_tps(self) -> None:
        """Assemble streams for measured pseudo-ranging on TPS grid"""

        self.tps_mprs = {
            mosa.value: compute.tps_mprs(
                self.scet_wrt_tps_local[mosa.sat.value],
                self.scet_wrt_tps_distant[mosa.value],
                self.ranging_noises[mosa.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.tps_mprs, "computing measured pseudo-ranges on TPS [MOSA_%s]"
        )

    def _assemble_tmi_local_beams(self) -> None:
        """Assemble test-mass interferometer local beams"""
        cfg = self.config

        # Propagating local carrier offsets to test-mass interferometer
        self.local_tmi_carrier_offsets = self.local_carrier_offsets

        self.local_tmi_carrier_fluctuations = compute.local_tmi_carrier_fluctuations(
            self.local_carrier_fluctuations,
            self.local_tmi_carrier_offsets,
            self.mosa_jitter_xs,
            self.testmass_noises,
            self.glitch_tms,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.local_tmi_carrier_fluctuations,
            "propagating local carrier fluctuations to test-mass interferometer [MOSA_%s]",
        )

        # Propagating local upper sideband offsets to test-mass interferometer
        self.local_tmi_usb_offsets = self.local_usb_offsets

        self.local_tmi_usb_fluctuations = compute.local_tmi_usb_fluctuations(
            self.local_usb_fluctuations,
            self.local_tmi_usb_offsets,
            self.mosa_jitter_xs,
            self.testmass_noises,
            self.glitch_tms,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.local_tmi_usb_fluctuations,
            "propagating local upper sideband fluctuations to test-mass interferometer [MOSA_%s]",
        )

    def _assemble_tmi_adjacent_beams(self) -> None:
        """Assemble streams for test-mass interferometer adjacent beams

        This just creates alias names. Note: we cannot set a new stream description
        as it would overwrite the previous description for the same stream.
        """

        # Propagating adjacent carrier offsets to test-mass interferometer"
        self.adjacent_tmi_carrier_offsets = self.adjacent_carrier_offsets

        # Propagating adjacent carrier fluctuations to test-mass interferometer
        self.adjacent_tmi_carrier_fluctuations = self.adjacent_carrier_fluctuations

        # Propagating adjacent upper sideband offsets to test-mass interferometer
        self.adjacent_tmi_usb_offsets = self.adjacent_usb_offsets

        # Propagating adjacent upper sideband fluctuations to test-mass interferometer
        self.adjacent_tmi_usb_fluctuations = self.adjacent_usb_fluctuations

    def _assemble_tmi_beatnotes(self) -> None:
        """Assemble streams for test-mass interferometer beatnotes on TPS (high-frequency)"""
        cfg = self.config

        self.tps_tmi_carrier_offsets = compute.tps_tmi_carrier_offsets(
            self.adjacent_tmi_carrier_offsets,
            self.local_tmi_carrier_offsets,
        )
        describe_streams_dict(
            self.tps_tmi_carrier_offsets,
            "Computing test-mass carrier beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_tmi_carrier_fluctuations = compute.tps_tmi_carrier_fluctuations(
            self.adjacent_tmi_carrier_fluctuations,
            self.local_tmi_carrier_fluctuations,
            self.oms_tmi_carrier_noises,
            self.glitch_readout_tmi_carriers,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_tmi_carrier_fluctuations,
            "Computing test-mass carrier beatnote fluctuations on TPS [MOSA_%s]",
        )

        self.tps_tmi_usb_offsets = compute.tps_tmi_usb_offsets(
            self.adjacent_tmi_usb_offsets, self.local_tmi_usb_offsets
        )
        describe_streams_dict(
            self.tps_tmi_usb_offsets,
            "Computing test-mass upper sideband beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_tmi_usb_fluctuations = compute.tps_tmi_usb_fluctuations(
            self.adjacent_tmi_usb_fluctuations,
            self.local_tmi_usb_fluctuations,
            self.oms_tmi_usb_noises,
            self.glitch_readout_tmi_usbs,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_tmi_usb_fluctuations,
            "Computing test-mass upper sideband beatnote fluctuations on TPS [MOSA_%s]",
        )

    def _assemble_ref_local_beams(self) -> None:
        """Assemble streams for reference interferometer local beams

        This just creates alias names. Note: we cannot set a new stream description
        as it would overwrite the previous description for the same stream.
        """

        # Propagating local carrier offsets to reference interferometer
        self.local_ref_carrier_offsets = self.local_carrier_offsets

        # Propagating local carrier fluctuations to reference interferometer
        self.local_ref_carrier_fluctuations = self.local_carrier_fluctuations

        # Propagating local upper sideband offsets to reference interferometer
        self.local_ref_usb_offsets = self.local_usb_offsets

        # Propagating local upper sideband fluctuations to reference interferometer
        self.local_ref_usb_fluctuations = self.local_usb_fluctuations

    def _assemble_ref_adjacent_beams(self) -> None:
        """Assemble streams for reference interferometer adjacent beams

        This just creates alias names. Note: we cannot set a new stream description
        as it would overwrite the previous description for the same stream.
        """

        # Propagating adjacent carrier offsets to reference interferometer
        self.adjacent_ref_carrier_offsets = self.adjacent_carrier_offsets

        # Propagating adjacent carrier fluctuations to reference interferometer
        self.adjacent_ref_carrier_fluctuations = self.adjacent_carrier_fluctuations

        # Propagating adjacent upper sideband offsets to reference interferometer
        self.adjacent_ref_usb_offsets = self.adjacent_usb_offsets

        # Propagating adjacent upper sideband fluctuations to reference interferometer
        self.adjacent_ref_usb_fluctuations = self.adjacent_usb_fluctuations

    def _assemble_ref_beatnotes(self) -> None:
        """Assemble streams for reference interferometer beatnotes on TPS (high-frequency)"""
        cfg = self.config

        self.tps_ref_carrier_offsets = compute.tps_ref_carrier_offsets(
            self.adjacent_ref_carrier_offsets,
            self.local_ref_carrier_offsets,
        )
        describe_streams_dict(
            self.tps_ref_carrier_offsets,
            "Computing reference carrier beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_ref_carrier_fluctuations = compute.tps_ref_carrier_fluctuations(
            self.adjacent_ref_carrier_fluctuations,
            self.local_ref_carrier_fluctuations,
            self.oms_ref_carrier_noises,
            self.glitch_readout_ref_carriers,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_ref_carrier_fluctuations,
            "Computing reference carrier beatnote fluctuations on TPS [MOSA_%s]",
        )

        self.tps_ref_usb_offsets = compute.tps_ref_usb_offsets(
            self.adjacent_ref_usb_offsets, self.local_ref_usb_offsets
        )
        describe_streams_dict(
            self.tps_ref_usb_offsets,
            "Computing reference upper sideband beatnote offsets on TPS [MOSA_%s]",
        )

        self.tps_ref_usb_fluctuations = compute.tps_ref_usb_fluctuations(
            self.adjacent_ref_usb_fluctuations,
            self.local_ref_usb_fluctuations,
            self.oms_ref_usb_noises,
            self.glitch_readout_ref_usbs,
            central_freq=cfg.central_freq,
        )
        describe_streams_dict(
            self.tps_ref_usb_fluctuations,
            "Computing reference upper sideband beatnote fluctuations on TPS [MOSA_%s]",
        )

    def _assemble_scet_resampling(self) -> None:
        """Assemble streams for resampling to SCET time grid

        This includes sampling beatnotes, DWS measurements, and measured pseudo-ranges
        """

        self.tps_wrt_scet = {
            sc: self._invert_scet_wrt_tps(self.scet_wrt_tps_local[sc])
            for sc in SatID.names()
        }
        describe_streams_dict(
            self.tps_wrt_scet, "Inverting SCET with respect to TPS [SC_%s]"
        )

        def timestamped(x):
            return {
                mosa.value: self.delays.delay_clock(
                    x[mosa.value], self.tps_wrt_scet[mosa.sat.value]
                )
                for mosa in MosaID
            }

        scet_sci_carrier_offsets_preshift = {
            mosa.value: compute.scet_sci_carrier_offsets_preshift(
                self.tps_sci_carrier_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_sci_carrier_offsets_preshift,
            "compute scet_sci_carrier_offsets_preshift [MOSA_%s]",
        )

        self.scet_sci_carrier_offsets = timestamped(scet_sci_carrier_offsets_preshift)
        describe_streams_dict(
            self.scet_sci_carrier_offsets,
            "Sampling inter-spacecraft carrier beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        scet_sci_carrier_fluctuations_preshift = {
            mosa.value: compute.scet_sci_carrier_fluctuations_preshift(
                self.tps_sci_carrier_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_sci_carrier_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_sci_carrier_fluctuations_preshift,
            "compute scet_sci_carrier_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_sci_carrier_fluctuations = timestamped(
            scet_sci_carrier_fluctuations_preshift
        )
        describe_streams_dict(
            self.scet_sci_carrier_fluctuations,
            "Sampling inter-spacecraft carrier beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        scet_sci_usb_offsets_preshift = {
            mosa.value: compute.scet_sci_usb_offsets_preshift(
                self.tps_sci_usb_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_sci_usb_offsets_preshift,
            "compute.scet_sci_usb_offsets_preshift [MOSA_%s]",
        )

        self.scet_sci_usb_offsets = timestamped(scet_sci_usb_offsets_preshift)
        describe_streams_dict(
            self.scet_sci_usb_offsets,
            "Sampling inter-spacecraft upper sideband beatnote offsets to SCET grid [MOSA_%s]",
        )

        scet_sci_usb_fluctuations_preshift = {
            mosa.value: compute.scet_sci_usb_fluctuations_preshift(
                self.tps_sci_usb_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_sci_usb_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_sci_usb_fluctuations_preshift,
            "compute scet_sci_usb_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_sci_usb_fluctuations = timestamped(scet_sci_usb_fluctuations_preshift)
        describe_streams_dict(
            self.scet_sci_usb_fluctuations,
            "Sampling inter-spacecraft upper sideband beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        self.scet_sci_dws_phis = timestamped(self.tps_sci_dws_phis)
        describe_streams_dict(
            self.scet_sci_dws_phis,
            "Sampling inter-spacecraft DWS phi-measurements to SCET grid [MOSA_%s]",
        )

        self.scet_sci_dws_etas = timestamped(self.tps_sci_dws_etas)
        describe_streams_dict(
            self.scet_sci_dws_phis,
            "Sampling inter-spacecraft DWS eta-measurements to SCET grid [MOSA_%s]",
        )

        self.scet_mprs = timestamped(self.tps_mprs)
        describe_streams_dict(
            self.scet_mprs, "Sampling measured pseudo-ranges to SCET grid [MOSA_%s]"
        )

        scet_tmi_carrier_offsets_preshift = {
            mosa.value: compute.scet_tmi_carrier_offsets_preshift(
                self.tps_tmi_carrier_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_tmi_carrier_offsets_preshift,
            "compute scet_tmi_carrier_offsets_preshift [MOSA_%s]",
        )

        self.scet_tmi_carrier_offsets = timestamped(scet_tmi_carrier_offsets_preshift)
        describe_streams_dict(
            self.scet_tmi_carrier_offsets,
            "Sampling test-mass carrier beatnote offsets to SCET grid [MOSA_%s]",
        )

        scet_tmi_carrier_fluctuations_preshift = {
            mosa.value: compute.scet_tmi_carrier_fluctuations_preshift(
                self.tps_tmi_carrier_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_tmi_carrier_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_tmi_carrier_fluctuations_preshift,
            "compute scet_tmi_carrier_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_tmi_carrier_fluctuations = timestamped(
            scet_tmi_carrier_fluctuations_preshift
        )
        describe_streams_dict(
            self.scet_tmi_carrier_fluctuations,
            "Sampling test-mass carrier beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        scet_tmi_usb_offsets_preshift = {
            mosa.value: compute.scet_tmi_usb_offsets_preshift(
                self.tps_tmi_usb_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_tmi_usb_offsets_preshift,
            "compute.scet_tmi_usb_offsets_preshift [MOSA_%s]",
        )

        self.scet_tmi_usb_offsets = timestamped(scet_tmi_usb_offsets_preshift)
        describe_streams_dict(
            self.scet_tmi_usb_offsets,
            "Sampling test-mass upper sideband beatnote offsets to SCET grid [MOSA_%s]",
        )

        scet_tmi_usb_fluctuations_preshift = {
            mosa.value: compute.scet_tmi_usb_fluctuations_preshift(
                self.tps_tmi_usb_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_tmi_usb_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_tmi_usb_fluctuations_preshift,
            "compute scet_tmi_usb_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_tmi_usb_fluctuations = timestamped(scet_tmi_usb_fluctuations_preshift)
        describe_streams_dict(
            self.scet_tmi_usb_fluctuations,
            "Sampling test-mass upper sideband beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        scet_ref_carrier_offsets_preshift = {
            mosa.value: compute.scet_ref_carrier_offsets_preshift(
                self.tps_ref_carrier_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_ref_carrier_offsets_preshift,
            "compute.scet_ref_carrier_offsets_preshift [MOSA_%s]",
        )

        self.scet_ref_carrier_offsets = timestamped(scet_ref_carrier_offsets_preshift)
        describe_streams_dict(
            self.scet_ref_carrier_offsets,
            "Sampling reference carrier beatnote offsets to SCET grid [MOSA_%s]",
        )

        scet_ref_carrier_fluctuations_preshift = {
            mosa.value: compute.scet_ref_carrier_fluctuations_preshift(
                self.tps_ref_carrier_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_ref_carrier_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_ref_carrier_fluctuations_preshift,
            "compute.scet_ref_carrier_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_ref_carrier_fluctuations = timestamped(
            scet_ref_carrier_fluctuations_preshift
        )
        describe_streams_dict(
            self.scet_ref_carrier_fluctuations,
            "Sampling reference carrier beatnote fluctuations to SCET grid [MOSA_%s]",
        )

        scet_ref_usb_offsets_preshift = {
            mosa.value: compute.scet_ref_usb_offsets_preshift(
                self.tps_ref_usb_offsets[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_ref_usb_offsets_preshift,
            "compute scet_ref_usb_offsets_preshift [MOSA_%s]",
        )

        self.scet_ref_usb_offsets = timestamped(scet_ref_usb_offsets_preshift)
        describe_streams_dict(
            self.scet_ref_usb_offsets,
            "Sampling reference upper sideband beatnote offsets to SCET grid [MOSA_%s]",
        )

        scet_ref_usb_fluctuations_preshift = {
            mosa.value: compute.scet_ref_usb_fluctuations_preshift(
                self.tps_ref_usb_fluctuations[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
                self.tps_ref_usb_offsets[mosa.value],
                self.clock_noise_fluctuations[mosa.sat.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            scet_ref_usb_fluctuations_preshift,
            "compute scet_ref_usb_fluctuations_preshift [MOSA_%s]",
        )

        self.scet_ref_usb_fluctuations = timestamped(scet_ref_usb_fluctuations_preshift)
        describe_streams_dict(
            self.scet_ref_usb_fluctuations,
            "Sampling reference upper sideband beatnote fluctuations to SCET grid [MOSA_%s]",
        )

    def _assemble_electro_delays(self) -> None:
        """Assemble streams for electronic delays"""
        cfg = self.config

        @for_each_mosa
        def electro_delay(x: StreamBase, delay: float):
            """Apply electronics delay"""
            ds = self.delays.delay_electro(x, StreamConst(delay))
            if not ((ds is x) or (x.description is None)):
                ds.set_description(f"{x.description} with electro delay")
            return ds

        self.electro_sci_carrier_offsets = electro_delay(
            self.scet_sci_carrier_offsets, cfg.electro_delays_scis
        )

        self.electro_sci_carrier_fluctuations = electro_delay(
            self.scet_sci_carrier_fluctuations, cfg.electro_delays_scis
        )

        self.electro_sci_usb_offsets = electro_delay(
            self.scet_sci_usb_offsets, cfg.electro_delays_scis
        )

        self.electro_sci_usb_fluctuations = electro_delay(
            self.scet_sci_usb_fluctuations, cfg.electro_delays_scis
        )

        self.electro_tmi_carrier_offsets = electro_delay(
            self.scet_tmi_carrier_offsets, cfg.electro_delays_tmis
        )

        self.electro_tmi_carrier_fluctuations = electro_delay(
            self.scet_tmi_carrier_fluctuations, cfg.electro_delays_tmis
        )

        self.electro_tmi_usb_offsets = electro_delay(
            self.scet_tmi_usb_offsets, cfg.electro_delays_tmis
        )

        self.electro_tmi_usb_fluctuations = electro_delay(
            self.scet_tmi_usb_fluctuations, cfg.electro_delays_tmis
        )

        self.electro_ref_carrier_offsets = electro_delay(
            self.scet_ref_carrier_offsets, cfg.electro_delays_refs
        )

        self.electro_ref_carrier_fluctuations = electro_delay(
            self.scet_ref_carrier_fluctuations, cfg.electro_delays_refs
        )

        self.electro_ref_usb_offsets = electro_delay(
            self.scet_ref_usb_offsets, cfg.electro_delays_refs
        )

        self.electro_ref_usb_fluctuations = electro_delay(
            self.scet_ref_usb_fluctuations, cfg.electro_delays_refs
        )

    def _assemble_antialiasing(self) -> None:
        """Assemble streams for Antialiasing filtering"""

        @for_each_mosa
        def aafilter_mosas(x: StreamBase) -> StreamBase:
            ds = self.aafilter(x)
            if not ((ds is x) or (x.description is None)):
                ds.set_description(f"AA-filter {x.description}")
            return ds

        self.filtered_sci_carrier_offsets = aafilter_mosas(
            self.electro_sci_carrier_offsets
        )
        self.filtered_sci_carrier_fluctuations = aafilter_mosas(
            self.electro_sci_carrier_fluctuations
        )
        self.filtered_sci_usb_offsets = aafilter_mosas(self.electro_sci_usb_offsets)
        self.filtered_sci_usb_fluctuations = aafilter_mosas(
            self.electro_sci_usb_fluctuations
        )

        self.filtered_sci_dws_phis = aafilter_mosas(self.scet_sci_dws_phis)
        self.filtered_sci_dws_etas = aafilter_mosas(self.scet_sci_dws_etas)

        self.filtered_mprs = aafilter_mosas(self.scet_mprs)

        self.filtered_tmi_carrier_offsets = aafilter_mosas(
            self.electro_tmi_carrier_offsets
        )
        self.filtered_tmi_carrier_fluctuations = aafilter_mosas(
            self.electro_tmi_carrier_fluctuations
        )
        self.filtered_tmi_usb_offsets = aafilter_mosas(self.electro_tmi_usb_offsets)
        self.filtered_tmi_usb_fluctuations = aafilter_mosas(
            self.electro_tmi_usb_fluctuations
        )

        self.filtered_ref_carrier_offsets = aafilter_mosas(
            self.electro_ref_carrier_offsets
        )
        self.filtered_ref_carrier_fluctuations = aafilter_mosas(
            self.electro_ref_carrier_fluctuations
        )
        self.filtered_ref_usb_offsets = aafilter_mosas(self.electro_ref_usb_offsets)
        self.filtered_ref_usb_fluctuations = aafilter_mosas(
            self.electro_ref_usb_fluctuations
        )

    def _assemble_downsampling(self) -> None:
        """Assemble streams for Downsampling"""
        cfg = self.config

        @for_each_mosa
        def downsample_mosas(x: StreamBase) -> StreamBase:
            ds = stream_downsample(cfg.physics_upsampling, 0)(x)
            if not ((ds is x) or (x.description is None)):
                ds.set_description(f"Downsampled {x.description}")
            return ds

        self.sci_carrier_offsets = downsample_mosas(self.filtered_sci_carrier_offsets)
        self.sci_carrier_fluctuations = downsample_mosas(
            self.filtered_sci_carrier_fluctuations
        )
        self.sci_usb_offsets = downsample_mosas(self.filtered_sci_usb_offsets)
        self.sci_usb_fluctuations = downsample_mosas(self.filtered_sci_usb_fluctuations)

        self.sci_dws_phis = downsample_mosas(self.filtered_sci_dws_phis)
        self.sci_dws_etas = downsample_mosas(self.filtered_sci_dws_etas)

        self.mprs_unambiguous = downsample_mosas(self.filtered_mprs)

        self.mprs = compute.mprs(self.mprs_unambiguous, prn_ambiguity=cfg.prn_ambiguity)
        describe_streams_dict(self.mprs, "compute mprs [MOSA_%s]")

        self.tmi_carrier_offsets = downsample_mosas(self.filtered_tmi_carrier_offsets)
        self.tmi_carrier_fluctuations = downsample_mosas(
            self.filtered_tmi_carrier_fluctuations
        )
        self.tmi_usb_offsets = downsample_mosas(self.filtered_tmi_usb_offsets)
        self.tmi_usb_fluctuations = downsample_mosas(self.filtered_tmi_usb_fluctuations)

        self.ref_carrier_offsets = downsample_mosas(self.filtered_ref_carrier_offsets)
        self.ref_carrier_fluctuations = downsample_mosas(
            self.filtered_ref_carrier_fluctuations
        )
        self.ref_usb_offsets = downsample_mosas(self.filtered_ref_usb_offsets)
        self.ref_usb_fluctuations = downsample_mosas(self.filtered_ref_usb_fluctuations)

    def _assemble_total_freqs(self) -> None:
        """Assemble the streams for the total frequencies"""

        self.sci_carriers = compute.sci_carriers(
            self.sci_carrier_offsets, self.sci_carrier_fluctuations
        )
        describe_streams_dict(
            self.sci_carriers,
            "computing total inter-spacecraft carrier beatnotes [MOSA_%s]",
        )

        self.sci_usbs = compute.sci_usbs(
            self.sci_usb_offsets, self.sci_usb_fluctuations
        )
        describe_streams_dict(
            self.sci_usbs,
            "Computing total inter-spacecraft upper sideband beatnotes [MOSA_%s]",
        )

        self.tmi_carriers = compute.tmi_carriers(
            self.tmi_carrier_offsets, self.tmi_carrier_fluctuations
        )
        describe_streams_dict(
            self.tmi_carriers, "Computing total test-mass carrier beatnotes [MOSA_%s]"
        )

        self.tmi_usbs = compute.tmi_usbs(
            self.tmi_usb_offsets, self.tmi_usb_fluctuations
        )
        describe_streams_dict(
            self.tmi_usbs,
            "Computing total test-mass upper sideband beatnotes [MOSA_%s]",
        )

        self.ref_carriers = compute.ref_carriers(
            self.ref_carrier_offsets, self.ref_carrier_fluctuations
        )
        describe_streams_dict(
            self.ref_carriers, "Computing total reference carrier beatnotes [MOSA_%s]"
        )

        self.ref_usbs = compute.ref_usbs(
            self.ref_usb_offsets, self.ref_usb_fluctuations
        )
        describe_streams_dict(
            self.ref_usbs,
            "Computing total reference upper sideband beatnotes [MOSA_%s]",
        )

    def _invert_scet_wrt_tps(self, scet_wrt_tps: StreamBase) -> StreamBase:
        r"""Set up streams for Inverting SCET with respect to TPS of a given spacecraft.

        Denoting the spacecraft clock time by :math:`\hat{\tau}` and the spacecraft proper
        time by :math:`\tau`, we define the coordinate transformation
        :math:`\hat{\tau} = \hat{\tau}^{\tau} (\tau)` and express it in terms of a
        time shift defined as
        :math:`\delta \hat{\tau}^{\tau} (\tau) \equiv  \hat{\tau}^{\tau}(\tau) - \tau`.

        The time shift is provided to this method via samples :math:`\delta \hat{\tau}^{\tau} (\tau_k)`
        where the sample locations :math:`\tau_k` are regularly spaced with respect to
        spacecraft proper time, and a sampling rate given by self.physics_fs.
        The time shift is specified in [s], not in units of the sampling period.

        The method computes the time shift as function of the clock time,
        :math:`\delta \tau^{\hat{\tau}}(\hat{\tau}) \equiv \tau^{\hat{\tau}}(\hat{\tau}) - \hat{\tau}`.
        The shift is evaluated at sample locations :math:`\hat{\tau}_k` which are regularly spaced
        with respect to clock time, again with sample rate given by self.physics_fs.

        The start time for the sample locations is unspecified, but the result corresponds
        to a start time  :math:`\hat{\tau}_0 = \tau_0`. In other words, the numerical
        values of the input and output sample locations are equal, even though they refer to
        different time coordinates.

        The method returns the values :math:`-\delta \tau^{\hat{\tau}}(\hat{\tau}_k)`.
        Note the minus sign. The result can also be expressed as
        :math:`-\delta \tau^{\hat{\tau}}(\hat{\tau}_k) = \delta \hat{\tau}^\tau(\tau^\hat{\tau}(\hat{\tau}_k))`.
        In other words, it is the time shift scet_wrt_tps interpolated to sample locations
        that correspond to the regularly spaced clock time locations transformed into proper spacecraft
        time coordinate.

        The result is computed using an iterative method, which finishes when the estimated
        maximum absolute error of the result is below self.clockinv_tolerance. If this does
        not succeed after self.clockinv_maxiter steps, an exception is raised.

        See lisainstrument.shift_inversion_numpy.ShiftInverseNumpy for the details
        of the solution algorithm.

        Args:
            scet_wrt_tps: stream with time shifts of SCETs with respect to TPS,
                          :math:`\delta \hat{\tau}^{\tau} (\tau_k)`

        Returns:
            Stream with time shifts :math:`\delta \hat{\tau}^\tau(\tau^\hat{\tau}(\hat{\tau}_k))`
        """

        return self.delays.shift_inversion(scet_wrt_tps)

    @staticmethod
    def _sample_func_mosas(
        func: Callable[[MosaID], FuncOfTimeTypes],
        t: StreamTimeGrid,
    ) -> dict[str, StreamBase]:
        """Create dictionary with streams of sampled function for each MOSA

        Arguments:
            func: Function returning a function to be sampled for a given MOSA
            t: Stream with time coordinate

        Returns:
            Dictionary mapping mosa name to steam with sampled data
        """
        return {mosa.value: stream_func_of_time(func(mosa))(t) for mosa in MosaID}

    @staticmethod
    def _sample_func_sats(
        func: Callable[[SatID], FuncOfTimeTypes],
        t: StreamTimeGrid,
    ) -> dict[str, StreamBase]:
        """Create dictionary with streams of sampled function for each spacecraft

        Arguments:
            func: Function returning a function to be sampled for a given SC
            t: Stream with time coordinate

        Returns:
            Dictionary mapping spacecraft name to sampled data
        """
        return {sc.value: stream_func_of_time(func(sc))(t) for sc in SatID}

    def _assemble_orbits(self) -> None:
        """Init orbit related arrays from abstract orbit data interface

        Create streams that sample the Orbit source functions to the
        time stream self.physics_t.

        Arguments:
            orbsrc: The orbit as OrbitSource instance
        """
        orbsrc = self.orbit_source

        self.pprs = self._sample_func_mosas(orbsrc.pprs, self.physics_t)

        self.d_pprs: dict[str, StreamBase]
        if self.config.dopplers_disable:
            self.d_pprs = make_mosa_dict_const(StreamConst(0.0))
        else:
            self.d_pprs = self._sample_func_mosas(orbsrc.d_pprs, self.physics_t)

        self.tps_wrt_tcb = self._sample_func_sats(orbsrc.tps_wrt_tcb, self.physics_t)

    def _assemble_glitches(self) -> None:
        """Initialize glitch arrays from functions provided by a GlitchSource instance"""

        src = self.glitchsrc

        self.glitch_readout_sci_carriers = self._sample_func_mosas(
            src.readout_sci_carrier, self.physics_t
        )
        self.glitch_readout_sci_usbs = self._sample_func_mosas(
            src.readout_sci_usbs, self.physics_t
        )
        self.glitch_readout_tmi_carriers = self._sample_func_mosas(
            src.readout_tmi_carriers, self.physics_t
        )
        self.glitch_readout_tmi_usbs = self._sample_func_mosas(
            src.readout_tmi_usbs, self.physics_t
        )
        self.glitch_readout_ref_carriers = self._sample_func_mosas(
            src.readout_ref_carriers, self.physics_t
        )
        self.glitch_readout_ref_usbs = self._sample_func_mosas(
            src.readout_ref_usbs, self.physics_t
        )
        self.glitch_tms = self._sample_func_mosas(src.test_mass, self.physics_t)
        self.glitch_lasers = self._sample_func_mosas(src.lasers, self.physics_t)

    def get_streams(self) -> StreamBundle:
        """Collect and name output streams and specify desired index ranges"""
        bundle = StreamBundle()
        ranges = self.output_ranges()
        dspropm = SimFullDatasetsMOSA.dataset_metadata()
        for dsn in SimResultsNumpyFull.mosa_dataset_names:
            cat = dspropm[dsn]
            out_rg = ranges[cat.idxspace]
            streams = getattr(self, dsn)
            for mosa in MosaID.names():
                dsid = make_dataset_id(cat.actual, dsn, mosa)
                bundle.add(dsid, streams[mosa], out_rg)
        dsprops = SimFullDatasetsSat.dataset_metadata()
        for dsn in SimResultsNumpyFull.sat_dataset_names:
            cat = dsprops[dsn]
            out_rg = ranges[cat.idxspace]
            streams = getattr(self, dsn)
            for sc in SatID.names():
                dsid = make_dataset_id(cat.actual, dsn, sc)
                bundle.add(dsid, streams[sc], out_rg)

        return bundle

    def output_ranges(self) -> dict[IdxSpace, tuple[int, int]]:
        """Dictionary with index range for each index space"""
        cfg = self.config
        i0_phys_ext = -cfg.initial_telemetry_size * cfg.telemetry_to_physics_dt
        i1_phys_ext = i0_phys_ext + cfg.physics_size_covering_telemetry
        return {
            IdxSpace.REGULAR: (0, cfg.size),
            IdxSpace.PHYSICS: (0, cfg.physics_size),
            IdxSpace.PHYSICS_EXT: (i0_phys_ext, i1_phys_ext),
            IdxSpace.TELEMETRY: (
                -cfg.initial_telemetry_size,
                -cfg.initial_telemetry_size + cfg.telemetry_size,
            ),
        }

    def _generate_noise(self, ndef: NoiseDefBase) -> StreamBase:
        """Generate noise stream from noise definition

        Arguments:
            ndef: Definition of noise to generate samples from

        Returns:
            Stream with noise samples
        """
        logger.debug("Using noise parameters %s", str(ndef))
        s = stream_noise(ndef, self.noises.seed)
        s.set_description(f"Noise {ndef.name}")
        return s

    def _generate_noise_sats(
        self, ndef: Callable[[SatID], NoiseDefBase]
    ) -> dict[str, StreamBase]:
        """Generate noise streams for all spacecrafts

        Arguments:
            ndef: Callable mapping spacecraft index to noise definition

        Returns:
            dictionary mapping spacecraft index (as str) to noise stream
        """
        return {sc.value: self._generate_noise(ndef(sc)) for sc in SatID}

    def _generate_noise_mosas(
        self,
        ndef: Callable[[MosaID], NoiseDefBase],
    ) -> dict[str, StreamBase]:
        """Generate noise stream for all MOSAs

        Arguments:
            ndef: Callable mapping MOSA index to noise definition

        Returns:
            dictionary mapping MOSA index (as str) to noise stream
        """
        return {mosa.value: self._generate_noise(ndef(mosa)) for mosa in MosaID}

    def _simulate_noises(self) -> None:  # pylint: disable=too-many-statements
        """Create streams for noises.

        Arguments:
            noises: InstruNoise instance providing all noise definitions
        """
        noises = self.noises
        cfg = self.config
        ## Laser noise

        # Laser noises are computed in `_simulate_locking()`

        ## Clock noise

        self.clock_noise_offsets = compute.clock_noise_offsets(
            self.physics_et,
            freqoffsets=cfg.clock_freqoffsets,
            freqlindrifts=cfg.clock_freqlindrifts,
            freqquaddrifts=cfg.clock_freqquaddrifts,
        )
        describe_streams_dict(
            self.clock_noise_offsets, "compute clock_noise_offsets [SC_%s]"
        )

        self.clock_noise_fluctuations_covering_telemetry = self._generate_noise_sats(
            noises.noise_def_clock
        )
        # Alias named as in the HDF5 files
        self.clock_noise_fluctuations_withinitial = (
            self.clock_noise_fluctuations_covering_telemetry
        )
        self.clock_noise_fluctuations = self.clock_noise_fluctuations_covering_telemetry

        self.integrated_clock_noise_fluctuations_covering_telemetry = {
            sc.value: stream_int_trapz(cfg.physics_dt)(
                self.clock_noise_fluctuations_covering_telemetry[sc.value]
            )
            for sc in SatID
        }

        # Alias named as in the HDF5 files
        self.integrated_clock_noise_fluctuations_withinitial = (
            self.integrated_clock_noise_fluctuations_covering_telemetry
        )

        self.integrated_clock_noise_fluctuations = (
            self.integrated_clock_noise_fluctuations_covering_telemetry
        )

        describe_streams_dict(
            self.integrated_clock_noise_fluctuations,
            "Integrating clock noise fluctuations [SC_%s]",
        )

        ## Modulation noise

        self.modulation_noises = self._generate_noise_mosas(noises.noise_def_modulation)

        ## Backlink noise

        self.backlink_noises = self._generate_noise_mosas(noises.noise_def_backlink)

        ## Test-mass acceleration noise

        self.testmass_noises = self._generate_noise_mosas(noises.noise_def_testmass)

        ## Ranging noise

        unbiased_ranging_noises = self._generate_noise_mosas(noises.noise_def_ranging)

        self.ranging_noises = compute.ranging_noises(
            unbiased_ranging_noises, ranging_biases=cfg.ranging_biases
        )
        describe_streams_dict(self.ranging_noises, "compute ranging_noises [MOSA_%s]")

        ## OMS noise

        self.oms_sci_carrier_noises = self._generate_noise_mosas(
            noises.noise_def_oms_sci_carrier
        )

        self.oms_sci_usb_noises = self._generate_noise_mosas(
            noises.noise_def_oms_sci_usb
        )

        self.oms_tmi_carrier_noises = self._generate_noise_mosas(
            noises.noise_def_oms_tmi_carrier
        )

        self.oms_tmi_usb_noises = self._generate_noise_mosas(
            noises.noise_def_oms_tmi_usb
        )

        self.oms_ref_carrier_noises = self._generate_noise_mosas(
            noises.noise_def_oms_ref_carrier
        )

        self.oms_ref_usb_noises = self._generate_noise_mosas(
            noises.noise_def_oms_ref_usb
        )

        ## DWS measurement noise

        self.dws_phi_noises = self._generate_noise_mosas(noises.noise_def_dws_phi)

        self.dws_eta_noises = self._generate_noise_mosas(noises.noise_def_dws_eta)

        ## MOC time correlation noise

        self.moc_time_correlation_noises = self._generate_noise_sats(
            noises.noise_def_moc_time_correlation
        )

        ## Longitudinal jitters

        self.mosa_jitter_xs = self._generate_noise_mosas(
            noises.noise_def_mosa_jitter_xs
        )

        ## Angular jitters

        self.sc_jitter_phis = self._generate_noise_sats(noises.noise_def_sc_jitter_phis)
        self.sc_jitter_etas = self._generate_noise_sats(noises.noise_def_sc_jitter_etas)
        self.sc_jitter_thetas = self._generate_noise_sats(
            noises.noise_def_sc_jitter_thetas
        )

        self.mosa_jitter_phis = self._generate_noise_mosas(
            noises.noise_def_mosa_jitter_phis
        )
        self.mosa_jitter_etas = self._generate_noise_mosas(
            noises.noise_def_mosa_jitter_etas
        )

        self.mosa_total_jitter_phis = {
            mosa.value: compute.mosa_total_jitter_phis(
                self.sc_jitter_phis[mosa.sat.value], self.mosa_jitter_phis[mosa.value]
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.mosa_total_jitter_phis, "compute mosa_total_jitter_phis [MOSA_%s]"
        )

        self.mosa_total_jitter_etas = {
            mosa.value: compute.mosa_total_jitter_etas(
                self.sc_jitter_etas[mosa.sat.value],
                self.sc_jitter_thetas[mosa.sat.value],
                self.mosa_jitter_etas[mosa.value],
                mosa_angles=cfg.mosa_angles[mosa.value],
            )
            for mosa in MosaID
        }
        describe_streams_dict(
            self.mosa_total_jitter_etas, "compute mosa_total_jitter_etas [MOSA_%s]"
        )

        ## Tilt-to-length coupling
        ## TTL couplings are defined as velocities [m/s]

        self.local_ttls = compute.local_ttls(
            self.mosa_total_jitter_phis,
            self.mosa_total_jitter_etas,
            ttl_coeffs_local_phis=cfg.ttl_coeffs_local_phis,
            ttl_coeffs_local_etas=cfg.ttl_coeffs_local_etas,
        )
        describe_streams_dict(
            self.local_ttls, "Computing local tilt-to-length couplings [MOSA_%s]"
        )

        self.distant_ttls = compute.distant_ttls(
            self.mosa_total_jitter_phis,
            self.mosa_total_jitter_etas,
            ttl_coeffs_distant_phis=cfg.ttl_coeffs_distant_phis,
            ttl_coeffs_distant_etas=cfg.ttl_coeffs_distant_etas,
        )
        describe_streams_dict(
            self.distant_ttls,
            "Computing unpropagated distant tilt-to-length couplings [MOSA_%s]",
        )

    def _lock_on_cavity(
        self,
        results: LockingResults,
        mosa: MosaID,
    ) -> None:
        """Create streams for carrier and upper sideband offsets and fluctuations
        for laser locked on cavity.

        We also create laser noise streams for lasers locked on cavities here.

        Args:
            results: LockingResults instance collecting the streams created here
            mosa: MOSA of the laser
        """
        logger.info("Generating laser noise for laser %s", mosa.value)

        results.laser_noises[mosa] = self._generate_noise(
            self.noises.noise_def_laser(mosa)
        )

        results.local_carrier_offsets[mosa] = StreamConst(
            self.config.offset_freqs[mosa.value]
        )
        results.local_carrier_offsets[mosa].set_description(
            f"Carrier offsets for primary local beam {mosa.value}"
        )

        results.local_carrier_fluctuations[mosa] = (
            compute.local_carrier_fluctuations_lock_cavity(
                results.laser_noises[mosa],
                self.glitch_lasers[mosa.value],
                self.tdir_modulations_tseries[mosa.value],
            )
        )

        results.local_carrier_fluctuations[mosa].set_description(
            f"Carrier fluctuations for primary local beam {mosa.value}"
        )

    def _lock_on_adjacent(self, results: LockingResults, mosa: MosaID) -> None:
        """Create streams for carrier and upper sideband offsets and fluctuations
        for laser locked to adjacent beam.

        Args:
            results: LockingResults instance collecting the streams created here
            mosa: MOSA of the laser
        """
        cfg = self.config

        logger.debug(
            "Carrier offsets for local beam %s are locked on adjacent beam %s",
            mosa.value,
            mosa.adjacent.value,
        )

        results.local_carrier_offsets[mosa] = (
            compute.local_carrier_offsets_lock_adjacent(
                results.local_carrier_offsets[mosa.adjacent],
                self.fplan_ts[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
        )

        logger.debug(
            "Carrier fluctuations for local beam %s are locked on adjacent beam %s",
            mosa.value,
            mosa.adjacent.value,
        )

        results.adjacent_carrier_fluctuations[mosa] = (
            compute.adjacent_carrier_fluctuations(
                results.local_carrier_fluctuations[mosa.adjacent],
                self.backlink_noises[mosa.value],
                central_freq=cfg.central_freq,
            )
        )

        results.local_carrier_fluctuations[mosa] = (
            compute.local_carrier_fluctuations_lock_adjacent(
                results.adjacent_carrier_fluctuations[mosa],
                self.clock_noise_fluctuations[mosa.sat.value],
                self.oms_ref_carrier_noises[mosa.value],
                self.fplan_ts[mosa.value],
                self.tdir_modulations_tseries[mosa.value],
                central_freq=cfg.central_freq,
            )
        )

    def _lock_on_distant(self, results: LockingResults, mosa: MosaID) -> None:
        """Create streams for carrier and upper sideband offsets and fluctuations
        for laser locked to distant beam.

        Args:
            results: LockingResults instance collecting the streams created here
            mosa: MOSA of the laser
        """
        cfg = self.config

        logger.debug(
            "Carrier offsets for local beam %s are locked on distant beam %s",
            mosa.value,
            mosa.distant.value,
        )

        carrier_offsets = results.local_carrier_offsets[mosa.distant]
        delayed_distant_carrier_offsets = self.delays.delay_isc(
            carrier_offsets, self.pprs[mosa.value]
        )

        results.distant_carrier_offsets[mosa] = compute.distant_carrier_offsets(
            self.d_pprs[mosa.value],
            delayed_distant_carrier_offsets,
            central_freq=cfg.central_freq,
        )

        results.local_carrier_offsets[mosa] = (
            compute.local_carrier_offsets_lock_distant(
                results.distant_carrier_offsets[mosa],
                self.fplan_ts[mosa.value],
                self.clock_noise_offsets[mosa.sat.value],
            )
        )

        logger.debug(
            "Carrier fluctuations for local beam %s are locked on distant beam %s",
            mosa.value,
            mosa.distant.value,
        )

        carrier_fluctuations = compute.carrier_fluctuations(
            results.local_carrier_fluctuations[mosa.distant],
            results.local_carrier_offsets[mosa.distant],
            self.mosa_jitter_xs[mosa.distant.value],
            self.distant_ttls[mosa.distant.value],
            central_freq=cfg.central_freq,
        )

        delayed_distant_carrier_fluctuations = self.delays.delay_isc(
            carrier_fluctuations, self.pprs[mosa.value]
        )

        propagated_carrier_fluctuations = compute.propagated_carrier_fluctuations(
            self.d_pprs[mosa.value], delayed_distant_carrier_fluctuations
        )

        results.distant_carrier_fluctuations[mosa] = (
            compute.distant_carrier_fluctuations(
                propagated_carrier_fluctuations,
                delayed_distant_carrier_offsets,
                self.gws[mosa.value],
                self.local_ttls[mosa.value],
                self.mosa_jitter_xs[mosa.value],
                central_freq=cfg.central_freq,
            )
        )

        results.local_carrier_fluctuations[mosa] = (
            compute.local_carrier_fluctuations_lock_distant(
                results.distant_carrier_fluctuations[mosa],
                self.clock_noise_fluctuations[mosa.sat.value],
                self.oms_sci_carrier_noises[mosa.value],
                self.fplan_ts[mosa.value],
                self.tdir_modulations_tseries[mosa.value],
                central_freq=cfg.central_freq,
            )
        )

    def _simulate_locking_finalize(self, results: LockingResults) -> None:
        """Create all streams not already obtained during locking

        Note: those used to be computed in the simulate() method, recomputing
        also those quantites already obtained here as intermediate results.

        Arguments:
            results: LockingResults instance collecting the streams created here
        """
        cfg = self.config

        for mosa in MosaID:
            if not (
                mosa in results.distant_carrier_offsets
                and mosa in results.distant_carrier_fluctuations
            ):
                delayed_distant_carrier_offsets = self.delays.delay_isc(
                    results.local_carrier_offsets[mosa.distant], self.pprs[mosa.value]
                )

                if not mosa in results.distant_carrier_offsets:
                    results.distant_carrier_offsets[mosa] = (
                        compute.distant_carrier_offsets(
                            self.d_pprs[mosa.value],
                            delayed_distant_carrier_offsets,
                            central_freq=cfg.central_freq,
                        )
                    )

                if not mosa in results.distant_carrier_fluctuations:
                    carrier_fluctuations = compute.carrier_fluctuations(
                        results.local_carrier_fluctuations[mosa.distant],
                        results.local_carrier_offsets[mosa.distant],
                        self.mosa_jitter_xs[mosa.distant.value],
                        self.distant_ttls[mosa.distant.value],
                        central_freq=cfg.central_freq,
                    )

                    delayed_distant_carrier_fluctuations = self.delays.delay_isc(
                        carrier_fluctuations, self.pprs[mosa.value]
                    )

                    propagated_carrier_fluctuations = (
                        compute.propagated_carrier_fluctuations(
                            self.d_pprs[mosa.value],
                            delayed_distant_carrier_fluctuations,
                        )
                    )

                    results.distant_carrier_fluctuations[mosa] = (
                        compute.distant_carrier_fluctuations(
                            propagated_carrier_fluctuations,
                            delayed_distant_carrier_offsets,
                            self.gws[mosa.value],
                            self.local_ttls[mosa.value],
                            self.mosa_jitter_xs[mosa.value],
                            central_freq=cfg.central_freq,
                        )
                    )

            if not mosa in results.adjacent_carrier_fluctuations:
                results.adjacent_carrier_fluctuations[mosa] = (
                    compute.adjacent_carrier_fluctuations(
                        results.local_carrier_fluctuations[mosa.adjacent],
                        self.backlink_noises[mosa.value],
                        central_freq=cfg.central_freq,
                    )
                )

            if not mosa in results.laser_noises:
                results.laser_noises[mosa] = StreamConst(0.0)

    def _locking_dependencies(self) -> dict[MosaID, MosaID | None]:
        """Compute the locking dependency for the lasers"""

        dependencies: dict[MosaID, MosaID | None] = {}
        for nmosa, nlock_type in self.config.lock.items():
            mosa, lock_type = MosaID(nmosa), LockTypeID(nlock_type)
            cases = {
                LockTypeID.CAVITY: None,
                LockTypeID.ADJACENT: mosa.adjacent,
                LockTypeID.DISTANT: mosa.distant,
            }
            dependencies[mosa] = cases[lock_type]

        logger.debug("Laser locking dependencies read: %s", dependencies)

        return dependencies

    def _assemble_locking(self) -> None:
        """Assemble streams for local beams from the locking configuration"""

        results = LockingResults()

        # Transform the lock dictionary into a dependency dictionary

        dependencies = self._locking_dependencies()

        # Apply locking conditions in order

        just_locked: list[None | MosaID] = [None]
        while dependencies:
            being_locked: list[None | MosaID] = []
            available_mosas = [
                mosa for mosa, dep in dependencies.items() if dep in just_locked
            ]
            for mosa in available_mosas:
                lock_type = LockTypeID(self.config.lock[mosa.value])
                match lock_type:
                    case LockTypeID.CAVITY:
                        logger.debug("Locking laser %s on cavity", mosa.value)
                        self._lock_on_cavity(results, mosa)
                    case LockTypeID.ADJACENT:
                        logger.debug(
                            "Locking laser %s on adjacent laser %s",
                            mosa.value,
                            mosa.adjacent.value,
                        )
                        self._lock_on_adjacent(results, mosa)
                    case LockTypeID.DISTANT:
                        logger.debug(
                            "Locking laser %s on distant laser %s",
                            mosa.value,
                            mosa.distant.value,
                        )
                        self._lock_on_distant(results, mosa)
                    case _ as unreachable:
                        assert_never(unreachable)

                being_locked.append(mosa)
                del dependencies[mosa]
            just_locked = being_locked
            if not just_locked:
                raise RuntimeError(
                    f"cannot apply locking conditions to remaining lasers '{list(dependencies.keys())}'"
                )

        self._simulate_locking_finalize(results)

        self.distant_carrier_offsets = make_mosa_dict(results.distant_carrier_offsets)
        self.local_carrier_offsets = make_mosa_dict(results.local_carrier_offsets)
        self.local_carrier_fluctuations = make_mosa_dict(
            results.local_carrier_fluctuations
        )
        self.distant_carrier_fluctuations = make_mosa_dict(
            results.distant_carrier_fluctuations
        )
        self.adjacent_carrier_fluctuations = make_mosa_dict(
            results.adjacent_carrier_fluctuations
        )
        self.laser_noises = make_mosa_dict(results.laser_noises)
