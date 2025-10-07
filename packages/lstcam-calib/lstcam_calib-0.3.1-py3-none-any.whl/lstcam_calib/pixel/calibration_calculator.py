"""Component for the estimation of the calibration coefficients  event."""

from importlib.resources import files
from pathlib import Path

import numpy as np
import tables
import yaml
from ctapipe.core import Component, traits
from ctapipe_io_lst import constants

from lstcam_calib.pixel.flatfield import FlatFieldCalculator
from lstcam_calib.pixel.pedestals import PedestalCalculator

__all__ = [
    "CalibrationCalculator",
    "LSTCalibrationCalculator",
]


class CalibrationCalculator(Component):
    """
    Parent class for the camera calibration calculators.

    Fills the MonitoringCameraContainer on the base of calibration events.
    """

    systematic_correction_file = traits.Path(
        default_value=None,
        allow_none=True,
        exists=True,
        directory_ok=False,
        help="Path to systematic correction file ",
    ).tag(config=True)

    std_noise_file = traits.Path(
        default_value=Path(
            files("lstcam_calib").joinpath("resources/npe_std_noise_parameters.yml")
        ),
        exists=True,
        help="Parameter file for the npe std estimation",
    ).tag(config=True)

    squared_excess_noise_factor = traits.Float(
        1.222,
        help="Excess noise factor squared: 1+ Var(gain)/Mean(Gain)**2",
    ).tag(config=True)

    pedestal_product = traits.ComponentName(
        PedestalCalculator,
        default_value="PedestalIntegrator",
    ).tag(config=True)

    flatfield_product = traits.ComponentName(
        FlatFieldCalculator,
        default_value="FlasherFlatFieldCalculator",
    ).tag(config=True)

    npe_median_cut_outliers = traits.List(
        [-5, 5],
        help="Interval (number of std) of accepted number of pe in FF events around camera median value",
    ).tag(config=True)

    use_scaled_low_gain = traits.Bool(
        default_value=False,
        help=(
            "If true, low gain calibration coefficients are scaled from high gain coefficients"
        ),
    ).tag(config=True)

    hg_lg_ratio = traits.Float(
        1.0,
        help="HG/LG ratio applied if use_scaled_low_gain is True. The ratio is ~1 for calibrated data, ~17.4 for uncalibrated data.",
    ).tag(config=True)

    classes = (
        [FlatFieldCalculator, PedestalCalculator]
        + traits.classes_with_traits(FlatFieldCalculator)
        + traits.classes_with_traits(PedestalCalculator)
    )

    def __init__(
        self,
        subarray,
        parent=None,
        config=None,
        **kwargs,
    ):
        super().__init__(parent=parent, config=config, **kwargs)

        if self.squared_excess_noise_factor <= 0:
            msg = "Argument squared_excess_noise_factor must have a positive value"
            raise ValueError(msg)

        self.flatfield = FlatFieldCalculator.from_name(
            self.flatfield_product,
            parent=self,
            subarray=subarray,
        )
        print(self.flatfield.sample_size)
        self.pedestal = PedestalCalculator.from_name(
            self.pedestal_product,
            parent=self,
            subarray=subarray,
        )

        msg = "tel_id not the same for all calibration components"
        if self.pedestal.tel_id != self.flatfield.tel_id:
            raise ValueError(msg)

        self.tel_id = self.flatfield.tel_id

        # load systematic correction term B
        self.quadratic_term = 0
        if self.systematic_correction_file is not None:
            try:
                with tables.open_file(self.systematic_correction_file, "r") as hf:
                    self.quadratic_term = hf.root.B_term[:]

            except Exception:
                raise OSError(
                    f"Problem in reading quadratic term file {self.systematic_correction_file}",
                )


class LSTCalibrationCalculator(CalibrationCalculator):
    """
    Calibration calculator for LST camera.

    Fills the MonitoringCameraContainer on the base of calibration events
    """

    def calculate_calibration_coefficients(self, event):
        """
        Calculate calibration coefficients from flatfield and pedestal statistics.

        Parameters
        ----------
        event: ArrayArrayEventContainer

        """
        ped_data = event.mon.tel[self.tel_id].pedestal
        ff_data = event.mon.tel[self.tel_id].flatfield
        status_data = event.mon.tel[self.tel_id].pixel_status
        calib_data = event.mon.tel[self.tel_id].calibration

        # find unusable pixel from pedestal and flat-field data
        unusable_pixels = np.logical_or(
            status_data.pedestal_failing_pixels,
            status_data.flatfield_failing_pixels,
        )

        signal = ff_data.charge_median - ped_data.charge_median

        # Extract calibration coefficients with F-factor method
        # Assume fixed excess noise factor must be known from elsewhere
        numerator = ff_data.charge_std**2 - ped_data.charge_std**2
        denominator = self.squared_excess_noise_factor * signal
        gain = np.divide(
            numerator,
            denominator,
            out=np.zeros_like(numerator),
            where=denominator != 0,
        )

        # correct for the quadratic term (which is zero if not given)
        systematic_correction = (
            self.quadratic_term**2 * signal / self.squared_excess_noise_factor
        )
        gain -= systematic_correction

        # calculate photon-electrons
        numerator = signal
        denominator = gain

        n_pe = np.divide(
            numerator,
            denominator,
            out=np.zeros_like(numerator),
            where=denominator != 0,
        )

        # fill WaveformCalibrationContainer
        calib_data.time = ff_data.sample_time
        calib_data.time_min = ff_data.sample_time_min
        calib_data.time_max = ff_data.sample_time_max
        calib_data.n_pe = n_pe

        # find signal median of good pixels over the camera (FF factor=<npe>/npe)
        masked_npe = np.ma.array(n_pe, mask=unusable_pixels)
        npe_median = np.ma.median(masked_npe, axis=1)

        # flat-fielded calibration coefficients
        numerator = npe_median[:, np.newaxis]
        denominator = signal
        calib_data.dc_to_pe = np.divide(
            numerator,
            denominator,
            out=np.zeros_like(denominator),
            where=denominator != 0,
        )

        # flat-field time corrections
        calib_data.time_correction = -ff_data.relative_time_median

        calib_data.pedestal_per_sample = (
            ped_data.charge_median
            / self.pedestal.extractor.window_width.tel[self.tel_id]
        )

        # define unusables on number of estimated pe
        npe_deviation = calib_data.n_pe - npe_median[:, np.newaxis]

        # cut on the base of the pe statistical uncertainty over the camera
        tot_std = self.expected_npe_std(npe_median, ff_data.n_events)

        npe_outliers = np.logical_or(
            npe_deviation < self.npe_median_cut_outliers[0] * tot_std[:, np.newaxis],
            npe_deviation > self.npe_median_cut_outliers[1] * tot_std[:, np.newaxis],
        )

        # calibration unusable pixels are an OR of all masks
        calib_data.unusable_pixels = np.logical_or(
            unusable_pixels,
            npe_outliers,
        ).filled(True)

        # give to the unusable pixels the median camera value for the dc_to_pe and pedestal
        # (these are the starting data for the Cat-B calibration)
        dc_to_pe_masked = np.ma.array(
            calib_data.dc_to_pe,
            mask=calib_data.unusable_pixels,
        )
        median_dc_to_pe = np.ma.median(dc_to_pe_masked, axis=1)[:, np.newaxis]
        fill_array = np.ones((constants.N_GAINS, constants.N_PIXELS)) * median_dc_to_pe
        calib_data.dc_to_pe = np.ma.filled(dc_to_pe_masked, fill_array)

        pedestal_per_sample_masked = np.ma.array(
            calib_data.pedestal_per_sample,
            mask=calib_data.unusable_pixels,
        )
        median_pedestal_per_sample = np.ma.median(pedestal_per_sample_masked, axis=1)[
            :,
            np.newaxis,
        ]
        fill_array = (
            np.ones((constants.N_GAINS, constants.N_PIXELS))
            * median_pedestal_per_sample
        )
        calib_data.pedestal_per_sample = np.ma.filled(
            pedestal_per_sample_masked,
            fill_array,
        )

        # set to zero time corrections of unusable pixels
        time_correction_masked = np.ma.array(
            calib_data.time_correction,
            mask=calib_data.unusable_pixels,
        )
        calib_data.time_correction = time_correction_masked.filled(0)

        # in the case FF intensity is not sufficiently high, better to scale low gain calibration from high gain results
        if self.use_scaled_low_gain:
            calib_data.unusable_pixels[constants.LOW_GAIN] = calib_data.unusable_pixels[
                constants.HIGH_GAIN
            ]
            calib_data.dc_to_pe[constants.LOW_GAIN] = (
                calib_data.dc_to_pe[constants.HIGH_GAIN] * self.hg_lg_ratio
            )
            calib_data.time_correction[constants.LOW_GAIN] = calib_data.time_correction[
                constants.HIGH_GAIN
            ]

        # eliminate inf values id any (still necessary?)
        calib_data.dc_to_pe[np.isinf(calib_data.dc_to_pe)] = 0

    def expected_npe_std(self, npe_median, n_events):
        """Estimate the expected standard deviation of the estimated npe over the camera.

        This is given in principle by:

        std_pe_mean=std_npe/sqrt((n_events)+ (relative_qe_dispersion*npe)**2)

        where the relative_qe_dispersion is mainly due to different detection QE among PMs.

        However, due to the systematics correction associated to the B term, a linear and quadratic
        noise component  must be added, these components depend on the sample statistics per pixel (n_events).
        The parameters in this function (linear_noise_params and quadratic_noise_params) have been obtained with
        a fit of the std of filter scan taken in date 2023/05/10 and considering
        n_events = [1000,2500,5000,7500,10000,30000]

        """
        # read the std noise parameters from file
        with open(self.std_noise_file) as f:
            std_noise = yaml.safe_load(f)

        basic_variance = (
            npe_median / n_events
            + (std_noise["relative_qe_dispersion"] * npe_median) ** 2
        )

        # function to estimate the added noise components as function of the sample statistcs
        def noise_term(n_events, par):
            return par[0] / (np.sqrt(n_events)) + par[1]

        linear_term = noise_term(n_events, std_noise["linear_noise_params"])
        quadratic_term = noise_term(n_events, std_noise["quadratic_noise_params"])

        added_variance = (linear_term * npe_median) ** 2 + (
            quadratic_term * npe_median**2
        ) ** 2

        std = np.sqrt(basic_variance + added_variance)

        return std
