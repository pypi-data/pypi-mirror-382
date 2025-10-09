#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexagon
=======

Simulation of the Hexagon experiment :cite:`Yamamoto:2021ujg`.

.. autoclass:: Hexagon
    :members:
"""

import logging

import numpy as np
from h5py import File

from . import noises
from .noises import generate_subseed

logger = logging.getLogger(__name__)


class Hexagon:
    """Represent the Hexagon instrument.

    Args:
        size (int): numer of samples in the simulation
        dt (float): sampling period [s]
        primary_laser_asd (float): ASD of primary laser 1 [Hz/sqrt(Hz)]
        locked_laser_asd (float): ASD added to locked lasers 2 & 3 [Hz/sqrt(Hz)]
        offset_freqs (dict or str): laser frequency offsets [Hz], or 'default'
        central_freq: central laser frequency [Hz]
        seed (int): random seed for reproducibility, or None to generate one
    """

    INDICES = ["1", "2", "3"]
    BEATNOTES = ["12", "23", "31"]

    def __init__(
        self,
        size=100,
        dt=1 / (80e6 / 2**17 / 10 / 6 / 3),
        primary_laser_asd=100,
        locked_laser_asd=60,
        offset_freqs="default",
        central_freq=2.816e14,
        laser_shape="white+infrared",
        seed: int | None = None,
    ):

        self.simulated = False

        self.size = int(size)
        self.dt = float(dt)
        self.fs = 1.0 / self.dt
        self.duration = self.size * self.dt
        self.time = np.arange(self.size) * self.dt

        logger.info(
            "Initialize hexagon experiment (size=%d, dt=%f, duration=%f",
            self.size,
            self.dt,
            self.duration,
        )

        self.primary_laser_asd = float(primary_laser_asd)
        self.locked_laser_asd = float(locked_laser_asd)
        self.laser_shape = laser_shape

        self.central_freq = float(central_freq)
        if offset_freqs == "default":
            logger.debug("Use default set of offset frequencies")
            self.offset_freqs = {"1": 0.0, "2": 15e6, "3": 7e6}
        else:
            self.offset_freqs = offset_freqs

        # Initialize single-laser-related attributes
        self.laser_noises = None
        self.carrier_offsets = None
        self.carrier_fluctuations = None
        # Initialize beatnote-related attributes
        self.carrier_beatnotes = None
        self.carrier_beatnote_offsets = None
        self.carrier_beatnote_fluctuations = None
        # Initialize signal-combination attributes
        self.three_signal_combination = None

        if seed is None:
            seed = noises.generate_random_seed()
        logger.debug("Using seed '%d' for random number generation", seed)
        self.seed = seed

    def simulate(self):
        """Run a simulation, and generate all intermediary signals."""

        logger.info("Starting simulation")
        if self.simulated:
            logger.warning("Overwriting previous simulated values")

        # Laser noise
        logger.debug("Generating laser noise")
        self.laser_noises = np.empty((self.size, 3))  # (size, laser) [Hz]
        # Laser 1 has its own stability
        self.laser_noises[:, 0] = noises.laser(
            fs=self.fs,
            size=self.size,
            asd=self.primary_laser_asd,
            shape=self.laser_shape,
            seed=generate_subseed(self.seed, "laser_1"),
        )
        # Laser 2 replicated laser 1 with added locking noise
        self.laser_noises[:, 1] = self.laser_noises[:, 0] + noises.white(
            fs=self.fs,
            size=self.size,
            asd=self.locked_laser_asd,
            seed=generate_subseed(self.seed, "laser_2"),
        )
        # Laser 3 replicated laser 1 with added locking noise
        self.laser_noises[:, 2] = self.laser_noises[:, 0] + noises.white(
            fs=self.fs,
            size=self.size,
            asd=self.locked_laser_asd,
            seed=generate_subseed(self.seed, "laser_3"),
        )

        # Carrier beams
        logger.debug("Simulating carrier beams")
        self.carrier_fluctuations = self.laser_noises  # (size, laser) [Hz]
        self.carrier_offsets = np.array(
            [[self.offset_freqs[index] for index in self.INDICES]]
        )  # (size, laser) [Hz]

        # Compute beatnotes
        # Convention is from paper: beatnote ij is beam j - beam i
        logger.debug("Computing carrier beatnotes")
        self.carrier_beatnote_offsets = np.stack(
            [
                self.carrier_offsets[:, int(ij[1]) - 1]
                - self.carrier_offsets[:, int(ij[0]) - 1]
                for ij in self.BEATNOTES
            ],
            axis=-1,
        )  # (size, beatnote) [Hz]
        self.carrier_beatnote_fluctuations = np.stack(
            [
                self.carrier_fluctuations[:, int(ij[1]) - 1]
                - self.carrier_fluctuations[:, int(ij[0]) - 1]
                for ij in self.BEATNOTES
            ],
            axis=-1,
        )  # (size, beatnote) [Hz]
        self.carrier_beatnotes = (
            self.carrier_beatnote_offsets + self.carrier_beatnote_fluctuations
        )

        # Three-signal combination
        logger.debug("Forming three-signal combination")
        self.three_signal_combination = (
            self.carrier_beatnotes[:, 0]
            + self.carrier_beatnotes[:, 1]
            + self.carrier_beatnotes[:, 2]
        )

        logger.info("Simulation complete")
        self.simulated = True

    def write(self, output="measurements.h5", mode="w"):
        """Write simulation results.

        Args:
            output: path to measurement file
            mode: measurement file opening mode
        """
        # Run simulation is needed
        if not self.simulated:
            logger.debug("No simulated data, running new simulation")
            self.simulate()

        logger.info("Writing simulated data to '%s'", output)
        logger.debug("Opening file '%s' (mode='%s')", output, mode)
        with File(output, mode) as hdf5:

            logger.debug("Saving simulation parameters as metadata")

            hdf5.attrs["size"] = self.size
            hdf5.attrs["dt"] = self.dt
            hdf5.attrs["fs"] = self.fs
            hdf5.attrs["duration"] = self.duration

            hdf5.attrs["primary_laser_asd"] = self.primary_laser_asd
            hdf5.attrs["locked_laser_asd"] = self.locked_laser_asd
            hdf5.attrs["offset_freqs"] = str(self.offset_freqs)
            hdf5.attrs["central_freq"] = self.central_freq

            logger.debug("Saving simulated data")

            self._write_dataset(hdf5, "laser_noises", indices=self.INDICES)
            self._write_dataset(hdf5, "carrier_offsets", indices=self.INDICES)
            self._write_dataset(hdf5, "carrier_fluctuations", indices=self.INDICES)
            self._write_dataset(hdf5, "carrier_beatnotes", indices=self.BEATNOTES)
            self._write_dataset(
                hdf5, "carrier_beatnote_offsets", indices=self.BEATNOTES
            )
            self._write_dataset(
                hdf5, "carrier_beatnote_fluctuations", indices=self.BEATNOTES
            )
            self._write_dataset(hdf5, "three_signal_combination")

    def _write_dataset(self, hdf5, data, indices=None):
        """Write a single object attribute on ``hdf5``.

        Args:
            hdf5 (:obj:`h5py.Group`): an HDF5 group or file
            data (array-like): data to write
            indices (list of str): index list, ``None`` if no indices
        """
        # Write target attribute
        hdf5[data] = getattr(self, data)
        # Write dimension scales
        if indices is not None:
            hdf5[data].attrs["indices"] = indices
