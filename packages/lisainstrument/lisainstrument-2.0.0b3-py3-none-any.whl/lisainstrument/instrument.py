# -*- coding: utf-8 -*-
"""
Instrument
==========

Instrumental simulation for the LISA mission. See :cite:`Bayle:2022okx` for
a more detailed description of the underlying physical models.

.. autoclass:: Instrument
    :members:
"""

import logging
import math
from typing import Any, Callable, Final, Literal, TypeVar

import numpy as np

from lisainstrument import version
from lisainstrument.instru import (
    InstruDelays,
    InstruNoises,
    InstruNoisesConfig,
    ModelConstellation,
    ModelConstellationCfg,
    SimMetaData,
    SimResultsNumpyCore,
    SimResultsNumpyFull,
    init_aafilter,
    init_fplan_source,
    init_glitch_source,
    init_gw_source,
    init_lock,
    init_orbit_source,
)
from lisainstrument.instru import instru_defaults as defaults
from lisainstrument.instru import store_instru_hdf5
from lisainstrument.noisy import LaserNoiseShape, TestMassNoiseShape, make_random_seed
from lisainstrument.orbiting import OrbitSourceStatic
from lisainstrument.orbiting.constellation_enums import (
    MosaDictFloat,
    MosaID,
    SatDictFloat,
    SatID,
    make_mosa_dict,
    make_mosa_dict_const,
    make_mosa_id_dict,
    make_sat_dict,
    make_sat_dict_const,
    make_sat_id_dict,
)
from lisainstrument.sigpro import ConstFuncOfTime
from lisainstrument.streams import (
    SchedulerConfigTypes,
    StreamBundle,
    ValidMetaDataTypes,
    store_bundle_numpy,
)

logger = logging.getLogger(__name__)

_T = TypeVar("_T", SimResultsNumpyFull, SimResultsNumpyCore)


class Instrument:
    """User interface for running an instrumental simulation.

    Args:
        size: number of measurement samples to generate
        dt: sampling period [s]
        t0: initial time [s], or 'orbits' to match that of the orbits (see also orbit_t0_margin)
        seed: seed for random noise generators, or None to generate a random seed
        physics_upsampling: ratio of sampling frequencies for physics vs. measurement simulation
        aafilter: antialiasing filter coefficients, tuple specifying Kaiser filter method,
            or None for no filter; to design a filter from a Kaiser window, use a tuple
            ('kaiser', attenuation [dB], f1 [Hz], f2 [Hz]) with f1 < f2 the frequencies defining
            the transition band
        telemetry_downsampling: ratio of sampling frequencies for measurements vs. telemetry events
        initial_telemetry_size: number of telemetry samples before :attr:`lisainstrument.Instrument.t0`
        orbits: path to orbit file, dictionary of constant PPRs for static arms, 'static'
            for a set of static PPRs corresponding to a fit of Keplerian orbits around t = 0,
            or dictionary of PPR time series
        orbit_dataset: datasets to read from orbit file, must be 'tps/ppr' or 'tcb/ltt';
            if set to 'tps/ppr', read proper pseudo-ranges (PPRs) in TPSs (proper times),
            if set to 'tcb/ltt', read light travel times (LTTs) in TCB (coordinate time);
            ignored if no orbit files are used
        gws: path to gravitational-wave file. If ``orbit_dataset`` is ``'tps/ppr'``, we try to read
             link responses as functions of the TPS instead of link responses in the TCB (fallback behavior)
        interpolation: interpolation method and parameters;
            use a tuple ('lagrange', order) where `order` is the Lagrange interpolation
            order, or None for no interpolation.
        glitches: path to glitch file
        lock: pre-defined laser locking configuration (e.g., 'N1-12' is configuration N1 with 12
            as primary laser), or 'six' for 6 lasers locked on cavities, or a dictionary of locking
            conditions
        fplan: path to frequency-plan file, dictionary of locking beatnote frequencies [Hz],
            or 'static' for a default set of constant locking beatnote frequencies
        laser_asds: dictionary of amplitude spectral densities for laser noise [Hz/sqrt(Hz)]
        laser_shape: laser noise spectral shape, either 'white' or 'white+infrared'
        central_freq: laser central frequency from which all offsets are computed [Hz]
        offset_freqs: dictionary of laser frequency offsets for unlocked lasers [Hz],
            defined with respect to :attr:`lisainstrument.Instrument.central_freq`,
            or 'default' for a default set of frequency offsets that yield valid beatnote
            frequencies for 'six' lasers locked on cavity and default set of constant PPRs
        modulation_asds: dictionary of amplitude spectral densities for modulation noise
            on each MOSA [s/sqrt(Hz)], or 'default' for a default set of levels with a factor
            10 higher on right-sided MOSAs to account for the frequency distribution system
        modulation_freqs: dictionary of modulation frequencies [Hz], or 'default'
        tdir_modulations: dictionary of callable generators of TDIR assistance modulations
            that take an array of TPS times as argument, or None
        clock_asds: dictionary of clock noise amplitude spectral densities [/sqrt(Hz)]
        clock_offsets: dictionary of clock offsets from TPS [s]
        clock_freqoffsets: dictionary of clock frequency offsets [s/s], or 'default'
        clock_freqlindrifts: dictionary of clock frequency linear drifts [s/s^2], or 'default'
        clock_freqquaddrifts: dictionary of clock frequency quadratic drifts [s/s^3], or 'default'
        clockinv_tolerance: convergence tolerance for clock noise inversion [s]
        clockinv_maxiter: maximum number of iterations for clock noise inversion
        backlink_asds: dictionary of amplitude spectral densities for backlink noise [m/sqrt(Hz)]
        backlink_fknees: dictionary of cutoff frequencied for backlink noise [Hz]
        testmass_asds: dictionary of amplitude spectral densities for test-mass noise [ms^(-2)/sqrt(Hz)]
        testmass_fknees: dictionary of low-frequency cutoff frequencies for test-mass noise [Hz]
        testmass_fbreak: dictionary of high-frequency break frequencies for test-mass noise [Hz]
        testmass_shape: test-mass noise spectral shape, either 'original' or 'lowfreq-relax'
        testmass_frelax: dictionary of low-frequency relaxation frequencies for test-mass noise [Hz]
        oms_asds: tuple of dictionaries of amplitude spectral densities for OMS noise [m/sqrt(Hz)],
            ordered as (sci_carrier, sci_usb, tmi_carrier, tmi_usb, ref_carrier, ref_usb)
        moc_time_correlation_asds: dictionary of amplitude spectral densities for MOC time
            correlation noise [s/sqrt(Hz)], the default ASD seems rather high, this is due
            to the small sampling rate (default 1 / 86400s)
        oms_fknees: dictionary of cutoff frequencies for OMS noise
        ttl_coeffs: tuple (local_phi, distant_phi, local_eta, distant_eta) of dictionaries of
            tilt-to-length coefficients on each MOSA [m/rad], 'default' for a default set of
            coefficients, or 'random' to draw a set of coefficients from uniform distributions
            (LISA-UKOB-INST-ML-0001-i2 LISA TTL STOP Model, summary table, 2.4 mm/rad and
            2.2mm/rad for distant and local coefficients, respectively)
        mosa_longitudinal_jitter_asds: dictionary of amplitude spectral densities for
            MOSA longitudinal jitter on the sensitive axis [m/sqrt(Hz)]
        sc_angular_jitter_asds: tuple of dictionaries of angular jitter amplitude spectral densities
            for spacecraft, ordered as (yaw, pitch, roll) [rad/sqrt(Hz)]
        sc_angular_jitter_fknees: tuple of dictionaries of cutoff frequencies for spacecraft angular jitter,
            ordered as (yaw, pitch, roll) [Hz]
        mosa_angular_jitter_asds: tuple of dictionaries of angular jitter amplitude spectral densities
            for MOSA, ordered as (yaw, pitch) [rad/sqrt(Hz)]
        mosa_angular_jitter_fknees: tuple of dictionaries of cutoff frequencies for MOSA angular jitter,
            ordered as (yaw, pitch) [Hz]
        mosa_angles: dictionary of oriented MOSA opening angles [deg], or 'default'
        dws_asds: dictionary of amplitude spectral densities for DWS measurement noise [rad/sqrt(Hz)]
        ranging_biases: dictionary of ranging noise bias [s]
        ranging_asds: dictionary of ranging noise amplitude spectral densities [s/sqrt(Hz)]
        prn_ambiguity: distance after which PRN code repeats itself [m] (reasonable value is 300 km),
            None or 0 for no ambiguities
        electro_delays: tuple (sci, tmi, ref) of dictionaries for electronic delays [s]
        delay_isc_min (float): minimum interspacecraft delay [s] that can occur in the simulation
        delay_isc_max (float): maximum interspacecraft delay [s] that can occur in the simulation
        delay_clock_max (float): maximum absolute clock delays [s] that can occur in the simulation
        chunk_gw_files (bool): whether to interpolate gw files in chunked fashion or globally
        noises_f_min_hz (float|None): cutoff frequency used for noises or None for inverse simulation length
        clock_f_min_hz (float): cutoff frequency used for clock noise
        orbit_t0_margin (float): Margin to be added to t0 for case t0="orbits"
    """

    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=too-many-public-methods

    SCS = SatID.names()
    """Spacecraft indices."""

    MOSAS = MosaID.names()
    """MOSA indices."""

    def __init__(
        self,
        *,
        # Sampling parameters
        size: int = 1200,
        dt: float = 1 / 4,
        t0: float | str = "orbits",
        seed: int | None = None,
        # Physics simulation sampling and filtering
        physics_upsampling: int = 4,
        aafilter: None | tuple[str, float, float, float] | list[float] | np.ndarray = (
            "kaiser",
            240,
            1.1,
            2.9,
        ),
        # Telemetry sampling
        telemetry_downsampling: int = 86400 * 4,
        initial_telemetry_size: int = 0,
        # Inter-spacecraft propagation
        orbits: str | dict[str, float] = "static",
        orbit_dataset: str = "tps/ppr",
        gws: str | None | dict[str, np.ndarray] = None,
        interpolation: None | tuple[str, int] = ("lagrange", 31),
        glitches: str | None = None,
        # Artifacts
        # Laser locking and frequency plan
        lock: str | dict[str, str] = "N1-12",
        fplan: str | float | dict[str, float] | np.ndarray = "static",
        laser_asds: float | dict[str, float] = 30.0,
        laser_shape: str = "white+infrared",
        central_freq: float = 2.816e14,
        offset_freqs="default",
        # Laser phase modulation
        modulation_asds: None | str | float | dict[str, float] = "default",
        modulation_freqs: str | float | dict[str, float] = "default",
        tdir_modulations: None | dict[str, Callable] = None,
        # Clocks
        clock_asds: float | dict[str, float] = 6.32e-14,
        clock_offsets: float | dict[str, float] = 0.0,
        clock_freqoffsets: str | float | dict[str, float] = "default",
        clock_freqlindrifts: str | float | dict[str, float] = "default",
        clock_freqquaddrifts: str | float | dict[str, float] = "default",
        # Clock inversion
        clockinv_tolerance: float = 1e-10,
        clockinv_maxiter: int = 5,
        # Backlink noises
        backlink_asds: float | dict[str, float] = 3e-12,
        backlink_fknees: float | dict[str, float] = 2e-3,
        # Test-mass noise
        testmass_asds: float | dict[str, float] = 2.4e-15,
        testmass_fknees: float | dict[str, float] = 0.4e-3,
        testmass_fbreak: float | dict[str, float] = 8e-3,
        testmass_shape: str = "original",
        testmass_frelax: float | dict[str, float] = 0.8e-4,
        # OMS noise
        oms_asds: tuple[float | dict[str, float], ...] = (
            6.35e-12,
            1.25e-11,
            1.42e-12,
            3.38e-12,
            3.32e-12,
            7.90e-12,
        ),
        oms_fknees: float | dict[str, float] = 2e-3,
        # MOC time correlation
        moc_time_correlation_asds: float | dict[str, float] = 0.42,
        # Longitudinal jitters
        mosa_longitudinal_jitter_asds: float | dict[str, float] = 2e-9,
        # Angular jitters
        sc_angular_jitter_asds: tuple[float | dict[str, float], ...] = (
            5e-9,
            5e-9,
            5e-9,
        ),
        sc_angular_jitter_fknees: tuple[float | dict[str, float], ...] = (
            8e-4,
            8e-4,
            8e-4,
        ),
        mosa_angular_jitter_asds: tuple[float | dict[str, float], ...] = (2e-9, 2e-9),
        mosa_angular_jitter_fknees: tuple[float | dict[str, float], ...] = (8e-4, 8e-4),
        mosa_angles: str | float | dict[str, float] = "default",
        # Tilt-to-length coupling
        ttl_coeffs="default",
        dws_asds: float | dict[str, float] = 7e-8 / 335,
        # Pseudo-ranging
        ranging_biases: float | dict[str, float] = 0.0,
        ranging_asds: float | dict[str, float] = 3e-9,
        prn_ambiguity: None | int | float = None,
        # Electronic delays
        electro_delays: tuple[float | dict[str, float], ...] = (0, 0, 0),
        delay_isc_min: float = 6.0,
        delay_isc_max: float = 12.0,
        delay_clock_max: float = 50.0,
        chunk_gw_files: bool = False,
        noises_f_min_hz: float | None = 5e-5,
        clock_f_min_hz: float = 1e-5,
        orbit_t0_margin: float = 75.0,
    ) -> None:
        # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-statements,too-many-locals,too-many-branches
        logger.info("Validating simulation parameters and opening data sources")
        logger.info("This is lisainstrument version %s", version.__version__)
        # ~ self.git_url = "https://gitlab.in2p3.fr/lisa-simulation/instrument"
        # ~ self.version = importlib.metadata.version("lisainstrument")

        self.orbit_source, self.orbit_file, self.orbit_dataset = init_orbit_source(
            orbits, orbit_dataset
        )
        orbit_t0_margin = float(orbit_t0_margin)
        match t0:
            case "orbits":
                self.t0 = self.orbit_source.t0 + orbit_t0_margin
                self.orbit_t0 = (
                    self.orbit_source.t0
                )  # self.orbit_t0 only used in metadata
            case float(start_time):
                self.t0 = start_time
                self.orbit_t0 = (
                    start_time
                    if isinstance(self.orbit_source, OrbitSourceStatic)
                    else self.orbit_source.t0
                )
            case _:
                msg = f"Parameter 't0' must be float or string 'orbits', got {t0}"
                raise RuntimeError(msg)

        match size:
            case int(size_positive) if size_positive > 0:
                self.size: Final[int] = size_positive
            case _:
                msg = f"Parameter 'size' must be integer > 0, got {size}"
                raise RuntimeError(msg)

        match dt:
            case float() | int() as dt_positive if dt_positive > 0:
                self.dt: Final[float] = float(dt_positive)
            case _:
                msg = f"Parameter 'dt' must be float > 0, got {dt}"
                raise RuntimeError(msg)

        self.fs: Final[float] = 1 / self.dt
        self.duration: Final[float] = self.dt * self.size

        # Physics sampling
        match physics_upsampling:
            case int(physics_upsampling_positive) if physics_upsampling_positive > 0:
                self.physics_upsampling: Final[int] = physics_upsampling_positive
            case _:
                msg = f"Parameter physics_upsampling must be integer > 0, got {physics_upsampling}"
                raise RuntimeError(msg)

        self.physics_size: Final[int] = self.size * self.physics_upsampling
        self.physics_dt: Final[float] = self.dt / self.physics_upsampling
        self.physics_fs: Final[float] = self.fs * self.physics_upsampling

        # Telemetry sampling
        match telemetry_downsampling:
            case int(
                telemetry_downsampling_positive
            ) if telemetry_downsampling_positive > 0:
                self.telemetry_downsampling: Final[int] = (
                    telemetry_downsampling_positive
                )
            case _:
                msg = f"Parameter telemetry_downsampling must be integer > 0, got {telemetry_downsampling}"
                raise RuntimeError(msg)

        self.telemetry_dt: Final[float] = self.dt * self.telemetry_downsampling
        self.telemetry_fs: Final[float] = self.fs / self.telemetry_downsampling
        # Extra telemetry samples before t0

        match initial_telemetry_size:
            case int(
                initial_telemetry_size_nonneg
            ) if initial_telemetry_size_nonneg >= 0:
                self.initial_telemetry_size: Final[int] = initial_telemetry_size_nonneg
            case _:
                msg = f"Parameter initial_telemetry_size must be integer >= 0, got {initial_telemetry_size}"
                raise RuntimeError(msg)

        self.telemetry_t0: Final[float] = (
            self.t0 - self.initial_telemetry_size * self.telemetry_dt
        )
        # Total telemetry size, includes initial telemetry samples
        # plus telemetry samples covering the entire measurement time vector,
        # hence the use of ``math.ceil`` -- the +1 is for the sample at t0
        self.telemetry_size: Final[int] = (
            self.initial_telemetry_size
            + 1
            + math.ceil(self.size / self.telemetry_downsampling)
        )

        # < Those are not used internally, candidates for deprecation
        self.telemetry_to_physics_dt: Final[int] = (
            self.telemetry_downsampling * self.physics_upsampling
        )
        self.physics_size_covering_telemetry: Final[int] = (
            self.telemetry_size * self.telemetry_to_physics_dt
        )
        # >

        # Noise Generator
        if seed is None:
            seed = make_random_seed()
            logger.info(
                "Seed for random number generators not specified, using random value"
            )
        logger.debug("Using seed '%d' for random number generation", seed)
        self.seed: Final[int] = seed

        self.gwsrc, self.gw_file, self.gw_group = init_gw_source(
            gws,
            self.orbit_dataset,
            chunk_gw_files,
            self.t0,
            self.t0 + self.physics_dt * self.physics_size,
        )

        self.glitchsrc, self.glitch_file = init_glitch_source(
            glitches, self.t0, self.t0 + self.physics_dt * self.physics_size
        )

        # Instrument topology
        match central_freq:
            case float(central_freq_positive) if central_freq_positive > 0:
                self.central_freq: Final[float] = central_freq_positive
            case _:
                msg = f"Parameter 'central_freq' must be float > 0 , got {central_freq}"
                raise RuntimeError(msg)

        self.lock, self.lock_config = init_lock(lock)

        self.fplansrc, self.fplan_file = init_fplan_source(
            fplan, self.orbit_source, self.lock, self.lock_config
        )

        # self.fplan only used for metadata
        self.fplan = {
            n: (c.const if isinstance(c, ConstFuncOfTime) else None)
            for n, c in self.fplansrc.items()
        }

        def param_mosa_dict_float(par: float | dict, name: str) -> MosaDictFloat:
            match par:
                case float() | int() as par_scalar:
                    res = make_mosa_dict_const(float(par_scalar))
                case dict(par_dict):
                    res = make_mosa_dict(par_dict)
                case _:
                    msg = (
                        f"Parameter {name} must be float or dict[str,float] , got {par}"
                    )
                    raise RuntimeError(msg)
            return res

        def param_sat_dict_float(par: float | dict, name: str) -> SatDictFloat:
            match par:
                case float() | int() as par_scalar:
                    res = make_sat_dict_const(float(par_scalar))
                case dict(par_dict):
                    res = make_sat_dict(par_dict)
                case _:
                    msg = (
                        f"Parameter {name} must be float or dict[str,float] , got {par}"
                    )
                    raise RuntimeError(msg)
            return res

        match offset_freqs:
            case "default":
                _offset_freqs = make_mosa_dict(defaults.OFFSET_FREQS)
            case dict(offset_freq_dict):
                _offset_freqs = make_mosa_dict(offset_freq_dict)
            case _:
                msg = f'Parameter offset_freqs must be dictionary or "default", got {offset_freqs}'
                raise RuntimeError(msg)
        self.offset_freqs: Final[MosaDictFloat] = _offset_freqs

        # Laser and modulation noise

        match noises_f_min_hz:
            case None:
                _noises_f_min_hz = 1.0 / self.duration
            case float(noises_f_min_hz_positive) if noises_f_min_hz_positive > 0:
                _noises_f_min_hz = noises_f_min_hz_positive
            case _:
                msg = f"noises_fmin_hz must be float > 0 or None, got {noises_f_min_hz}"
                raise ValueError(msg)
        self._noises_f_min_hz: Final[float] = _noises_f_min_hz

        match clock_f_min_hz:
            case float(clock_f_min_hz_positive) if clock_f_min_hz_positive > 0:
                self._clock_f_min_hz: Final[float] = clock_f_min_hz_positive
            case _:
                msg = f"clock_fmin_hz must be float > 0, got {clock_f_min_hz}"
                raise ValueError(msg)

        self.laser_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            laser_asds, "laser_asds"
        )

        if laser_shape not in ["white", "white+infrared"]:
            raise ValueError(f"invalid laser noise spectral shape '{laser_shape}'")
        self.laser_shape = laser_shape

        match modulation_asds:
            case "default":
                _modulation_asds = make_mosa_dict(defaults.MODULATION_ASDS)
            case None:
                _modulation_asds = make_mosa_dict_const(0.0)
            case float() | int() as modulation_asds_scalar:
                _modulation_asds = make_mosa_dict_const(float(modulation_asds_scalar))
            case dict(modulation_asds_dict):
                _modulation_asds = make_mosa_dict(modulation_asds_dict)
            case _:
                msg = (
                    'Parameter modulation_asds must be "default", '
                    f"None, float, or dict[str,float], got {modulation_asds}"
                )
                raise RuntimeError(msg)
        self.modulation_asds: Final[MosaDictFloat] = _modulation_asds

        match modulation_freqs:
            case "default":
                _modulation_freqs = make_mosa_dict(defaults.MODULATION_FREQS)
            case float() | int() as modulation_freqs_scalar:
                _modulation_freqs = make_mosa_dict_const(float(modulation_freqs_scalar))
            case dict(modulation_freqs_dict):
                _modulation_freqs = make_mosa_dict(modulation_freqs_dict)
            case _:
                msg = f'Parameter modulation_freqs must be "default", float, or dict[str,float], got {modulation_freqs}'
                raise RuntimeError(msg)
        self.modulation_freqs: Final[MosaDictFloat] = _modulation_freqs

        match tdir_modulations:
            case None:
                _tdir_modulations = None
            case dict(tdir_modulations_dict) if all(
                (callable(f) for f in tdir_modulations_dict.values())
            ):
                _tdir_modulations = make_mosa_dict(tdir_modulations_dict)
            case _:
                msg = (
                    "Parameter tdir_modulations must be None or dictionary of callables"
                )
                raise RuntimeError(msg)
        self.tdir_modulations: Final[dict[str, Callable] | None] = _tdir_modulations

        # Clocks

        self.clock_asds: Final[SatDictFloat] = param_sat_dict_float(
            clock_asds, "clock_asds"
        )
        self.clock_offsets: Final[SatDictFloat] = param_sat_dict_float(
            clock_offsets, "clock_offsets"
        )

        match clock_freqoffsets:
            case "default":
                _clock_freqoffsets = make_sat_dict(defaults.CLOCK_FREQOFFSETS)
            case float() | int() as clock_freqoffsets_scalar:
                _clock_freqoffsets = make_sat_dict_const(
                    float(clock_freqoffsets_scalar)
                )
            case dict(clock_freqoffsets_dict):
                _clock_freqoffsets = make_sat_dict(clock_freqoffsets_dict)
            case _:
                msg = (
                    f'Parameter clock_freqoffsets must be "default", '
                    f"float, or dict[str,float], got {clock_freqoffsets}"
                )
                raise RuntimeError(msg)
        self.clock_freqoffsets: Final[SatDictFloat] = _clock_freqoffsets

        match clock_freqlindrifts:
            case "default":
                _clock_freqlindrifts = make_sat_dict(defaults.CLOCK_FREQLINDRIFTS)
            case float() | int() as clock_freqlindrifts_scalar:
                _clock_freqlindrifts = make_sat_dict_const(
                    float(clock_freqlindrifts_scalar)
                )
            case dict(clock_freqlindrifts_dict):
                _clock_freqlindrifts = make_sat_dict(clock_freqlindrifts_dict)
            case _:
                msg = (
                    'Parameter clock_freqlindrifts must be "default", '
                    "float, or dict[str,float], got {clock_freqlindrifts}"
                )
                raise RuntimeError(msg)
        self.clock_freqlindrifts: Final[SatDictFloat] = _clock_freqlindrifts

        match clock_freqquaddrifts:
            case "default":
                _clock_freqquaddrifts = make_sat_dict(defaults.CLOCK_FREQQUADDRIFTS)
            case float() | int() as clock_freqquaddrifts_scalar:
                _clock_freqquaddrifts = make_sat_dict_const(
                    float(clock_freqquaddrifts_scalar)
                )
            case dict(clock_freqquaddrifts_dict):
                _clock_freqquaddrifts = make_sat_dict(clock_freqquaddrifts_dict)
            case _:
                msg = (
                    f'Parameter clock_freqquaddrifts must be "default", '
                    f"float, or dict[str,float], got {clock_freqquaddrifts}"
                )
                raise RuntimeError(msg)
        self.clock_freqquaddrifts: Final[SatDictFloat] = _clock_freqquaddrifts

        # MOC time correlation

        self.moc_time_correlation_asds: Final[SatDictFloat] = param_sat_dict_float(
            moc_time_correlation_asds, "moc_time_correlation_asds"
        )

        # Ranging noise
        match ranging_biases:
            case dict(ranging_biases_dict) if any(
                (isinstance(e, np.ndarray) for e in ranging_biases_dict.values())
            ):
                msg = (
                    "Passing numpy arrays in Parameter ranging_biases is forbidden "
                    "since the switch to chunked processing"
                )
                raise RuntimeError(msg)
            case dict(ranging_biases_dict):
                _ranging_biases = make_mosa_dict(ranging_biases_dict)
            case float() | int() as ranging_biases_scalar:
                _ranging_biases = make_mosa_dict_const(float(ranging_biases_scalar))
            case _:
                msg = f"Parameter ranging_biases must be float, or dict[str,float], got {ranging_biases}"
                raise RuntimeError(msg)
        self.ranging_biases: Final[MosaDictFloat] = _ranging_biases

        self.ranging_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            ranging_asds, "ranging_asds"
        )

        match prn_ambiguity:
            case None | 0:
                _prn_ambiguity = None
            case float() | int():
                _prn_ambiguity = float(prn_ambiguity)
        self.prn_ambiguity: Final[None | float] = _prn_ambiguity

        # Backlink, OMS and test-mass acceleration noise

        self.backlink_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            backlink_asds, "backlink_asds"
        )
        self.backlink_fknees: Final[MosaDictFloat] = param_mosa_dict_float(
            backlink_fknees, "backlink_fknees"
        )

        match oms_asds:
            case (sci_carrier, sci_usb, tmi_carrier, tmi_usb, ref_carrier, ref_usb):
                self.oms_sci_carrier_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    sci_carrier, "oms_asds[0]"
                )
                self.oms_sci_usb_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    sci_usb, "oms_asds[1]"
                )
                self.oms_tmi_carrier_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    tmi_carrier, "oms_asds[2]"
                )
                self.oms_tmi_usb_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    tmi_usb, "oms_asds[3]"
                )
                self.oms_ref_carrier_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    ref_carrier, "oms_asds[4]"
                )
                self.oms_ref_usb_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    ref_usb, "oms_asds[5]"
                )
            case _:
                msg = f"Parameter oms_ads must be tuple of length 6, got {oms_asds}"
                raise RuntimeError(msg)

        self.oms_fknees: Final[MosaDictFloat] = param_mosa_dict_float(
            oms_fknees, "oms_fknees"
        )

        # Test-mass noise
        if testmass_shape not in ["original", "lowfreq-relax"]:
            raise ValueError(
                f"invalid test-mass noise spectral shape '{testmass_shape}'"
            )
        self.testmass_shape: Final[str] = testmass_shape

        self.testmass_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            testmass_asds, "testmass_asds"
        )
        self.testmass_fknees: Final[MosaDictFloat] = param_mosa_dict_float(
            testmass_fknees, "testmass_fknees"
        )
        self.testmass_fbreak: Final[MosaDictFloat] = param_mosa_dict_float(
            testmass_fbreak, "testmass_fbreak"
        )
        self.testmass_frelax: Final[MosaDictFloat] = param_mosa_dict_float(
            testmass_frelax, "testmass_frelax"
        )

        # Longitudinal jitters

        self.mosa_jitter_x_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            mosa_longitudinal_jitter_asds, "mosa_longitudinal_jitter_asds"
        )

        # Tilt-to-length
        match ttl_coeffs:
            # static type check would trigger mypy bug
            case "default":
                _ttl_coeffs_local_phis = make_mosa_dict(defaults.TTL_COEFFS_LOCAL_PHIS)
                _ttl_coeffs_distant_phis = make_mosa_dict(
                    defaults.TTL_COEFFS_DISTANT_PHIS
                )
                _ttl_coeffs_local_etas = make_mosa_dict(defaults.TTL_COEFFS_LOCAL_ETAS)
                _ttl_coeffs_distant_etas = make_mosa_dict(
                    defaults.TTL_COEFFS_DISTANT_ETAS
                )
            case "random":
                _ttl_coeffs_local_phis = make_mosa_dict(
                    defaults.random_ttl_coeffs_local_phis()
                )
                _ttl_coeffs_distant_phis = make_mosa_dict(
                    defaults.random_ttl_coeffs_distant_phis()
                )
                _ttl_coeffs_local_etas = make_mosa_dict(
                    defaults.random_ttl_coeffs_local_etas()
                )
                _ttl_coeffs_distant_etas = make_mosa_dict(
                    defaults.random_ttl_coeffs_distant_etas()
                )
            case (local_phi, distant_phi, local_eta, distant_eta):
                _ttl_coeffs_local_phis = param_mosa_dict_float(
                    local_phi, "ttl_coeffs[0]"
                )
                _ttl_coeffs_distant_phis = param_mosa_dict_float(
                    distant_phi, "ttl_coeffs[1]"
                )
                _ttl_coeffs_local_etas = param_mosa_dict_float(
                    local_eta, "ttl_coeffs[2]"
                )
                _ttl_coeffs_distant_etas = param_mosa_dict_float(
                    distant_eta, "ttl_coeffs[3]"
                )
            case _:
                msg = f'Parameter ttl_coeffs must be "default", "random", or tuple of length 4, got {ttl_coeffs}'
                raise RuntimeError(msg)

        self.ttl_coeffs_local_phis: Final[MosaDictFloat] = _ttl_coeffs_local_phis
        self.ttl_coeffs_distant_phis: Final[MosaDictFloat] = _ttl_coeffs_distant_phis
        self.ttl_coeffs_local_etas: Final[MosaDictFloat] = _ttl_coeffs_local_etas
        self.ttl_coeffs_distant_etas: Final[MosaDictFloat] = _ttl_coeffs_distant_etas

        self.dws_asds: Final[MosaDictFloat] = param_mosa_dict_float(
            dws_asds, "dws_asds"
        )

        # Angular jitters
        match sc_angular_jitter_asds:
            case (yaw, pitch, roll):
                self.sc_jitter_phi_asds: Final[SatDictFloat] = param_sat_dict_float(
                    yaw, "sc_angular_jitter_asds[0]"
                )
                self.sc_jitter_eta_asds: Final[SatDictFloat] = param_sat_dict_float(
                    pitch, "sc_angular_jitter_asds[1]"
                )
                self.sc_jitter_theta_asds: Final[SatDictFloat] = param_sat_dict_float(
                    roll, "sc_angular_jitter_asds[2]"
                )
            case _:
                msg = f"Parameter sc_angular_jitter_asds must be tuple of length 3, got {sc_angular_jitter_asds}"
                raise RuntimeError(msg)

        match sc_angular_jitter_fknees:
            case (yaw, pitch, roll):
                self.sc_jitter_phi_fknees: Final[SatDictFloat] = param_sat_dict_float(
                    yaw, "sc_angular_jitter_fknees[0]"
                )
                self.sc_jitter_eta_fknees: Final[SatDictFloat] = param_sat_dict_float(
                    pitch, "sc_angular_jitter_fknees[1]"
                )
                self.sc_jitter_theta_fknees: Final[SatDictFloat] = param_sat_dict_float(
                    roll, "sc_angular_jitter_fknees[2]"
                )
            case _:
                msg = f"Parameter sc_angular_jitter_fknees must be tuple of length 3, got {sc_angular_jitter_fknees}"
                raise RuntimeError(msg)

        match mosa_angular_jitter_asds:
            case (yaw, pitch):
                self.mosa_jitter_phi_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    yaw, "mosa_angular_jitter_asds[0]"
                )
                self.mosa_jitter_eta_asds: Final[MosaDictFloat] = param_mosa_dict_float(
                    pitch, "mosa_angular_jitter_asds[1]"
                )
            case _:
                msg = f"Parameter mosa_angular_jitter_asds must be tuple of length 2, got {mosa_angular_jitter_asds}"
                raise RuntimeError(msg)

        match mosa_angular_jitter_fknees:
            case (yaw, pitch):
                self.mosa_jitter_phi_fknees: Final[MosaDictFloat] = (
                    param_mosa_dict_float(yaw, "mosa_angular_jitter_fknees[0]")
                )
                self.mosa_jitter_eta_fknees: Final[MosaDictFloat] = (
                    param_mosa_dict_float(pitch, "mosa_angular_jitter_fknees[1]")
                )
            case _:
                msg = (
                    "Parameter mosa_angular_jitter_fknees must be tuple "
                    f"of length 2, got {mosa_angular_jitter_fknees}"
                )
                raise RuntimeError(msg)

        # MOSA opening angles

        match mosa_angles:
            case "default":
                _mosa_angles = make_mosa_dict(defaults.MOSA_ANGLES)
            case float() | int() as mosa_angles_scalar:
                _mosa_angles = make_mosa_dict_const(float(mosa_angles_scalar))
            case dict(mosa_angles_dict):
                _mosa_angles = make_mosa_dict(mosa_angles_dict)
            case _:
                msg = f'Parameter mosa_angles must be "default", float, or dict[str, float], got {mosa_angles}'
                raise RuntimeError(msg)
        self.mosa_angles: Final[MosaDictFloat] = _mosa_angles

        # Interpolation and clock-noise inversion

        self.delays: Final = InstruDelays(
            interpolation,
            delay_isc_min,
            delay_isc_max,
            delay_clock_max,
            clockinv_tolerance,
            clockinv_maxiter,
            self.physics_fs,
        )
        # metadata
        self.clockinv_tolerance: Final = self.delays.clockinv_tolerance
        self.clockinv_maxiter: Final = self.delays.clockinv_maxiter
        self.interpolation_order: Final = self.delays.interpolation_order
        self.delay_isc_min: Final = self.delays.delay_isc_min
        self.delay_isc_max: Final = self.delays.delay_isc_max
        self.delay_clock_max: Final = self.delays.delay_clock_max

        # Antialiasing filter

        self._aafilter, self.aafilter_coeffs, self.aafilter_group_delay = init_aafilter(
            aafilter, self.physics_fs
        )

        # Electronic delays

        match electro_delays:
            case (scis, tmis, refs):
                self.electro_delays_scis: Final[MosaDictFloat] = param_mosa_dict_float(
                    scis, "electro_delays_checked[0]"
                )
                self.electro_delays_tmis: Final[MosaDictFloat] = param_mosa_dict_float(
                    tmis, "electro_delays_checked[1]"
                )
                self.electro_delays_refs: Final[MosaDictFloat] = param_mosa_dict_float(
                    refs, "electro_delays_checked[2]"
                )
            case _:
                msg = f"Parameter electro_delays must be tuple of length 3, got {electro_delays}"
                raise RuntimeError(msg)

        self._dopplers_disable = False

    def _make_noise_config(self):
        """Adaptor between noise parameters of Instrument class to new  InstruNoisesConfig

        This is a transitional method until the parameter handling of Instrument will be cleaned.
        """
        return InstruNoisesConfig(
            physics_fs=self.physics_fs,
            telemetry_fs=self.telemetry_fs,
            noises_fmin=self._noises_f_min_hz,
            laser_asds=make_mosa_id_dict(self.laser_asds),
            laser_shape=LaserNoiseShape(self.laser_shape),
            modulation_asds=make_mosa_id_dict(self.modulation_asds),
            ranging_asds=make_mosa_id_dict(self.ranging_asds),
            backlink_asds=make_mosa_id_dict(self.backlink_asds),
            backlink_fknees=make_mosa_id_dict(self.backlink_fknees),
            testmass_asds=make_mosa_id_dict(self.testmass_asds),
            testmass_fknees=make_mosa_id_dict(self.testmass_fknees),
            testmass_fbreak=make_mosa_id_dict(self.testmass_fbreak),
            testmass_frelax=make_mosa_id_dict(self.testmass_frelax),
            testmass_shape=TestMassNoiseShape(self.testmass_shape),
            oms_sci_carrier_asds=make_mosa_id_dict(self.oms_sci_carrier_asds),
            oms_sci_usb_asds=make_mosa_id_dict(self.oms_sci_usb_asds),
            oms_tmi_carrier_asds=make_mosa_id_dict(self.oms_tmi_carrier_asds),
            oms_tmi_usb_asds=make_mosa_id_dict(self.oms_tmi_usb_asds),
            oms_ref_carrier_asds=make_mosa_id_dict(self.oms_ref_carrier_asds),
            oms_ref_usb_asds=make_mosa_id_dict(self.oms_ref_usb_asds),
            oms_fknees=make_mosa_id_dict(self.oms_fknees),
            mosa_jitter_x_asds=make_mosa_id_dict(self.mosa_jitter_x_asds),
            mosa_jitter_phi_asds=make_mosa_id_dict(self.mosa_jitter_phi_asds),
            mosa_jitter_eta_asds=make_mosa_id_dict(self.mosa_jitter_eta_asds),
            mosa_jitter_phi_fknees=make_mosa_id_dict(self.mosa_jitter_phi_fknees),
            mosa_jitter_eta_fknees=make_mosa_id_dict(self.mosa_jitter_eta_fknees),
            dws_asds=make_mosa_id_dict(self.dws_asds),
            moc_time_correlation_asds=make_sat_id_dict(self.moc_time_correlation_asds),
            clock_asds=make_sat_id_dict(self.clock_asds),
            clock_fmin=self._clock_f_min_hz,
            sc_jitter_phi_asds=make_sat_id_dict(self.sc_jitter_phi_asds),
            sc_jitter_eta_asds=make_sat_id_dict(self.sc_jitter_eta_asds),
            sc_jitter_theta_asds=make_sat_id_dict(self.sc_jitter_theta_asds),
            sc_jitter_phi_fknees=make_sat_id_dict(self.sc_jitter_phi_fknees),
            sc_jitter_eta_fknees=make_sat_id_dict(self.sc_jitter_eta_fknees),
            sc_jitter_theta_fknees=make_sat_id_dict(self.sc_jitter_theta_fknees),
        )

    def get_noise_defs(self) -> InstruNoises:
        """Return object defining all instrumental noises"""
        return InstruNoises(self._make_noise_config(), self.seed)

    def _make_model_config(self) -> ModelConstellationCfg:
        """Collect parameters to model constellation

        This is an adaptor between user-facing interface given by the
        the Instrument class and the core functionality implemented in the
        ModelConstellation class.
        """
        return ModelConstellationCfg(
            size=self.size,
            t0=self.t0,
            dt=self.dt,
            physics_upsampling=self.physics_upsampling,
            telemetry_downsampling=self.telemetry_downsampling,
            initial_telemetry_size=self.initial_telemetry_size,
            lock=self.lock,
            clock_offsets=self.clock_offsets,
            clock_freqoffsets=self.clock_freqoffsets,
            clock_freqlindrifts=self.clock_freqlindrifts,
            clock_freqquaddrifts=self.clock_freqquaddrifts,
            central_freq=self.central_freq,
            offset_freqs=self.offset_freqs,
            modulation_freqs=self.modulation_freqs,
            dopplers_disable=self._dopplers_disable,
            prn_ambiguity=self.prn_ambiguity,
            ranging_biases=self.ranging_biases,
            mosa_angles=self.mosa_angles,
            ttl_coeffs_local_phis=self.ttl_coeffs_local_phis,
            ttl_coeffs_distant_phis=self.ttl_coeffs_distant_phis,
            ttl_coeffs_local_etas=self.ttl_coeffs_local_etas,
            ttl_coeffs_distant_etas=self.ttl_coeffs_distant_etas,
            electro_delays_scis=self.electro_delays_scis,
            electro_delays_tmis=self.electro_delays_tmis,
            electro_delays_refs=self.electro_delays_refs,
        )

    def disable_dopplers(self):
        """Set proper pseudo-range derivatives to zero to turn off Doppler effects."""
        logger.info("disable dopplers")
        self._dopplers_disable = True

    def disable_all_noises(
        self, excluding: set[str] | list[str] | str | None = None
    ) -> None:
        """Turn off all instrumental noises.

        Use ``excluding`` to specify a list of noises to keep.

        Note that Doppler effect is not considered as a noise, and won't be
        turned off by this method. Use `disable_dopplers()` to turn off Doppler
        effects.

        Args:
            excluding: noises to keep on, to be chosen in ('laser', 'modulation',
                'clock', 'test-mass', 'backlink', 'oms', 'ranging', 'angular-jitters', 'dws',
                'moc-time-correlation', 'longitudinal-jitters')
        """

        valid_noises = {
            "laser": self.disable_laser_noise,
            "modulation": self.disable_modulation_noise,
            "clock": self.disable_clock_noise,
            "test-mass": self.disable_testmass_noise,
            "backlink": self.disable_backlink_noise,
            "oms": self.disable_oms_noise,
            "ranging": self.disable_ranging_noises,
            "angular-jitters": self.disable_angular_jitters,
            "dws": self.disable_dws_noise,
            "moc-time-correlation": self.disable_moc_time_correlation_noise,
            "longitudinal-jitters": self.disable_longitudinal_jitters,
        }

        if excluding is None:
            excluding = []
        if isinstance(excluding, str):
            excluding = [excluding]

        for excluded in excluding:
            if excluded not in valid_noises:
                raise ValueError(f"unknown noise '{excluded}'")

        for name, disabler in valid_noises.items():
            if not name in excluding:
                disabler()

    def disable_laser_noise(self):
        """Turn off laser noise."""
        logger.info("disable laser noise")
        self.laser_asds = make_mosa_dict_const(0.0)

    def disable_modulation_noise(self):
        """Turn off sideband modulation noise."""
        logger.info("disable modulation noise")
        self.modulation_asds = make_mosa_dict_const(0.0)

    def disable_clock_noise(self):
        """Turn off all imperfections on clocks.

        This includes the in-band clock noise, as well as clock offsets,
        frequency offsets, and frequency linear and quadratic drifts.
        """
        logger.info("disable clock noise")
        self.clock_asds = make_sat_dict_const(0.0)
        self.clock_offsets = make_sat_dict_const(0.0)
        self.clock_freqoffsets = make_sat_dict_const(0.0)
        self.clock_freqlindrifts = make_sat_dict_const(0.0)
        self.clock_freqquaddrifts = make_sat_dict_const(0.0)

    def disable_testmass_noise(self):
        """Turn off all test-mass noise."""
        logger.info("disable testmass noise")
        self.testmass_asds = make_mosa_dict_const(0.0)

    def disable_backlink_noise(self):
        """Turn off all backlink noise."""
        logger.info("disable backlink noise")
        self.backlink_asds = make_mosa_dict_const(0.0)

    def disable_oms_noise(self):
        """Turn off OMS noise in all interferometers."""
        logger.info("disable oms noise")
        self.oms_sci_carrier_asds = make_mosa_dict_const(0.0)
        self.oms_sci_usb_asds = make_mosa_dict_const(0.0)
        self.oms_tmi_carrier_asds = make_mosa_dict_const(0.0)
        self.oms_tmi_usb_asds = make_mosa_dict_const(0.0)
        self.oms_ref_carrier_asds = make_mosa_dict_const(0.0)
        self.oms_ref_usb_asds = make_mosa_dict_const(0.0)

    def disable_ranging_noises(self):
        """Turn off all pseudo-ranging noises."""
        logger.info("disable ranging noise")
        self.ranging_biases = make_mosa_dict_const(0.0)
        self.ranging_asds = make_mosa_dict_const(0.0)

    def disable_angular_jitters(self):
        """Turn off all angular jitters."""
        logger.info("disable angular jitters")
        self.sc_jitter_phi_asds = make_sat_dict_const(0.0)
        self.sc_jitter_eta_asds = make_sat_dict_const(0.0)
        self.sc_jitter_theta_asds = make_sat_dict_const(0.0)
        self.mosa_jitter_phi_asds = make_mosa_dict_const(0.0)
        self.mosa_jitter_eta_asds = make_mosa_dict_const(0.0)

    def disable_dws_noise(self):
        """Turn off DWS measurement noise."""
        logger.info("disable dws noise")
        self.dws_asds = make_mosa_dict_const(0.0)

    def disable_moc_time_correlation_noise(self):
        """Turn off MOC time correlation noise."""
        logger.info("disable moc time correlation noise")
        self.moc_time_correlation_asds = make_sat_dict_const(0.0)

    def disable_longitudinal_jitters(self):
        """Turn off all longitudinal jitters."""
        logger.info("disable longitudinal jitters")
        self.mosa_jitter_x_asds = make_mosa_dict_const(0.0)

    def _log_sim_summary(self, bundle: StreamBundle) -> None:
        """Log metadata and stream setup"""

        logger.info("Simulation metadata")
        for md_key, md_val in self.metadata_dict().items():
            logger.info("%s = %s", md_key, md_val)

        allstreams = bundle.get_streams()
        logger.debug("Created %d streams", len(allstreams))
        for stream in allstreams.values():
            logger.debug(str(stream))

    def metadata_value(self, name: str) -> ValidMetaDataTypes:
        """Get a metadata item by name

        The purpose of this method is to convert the internal variables such that they
        can be stored in SimMetaData objects. Filter coefficients are stored as list.
        The tdir_modulations attribute is replaced by its string representation.

        To avoid confusion: this method has nothing to do with translating data into types
        that can be stored as HDF5 attributes when exporting to file. This sort of mapping
        happens in the streams.store_hdf5 module, for example, converting None to "None".

        This method was created to support transitioning the handling of user-facing metadata.
        Before the refactoring, there was no distinction between internal variables
        of the Instrument class and public metadata, users were just directly using the
        internals. There was a selected set that gets written to HDF5 attributes though.
        Those variables were mostly container objects holding float vaues for each MOSA
        or spacecraft, but also some variables that could be time series (fplan,
        ranging_bias) and one function object (lambda expression for tdir_modulations).
        When writing to hdf5, container and function objects were converted to strings.

        After the refactoring, user-facing metadata is provided as SimMetaData objects.
        This holds only simple short data, not time series or functions. In particular,
        it contains no streams. SimMetaData contains all metadata that would also be
        saved to HDF5. To keep the format changes to the minimum required to work with
        streams/long simulations, we still include all attributes that were exported originally,
        but replace data with problematic types with placeholder values. If there is any
        need to access those variables that suffer information loss, one still needs to
        use Instrument directly, keeping up with internal changes.
        """
        if not name in SimResultsNumpyFull.metadata_names:
            msg = f"Simulation results have no metadata named {name}"
            raise RuntimeError(msg)

        if name == "tdir_modulations":
            return str(self.tdir_modulations)

        v = getattr(self, name)
        u: ValidMetaDataTypes
        match v:
            case int() | float() | str() | None:
                u = v
            case list() if all((isinstance(e, (float, int)) for e in v)):
                u = v
            case dict() if all((isinstance(e, (float, int)) for e in v.values())):
                u = v
            case dict():
                u = {n: None for n in v}
            case _:
                msg = f"Unexpected type {type(v)} for field {name}"
                raise RuntimeError(msg)

        return u

    def metadata_dict(self) -> dict[str, ValidMetaDataTypes]:
        """Dictionary containing all metadata"""
        return {n: self.metadata_value(n) for n in SimResultsNumpyFull.metadata_names}

    def export_metadata(self) -> SimMetaData:
        """SimMetaData data class containing all metadata"""
        mdd: dict[str, Any] = self.metadata_dict()
        return SimMetaData(**mdd)

    def get_model(self) -> ModelConstellation:
        """Obtain constellation model for given Instrument parameters

        Returns:
            ModelConstellation
        """

        noises = self.get_noise_defs()
        cmcfg = self._make_model_config()

        tdir_modulations: dict[str, Callable | None] = {}
        for m in MosaID.names():
            tdir_modulations[m] = (
                None if self.tdir_modulations is None else self.tdir_modulations[m]
            )

        return ModelConstellation(
            noises,
            self.orbit_source,
            self.fplansrc,
            self.gwsrc,
            self.glitchsrc,
            tdir_modulations,
            self.delays,
            self._aafilter,
            cmcfg,
        )

    def stream_bundle(self) -> StreamBundle:
        """Present simulation model as StreamBundle

        This is used when exporting to HDF5 or numpy arrays.

        Returns:
            StreamBundle from which one compute the simulation results
        """
        model = self.get_model()
        bundle = model.get_streams()
        self._log_sim_summary(bundle)
        return bundle

    def simulate(self):
        """Deprecated method which is not needed anymore

        This used to do the computation, but since the switch to chunked processing that
        happens when exporting the data
        """
        logger.warning(
            "Calling the simulate method is not required anymore and does nothing"
        )

    def write(
        self, output="measurements.h5", mode: Literal["w", "w-"] = "w-", keep_all=False
    ):
        """Deprecated interface, use export_hdf5 instead in new code.

        This will create an HDF5 file with the time series and metadata
        of the simulation. By default, only a standard set of time series
        is included.

        Note: it is not required anymore to call simulation before using this.

        Arguments:
            output: path of the file to use
            mode: truncate existing files ('w') or fail ('w-')
            keep_all: store all time series, not just the standard set.
        """

        overwrite = {"w": True, "w-": False}[mode]
        logger.info("Writing simulation to '%s'", output)
        self.export_hdf5(output, overwrite=overwrite, keep_all=keep_all)

    def export_hdf5(
        self,
        path="measurements.h5",
        *,
        description: str | None = None,
        overwrite=False,
        keep_all=False,
        cfgscheduler: SchedulerConfigTypes | None = None,
    ):
        """Compute simulation and store results in a hdf5 file.

        This will create an HDF5 file with the time series and metadata
        of the simulation. By default, only a standard set of time series
        is included.

        By default, the streams are evaluated with conservative resource usage. The
        number of CPUs and memory usage can be adjusted with cfgscheduler parameter (see
        streams.scheduler).

        Arguments:
            path: Path of the file to use
            overwrite: If True, any existing file will be overwritten.
            keep_all: store all time series, not just the standard set.
            cfgscheduler: Parameters for the scheduling
        """

        meta = self.metadata_dict()
        source = self.stream_bundle()

        datasets = (
            SimResultsNumpyFull.dataset_identifier_set()
            if keep_all
            else SimResultsNumpyCore.dataset_identifier_set()
        )

        store_instru_hdf5(
            path,
            source,
            meta,
            datasets=datasets,
            description=description,
            overwrite=overwrite,
            cfgscheduler=cfgscheduler,
        )

    def _export_numpy_gen(
        self,
        cls: type[_T],
        cfgscheduler: SchedulerConfigTypes | None = None,
    ) -> _T:
        """Compute simulation and store all results in memory as numpy arrays

        The resulting object has the full set of data attributes for results of the
        simulation evaluated as numpy arrays, as well as the metadata.

        This should only be called if the data is expected to fit the available memory.

        By default, the streams are evaluated with conservative resource usage. The
        number of CPUs and memory usage can be adjusted with cfgscheduler parameter (see
        streams.scheduler).

        Arguments:
            cfgscheduler: Parameters for the scheduling

        Returns:
            SimResultsNumpyFull instance with simulation full results
        """

        model = self.get_model()
        source = model.get_streams()
        self._log_sim_summary(source)
        datasets = cls.dataset_identifier_set()
        store = store_bundle_numpy(source, datasets, cfgscheduler=cfgscheduler)
        data = store.as_dict()
        ranges = model.output_ranges()
        return cls(data, ranges, self.metadata_dict())

    def export_numpy_full(
        self,
        cfgscheduler: SchedulerConfigTypes | None = None,
    ) -> SimResultsNumpyFull:
        """Compute simulation and store all results in memory as numpy arrays

        The resulting object has the full set of data attributes for results of the
        simulation evaluated as numpy arrays, as well as the metadata.

        This should only be called if the data is expected to fit the available memory.

        By default, the streams are evaluated with conservative resource usage. The
        number of CPUs and memory usage can be adjusted with cfgscheduler parameter (see
        streams.scheduler).

        Arguments:
            cfgscheduler: Parameters for the scheduling

        Returns:
            SimResultsNumpyFull instance with simulation full results
        """
        return self._export_numpy_gen(SimResultsNumpyFull, cfgscheduler)

    def export_numpy_core(
        self,
        cfgscheduler: SchedulerConfigTypes | None = None,
    ) -> SimResultsNumpyCore:
        """Compute simulation and store all results in memory as numpy arrays

        The resulting object has the core data data attributes for results of the
        simulation evaluated as numpy arrays, as well as the metadata.

        This should only be called if the data is expected to fit the available memory.

        By default, the streams are evaluated with conservative resource usage. The
        number of CPUs and memory usage can be adjusted with cfgscheduler parameter (see
        streams.scheduler).

        Arguments:
            cfgscheduler: Parameters for the scheduling

        Returns:
            SimResultsNumpyCore instance with simulation core results
        """
        return self._export_numpy_gen(SimResultsNumpyCore, cfgscheduler)

    def export_numpy(
        self,
        *,
        keep_all: bool,
        cfgscheduler: SchedulerConfigTypes | None = None,
    ) -> SimResultsNumpyCore | SimResultsNumpyFull:
        """Compute simulation and store all results in memory as numpy arrays

        This returns either the full or a core set of simulation results,
        see export_numpy_core and export_numpy_full methods.

        Note: Using this method hinders static type checking for attributes
        of the resulting object. Use export_numpy_core or export_numpy_full
        if possible.

        Arguments:
            keep_all: If True, store all time series, else just the standard set.
            cfgscheduler: Parameters for the scheduling

        Returns:
            Simulation results
        """
        if keep_all:
            return self.export_numpy_full(cfgscheduler)
        return self.export_numpy_core(cfgscheduler)
