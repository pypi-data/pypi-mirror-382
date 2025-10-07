import math
from importlib.resources import files

import tables
from ctapipe.core import run_tool

from lstcam_calib.conftest import test_data
from lstcam_calib.tools.create_fit_intensity_scan_file import (
    FitIntensityScan,
)
from lstcam_calib.version import __version__ as lstcam_calib_version


def test_fit_intensity_scan(tmp_path):
    """Test create_fit_intensity_scan_file tool."""

    input_dir = (
        test_data / "real/service/PixelCalibration/Cat-A/calibration/20221001/pro"
    )
    config_file = files("lstcam_calib").joinpath(
        "resources/fit_intensity_scan_config_example.yml"
    )

    ret = run_tool(
        FitIntensityScan(),
        argv=[f"--config={config_file}", f"--input-dir={input_dir}"],
        cwd=tmp_path,
    )

    assert ret == 0, "Running tool FitIntensityScan failed"

    # test fit output
    fit_data = tables.open_file(f"{tmp_path}/filter_scan_fit.h5")
    gain = fit_data.root.gain
    pixel = 0
    assert math.isclose(gain[0, pixel], 75.8, abs_tol=0.1)
    assert math.isclose(gain[1, pixel], 4.21, abs_tol=0.01)

    # test metadata
    assert (
        fit_data.root._v_attrs["CTA ACTIVITY SOFTWARE VERSION"] == lstcam_calib_version
    )

    fit_data.close()
