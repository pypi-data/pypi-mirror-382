import numpy as np
import pytest
import tables
from astropy.io import fits
from ctapipe.core import run_tool
from ctapipe.io import read_table

from lstcam_calib.conftest import test_data, test_drs4_timelapse_histo_file


def test_combine_stats():
    from lstcam_calib.tools.create_drs4_timelapse_file import _combine_stats

    rng = np.random.default_rng(0)

    def create_dist(mean, std):
        dist = rng.normal(mean, std, 10000)

        data = {
            "hist": np.array([[len(dist)]]),
            "mean": np.atleast_1d(np.mean(dist)),
            "std": np.atleast_1d(np.std(dist)),
        }

        return dist, data

    dist_a, data_a = create_dist(2, 1)
    dist_b, data_b = create_dist(5, 2)

    result = _combine_stats(data_a, data_b)

    np.testing.assert_array_equal(result["hist"], [[20000]])

    dist = np.concatenate([dist_a, dist_b])
    np.testing.assert_allclose(result["mean"], np.mean(dist))
    np.testing.assert_allclose(result["std"], np.std(dist))


def test_extract_and_aggregate_drs4_time_lapse_data(tmp_path):
    from lstcam_calib.tools.aggregate_drs4_timelapse_data import DRS4TimelapseAggregator
    from lstcam_calib.tools.extract_drs4_timelapse_data import DRS4Timelapse

    input_file = test_data / "real/R0/20200218/LST-1.1.Run02005.0000_first50.fits.fz"
    output_file = tmp_path / "drs4_timelapse_data_02005.h5"

    run_tool(
        DRS4Timelapse(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert output_file.is_file(), "Output file not written"

    with tables.open_file(output_file, "r") as f:
        assert np.isclose(np.mean(f.root.values[1, 1]), 385.35, rtol=0.1)

        # test metadata
        assert f.root._v_attrs["obs_id"] == 2005

    input_file = output_file
    output_file = tmp_path / "drs4_timelapse_histo_02005.h5"

    run_tool(
        DRS4TimelapseAggregator(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert output_file.is_file(), "Output file not written"
    with tables.open_file(output_file, "r") as f:
        assert np.isclose(
            f.root.r0.service.timelapse_data.tel_001[0][3][13], 43.387, rtol=0.01
        )


@pytest.mark.parametrize("fmt", ["fits.gz", "h5"])
def test_create_drs4_timelapse_file(tmp_path, fmt):
    from lstcam_calib.tools.create_drs4_timelapse_file import DRS4TimelapseFitter

    input_file = test_drs4_timelapse_histo_file
    output_file = tmp_path / f"drs4_timelapse_coefficients.{fmt}"
    plot_file = tmp_path / "drs4_timelapse_coefficients.pdf"

    run_tool(
        DRS4TimelapseFitter(),
        argv=[
            f"--input-file={input_file}",
            f"--output-file={output_file}",
            f"--plot-output={plot_file}",
            "--group-by=batch",
            "--overwrite",
        ],
        cwd=tmp_path,
    )

    assert output_file.is_file(), "Output file not written"
    expected_names = ["scale", "exponent", "t0", "chi2", "mean_10ms", "pixel_batch"]
    if fmt == "h5":
        coeffs = read_table(output_file, "r0/service/timelapse_coefficients/tel_001")[0]
        assert coeffs.colnames == expected_names
        np.testing.assert_array_equal(coeffs["pixel_batch"], 0)
    else:
        with fits.open(output_file) as hdul:
            names = [hdu.name for hdu in hdul[1:]]
            assert names == [n.upper() for n in expected_names]

    assert plot_file.is_file(), "Plots not created"
