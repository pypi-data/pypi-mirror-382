import numpy as np
import tables
from ctapipe.core import run_tool
from ctapipe.io import read_table
from ctapipe_io_lst.constants import N_GAINS, N_PIXELS

from lstcam_calib.conftest import (
    test_calibration_file,
    test_interleaved_r1_path,
    test_systematics_file,
)
from lstcam_calib.onsite import DEFAULT_CONFIG_CAT_B
from lstcam_calib.version import __version__ as lstcam_calib_version


def test_create_cat_b_calibration_file(tmp_path):
    """Test the create_cat_b_calibration_file tool."""
    from lstcam_calib.tools.create_cat_b_calibration_file import (
        CatBCalibrationHDF5Writer,
    )

    input_path = test_interleaved_r1_path
    output_file = tmp_path / "calibration_cat_B_02006.h5"
    stat_events = 90

    ret = run_tool(
        CatBCalibrationHDF5Writer(),
        argv=[
            f"--input-path={input_path}",
            f"--output-file={output_file}",
            f"--cat-a-calibration-file={test_calibration_file}",
            f"--LSTCalibrationCalculator.systematic_correction_file={test_systematics_file}",
            f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
            f"--PedestalIntegrator.sample_size={stat_events}",
            f"--config={DEFAULT_CONFIG_CAT_B}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert ret == 0, "Running CalibrationHDF5Writer tool failed"
    assert output_file.is_file(), "Output file not written"

    cal_data = read_table(output_file, "/tel_1/calibration")[0]

    n_pe = cal_data["n_pe"]
    unusable_pixels = cal_data["unusable_pixels"]
    dc_to_pe = cal_data["dc_to_pe"]

    assert n_pe.shape == (N_GAINS, N_PIXELS)

    assert np.sum(unusable_pixels) == 8
    assert np.isclose(np.median(n_pe[~unusable_pixels]), 86.34, rtol=0.1)
    assert np.isclose(np.median(dc_to_pe[~unusable_pixels], axis=0), 1.07, rtol=0.01)

    # test metadata
    with tables.open_file(output_file, "r") as f:
        assert f.root._v_attrs["CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version
