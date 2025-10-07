import astropy.units as u
import numpy as np
import tables
from astropy.io import fits
from astropy.table import Table
from ctapipe.core import run_tool
from ctapipe.io import read_table
from ctapipe_io_lst.constants import N_GAINS, N_PIXELS

from lstcam_calib.conftest import (
    test_data,
    test_drs4_pedestal_file,
    test_run_summary_file,
    test_systematics_file,
    test_time_calib_file,
)
from lstcam_calib.onsite import DEFAULT_CONFIG_CAT_A
from lstcam_calib.version import __version__ as lstcam_calib_version


def test_create_calibration_file_h5(tmp_path):
    """Test the create_calibration_file tool with output in h5 format."""
    from lstcam_calib.tools.create_calibration_file import (
        CalibrationWriter,
    )

    input_file = test_data / "real/R0/20200218/LST-1.1.Run02006.0000_first50.fits.fz"
    output_file = tmp_path / "calibration_02006.h5"
    stat_events = 90

    ret = run_tool(
        CalibrationWriter(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            f"--systematics-file={test_systematics_file}",
            f"--run-summary-file={test_run_summary_file}",
            f"--time-calibration-file={test_time_calib_file}",
            f"--pedestal-file={test_drs4_pedestal_file}",
            "--LSTEventSource.default_trigger_type=tib",
            f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
            f"--PedestalIntegrator.sample_size={stat_events}",
            "--events-to-skip=0",
            f"--config={DEFAULT_CONFIG_CAT_A}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert ret == 0, "Running CalibrationWriter tool failed"
    assert output_file.is_file(), "Output file not written"

    cal_data = read_table(output_file, "/tel_1/calibration")[0]

    n_pe = cal_data["n_pe"]
    unusable_pixels = cal_data["unusable_pixels"]
    dc_to_pe = cal_data["dc_to_pe"]

    assert n_pe.shape == (N_GAINS, N_PIXELS)
    assert np.sum(unusable_pixels) == 9
    assert np.isclose(np.median(n_pe[~unusable_pixels]), 86.45, rtol=0.1)
    assert np.isclose(np.median(dc_to_pe[~unusable_pixels], axis=0), 0.0137, rtol=0.01)

    # test metadata
    with tables.open_file(output_file, "r") as f:
        assert f.root._v_attrs["CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version


def test_create_calibration_file_fits(tmp_path):
    """Test the create_calibration_file tool with output in fits format."""
    from lstcam_calib.tools.create_calibration_file import (
        CalibrationWriter,
    )

    input_file = test_data / "real/R0/20200218/LST-1.1.Run02006.0000_first50.fits.fz"
    output_file = tmp_path / "calibration_02006.fits.gz"
    stat_events = 90

    ret = run_tool(
        CalibrationWriter(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            f"--systematics-file={test_systematics_file}",
            f"--run-summary-file={test_run_summary_file}",
            f"--time-calibration-file={test_time_calib_file}",
            f"--pedestal-file={test_drs4_pedestal_file}",
            "--LSTEventSource.default_trigger_type=tib",
            f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
            f"--PedestalIntegrator.sample_size={stat_events}",
            "--events-to-skip=0",
            f"--config={DEFAULT_CONFIG_CAT_A}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert ret == 0, "Running CalibrationWriter tool failed"
    assert output_file.is_file(), "Output file not written"

    f = fits.open(output_file)
    cal_data = f["calibration"].data[0]

    n_pe = cal_data["n_pe"]
    unusable_pixels = cal_data["unusable_pixels"]
    dc_to_pe = cal_data["dc_to_pe"]

    assert n_pe.shape == (N_GAINS, N_PIXELS)
    assert np.sum(unusable_pixels) == 9
    assert np.isclose(np.median(n_pe[~unusable_pixels]), 86.45, rtol=0.1)
    assert np.isclose(np.median(dc_to_pe[~unusable_pixels], axis=0), 0.0137, rtol=0.01)

    metadata = f["PRIMARY"].header
    assert metadata["HIERARCH CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version

    f.close()

    calib_table = Table.read(output_file, hdu="calibration")
    assert calib_table["time_correction"].unit == u.ns


def test_create_mc_calibration_file(tmp_path):
    """Test the create_calibration_file tool."""
    from lstcam_calib.tools.create_calibration_file import (
        CalibrationWriter,
    )

    input_file = test_data / "mc/calibration/filter_52_pe_245_n_eve_50.gz"
    output_file = tmp_path / "calibration_MC.h5"
    stat_events = 50
    min_ff = 2000
    max_ped = 300

    ret = run_tool(
        CalibrationWriter(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            "--EventSource.skip_calibration_events=False",
            f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
            f"--PedestalIntegrator.sample_size={stat_events}",
            f"--mc-min-flatfield-adc={min_ff}",
            f"--mc-max-pedestal-adc={max_ped}",
            "--events-to-skip=0",
            f"--config={DEFAULT_CONFIG_CAT_A}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert ret == 0, "Running CalibrationWriter tool failed"
    assert output_file.is_file(), "Output file not written"

    cal_data = read_table(output_file, "/tel_1/calibration")[0]

    n_pe = cal_data["n_pe"]
    unusable_pixels = cal_data["unusable_pixels"]
    dc_to_pe = cal_data["dc_to_pe"]

    assert n_pe.shape == (N_GAINS, N_PIXELS)
    assert np.sum(unusable_pixels) == 1
    assert np.isclose(np.median(n_pe[~unusable_pixels]), 90.68, rtol=0.1)
    assert np.isclose(np.median(dc_to_pe[~unusable_pixels], axis=0), 0.0149, rtol=0.01)
