"""This module collect all formulas relating the simulated timeseries

The expressions are formulated using normal numpy arrays. Support for
streams is added using the stream_expression decorator, which turns
numpy positional arguments into arguments accepting StreamBase instances.
Keyword-only arguments are used to pass parameters that are not time
series. Under no circumstance should keyword-only arguments in this module
be used to pass time series of any form.

Most formulas will be applied to all MOSAs or spacecrafts, passing
dictionaries those arguments that depend on MOSA/SC. Those functions
are decorated by for_each_sat or for_each_mosa, which handle the
iteration.
"""

from typing import Callable

import numpy as np
from lisaconstants import SPEED_OF_LIGHT as C_SI

from lisainstrument.orbiting.constellation_enums import for_each_mosa, for_each_sat
from lisainstrument.streams import StreamBase, StreamConst, stream_expression


@for_each_sat
@stream_expression(np.float64)
def scet_wrt_tps_local(
    t_: np.ndarray,
    integrated_clock_noise_fluctuations_: np.ndarray | float,
    *,
    clock_offsets: float,
    clock_freqoffsets: float,
    clock_freqlindrifts: float,
    clock_freqquaddrifts: float,
) -> np.ndarray:
    """Compute scet_wrt_tps_local"""
    return (
        clock_offsets
        + clock_freqoffsets * t_
        + (clock_freqlindrifts / 2) * t_**2
        + (clock_freqquaddrifts / 3) * t_**3
        + integrated_clock_noise_fluctuations_
    )


@for_each_sat
@stream_expression(np.float64)
def scet_wrt_tcb_withinitial(
    t_: np.ndarray,
    tps_wrt_tcb_: np.ndarray | float,
    clock_noise_fluctuations_covering_telemetry_: np.ndarray | float,
    integrated_clock_noise_fluctuations_covering_telemetry_: np.ndarray | float,
    *,
    clock_offsets: float,
    clock_freqoffsets: float,
    clock_freqlindrifts: float,
    clock_freqquaddrifts: float,
) -> np.ndarray:
    """Compute scet_wrt_tcb_withinitial"""
    tplus = t_ + tps_wrt_tcb_
    return (
        tps_wrt_tcb_
        + clock_offsets
        + clock_freqoffsets * tplus
        + (clock_freqlindrifts / 2) * tplus**2
        + (clock_freqquaddrifts / 3) * tplus**3
        + tps_wrt_tcb_ * clock_noise_fluctuations_covering_telemetry_
        + integrated_clock_noise_fluctuations_covering_telemetry_
    )


@for_each_sat
@stream_expression(np.float64)
def moc_time_correlations(
    moc_time_correlation_noises_: np.ndarray | float,
    scet_wrt_tcb_telemetry_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute moc_time_correlations"""
    return moc_time_correlation_noises_ + scet_wrt_tcb_telemetry_


@stream_expression(np.float64)
def local_usb_offsets(
    local_carrier_offsets_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    *,
    modulation_freqs: float,
) -> np.ndarray | float:
    """Compute local_usb_offsets"""
    return local_carrier_offsets_ + modulation_freqs * (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def tdir_modulations_tseries(
    physics_et_: np.ndarray,
    scet_wrt_tps_local_: np.ndarray,
    *,
    tdir_modulations: Callable[[np.ndarray], np.ndarray] | None,
) -> np.ndarray:
    """Compute tdir_modulations_tseries"""
    if tdir_modulations is None:
        return np.zeros_like(physics_et_)
    return tdir_modulations(physics_et_ + scet_wrt_tps_local_)


@stream_expression(np.float64)
def local_usb_fluctuations(
    local_carrier_fluctuations_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
    modulation_noises_: np.ndarray | float,
    *,
    modulation_freqs: float,
) -> np.ndarray | float:
    """Compute local_usb_fluctuations"""
    return local_carrier_fluctuations_ + modulation_freqs * (
        clock_noise_fluctuations_ + modulation_noises_
    )


@stream_expression(np.float64)
def distant_carrier_offsets(
    d_pprs_: np.ndarray | float,
    delayed_distant_carrier_offsets_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute distant_carrier_offsets"""
    return -d_pprs_ * central_freq + (1 - d_pprs_) * delayed_distant_carrier_offsets_


@stream_expression(np.float64)
def carrier_fluctuations(
    local_carrier_fluctuations_: np.ndarray | float,
    local_carrier_offsets_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    distant_ttls_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute carrier_fluctuations"""
    return (
        local_carrier_fluctuations_
        - (central_freq + local_carrier_offsets_)
        * (distant_ttls_ - mosa_jitter_xs_)
        / C_SI
    )


@stream_expression(np.float64)
def propagated_carrier_fluctuations(
    d_pprs_: np.ndarray | float,
    delayed_distant_carrier_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute propagated_carrier_fluctuations"""
    return (1 - d_pprs_) * delayed_distant_carrier_fluctuations_


@stream_expression(np.float64)
def distant_carrier_fluctuations(
    propagated_carrier_fluctuations_: np.ndarray | float,
    delayed_distant_carrier_offsets_: np.ndarray | float,
    gws_: np.ndarray | float,
    local_ttls_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute distant_carrier_fluctuations"""
    distant_carrier = central_freq + delayed_distant_carrier_offsets_
    return (
        propagated_carrier_fluctuations_
        + distant_carrier * gws_
        - distant_carrier * (local_ttls_ - mosa_jitter_xs_) / C_SI
    )


@for_each_mosa
@stream_expression(np.float64)
def distant_usb_offsets(
    d_pprs_: np.ndarray | float,
    delayed_distant_usb_offsets_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute distant_usb_offsets"""
    return -d_pprs_ * central_freq + (1 - d_pprs_) * delayed_distant_usb_offsets_


@for_each_mosa
@stream_expression(np.float64)
def usb_fluctuations(
    local_usb_fluctuations_: np.ndarray | float,
    local_usb_offsets_: np.ndarray | float,
    distant_ttls_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute usb_fluctuations"""
    return (
        local_usb_fluctuations_
        - (central_freq + local_usb_offsets_) * (distant_ttls_ - mosa_jitter_xs_) / C_SI
    )


@for_each_mosa
@stream_expression(np.float64)
def propagated_usb_fluctuations(
    d_pprs_: np.ndarray | float, delayed_distant_usb_fluctuations_: np.ndarray | float
) -> np.ndarray | float:
    """Compute propagated_usb_fluctuations"""
    return (1 - d_pprs_) * delayed_distant_usb_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def distant_usb_fluctuations(
    propagated_usb_fluctuations_: np.ndarray | float,
    delayed_distant_usb_offsets_: np.ndarray | float,
    gws_: np.ndarray | float,
    local_ttls_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute distant_usb_fluctuations"""
    distant_freq = central_freq + delayed_distant_usb_offsets_
    return (
        propagated_usb_fluctuations_
        + distant_freq * gws_
        - distant_freq * (local_ttls_ - mosa_jitter_xs_) / C_SI
    )


@for_each_mosa
@stream_expression(np.float64)
def scet_wrt_tps_distant(
    delayed_distant_scet_wrt_tps_: np.ndarray | float, pprs_: np.ndarray | float
) -> np.ndarray | float:
    """Compute scet_wrt_tps_distant"""
    return delayed_distant_scet_wrt_tps_ - pprs_


@stream_expression(np.float64)
def adjacent_carrier_fluctuations(
    local_carrier_fluctuations_: np.ndarray | float,
    backlink_noises_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute adjacent_carrier_fluctuations"""
    return local_carrier_fluctuations_ + central_freq * backlink_noises_


@stream_expression(np.float64)
def adjacent_usb_fluctuations(
    adjacent_usb_fluctuations_: np.ndarray | float,
    backlink_noises_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute adjacent_usb_fluctuations"""
    return adjacent_usb_fluctuations_ + central_freq * backlink_noises_


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_carrier_offsets(
    distant_sci_carrier_offsets_: np.ndarray | float,
    local_sci_carrier_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_sci_carrier_offsets"""
    return distant_sci_carrier_offsets_ - local_sci_carrier_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_carrier_fluctuations(
    distant_sci_carrier_fluctuations_: np.ndarray | float,
    local_sci_carrier_fluctuations_: np.ndarray | float,
    oms_sci_carrier_noises_: np.ndarray | float,
    glitch_readout_sci_carriers_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_sci_carrier_fluctuations"""
    return (
        distant_sci_carrier_fluctuations_
        - local_sci_carrier_fluctuations_
        + central_freq * oms_sci_carrier_noises_
        + glitch_readout_sci_carriers_
    )


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_usb_offsets(
    distant_sci_usb_offsets_: np.ndarray | float,
    local_sci_usb_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_sci_usb_offsets"""
    return distant_sci_usb_offsets_ - local_sci_usb_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_usb_fluctuations(
    distant_sci_usb_fluctuations_: np.ndarray | float,
    local_sci_usb_fluctuations_: np.ndarray | float,
    oms_sci_usb_noises_: np.ndarray | float,
    glitch_readout_sci_usbs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_sci_usb_fluctuations"""
    return (
        distant_sci_usb_fluctuations_
        - local_sci_usb_fluctuations_
        + central_freq * oms_sci_usb_noises_
        + glitch_readout_sci_usbs_
    )


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_dws_phis(
    mosa_total_jitter_phis_: np.ndarray | float, dws_phi_noises_: np.ndarray | float
) -> np.ndarray | float:
    """Compute tps_sci_dws_phis"""
    return mosa_total_jitter_phis_ + dws_phi_noises_


@for_each_mosa
@stream_expression(np.float64)
def tps_sci_dws_etas(
    mosa_total_jitter_etas_: np.ndarray | float,
    dws_eta_noises_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_sci_dws_etas"""
    return mosa_total_jitter_etas_ + dws_eta_noises_


@stream_expression(np.float64)
def tps_mprs(
    scet_wrt_tps_local_: np.ndarray | float,
    scet_wrt_tps_distant_: np.ndarray | float,
    ranging_noises_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_mprs"""
    return scet_wrt_tps_local_ - scet_wrt_tps_distant_ + ranging_noises_


@for_each_mosa
@stream_expression(np.float64)
def local_tmi_carrier_fluctuations(
    local_carrier_fluctuations_: np.ndarray | float,
    local_tmi_carrier_offsets_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    testmass_noises_: np.ndarray | float,
    glitch_tms_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute local_tmi_carrier_fluctuations"""
    return local_carrier_fluctuations_ - (central_freq + local_tmi_carrier_offsets_) * (
        mosa_jitter_xs_ - testmass_noises_ - glitch_tms_
    ) * (2 / C_SI)


@for_each_mosa
@stream_expression(np.float64)
def local_tmi_usb_fluctuations(
    local_usb_fluctuations_: np.ndarray | float,
    local_tmi_usb_offsets_: np.ndarray | float,
    mosa_jitter_xs_: np.ndarray | float,
    testmass_noises_: np.ndarray | float,
    glitch_tms_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute local_tmi_usb_fluctuations"""
    return local_usb_fluctuations_ - (central_freq + local_tmi_usb_offsets_) * (
        mosa_jitter_xs_ - testmass_noises_ - glitch_tms_
    ) * (2 / C_SI)


@for_each_mosa
@stream_expression(np.float64)
def tps_tmi_carrier_offsets(
    adjacent_tmi_carrier_offsets_: np.ndarray | float,
    local_tmi_carrier_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_tmi_carrier_offsets"""
    return adjacent_tmi_carrier_offsets_ - local_tmi_carrier_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_tmi_carrier_fluctuations(
    adjacent_tmi_carrier_fluctuations_: np.ndarray | float,
    local_tmi_carrier_fluctuations_: np.ndarray | float,
    oms_tmi_carrier_noises_: np.ndarray | float,
    glitch_readout_tmi_carriers_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_tmi_carrier_fluctuations"""
    return (
        adjacent_tmi_carrier_fluctuations_
        - local_tmi_carrier_fluctuations_
        + central_freq * oms_tmi_carrier_noises_
        + glitch_readout_tmi_carriers_
    )


@for_each_mosa
@stream_expression(np.float64)
def tps_tmi_usb_offsets(
    adjacent_tmi_usb_offsets_: np.ndarray | float,
    local_tmi_usb_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_tmi_usb_offsets"""
    return adjacent_tmi_usb_offsets_ - local_tmi_usb_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_tmi_usb_fluctuations(
    adjacent_tmi_usb_fluctuations_: np.ndarray | float,
    local_tmi_usb_fluctuations_: np.ndarray | float,
    oms_tmi_usb_noises_: np.ndarray | float,
    glitch_readout_tmi_usbs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_tmi_usb_fluctuations"""
    return (
        adjacent_tmi_usb_fluctuations_
        - local_tmi_usb_fluctuations_
        + central_freq * oms_tmi_usb_noises_
        + glitch_readout_tmi_usbs_
    )


@for_each_mosa
@stream_expression(np.float64)
def tps_ref_carrier_offsets(
    adjacent_ref_carrier_offsets_: np.ndarray | float,
    local_ref_carrier_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_ref_carrier_offsets"""
    return adjacent_ref_carrier_offsets_ - local_ref_carrier_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_ref_usb_offsets(
    adjacent_ref_usb_offsets_: np.ndarray | float,
    local_ref_usb_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tps_ref_usb_offsets"""
    return adjacent_ref_usb_offsets_ - local_ref_usb_offsets_


@for_each_mosa
@stream_expression(np.float64)
def tps_ref_carrier_fluctuations(
    adjacent_ref_carrier_fluctuations_: np.ndarray | float,
    local_ref_carrier_fluctuations_: np.ndarray | float,
    oms_ref_carrier_noises_: np.ndarray | float,
    glitch_readout_ref_carriers_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_ref_carrier_fluctuations"""
    return (
        adjacent_ref_carrier_fluctuations_
        - local_ref_carrier_fluctuations_
        + central_freq * oms_ref_carrier_noises_
        + glitch_readout_ref_carriers_
    )


@for_each_mosa
@stream_expression(np.float64)
def tps_ref_usb_fluctuations(
    adjacent_ref_usb_fluctuations_: np.ndarray | float,
    local_ref_usb_fluctuations_: np.ndarray | float,
    oms_ref_usb_noises_: np.ndarray | float,
    glitch_readout_ref_usbs_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute tps_ref_usb_fluctuations"""
    return (
        adjacent_ref_usb_fluctuations_
        - local_ref_usb_fluctuations_
        + central_freq * oms_ref_usb_noises_
        + glitch_readout_ref_usbs_
    )


@stream_expression(np.float64)
def scet_sci_carrier_offsets_preshift(
    tps_sci_carrier_offsets_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_sci_carrier_offsets_preshift"""
    return tps_sci_carrier_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_sci_carrier_fluctuations_preshift(
    tps_sci_carrier_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_sci_carrier_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_sci_carrier_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_sci_carrier_fluctuations_ / cno_plus1
        - tps_sci_carrier_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@stream_expression(np.float64)
def scet_sci_usb_offsets_preshift(
    tps_sci_usb_offsets_: np.ndarray | float, clock_noise_offsets_: np.ndarray | float
) -> np.ndarray | float:
    """Compute scet_sci_usb_offsets_preshift"""
    return tps_sci_usb_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_sci_usb_fluctuations_preshift(
    tps_sci_usb_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_sci_usb_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_sci_usb_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_sci_usb_fluctuations_ / cno_plus1
        - tps_sci_usb_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@stream_expression(np.float64)
def scet_tmi_carrier_offsets_preshift(
    tps_tmi_carrier_offsets_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_tmi_carrier_offsets_preshift"""
    return tps_tmi_carrier_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_tmi_carrier_fluctuations_preshift(
    tps_tmi_carrier_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_tmi_carrier_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_tmi_carrier_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_tmi_carrier_fluctuations_ / cno_plus1
        - tps_tmi_carrier_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@stream_expression(np.float64)
def scet_tmi_usb_offsets_preshift(
    tps_tmi_usb_offsets_: np.ndarray | float, clock_noise_offsets_: np.ndarray | float
) -> np.ndarray | float:
    """Compute scet_tmi_usb_offsets_preshift"""
    return tps_tmi_usb_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_tmi_usb_fluctuations_preshift(
    tps_tmi_usb_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_tmi_usb_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_tmi_usb_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_tmi_usb_fluctuations_ / cno_plus1
        - tps_tmi_usb_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@stream_expression(np.float64)
def scet_ref_carrier_offsets_preshift(
    tps_ref_carrier_offsets_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_ref_carrier_offsets_preshift"""
    return tps_ref_carrier_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_ref_carrier_fluctuations_preshift(
    tps_ref_carrier_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_ref_carrier_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_ref_carrier_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_ref_carrier_fluctuations_ / cno_plus1
        - tps_ref_carrier_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@stream_expression(np.float64)
def scet_ref_usb_offsets_preshift(
    tps_ref_usb_offsets_: np.ndarray | float, clock_noise_offsets_: np.ndarray | float
) -> np.ndarray | float:
    """Compute scet_ref_usb_offsets_preshift"""
    return tps_ref_usb_offsets_ / (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def scet_ref_usb_fluctuations_preshift(
    tps_ref_usb_fluctuations_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
    tps_ref_usb_offsets_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute scet_ref_usb_fluctuations_preshift"""
    cno_plus1 = 1 + clock_noise_offsets_
    return (
        tps_ref_usb_fluctuations_ / cno_plus1
        - tps_ref_usb_offsets_ * clock_noise_fluctuations_ / cno_plus1**2
    )


@for_each_mosa
@stream_expression(np.float64)
def mprs(
    mprs_unambiguous_: np.ndarray | float, *, prn_ambiguity: float | None
) -> np.ndarray | float:
    """Compute mprs"""
    if prn_ambiguity is None:
        return mprs_unambiguous_
    return np.mod(mprs_unambiguous_, prn_ambiguity / C_SI)


@stream_expression(np.float64)
def mosa_total_jitter_etas(
    sc_jitter_etas_: np.ndarray | float,
    sc_jitter_thetas_: np.ndarray | float,
    mosa_jitter_etas_: np.ndarray | float,
    *,
    mosa_angles: float,
) -> np.ndarray | float:
    """Compute mosa_total_jitter_etas"""
    mosa_angles_rad = mosa_angles * np.pi / 180
    cos_mosa_angles = np.cos(mosa_angles_rad)
    sin_mosa_angles = np.sin(mosa_angles_rad)
    return (
        cos_mosa_angles * sc_jitter_etas_
        - sin_mosa_angles * sc_jitter_thetas_
        + mosa_jitter_etas_
    )


@for_each_mosa
@stream_expression(np.float64)
def sci_carriers(
    sci_carrier_offsets_: np.ndarray | float,
    sci_carrier_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute sci_carriers"""
    return sci_carrier_offsets_ + sci_carrier_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def sci_usbs(
    sci_usb_offsets_: np.ndarray | float, sci_usb_fluctuations_: np.ndarray | float
) -> np.ndarray | float:
    """Compute sci_usbs"""
    return sci_usb_offsets_ + sci_usb_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def tmi_carriers(
    tmi_carrier_offsets_: np.ndarray | float,
    tmi_carrier_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tmi_carriers"""
    return tmi_carrier_offsets_ + tmi_carrier_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def tmi_usbs(
    tmi_usb_offsets_: np.ndarray | float,
    tmi_usb_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute tmi_usbs"""
    return tmi_usb_offsets_ + tmi_usb_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def ref_carriers(
    ref_carrier_offsets_: np.ndarray | float,
    ref_carrier_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute ref_carriers"""
    return ref_carrier_offsets_ + ref_carrier_fluctuations_


@for_each_mosa
@stream_expression(np.float64)
def ref_usbs(
    ref_usb_offsets_: np.ndarray | float,
    ref_usb_fluctuations_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute ref_usbs"""
    return ref_usb_offsets_ + ref_usb_fluctuations_


@stream_expression(np.float64)
def clock_noise_drift(
    t_: np.ndarray,
    *,
    freqoffsets: float,
    freqlindrifts: float,
    freqquaddrifts: float,
) -> np.ndarray:
    """Compute clock noise drift"""
    return freqoffsets + freqlindrifts * t_ + freqquaddrifts * t_**2


@for_each_sat
def clock_noise_offsets(
    t_: StreamBase,
    *,
    freqoffsets: float,
    freqlindrifts: float,
    freqquaddrifts: float,
) -> StreamBase:
    """Set up clock noise offset arrays, with optimization for constant case"""
    if freqlindrifts == freqquaddrifts == 0:
        # Optimize to use a scalar if we only have a constant frequency offset
        return StreamConst(freqoffsets)

    return clock_noise_drift(
        t_,
        freqoffsets=freqoffsets,
        freqlindrifts=freqlindrifts,
        freqquaddrifts=freqquaddrifts,
    )


@for_each_mosa
@stream_expression(np.float64)
def ranging_noises(
    unbiased_ranging_noises_: np.ndarray | float, *, ranging_biases: float
) -> np.ndarray | float:
    """Compute ranging_noises"""
    return unbiased_ranging_noises_ + ranging_biases


@stream_expression(np.float64)
def mosa_total_jitter_phis(
    sc_jitter_phis_: np.ndarray | float, mosa_jitter_phis_: np.ndarray | float
) -> np.ndarray | float:
    """Compute mosa_total_jitter_phis"""
    return sc_jitter_phis_ + mosa_jitter_phis_


@for_each_mosa
@stream_expression(np.float64)
def local_ttls(
    mosa_total_jitter_phis_: np.ndarray | float,
    mosa_total_jitter_etas_: np.ndarray | float,
    *,
    ttl_coeffs_local_phis: float,
    ttl_coeffs_local_etas: float,
) -> np.ndarray | float:
    """Compute local_ttls"""
    return (
        ttl_coeffs_local_phis * mosa_total_jitter_phis_
        + ttl_coeffs_local_etas * mosa_total_jitter_etas_
    )


@for_each_mosa
@stream_expression(np.float64)
def distant_ttls(
    mosa_total_jitter_phis_: np.ndarray | float,
    mosa_total_jitter_etas_: np.ndarray | float,
    *,
    ttl_coeffs_distant_phis: float,
    ttl_coeffs_distant_etas: float,
) -> np.ndarray | float:
    """Compute distant_ttls"""
    return (
        ttl_coeffs_distant_phis * mosa_total_jitter_phis_
        + ttl_coeffs_distant_etas * mosa_total_jitter_etas_
    )


@stream_expression(np.float64)
def local_carrier_offsets_lock_adjacent(
    adjacent_carrier_offsets_: np.ndarray | float,
    fplan_ts_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute local carrier offset when locking to adjacent spacecraft"""
    return adjacent_carrier_offsets_ - fplan_ts_ * (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def local_carrier_offsets_lock_distant(
    distant_carrier_offsets_: np.ndarray | float,
    fplan_ts_: np.ndarray | float,
    clock_noise_offsets_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute local carrier offset when locking to distant spacecraft"""
    return distant_carrier_offsets_ - fplan_ts_ * (1 + clock_noise_offsets_)


@stream_expression(np.float64)
def local_carrier_fluctuations_lock_cavity(
    laser_noises_: np.ndarray | float,
    glitch_lasers_: np.ndarray | float,
    tdir_modulations_tseries_: np.ndarray | float,
) -> np.ndarray | float:
    """Compute local carrier fluctuations when locking to cavity"""
    return laser_noises_ + glitch_lasers_ + tdir_modulations_tseries_


@stream_expression(np.float64)
def local_carrier_fluctuations_lock_adjacent(
    adjacent_carrier_fluctuations_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
    oms_ref_carrier_noises_: np.ndarray | float,
    fplan_ts_: np.ndarray | float,
    tdir_modulations_tseries_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute local carrier fluctuations when locking to adjacent spacecraft"""
    return (
        adjacent_carrier_fluctuations_
        - fplan_ts_ * clock_noise_fluctuations_
        + central_freq * oms_ref_carrier_noises_
        + tdir_modulations_tseries_
    )


@stream_expression(np.float64)
def local_carrier_fluctuations_lock_distant(
    distant_carrier_fluctuations_: np.ndarray | float,
    clock_noise_fluctuations_: np.ndarray | float,
    oms_sci_carrier_noises_: np.ndarray | float,
    fplan_ts_: np.ndarray | float,
    tdir_modulations_tseries_: np.ndarray | float,
    *,
    central_freq: float,
) -> np.ndarray | float:
    """Compute local carrier fluctuations when locking to distant spacecraft"""
    return (
        distant_carrier_fluctuations_
        - fplan_ts_ * clock_noise_fluctuations_
        + central_freq * oms_sci_carrier_noises_
        + tdir_modulations_tseries_
    )
