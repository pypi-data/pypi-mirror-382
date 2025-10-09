#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital signal processing
=========================

Time shifting
-------------

.. autofunction:: timeshift

.. autofunction:: lagrange_taps

"""

import logging

import numpy as np
import scipy.sparse

logger = logging.getLogger(__name__)


def timeshift(data, shifts, order=31):
    """Shift `data` in time by `shifts` samples.

    Args:
        data: input array
        shifts: array of time shifts [samples]
        order: interpolation order
    """
    logger.debug(
        "Time shifting data '%s' by '%s' samples (order=%d)", data, shifts, order
    )

    # Handle constant input and vanishing shifts
    data = np.asarray(data)
    shifts = np.asarray(shifts)
    if data.size == 1:
        logger.debug("Input data is constant, skipping time-shift operation")
        return data
    if np.all(shifts == 0):
        logger.debug("Time shifts are vanishing, skipping time-shift operation")
        return data

    logger.debug("Computing Lagrange coefficients")
    halfp = (order + 1) // 2
    shift_ints = np.floor(shifts).astype(int)
    shift_fracs = shifts - shift_ints
    taps = lagrange_taps(shift_fracs, halfp)

    # Handle constant shifts
    if shifts.size == 1:
        logger.debug("Constant shifts, using correlation method")
        i_min = shift_ints - (halfp - 1)
        i_max = shift_ints + halfp + data.size
        if i_max - 1 < 0:
            return np.repeat(data[0], data.size)
        if i_min > data.size - 1:
            return np.repeat(data[-1], data.size)
        logger.debug(
            "Padding data (left=%d, right=%d)",
            max(0, -i_min),
            max(0, i_max - data.size),
        )
        data_trimmed = data[max(0, i_min) : min(data.size, i_max)]
        data_padded = np.pad(
            data_trimmed, (max(0, -i_min), max(0, i_max - data.size)), mode="edge"
        )
        logger.debug("Computing correlation product")
        return np.correlate(data_padded, taps[0], mode="valid")

    # Check that sizes or compatible
    if data.size != shifts.size:
        raise ValueError(
            f"`data` and `shift` must be of the same size (got {data.size}, {shifts.size})"
        )

    # Handle time-varying shifts
    logger.debug("Time-varying shifts, using matrix method")
    indices = np.arange(data.size)
    i_min = np.min(shift_ints - (halfp - 1) + indices)
    i_max = np.max(shift_ints + halfp + indices + 1)
    csr_ind = (
        np.tile(np.arange(order + 1), data.size)
        + np.repeat(shift_ints + indices, order + 1)
        - (halfp - 1)
    )
    csr_ptr = (order + 1) * np.arange(data.size + 1)
    mat = scipy.sparse.csr_matrix(
        (taps.reshape(-1), csr_ind - i_min, csr_ptr), shape=(data.size, i_max - i_min)
    )
    logger.debug(
        "Padding data (left=%d, right=%d)", max(0, -i_min), max(0, i_max - data.size)
    )
    data_trimmed = data[max(0, i_min) : min(data.size, i_max)]
    data_padded = np.pad(data_trimmed, (max(0, -i_min), max(0, i_max - data.size)))
    logger.debug("Computing matrix-vector product")
    return mat.dot(data_padded)


def lagrange_taps(shift_fracs, halfp):
    """Return array of Lagrange coefficients.

    Args:
        shift_fracs: array of fractional time shifts [samples]
        halfp: number of points on each side, equivalent to (order + 1) // 2
    """
    taps = np.zeros((2 * halfp, shift_fracs.size))

    if halfp > 1:
        factor = np.ones(shift_fracs.size, dtype=np.float64)
        factor *= shift_fracs * (1 - shift_fracs)

        for j in range(1, halfp):
            factor *= (-1) * (1 - j / halfp) / (1 + j / halfp)
            taps[halfp - 1 - j] = factor / (j + shift_fracs)
            taps[halfp + j] = factor / (j + 1 - shift_fracs)

        taps[halfp - 1] = 1 - shift_fracs
        taps[halfp] = shift_fracs

        for j in range(2, halfp):
            taps *= 1 - (shift_fracs / j) ** 2

        taps *= (1 + shift_fracs) * (1 - shift_fracs / halfp)
    else:
        taps[halfp - 1] = 1 - shift_fracs
        taps[halfp] = shift_fracs

    return taps.T
