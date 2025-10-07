"""Configuration of Tests."""
import shutil
from pathlib import Path

import pytest
from ctapipe_io_lst import LSTEventSource

test_data = Path("test_data").absolute()

test_calib_path = test_data / "real/service/PixelCalibration/Cat-A"

test_calibration_file = (
    test_calib_path / "calibration/20200218/pro/calibration_filters_52.Run02006.0000.h5"
)
test_calibration_provenance_log = (
    test_calib_path
    / "calibration/20200218/pro/log/calibration_filters_52.Run02006.0000_2024-10-14T11:26:32.provenance.log"
)

test_run_summary_file = (
    test_data / "real/monitoring/RunSummary/RunSummary_20200218.ecsv"
)

test_systematics_file = (
    test_calib_path / "ffactor_systematics/20200725/pro/ffactor_systematics_20200725.h5"
)

test_systematics_provenance_log = (
    test_calib_path
    / "ffactor_systematics/20200725/pro/log/scan_fit_20200725.0000_2024-09-12T15:07:26.provenance.log"
)

test_time_calib_file = (
    test_calib_path
    / "drs4_time_sampling_from_FF/20191124/pro/time_calibration.Run01625.0000.h5"
)
test_time_calib_provenance_log = (
    test_calib_path
    / "drs4_time_sampling_from_FF/20191124/pro/log/time_calibration.Run01625.0000_2024-07-15T13:28:12.provenance.log"
)
test_drs4_pedestal_file = (
    test_calib_path / "drs4_baseline/20200218/pro/drs4_pedestal.Run02005.0000.h5"
)

test_drs4_pedestal_provenance_log = (
    test_calib_path
    / "drs4_baseline/20200218/pro/log/drs4_pedestal.Run02005.0000_2024-07-15T14:10:06.provenance.log"
)

test_drs4_timelapse_histo_file = (
    test_calib_path
    / "drs4_timelapse/20200218/pro/drs4_timelapse_histo.Run02005.0000.h5"
)

test_drs4_timelapse_histo_provenance_log = (
    test_calib_path
    / "drs4_timelapse/20200218/pro/log/drs4_timelapse_histo.Run02005.0000_2025-02-28T09:44:10.provenance.log"
)

test_drs4_timelapse_file = (
    test_calib_path / "drs4_timelapse/20200218/pro/drs4_timelapse.Run02005.0000.h5"
)

test_drs4_timelapse_provenance_log = (
    test_calib_path
    / "drs4_timelapse/20200218/pro/log/drs4_timelapse.Run02005.0000_2025-03-03T11:12:36.provenance.log"
)

test_drs4_timelapse_histo_file = (
    test_calib_path
    / "drs4_timelapse/20200218/pro/drs4_timelapse_histo.Run02005.0000.h5"
)

test_drs4_timelapse_histo_provenance_log = (
    test_calib_path
    / "drs4_timelapse/20200218/pro/log/drs4_timelapse_histo.Run02005.0000_2025-03-03T10:45:06.provenance.log"
)

test_interleaved_r1_path = test_data / "real/DL1/20200218/v0.10/interleaved"

test_drs4_r1_path = test_data / "real/R0/20200218/LST-1.1.Run02005.0000_first50.fits.fz"
test_calib_r1_path = (
    test_data / "real/R0/20200218/LST-1.1.Run02006.0000_first50.fits.fz"
)

TEST_DB = "test_db_functions"
TEST_ONSITE = "test_onsite_functions"


@pytest.fixture(scope="session")
def lst1_subarray():
    return LSTEventSource.create_subarray(tel_id=1)


@pytest.fixture(scope="session")
def clean_database():
    from lstcam_calib.io.database import CalibrationDB

    with CalibrationDB(
        db_name=TEST_DB,
        data_tree_root=test_data / "real",
    ) as db:
        yield db

        db.client.drop_database(db.db_name)


@pytest.fixture()
def onsite_test_tree(tmp_path_factory):
    path = tmp_path_factory.mktemp("onsite_test_tree_") / "real"
    shutil.copytree(test_data / "real/service", path / "service", symlinks=True)
    shutil.copytree(test_data / "real/monitoring", path / "monitoring", symlinks=True)
    return path


@pytest.fixture()
def onsite_database(onsite_test_tree):
    from lstcam_calib.io.database import CalibrationDB, CalibrationType

    def relative_to_test(path):
        return onsite_test_tree / path.relative_to(test_data / "real")

    with CalibrationDB(db_name=TEST_ONSITE, data_tree_root=onsite_test_tree) as db:
        # add baseline file and validate it
        run = 2005
        drs4_baseline = relative_to_test(test_drs4_pedestal_file)
        db.add_drs4_baseline_file(
            path=drs4_baseline,
            provenance_path=relative_to_test(test_drs4_pedestal_provenance_log),
            obs_id=run,
            local_run_id=run,
        )
        db.validate_file_quality(CalibrationType.DRS4_BASELINE, drs4_baseline)
        db.enable_file_usage(CalibrationType.DRS4_BASELINE, drs4_baseline)

        # add tamelapse file and validate it
        run = 2005
        drs4_timelapse = relative_to_test(test_drs4_timelapse_file)
        db.add_drs4_timelapse_file(
            path=drs4_timelapse,
            provenance_path=relative_to_test(test_drs4_timelapse_provenance_log),
            obs_id=run,
            local_run_id=run,
        )
        db.validate_file_quality(CalibrationType.DRS4_TIME_LAPSE, drs4_timelapse)
        db.enable_file_usage(CalibrationType.DRS4_TIME_LAPSE, drs4_timelapse)

        run = 1625
        # add drs4 time sampling file and validate it
        drs4_time_calib = relative_to_test(test_time_calib_file)
        db.add_drs4_time_sampling_file(
            path=drs4_time_calib,
            provenance_path=relative_to_test(test_time_calib_provenance_log),
            obs_id=run,
            local_run_id=run,
            drs4_baseline_path=drs4_baseline,
        )
        db.validate_file_quality(CalibrationType.DRS4_TIME_SAMPLING, drs4_time_calib)
        db.enable_file_usage(CalibrationType.DRS4_TIME_SAMPLING, drs4_time_calib)

        # add ffactor systematics file and validate it
        sys_file = relative_to_test(test_systematics_file)
        db.add_ffactor_systematics_file(
            path=sys_file,
            provenance_path=relative_to_test(test_systematics_provenance_log),
        )
        db.validate_file_quality(CalibrationType.FFACTOR_SYSTEMATICS, sys_file)
        db.enable_file_usage(CalibrationType.FFACTOR_SYSTEMATICS, sys_file)

        # add files for test of the intensity scan fit

        runs = [9493, 9495, 9497, 9498, 9503, 9506]
        for run in runs:
            cal_file = list(test_calib_path.rglob(f"calibration/20221001/pro/*{run}*"))[
                0
            ]
            file = relative_to_test(cal_file)
            cal_prov_file = list(
                test_calib_path.rglob(
                    f"calibration/20221001/pro/log/*{run}*.provenance.log"
                )
            )[0]
            prov_file = relative_to_test(cal_prov_file)

            db.add_calibration_file(
                path=file,
                provenance_path=prov_file,
                obs_id=run,
                local_run_id=run,
                drs4_baseline_path=drs4_baseline,
                drs4_time_sampling_path=drs4_time_calib,
                ffactor_systematics_path=sys_file,
            )
            # these files are only validated because the are not used as calibrations
            db.validate_file_quality(CalibrationType.CALIBRATION, file)

        yield db

        db.client.drop_database(db.db_name)
