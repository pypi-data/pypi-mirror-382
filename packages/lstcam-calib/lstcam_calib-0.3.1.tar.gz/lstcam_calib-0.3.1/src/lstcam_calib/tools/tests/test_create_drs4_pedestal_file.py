from pathlib import Path

import numpy as np
import pytest
import tables
from astropy.io import fits
from ctapipe.core import run_tool
from ctapipe_io_lst.constants import N_CAPACITORS_PIXEL, N_GAINS, N_PIXELS

from lstcam_calib.version import __version__ as lstcam_calib_version

test_data = Path("test_data").absolute()


def test_create_drs4_pedestal_file_h5(tmp_path):
    """Test create_drs4_pedestal_file tool"""
    from lstcam_calib.tools.create_drs4_pedestal_file import (
        DRS4PedestalAndSpikeHeight,
    )

    input_file = test_data / "real/R0/20200218/LST-1.1.Run02005.0000_first50.fits.fz"
    output_file = tmp_path / "drs4_pedestal_02005.h5"

    # to few events in test file to have spike heights for all pixels
    with pytest.warns(RuntimeWarning, match="invalid value encountered in cast"):
        ret = run_tool(
            DRS4PedestalAndSpikeHeight(),
            argv=[
                f"--input-file={input_file}",
                f"--output-file={output_file}",
                "--overwrite",
            ],
            cwd=tmp_path,
        )

    assert ret == 0, "Running DRS4PedestalAndSpikeHeight tool failed"
    assert output_file.is_file(), "Output file not written"

    with tables.open_file(output_file, "r") as f:
        drs4_data = f.root.r1.monitoring.drs4_baseline.tel_001[0]
        baseline_mean = drs4_data["baseline_mean"]
        baseline_counts = drs4_data["baseline_counts"]

        assert baseline_mean.dtype == np.int16
        assert baseline_mean.shape == (N_GAINS, N_PIXELS, N_CAPACITORS_PIXEL)
        mean_pixel_baseline = np.average(
            baseline_mean[baseline_counts > 0],
            weights=baseline_counts[baseline_counts > 0],
        )
        assert np.isclose(mean_pixel_baseline, 400, rtol=0.05)

        spike_height = drs4_data["spike_height"]
        assert spike_height.dtype == np.int16
        mean_spike_height = np.nanmean(spike_height, axis=(0, 1))

        # these are the expected spike heights, but due to the low statistics,
        # we need to use a rather large atol
        assert np.allclose(mean_spike_height, [46, 53, 7], atol=2)

        # test metadata
        assert f.root._v_attrs["CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version


def test_create_drs4_pedestal_file_fits(tmp_path):
    """Test create_drs4_pedestal_file tool with fits output format"""
    from lstcam_calib.tools.create_drs4_pedestal_file import (
        DRS4PedestalAndSpikeHeight,
    )

    input_file = test_data / "real/R0/20200218/LST-1.1.Run02005.0000_first50.fits.fz"
    output_file = tmp_path / "drs4_pedestal_02005.fits.gz"

    # to few events in test file to have spike heights for all pixels
    with pytest.warns(RuntimeWarning, match="invalid value encountered in cast"):
        ret = run_tool(
            DRS4PedestalAndSpikeHeight(),
            argv=[
                f"--input-file={input_file}",
                f"--output-file={output_file}",
                "--overwrite",
            ],
            cwd=tmp_path,
        )

    assert ret == 0, "Running DRS4PedestalAndSpikeHeight tool failed"
    assert output_file.is_file(), "Output file not written"

    f = fits.open(output_file)
    baseline_mean = f["baseline_mean"].data
    baseline_counts = f["baseline_counts"].data
    spike_height = f["spike_height"].data

    assert baseline_mean.dtype == ">i2"
    assert baseline_mean.shape == (N_GAINS, N_PIXELS, N_CAPACITORS_PIXEL)
    mean_pixel_baseline = np.average(
        baseline_mean[baseline_counts > 0],
        weights=baseline_counts[baseline_counts > 0],
    )
    assert np.isclose(mean_pixel_baseline, 400, rtol=0.05)

    assert spike_height.dtype == ">i2"
    mean_spike_height = np.nanmean(spike_height, axis=(0, 1))

    # these are the expected spike heights, but due to the low statistics,
    # we need to use a rather large atol
    assert np.allclose(mean_spike_height, [46, 53, 7], atol=2)

    # test metadata
    metadata = f["PRIMARY"].header
    assert metadata["HIERARCH CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version
