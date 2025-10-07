import numpy as np
from astropy.time import Time
from ctapipe.image.extractor import FixedWindowSum, NeighborPeakWindowSum
from ctapipe_io_lst.calibration import N_GAINS, N_PIXELS
from traitlets.config import Config

from lstcam_calib.conftest import test_systematics_file


def test_calculator_config(lst1_subarray):
    from lstcam_calib.pixel.calibration_calculator import (
        CalibrationCalculator,
        LSTCalibrationCalculator,
    )
    from lstcam_calib.pixel.flatfield import FlasherFlatFieldCalculator
    from lstcam_calib.pixel.pedestals import PedestalIntegrator

    # WARNING: this config contains nonsense value to test if the
    # nodefault values are taken over. DO NOT USE.
    config = Config(
        {
            "LSTCalibrationCalculator": {
                "systematic_correction_file": test_systematics_file,
                "squared_excess_noise_factor": 10,
                "flatfield_product": "FlasherFlatFieldCalculator",
                "FlasherFlatFieldCalculator": {
                    "sample_size": 10,
                    "sample_duration": 5,
                    "tel_id": 7,
                    "charge_median_cut_outliers": [-0.2, 0.2],
                    "charge_std_cut_outliers": [-5, 5],
                    "time_cut_outliers": [5, 35],
                    "charge_product": "NeighborPeakWindowSum",
                    "NeighborPeakWindowSum": {
                        "window_shift": 7,
                        "window_width": 10,
                        "apply_integration_correction": False,
                    },
                },
                "pedestal_product": "PedestalIntegrator",
                "PedestalIntegrator": {
                    "sample_size": 2000,
                    "sample_duration": 100,
                    "tel_id": 7,
                    "charge_median_cut_outliers": [-5, 5],
                    "charge_std_cut_outliers": [-7, 7],
                    "charge_product": "FixedWindowSum",
                    "FixedWindowSum": {
                        "window_shift": 10,
                        "window_width": 20,
                        "peak_index": 15,
                        "apply_integration_correction": False,
                    },
                },
            },
        },
    )

    calibration_calculator = CalibrationCalculator.from_name(
        "LSTCalibrationCalculator",
        config=config,
        subarray=lst1_subarray,
    )

    assert isinstance(calibration_calculator, LSTCalibrationCalculator)
    assert (
        calibration_calculator.systematic_correction_file.resolve().absolute()
        == test_systematics_file.resolve().absolute()
    )
    assert calibration_calculator.squared_excess_noise_factor == 10

    ff = calibration_calculator.flatfield
    assert isinstance(ff, FlasherFlatFieldCalculator)
    assert isinstance(ff.extractor, NeighborPeakWindowSum)
    assert ff.extractor.window_shift.tel[1] == 7
    assert ff.extractor.window_width.tel[1] == 10
    assert ff.extractor.apply_integration_correction.tel[1] is False

    ped = calibration_calculator.pedestal
    assert isinstance(ped, PedestalIntegrator)
    assert isinstance(ped.extractor, FixedWindowSum)
    assert ped.extractor.window_shift.tel[1] == 10
    assert ped.extractor.window_width.tel[1] == 20
    assert ped.extractor.peak_index.tel[1] == 15
    assert ped.extractor.apply_integration_correction.tel[1] is False


def test_calculator(lst1_subarray):
    from ctapipe_io_lst.containers import LSTArrayEventContainer

    from lstcam_calib.pixel.calibration_calculator import (
        CalibrationCalculator,
    )

    f2 = 1.222

    config = Config(
        {
            "LSTCalibrationCalculator": {
                "systematic_correction_file": None,
                "npe_median_cut_outliers": [-5, 5],
                "squared_excess_noise_factor": f2,
                "flatfield_product": "FlasherFlatFieldCalculator",
                "pedestal_product": "PedestalIntegrator",
                "PedestalIntegrator": {
                    "sample_size": 10000,
                    "sample_duration": 100000,
                    "tel_id": 1,
                    "charge_median_cut_outliers": [-10, 10],
                    "charge_std_cut_outliers": [-10, 10],
                    "charge_product": "FixedWindowSum",
                    "FixedWindowSum": {
                        "window_shift": 6,
                        "window_width": 12,
                        "peak_index": 18,
                        "apply_integration_correction": False,
                    },
                },
                "FlasherFlatFieldCalculator": {
                    "sample_size": 10000,
                    "sample_duration": 100000,
                    "tel_id": 1,
                    "charge_product": "LocalPeakWindowSum",
                    "charge_median_cut_outliers": [-0.9, 2],
                    "charge_std_cut_outliers": [-10, 10],
                    "time_cut_outliers": [2, 38],
                    "LocalPeakWindowSum": {
                        "window_shift": 5,
                        "window_width": 12,
                        "apply_integration_correction": False,
                    },
                },
            }
        }
    )

    calibration_calculator = CalibrationCalculator.from_name(
        "LSTCalibrationCalculator", config=config, subarray=lst1_subarray
    )

    # simulate calibration event
    tel_id = 1
    event = LSTArrayEventContainer()

    # 1 ADC per pedestal sample
    adc_ped = (
        config.LSTCalibrationCalculator.PedestalIntegrator.FixedWindowSum.window_width
    )
    # change in ADC
    adc_signal = 10000

    # gain similar to LST high gain
    gain = 80

    dc_to_pe = 1 / gain
    adc_std = np.sqrt(gain * f2 * adc_signal)

    event.mon.tel[tel_id].flatfield.charge_median = np.ones((N_GAINS, N_PIXELS)) * (
        adc_signal + adc_ped
    )
    event.mon.tel[tel_id].flatfield.charge_std = np.ones((N_GAINS, N_PIXELS)) * adc_std
    event.mon.tel[tel_id].flatfield.n_events = 10000
    event.mon.tel[tel_id].flatfield.sample_time = Time("2024-01-01T20:00:00")
    event.mon.tel[tel_id].flatfield.sample_time_min = Time("2024-01-01T19:59:00")
    event.mon.tel[tel_id].flatfield.sample_time_max = Time("2024-01-01T20:01:00")

    mu, sigma = 0, 1
    rng = np.random.default_rng(0)
    event.mon.tel[tel_id].flatfield.relative_time_median = rng.normal(
        mu, sigma, (N_GAINS, N_PIXELS)
    )

    event.mon.tel[tel_id].pedestal.charge_median = (
        np.ones((N_GAINS, N_PIXELS)) * adc_ped
    )
    event.mon.tel[tel_id].pedestal.charge_std = np.zeros((N_GAINS, N_PIXELS))

    pixel_status = event.mon.tel[tel_id].pixel_status
    pixel_status.flatfield_failing_pixels = np.zeros((N_GAINS, N_PIXELS), dtype=bool)
    pixel_status.pedestal_failing_pixels = np.zeros((N_GAINS, N_PIXELS), dtype=bool)

    # add failing pixels
    expected_failing = np.zeros((N_GAINS, N_PIXELS), dtype=bool)
    failing_charge = 0

    # set failing flatfields
    failing_ff_channel = np.array([0])
    failing_ff_pixel = np.array([0])
    expected_failing[failing_ff_channel, failing_ff_pixel] = True
    event.mon.tel[tel_id].flatfield.charge_median[
        failing_ff_channel, failing_ff_pixel
    ] = failing_charge + adc_ped
    pixel_status.flatfield_failing_pixels[failing_ff_channel, failing_ff_pixel] = True

    # set failing pedestals
    failing_ped_channel = np.array([1])
    failing_ped_pixel = np.array([1854])
    pixel_status.pedestal_failing_pixels[failing_ped_channel, failing_ped_pixel] = True

    event.mon.tel[tel_id].pedestal.charge_median[
        failing_ped_channel, failing_ped_pixel
    ] = failing_charge + adc_ped
    expected_failing[failing_ped_channel, failing_ped_pixel] = True

    # set failing npe values
    failing_npe_channel = np.array([0, 1])
    failing_npe_pixel = np.array([1000])
    std_scale = 100
    event.mon.tel[tel_id].flatfield.charge_std[
        failing_npe_channel, failing_npe_pixel
    ] = adc_std * std_scale
    expected_failing[failing_npe_channel, failing_npe_pixel] = True
    expected_failing_npe_value = np.array(
        [dc_to_pe * adc_signal / std_scale**2, dc_to_pe * adc_signal / std_scale**2]
    )

    # calculate calibration values
    calibration_calculator.calculate_calibration_coefficients(event)

    # test unusable pixels
    unusable_pixels = event.mon.tel[tel_id].calibration.unusable_pixels

    # verify known failing
    assert unusable_pixels[failing_ff_channel, failing_ff_pixel]
    assert unusable_pixels[failing_ped_channel, failing_ped_pixel]
    assert unusable_pixels[failing_npe_channel, failing_npe_pixel].all()

    # verify all the others
    np.testing.assert_array_equal(unusable_pixels, expected_failing)

    select = ~event.mon.tel[tel_id].calibration.unusable_pixels

    # check time
    assert event.mon.tel[tel_id].calibration.time == Time("2024-01-01T20:00:00")
    assert event.mon.tel[tel_id].calibration.time_min == Time("2024-01-01T19:59:00")
    assert event.mon.tel[tel_id].calibration.time_max == Time("2024-01-01T20:01:00")

    # gain is set for all the pixels (unusable pixels get the median camera value)
    assert np.isclose(
        np.mean(event.mon.tel[tel_id].calibration.dc_to_pe), dc_to_pe, rtol=0.0001
    )
    assert np.isclose(
        np.mean(event.mon.tel[tel_id].calibration.n_pe[select]),
        dc_to_pe * adc_signal,
        rtol=0.0001,
    )

    # n_pe
    assert np.isclose(
        np.mean(event.mon.tel[tel_id].calibration.n_pe[select]),
        dc_to_pe * adc_signal,
        rtol=0.0001,
    )
    np.testing.assert_allclose(
        event.mon.tel[tel_id].calibration.n_pe[failing_npe_channel, failing_npe_pixel],
        expected_failing_npe_value,
        rtol=0.0001,
    )

    # pedestal
    assert np.isclose(
        event.mon.tel[tel_id].calibration.pedestal_per_sample.any(), 1, rtol=0.0001
    )

    # test std expected std values
    hg_std, lg_std = calibration_calculator.expected_npe_std(
        np.median(event.mon.tel[tel_id].calibration.n_pe[select]),
        event.mon.tel[tel_id].flatfield.n_events,
    )

    assert np.isclose(hg_std, 9.2, rtol=0.1)
    assert np.isclose(lg_std, 10.1, rtol=0.1)
