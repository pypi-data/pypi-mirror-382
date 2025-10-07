"""Component for the estimation of the DRS4 time corrections."""

import numpy as np
from ctapipe.containers import EventType
from ctapipe.core import Component, traits
from ctapipe.image.extractor import ImageExtractor
from ctapipe_io_lst.calibration import get_first_capacitors_for_pixels
from ctapipe_io_lst.constants import HIGH_GAIN, LOW_GAIN, N_GAINS, N_PIXELS
from numba import njit, prange

__all__ = ["TimeCorrectionCalculator"]


class TimeCorrectionCalculator(Component):
    """
    Create h5 file with time correction values of DRS4.

    Description of this method: "Analysis techniques
    and performance of the Domino Ring Sampler version 4
    based readout for the MAGIC telescopes [arxiv:1305.1007]
    """

    minimum_charge = traits.Float(200, help="Cut on charge. Default 200 ADC").tag(
        config=True
    )

    tel_id = traits.Int(1, help="Id of the telescope to calibrate").tag(config=True)

    n_combine = traits.Int(
        8, help="How many capacitors are combines in a single bin. Default 8"
    ).tag(config=True)

    n_harmonics = traits.Int(
        16, help="Number of harmonic for Fourier series expansion. Default 16"
    ).tag(config=True)

    n_capacitors = traits.Int(
        1024, help="Number of capacitors (1024 or 4096). Default 1024."
    ).tag(config=True)

    min_stat_per_capacitor = traits.Int(
        10, help="Minimum number of counts per capacitor."
    ).tag(config=True)

    charge_product = traits.ComponentName(
        ImageExtractor,
        default_value="LocalPeakWindowSum",
        help="Name of the charge extractor to be used",
    ).tag(config=True)

    def __init__(self, subarray, parent=None, config=None, **kwargs):
        super().__init__(parent=parent, config=config, **kwargs)

        if self.n_capacitors != 1024 and self.n_capacitors != 4096:
            raise ValueError(
                f"n_capacitor must be 1024 or 4096, not {self.n_capacitors}"
            )

        if self.n_capacitors % self.n_combine != 0:
            raise ValueError(
                f"n_capacitors ({self.n_capacitors}) must be a multiple of n_combine ({self.n_combine})",
            )

        if self.min_stat_per_capacitor <= 0:
            raise ValueError(
                f"min_stat_per_capacitor must be greater than zero, not {self.min_stat_per_capacitor}",
            )

        self.n_bins = int(self.n_capacitors / self.n_combine)

        self.mean_values_per_bin = np.zeros((N_GAINS, N_PIXELS, self.n_bins))
        self.entries_per_bin = np.zeros((N_GAINS, N_PIXELS, self.n_bins), dtype=int)

        # load the waveform charge extractor
        self.extractor = ImageExtractor.from_name(
            self.charge_product, parent=self, subarray=subarray
        )

        self.log.info("extractor %s", self.extractor)
        self.n_events_processed = 0

        self.fan_array = np.zeros((N_GAINS, N_PIXELS, self.n_harmonics))
        self.fbn_array = np.zeros((N_GAINS, N_PIXELS, self.n_harmonics))

    def calibrate_peak_time(self, event):
        """
        Fill bins using time pulse from LocalPeakWindowSum.

        Parameters
        ----------
        event : `ctapipe` event-container
        """
        if event.trigger.event_type == EventType.FLATFIELD:
            pixel_ids = event.lst.tel[self.tel_id].svc.pixel_ids
            first_capacitor_ids = event.lst.tel[self.tel_id].evt.first_capacitor_id
            first_cap_array = get_first_capacitors_for_pixels(
                first_capacitor_ids, pixel_ids
            )

            # select both gain
            broken_pixels = event.mon.tel[
                self.tel_id
            ].pixel_status.hardware_failing_pixels
            dl1 = self.extractor(
                event.r1.tel[self.tel_id].waveform,
                self.tel_id,
                selected_gain_channel=None,
                broken_pixels=broken_pixels,
            )

            self.calib_peak_time_jit(
                dl1.image,
                dl1.peak_time,
                first_cap_array,
                self.mean_values_per_bin,
                self.entries_per_bin,
                n_cap=self.n_capacitors,
                n_combine=self.n_combine,
                min_charge=self.minimum_charge,
            )
            self.n_events_processed += 1

    @staticmethod
    @njit(parallel=False)
    def calib_peak_time_jit(
        charge,
        peak_time,
        first_cap_array,
        mean_values_per_bin,
        entries_per_bin,
        n_cap,
        n_combine,
        min_charge,
    ):
        """
        Numba function for calibration pulse time.

        Parameters
        ----------
        pulse : ndarray
            Pulse time stored in a numpy array of shape
            (n_gain, n_pixels).
        charge : ndarray
            Charge in each pixel.
            (n_gain, n_pixels).
        first_cap_array : ndarray
            Value of first capacitor stored in a numpy array of shape
            (n_clus, n_gain, n_pix).
        mean_values_per_bin : ndarray
            Array to fill using pulse time
            stored in a numpy array of shape
            (n_gain, n_pixels, n_bins).
        entries_per_bin : ndarray
            Array to store number of entries per bin
            stored in a numpy array of shape
            (n_gain, n_pixels, n_bins).
        n_cap : int
            Number of capacitors
        n_combine : int
            Number of combine capacitors in a single bin

        """
        for pixel in prange(N_PIXELS):
            for gain in prange(N_GAINS):
                if charge[gain, pixel] > min_charge:  # cut change
                    first_cap = first_cap_array[gain, pixel] % n_cap
                    binc = int(first_cap / n_combine)
                    mean_values_per_bin[gain, pixel, binc] += peak_time[gain, pixel]
                    entries_per_bin[gain, pixel, binc] += 1

    def finalize(self):
        """Finalize."""
        if (self.entries_per_bin < self.min_stat_per_capacitor).any():
            self.log.warning(
                "No enough statistics for some capacitors (required %d). "
                "It might help to use more events to create the calibration file. "
                "Minimum statistics : %5.1f, Mean statistics over all capacitors: %5.1f",
                self.min_stat_per_capacitor,
                self.min_stat_per_capacitor,
                self.entries_per_bin.mean(),
            )
        else:
            self.mean_values_per_bin = self.mean_values_per_bin / self.entries_per_bin

        for pix_id in range(N_PIXELS):
            fan, fbn = self.fit(pix_id, gain=HIGH_GAIN)

            self.fan_array[HIGH_GAIN, pix_id, :] = fan
            self.fbn_array[HIGH_GAIN, pix_id, :] = fbn

            fan, fbn = self.fit(pix_id, gain=LOW_GAIN)
            self.fan_array[LOW_GAIN, pix_id, :] = fan
            self.fbn_array[LOW_GAIN, pix_id, :] = fbn

    def fit(self, pixel_id, gain):
        """
        Fit data bins using Fourier series expansion.

        Parameters
        ----------
        pixel_id : ndarray
        Array stored expected pixel id of shape
        (n_pixels).
        gain: int
        0 for high gain, 1 for low gain
        """
        pos = np.zeros(self.n_bins)
        for i in range(0, self.n_bins):
            pos[i] = (i + 0.5) * self.n_combine

        fan = np.zeros(self.n_harmonics)  # cos coeff
        fbn = np.zeros(self.n_harmonics)  # sin coeff

        for n in range(0, self.n_harmonics):
            self.integrate_with_trig(
                pos,
                self.mean_values_per_bin[gain, pixel_id],
                n,
                fan,
                fbn,
            )
        return fan, fbn

    def integrate_with_trig(self, x, y, n, an, bn):
        """
        Expand into Fourier series.

        Parameters
        ----------
        x : ndarray
        Array stored position in DRS4 ring of shape
        (n_bins).
        y: ndarray
        Array stored mean pulse time per bin of shape
        (n_bins)
        n : int
        n harmonic
        an: ndarray
        Array to fill with cos coeff of shape
        (n_harmonics)
        bn: ndarray
        Array to fill with sin coeff of shape
        (n_harmonics)
        """
        suma = 0
        sumb = 0

        for i in range(0, self.n_bins):
            suma += (
                y[i]
                * self.n_combine
                * np.cos(2 * np.pi * n * (x[i] / float(self.n_capacitors)))
            )
            sumb += (
                y[i]
                * self.n_combine
                * np.sin(2 * np.pi * n * (x[i] / float(self.n_capacitors)))
            )

        an[n] = suma * (2.0 / (self.n_bins * self.n_combine))
        bn[n] = sumb * (2.0 / (self.n_bins * self.n_combine))
