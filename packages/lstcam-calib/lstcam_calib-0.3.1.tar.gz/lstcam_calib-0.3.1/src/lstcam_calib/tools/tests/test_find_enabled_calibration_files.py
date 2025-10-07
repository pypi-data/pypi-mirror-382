from ctapipe.core import run_tool

from lstcam_calib.conftest import TEST_ONSITE
from lstcam_calib.tools.find_enabled_calibration_files import (
    FindEnabledCalibrationFiles,
)


def test_find_enabled_calibration_files(onsite_test_tree, onsite_database):
    """Test create_fit_intensity_scan_file tool."""

    ret = run_tool(
        FindEnabledCalibrationFiles(),
        argv=[
            f"-b={onsite_test_tree}",
            f"--db-name={TEST_ONSITE}",
            "-t=DRS4_BASELINE",
        ],
        cwd=onsite_test_tree,
    )

    assert ret == 0
