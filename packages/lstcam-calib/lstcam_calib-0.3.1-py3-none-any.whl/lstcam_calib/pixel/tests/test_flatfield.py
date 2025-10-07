from copy import deepcopy

import astropy.units as u
import numpy as np
from astropy.time import Time
from ctapipe.containers import ArrayEventContainer
from traitlets.config.loader import Config

from lstcam_calib.pixel.flatfield import FlasherFlatFieldCalculator


def test_flasherflatfieldcalculator(lst1_subarray):
    """test of flasherFlatFieldCalculator"""
    tel_id = 1
    n_gain = 2
    n_events = 1000
    n_pixels = 1855
    ff_level = 10000
    ff_std = 10

    subarray = deepcopy(lst1_subarray)
    subarray.tel[tel_id].camera.readout.reference_pulse_shape = np.ones((1, 2))
    subarray.tel[tel_id].camera.readout.reference_pulse_sample_width = u.Quantity(
        1,
        u.ns,
    )

    config = Config(
        {
            "FixedWindowSum": {
                "window_shift": 5,
                "window_width": 10,
                "peak_index": 20,
                "apply_integration_correction": False,
            },
        },
    )
    ff_calculator = FlasherFlatFieldCalculator(
        subarray=subarray,
        charge_product="FixedWindowSum",
        sample_size=n_events,
        tel_id=tel_id,
        config=config,
    )
    # create one event
    data = ArrayEventContainer()
    data.meta["origin"] = "test"

    event_time = Time("2024-01-01T20:00:00")

    # initialize mon and r1 data
    data.mon.tel[tel_id].pixel_status.hardware_failing_pixels = np.zeros(
        (n_gain, n_pixels),
        dtype=bool,
    )
    data.mon.tel[tel_id].pixel_status.pedestal_failing_pixels = np.zeros(
        (n_gain, n_pixels),
        dtype=bool,
    )
    data.mon.tel[tel_id].pixel_status.flatfield_failing_pixels = np.zeros(
        (n_gain, n_pixels),
        dtype=bool,
    )
    data.r1.tel[tel_id].waveform = np.zeros((n_gain, n_pixels, 40), dtype=np.float32)

    rng = np.random.default_rng(0)

    # First test: good event
    while ff_calculator.num_events_seen < n_events:
        # flatfield events with 100 Events / s
        data.trigger.time = event_time
        data.trigger.tel[tel_id].time = data.trigger.time

        # flat-field signal put == delta function of height ff_level at sample 20
        data.r1.tel[tel_id].waveform[:, :, 20] = rng.normal(ff_level, ff_std)

        if ff_calculator.calculate_relative_gain(data):
            result = data.mon.tel[tel_id].flatfield
            print(result)

            assert result is not None
            assert np.isclose(np.mean(result.charge_median), ff_level, rtol=0.01)
            assert np.isclose(np.mean(result.charge_std), ff_std, rtol=0.05)
            assert np.isclose(np.mean(result.relative_gain_median), 1, rtol=0.01)
            assert np.isclose(np.mean(result.relative_gain_std), 0, rtol=0.01)
            assert result.sample_time_min == Time("2024-01-01T20:00").unix * u.s
            assert u.isclose(result.sample_time, result.sample_time_min + 5 * u.s)
            assert u.isclose(result.sample_time_max, result.sample_time_min + 10 * u.s)

        event_time += 0.01 * u.s

    # Second test: introduce some failing pixels
    failing_pixels_id = np.array([10, 20, 30, 40])
    data.r1.tel[tel_id].waveform[:, failing_pixels_id, :] = 0
    data.mon.tel[tel_id].pixel_status.pedestal_failing_pixels[
        :,
        failing_pixels_id,
    ] = True

    while ff_calculator.num_events_seen < n_events:
        if ff_calculator.calculate_relative_gain(data):
            # working pixel have good gain
            assert data.mon.tel[tel_id].flatfield.relative_gain_median[0, 0] == 1

            # bad pixels do non influence the gain
            assert np.mean(data.mon.tel[tel_id].flatfield.relative_gain_std) == 0
