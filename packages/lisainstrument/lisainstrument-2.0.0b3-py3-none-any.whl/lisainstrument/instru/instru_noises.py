"""The instru.instru_noises module handles the configuration of all noise parameters in the simulator

The InstruNoisesConfig class collects all noise related parameters. The
InstruNoises class provides noise definitions in terms of NoiseDefBase,
which can be used to generate noises.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from lisainstrument.noisy import (
    LaserNoiseShape,
    NoiseDefAngularJitter,
    NoiseDefBacklink,
    NoiseDefBase,
    NoiseDefClock,
    NoiseDefDWS,
    NoiseDefLaser,
    NoiseDefLongitudinalJitter,
    NoiseDefMocTimeCorrelation,
    NoiseDefModulation,
    NoiseDefOMS,
    NoiseDefRanging,
    NoiseDefTestMass,
    TestMassNoiseShape,
)
from lisainstrument.orbiting.constellation_enums import MosaID, SatID


@dataclass(frozen=True)
class InstruNoisesConfig:
    """Immutable data class collecting all parameters needed to generate the noises"""

    physics_fs: float
    telemetry_fs: float
    noises_fmin: float
    laser_asds: dict[MosaID, float]
    laser_shape: LaserNoiseShape
    modulation_asds: dict[MosaID, float]
    ranging_asds: dict[MosaID, float]
    backlink_asds: dict[MosaID, float]
    backlink_fknees: dict[MosaID, float]
    testmass_asds: dict[MosaID, float]
    testmass_fknees: dict[MosaID, float]
    testmass_fbreak: dict[MosaID, float]
    testmass_frelax: dict[MosaID, float]
    testmass_shape: TestMassNoiseShape
    oms_sci_carrier_asds: dict[MosaID, float]
    oms_sci_usb_asds: dict[MosaID, float]
    oms_tmi_carrier_asds: dict[MosaID, float]
    oms_tmi_usb_asds: dict[MosaID, float]
    oms_ref_carrier_asds: dict[MosaID, float]
    oms_ref_usb_asds: dict[MosaID, float]
    oms_fknees: dict[MosaID, float]
    mosa_jitter_x_asds: dict[MosaID, float]
    mosa_jitter_phi_asds: dict[MosaID, float]
    mosa_jitter_eta_asds: dict[MosaID, float]
    mosa_jitter_phi_fknees: dict[MosaID, float]
    mosa_jitter_eta_fknees: dict[MosaID, float]
    dws_asds: dict[MosaID, float]
    moc_time_correlation_asds: dict[SatID, float]
    clock_asds: dict[SatID, float]
    clock_fmin: float
    sc_jitter_phi_asds: dict[SatID, float]
    sc_jitter_eta_asds: dict[SatID, float]
    sc_jitter_theta_asds: dict[SatID, float]
    sc_jitter_phi_fknees: dict[SatID, float]
    sc_jitter_eta_fknees: dict[SatID, float]
    sc_jitter_theta_fknees: dict[SatID, float]


class InstruNoises:  # pylint: disable = too-many-public-methods
    """Class providing the definition for any noise in the instrument simulator

    The purpose is to provide a unified view of all noises. Instead of working
    with heterogenuous parametrizations of the different noises, InstruNoise
    instances provide a method defining each noise via the NoiseDefBase
    protocol. The latter can be used directly to generate noise with any of the
    noise generators in the lisainstrument.noisy or lisainstrument.streams
    packages. Besides the noise definitions, this also stores a master seed
    value.
    """

    def __init__(self, config: InstruNoisesConfig, seed: int) -> None:
        """Constructor

        Arguments:
            config: InstruNoisesConfig instance with all noise parameters
            seed: master seed value
        """
        self._config = config
        self._seed = seed

    @property
    def seed(self) -> int:
        """Master seed value"""
        return self._seed

    def modified(self, **args) -> InstruNoises:
        """Return another instance with same seed but selected parameters modified"""
        newcfg = replace(self._config, **args)
        return InstruNoises(newcfg, self._seed)

    def noise_def_clock(self, sc: SatID) -> NoiseDefBase:
        """Definition of clock noise used for given spacecraft"""
        cfg = self._config
        return NoiseDefClock(
            asd_onesided_at_1hz=cfg.clock_asds[sc],
            f_min_hz=cfg.clock_fmin,
            f_sample=cfg.physics_fs,
            name=f"clock_{sc.value}",
        )

    def noise_def_modulation(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of modulation noise used for given MOSA"""
        cfg = self._config
        return NoiseDefModulation(
            asd_onesided_at_1hz=cfg.modulation_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_sample=cfg.physics_fs,
            name=f"modulation_{mosa.value}",
        )

    def noise_def_backlink(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of backlink noise used for given MOSA"""
        cfg = self._config
        return NoiseDefBacklink(
            displacement_asd_onesided=cfg.backlink_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.backlink_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"backlink_{mosa.value}",
        )

    def noise_def_testmass(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of testmass noise used for given MOSA"""
        cfg = self._config
        return NoiseDefTestMass(
            accel_asd_onesided=cfg.testmass_asds[mosa],
            shape=cfg.testmass_shape,
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.testmass_fknees[mosa],
            f_break_hz=cfg.testmass_fbreak[mosa],
            f_relax_hz=cfg.testmass_frelax[mosa],
            f_sample=cfg.physics_fs,
            name=f"testmass_{mosa.value}",
        )

    def noise_def_ranging(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of ranging noise used for given MOSA"""
        cfg = self._config
        return NoiseDefRanging(
            asd_onesided_const=cfg.ranging_asds[mosa],
            f_sample=cfg.physics_fs,
            name=f"ranging_{mosa.value}",
        )

    def noise_def_oms_sci_carrier(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS ISI carrier noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_sci_carrier_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_sci_carrier_{mosa.value}",
        )

    def noise_def_oms_sci_usb(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS ISI usb noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_sci_usb_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_sci_usb_{mosa.value}",
        )

    def noise_def_oms_tmi_carrier(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS TMI carrier noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_tmi_carrier_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_tmi_carrier_{mosa.value}",
        )

    def noise_def_oms_tmi_usb(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS TMI usb noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_tmi_usb_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_tmi_usb_{mosa.value}",
        )

    def noise_def_oms_ref_carrier(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS RFI carrier noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_ref_carrier_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_ref_carrier_{mosa.value}",
        )

    def noise_def_oms_ref_usb(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of OMS RFI usb noise used for given MOSA"""
        cfg = self._config
        return NoiseDefOMS(
            displacement_asd_onesided=cfg.oms_ref_usb_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.oms_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"oms_ref_usb_{mosa.value}",
        )

    def noise_def_dws_phi(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of DWS phi angle noise used for given MOSA"""
        cfg = self._config
        return NoiseDefDWS(
            angle_asd_onesided=cfg.dws_asds[mosa],
            f_sample=cfg.physics_fs,
            name=f"dws_phi_{mosa.value}",
        )

    def noise_def_dws_eta(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of DWS eta angle noise used for given MOSA"""
        cfg = self._config
        return NoiseDefDWS(
            angle_asd_onesided=cfg.dws_asds[mosa],
            f_sample=cfg.physics_fs,
            name=f"dws_eta_{mosa.value}",
        )

    def noise_def_moc_time_correlation(self, sc: SatID) -> NoiseDefBase:
        """Definition of MOC time correlation noise used for given spacecraft"""
        cfg = self._config
        return NoiseDefMocTimeCorrelation(
            asd_onesided_const=cfg.moc_time_correlation_asds[sc],
            f_sample=cfg.telemetry_fs,
            name=f"moc_time_correlation_{sc.value}",
        )

    def noise_def_mosa_jitter_xs(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of longitudinal noise used for given MOSA"""
        cfg = self._config
        return NoiseDefLongitudinalJitter(
            displacement_asd_onesided=cfg.mosa_jitter_x_asds[mosa],
            f_sample=cfg.physics_fs,
            name=f"mosa_jitter_xs_{mosa.value}",
        )

    def noise_def_sc_jitter_phis(self, sc: SatID) -> NoiseDefBase:
        """Definition of spacecraft phi-angle noise used for given spacecraft"""
        cfg = self._config
        return NoiseDefAngularJitter(
            angle_asd_onesided=cfg.sc_jitter_phi_asds[sc],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.sc_jitter_phi_fknees[sc],
            f_sample=cfg.physics_fs,
            name=f"sc_jitter_phis_{sc.value}",
        )

    def noise_def_sc_jitter_etas(self, sc: SatID) -> NoiseDefBase:
        """Definition of spacecraft eta-angle noise used for given spacecraft"""
        cfg = self._config
        return NoiseDefAngularJitter(
            angle_asd_onesided=cfg.sc_jitter_eta_asds[sc],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.sc_jitter_eta_fknees[sc],
            f_sample=cfg.physics_fs,
            name=f"sc_jitter_eta_{sc.value}",
        )

    def noise_def_sc_jitter_thetas(self, sc: SatID) -> NoiseDefBase:
        """Definition of spacecraft theta-angle noise used for given spacecraft"""
        cfg = self._config
        return NoiseDefAngularJitter(
            angle_asd_onesided=cfg.sc_jitter_theta_asds[sc],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.sc_jitter_theta_fknees[sc],
            f_sample=cfg.physics_fs,
            name=f"sc_jitter_theta_{sc.value}",
        )

    def noise_def_mosa_jitter_phis(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of phi-angle noise used for given MOSA"""
        cfg = self._config
        return NoiseDefAngularJitter(
            angle_asd_onesided=cfg.mosa_jitter_phi_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.mosa_jitter_phi_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"mosa_jitter_phi_{mosa.value}",
        )

    def noise_def_mosa_jitter_etas(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of eta-angle noise used for given MOSA"""
        cfg = self._config
        return NoiseDefAngularJitter(
            angle_asd_onesided=cfg.mosa_jitter_eta_asds[mosa],
            f_min_hz=cfg.noises_fmin,
            f_knee_hz=cfg.mosa_jitter_eta_fknees[mosa],
            f_sample=cfg.physics_fs,
            name=f"mosa_jitter_eta_{mosa.value}",
        )

    def noise_def_laser(self, mosa: MosaID) -> NoiseDefBase:
        """Definition of laser noise used for given MOSA"""
        cfg = self._config
        return NoiseDefLaser(
            asd_onesided_const=cfg.laser_asds[mosa],
            shape=cfg.laser_shape,
            f_min_hz=cfg.noises_fmin,
            f_sample=cfg.physics_fs,
            name=f"laser_{mosa.value}",
        )
