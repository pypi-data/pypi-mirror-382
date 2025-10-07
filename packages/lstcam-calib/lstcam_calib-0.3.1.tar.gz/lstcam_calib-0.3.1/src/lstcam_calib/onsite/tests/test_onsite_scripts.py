import shutil
import subprocess as sp
from importlib.metadata import entry_points
from importlib.resources import files

import lstcam_calib
import pytest
from lstcam_calib.conftest import TEST_ONSITE, test_data, test_drs4_timelapse_histo_file
from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import PIXEL_DIR_CAT_A

ALL_SCRIPTS = [
    ep.name
    for ep in entry_points(group="console_scripts")
    if ep.name.startswith("lstcam_calib")
]

OUTPUT_FILE_ERROR = "Output file not written"


def run_program(*args):
    result = sp.run(args, stdout=sp.PIPE, stderr=sp.STDOUT, encoding="utf-8")

    if result.returncode != 0:
        raise ValueError(
            f"Running {args[0]} failed with return code {result.returncode}"
            f", output: \n {result.stdout} "
        )
    else:
        return result


@pytest.mark.parametrize("script", ALL_SCRIPTS)
def test_all_help(script):
    """Test for all scripts if at least the help works."""
    run_program(script, "--help")


def test_onsite_create_drs4_pedestal_file(onsite_test_tree):
    """Test onsite drs4 create pedestal file script."""

    run = 2005

    run_program(
        "lstcam_calib_onsite_create_drs4_pedestal_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "-f=h5",
        "-y",
        "--no-pro-symlink",
        "-m 100",
        "--no-db",
    )

    # check output file
    date = "20200218"
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_baseline" / date / prod_id

    output_file = output_dir / "drs4_pedestal.Run02005.0000.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR


def test_onsite_create_drs4_pedestal_file_with_db(onsite_test_tree, onsite_database):
    """Test onsite drs4 create pedestal file script."""

    run = 2005

    run_program(
        "lstcam_calib_onsite_create_drs4_pedestal_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "--no-pro-symlink",
        "-y",
        "-m 100",
        f"--db-name={TEST_ONSITE}",
    )

    # check output file
    date = "20200218"
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_baseline" / date / prod_id

    output_file = output_dir / "drs4_pedestal.Run02005.0000.fits.gz"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # check database
    with CalibrationDB(data_tree_root=onsite_test_tree, db_name=TEST_ONSITE) as db:
        doc = db.find_document_by_file(CalibrationType.DRS4_BASELINE, output_file)
        assert doc["path"] == str(output_file.absolute().relative_to(onsite_test_tree))


def test_onsite_create_drs4_timelapse_file(onsite_test_tree):
    """Test onsite drs4 create timelapse script file script."""

    run = 2005

    # test data extraction
    run_program(
        "lstcam_calib_onsite_create_drs4_timelapse_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "-y",
        "--no-pro-symlink",
        "--no-data-aggregation",
        "--no-timelapse-corr",
        "--no-db",
    )

    # check extraction output file
    date = "20200218"
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_timelapse" / date / prod_id

    output_file = output_dir / "drs4_timelapse_data.Run02005.0000.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # test data aggregation
    run_program(
        "lstcam_calib_onsite_create_drs4_timelapse_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "-y",
        "--no-pro-symlink",
        "--no-data-extraction",
        "--no-timelapse-corr",
        "--no-db",
    )
    # check data aggregation output file
    output_file = output_dir / "drs4_timelapse_histo.Run02005.0000.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # test timelapse coefficient evaluation
    with pytest.raises(ValueError, match="Invalid fit"):
        run_program(
            "lstcam_calib_onsite_create_drs4_timelapse_file",
            f"--base-dir={onsite_test_tree}",
            f"-r {run}",
            f"--r0-dir={test_data}/real/R0",
            "-y",
            "--no-pro-symlink",
            "--no-data-extraction",
            "--no-data-aggregation",
            "--no-db",
        )

    # copy histo file from test tree
    shutil.copyfile(
        test_drs4_timelapse_histo_file,
        output_dir / "drs4_timelapse_histo.Run02005.0000.h5",
    )

    # test timelapse with db
    run_program(
        "lstcam_calib_onsite_create_drs4_timelapse_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "-y",
        "--no-pro-symlink",
        "--no-data-extraction",
        "--no-data-aggregation",
        f"--db-name={TEST_ONSITE}",
        "--output-format=fits",
    )

    # check timelapse output file
    date = "20200218"
    prod_id = f"v{lstcam_calib.__version__}"

    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_timelapse" / date / prod_id

    output_file = output_dir / "drs4_timelapse.Run02005.0000.fits"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # check database
    with CalibrationDB(data_tree_root=onsite_test_tree, db_name=TEST_ONSITE) as db:
        doc = db.find_document_by_file(CalibrationType.DRS4_TIME_LAPSE, output_file)
        assert doc["path"] == str(output_file.relative_to(onsite_test_tree))


def test_onsite_create_calibration_file_with_db(onsite_test_tree, onsite_database):
    """Test onsite create calibration file script."""

    run = 2006

    run_program(
        "lstcam_calib_onsite_create_calibration_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"--r0-dir={test_data}/real/R0",
        "--sys-date=2020-07-26 01:25:53.000",
        "-y",
        "-f=h5",
        "--statistics=90",
        "--filters=52",
        "--CalibrationWriter.events_to_skip=0",
        f"--db-name={TEST_ONSITE}",
        "--apply-drs4-corrections",
        "--apply-pedestal-correction",
    )

    # check output file
    date = "20200218"
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "calibration" / date / prod_id

    output_file = output_dir / "calibration_filters_52.Run02006.0000.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # check database
    with CalibrationDB(data_tree_root=onsite_test_tree, db_name=TEST_ONSITE) as db:
        doc = db.find_document_by_file(CalibrationType.CALIBRATION, output_file)
        assert doc["path"] == str(output_file.relative_to(onsite_test_tree))


def test_onsite_create_fit_intensity_scan_file(onsite_test_tree):
    """Test onsite script to create the fit intensity scan."""

    config_file = files("lstcam_calib").joinpath(
        "resources/fit_intensity_scan_config_example.yml"
    )

    date = "20221001"

    run_program(
        "lstcam_calib_onsite_create_fit_intensity_scan_file",
        f"--base-dir={onsite_test_tree}",
        f"--date={date}",
        f"--config={config_file}",
        "--no-db",
        "-y",
    )

    # check output file
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A

    output_dir = calib_dir / "ffactor_systematics" / date / prod_id
    output_file = output_dir / "scan_fit_20221001.0000.h5"

    assert output_file.is_file(), OUTPUT_FILE_ERROR


def test_onsite_create_fit_intensity_scan_file_with_db(
    onsite_test_tree, onsite_database
):
    """Test onsite script to create the fit intensity scan."""

    config_file = files("lstcam_calib").joinpath(
        "resources/fit_intensity_scan_config_example.yml"
    )

    date = "20221001"

    run_program(
        "lstcam_calib_onsite_create_fit_intensity_scan_file",
        f"--base-dir={onsite_test_tree}",
        f"--date={date}",
        f"--config={config_file}",
        f"--db-name={TEST_ONSITE}",
        "-y",
    )

    # check output file
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / PIXEL_DIR_CAT_A

    output_dir = calib_dir / "ffactor_systematics" / date / prod_id
    output_file = output_dir / "scan_fit_20221001.0000.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR

    # check database
    with CalibrationDB(data_tree_root=onsite_test_tree, db_name=TEST_ONSITE) as db:
        doc = db.find_document_by_file(CalibrationType.FFACTOR_SYSTEMATICS, output_file)
        assert doc["path"] == str(output_file.relative_to(onsite_test_tree))


def test_onsite_create_cat_b_calibration_file(onsite_test_tree):
    """Test onsite create cat b calibration file script."""

    run = 2006
    cal_run = 2006

    date = "20200218"

    run_program(
        "lstcam_calib_onsite_create_cat_B_calibration_file",
        f"--base-dir={onsite_test_tree}",
        f"-r {run}",
        f"-c {cal_run}",
        f"--r0-dir={test_data}/real/R0",
        f"--dl1-dir={test_data}/real/DL1",
        "-y",
        "--statistics=40",
        "--filters=52",
        "--catA-format=h5",
    )
    prod_id = f"v{lstcam_calib.__version__}"
    calib_dir = onsite_test_tree / "monitoring/PixelCalibration/Cat-B"
    output_dir = calib_dir / "calibration" / date / prod_id

    output_file = output_dir / "cat_B_calibration_filters_52.Run02006.h5"
    assert output_file.is_file(), OUTPUT_FILE_ERROR
