from datetime import timedelta
from pathlib import Path

import pytest
from lstcam_calib.conftest import (
    test_calibration_file,
    test_calibration_provenance_log,
    test_drs4_pedestal_file,
    test_drs4_pedestal_provenance_log,
    test_drs4_timelapse_file,
    test_drs4_timelapse_provenance_log,
    test_systematics_file,
    test_systematics_provenance_log,
    test_time_calib_file,
    test_time_calib_provenance_log,
)
from lstcam_calib.io.database import CalibrationStatus, CalibrationType


@pytest.mark.order(1)
def test_add_drs4_timelapse_file(clean_database):
    """add baseline doc to db."""
    db = clean_database

    run = 2005

    # add a baseline file to db
    result = db.add_drs4_timelapse_file(
        path=test_drs4_timelapse_file,
        provenance_path=test_drs4_timelapse_provenance_log,
        obs_id=run,
        local_run_id=run,
    )

    # verify result
    assert result.acknowledged

    query = {"_id": result.inserted_id}
    assert db.collections[CalibrationType.DRS4_TIME_LAPSE].find_one(query)


@pytest.mark.order(2)
def test_add_drs4_baseline_file(clean_database):
    """add baseline doc to db."""
    db = clean_database

    run = 2005

    # add a baseline file to db
    result = db.add_drs4_baseline_file(
        path=test_drs4_pedestal_file,
        provenance_path=test_drs4_pedestal_provenance_log,
        obs_id=run,
        local_run_id=run,
    )

    # verify result
    assert result.acknowledged

    query = {"_id": result.inserted_id}
    assert db.collections[CalibrationType.DRS4_BASELINE].find_one(query)


@pytest.mark.order(3)
def test_add_drs4_time_sampling_file(clean_database):
    """add time doc to db."""

    db = clean_database

    # add the time file
    run = 2006
    result = db.add_drs4_time_sampling_file(
        path=test_time_calib_file,
        provenance_path=test_time_calib_provenance_log,
        obs_id=run,
        local_run_id=run,
        drs4_baseline_path=test_drs4_pedestal_file,
    )

    # verify result
    assert result.acknowledged


@pytest.mark.order(4)
def test_add_ffactor_systematics_file(clean_database):
    """add ffactor systematics doc to db."""

    db = clean_database

    result = db.add_ffactor_systematics_file(
        path=test_systematics_file,
        provenance_path=test_systematics_provenance_log,
    )

    # verify result
    assert result.acknowledged
    query = {"_id": result.inserted_id}
    assert db.collections[CalibrationType.FFACTOR_SYSTEMATICS].find_one(query)


@pytest.mark.order(5)
def test_add_calibration_file(clean_database):
    """add calibration doc to db."""

    db = clean_database

    run = 2006

    # finally, add calibration file
    result = db.add_calibration_file(
        path=test_calibration_file,
        provenance_path=test_calibration_provenance_log,
        obs_id=run,
        local_run_id=run,
        drs4_baseline_path=test_drs4_pedestal_file,
        drs4_time_sampling_path=test_time_calib_file,
        ffactor_systematics_path=test_systematics_file,
    )

    # verify result
    assert result.acknowledged
    query = {"_id": result.inserted_id}
    assert db.collections[CalibrationType.CALIBRATION].find_one(query)


@pytest.mark.order(6)
def test_validate_file_quality(clean_database):
    db = clean_database

    # validate the drs4 file in db corresponding to run 2005
    first_doc = db.validate_file_quality(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )

    assert first_doc["status"] == CalibrationStatus.VALID.value


@pytest.mark.order(7)
def test_enable_file_usage(clean_database):
    db = clean_database

    # validate the drs4 file in db corresponding to run 2005
    first_doc, _, _ = db.enable_file_usage(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )

    assert first_doc["usage_start"] is not None

    # add a new file successive in time to 2005 and activate it
    # we use run 2006  (even if it is a calibration run)
    run = 2006

    result = db.add_drs4_baseline_file(
        path=test_calibration_file,
        provenance_path=test_calibration_provenance_log,
        obs_id=run,
        local_run_id=run,
    )
    query = {"_id": result.inserted_id}
    _ = db.collections[CalibrationType.DRS4_BASELINE].find_one(query)

    # test enable the second file before validation
    with pytest.raises(
        ValueError,
        match="'File status is %s, it must be valid ', 'not_validated'",
    ):
        _ = db.enable_file_usage(CalibrationType.DRS4_BASELINE, test_calibration_file)

    # validate the second file
    db.validate_file_quality(CalibrationType.DRS4_BASELINE, test_calibration_file)

    # enable the second file in order to become the file to be used
    second_doc, first_doc, next_doc = db.enable_file_usage(
        CalibrationType.DRS4_BASELINE, test_calibration_file
    )

    # verify the second file is now enabled
    assert second_doc["usage_start"] is not None

    # verify the first used file has now a correct usage_stop
    first_doc = db.find_document_by_file(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )
    assert first_doc["usage_stop"] == second_doc["usage_start"]


@pytest.mark.order(8)
def test_find_document_by_file(clean_database):
    db = clean_database

    doc = db.find_document_by_file(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )

    assert db.data_tree_root / doc["path"] == test_drs4_pedestal_file.resolve()


@pytest.mark.order(9)
def test_find_document_by_usage_start(clean_database):
    db = clean_database

    doc = db.find_document_by_file(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )

    date = doc["usage_start"]

    doc = db.find_document_by_usage_start(CalibrationType.DRS4_BASELINE, date=date)

    assert db.data_tree_root / doc["path"] == test_drs4_pedestal_file.resolve()


@pytest.mark.order(10)
def test_find_document_by_run(clean_database):
    db = clean_database

    doc = db.find_document_by_run(CalibrationType.DRS4_BASELINE, run=2005)

    assert db.data_tree_root / doc["path"] == test_drs4_pedestal_file.resolve()


@pytest.mark.order(11)
def test_find_used_document_in_date(clean_database):
    db = clean_database

    first_doc = db.find_document_by_file(
        CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
    )

    second_doc = db.find_document_by_file(
        CalibrationType.DRS4_BASELINE, test_calibration_file
    )

    # find it back by date for data taken between the two files
    data_run_start = first_doc["usage_start"] + timedelta(minutes=5)
    doc = db.find_used_document_in_date(CalibrationType.DRS4_BASELINE, data_run_start)
    assert db.data_tree_root / doc["path"] == test_drs4_pedestal_file.resolve()

    # find it back by date for data taken after the second file
    data_run_start = second_doc["usage_start"] + timedelta(minutes=5)
    doc = db.find_used_document_in_date(CalibrationType.DRS4_BASELINE, data_run_start)
    assert db.data_tree_root / doc["path"] == test_calibration_file.resolve()

    # Test failing: find it back before any pedestal date
    data_run_start = first_doc["usage_start"] - timedelta(minutes=5)

    doc = db.find_used_document_in_date(CalibrationType.DRS4_BASELINE, data_run_start)
    assert doc is None


@pytest.mark.order(12)
def test_disable_file_usage(clean_database):
    db = clean_database

    # disable use of fake drs4 file in db corresponding to run 2006
    disabled_doc, previous_enabled_doc = db.disable_file_usage(
        CalibrationType.DRS4_BASELINE, test_calibration_file
    )

    assert disabled_doc["usage_start"] is None
    assert previous_enabled_doc["usage_stop"] is None


@pytest.mark.order(13)
def test_invalidate_file_quality(clean_database):
    db = clean_database

    # invalidate drs4 file corresponding to run 2005 (still in use)
    with pytest.raises(
        ValueError,
        match="'File is in use: usage_start = %s, you must desable its usage before invalidating'",
    ):
        db.invalidate_file_quality(
            CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file
        )

    # invalidate drs4 corresponding to run 2006 (not in use)
    first_doc = db.invalidate_file_quality(
        CalibrationType.DRS4_BASELINE, test_calibration_file
    )

    assert first_doc["status"] == CalibrationStatus.INVALID.value


@pytest.mark.order(14)
def test_remove_file(clean_database):
    db = clean_database

    # remove drs4 file corresponding to run 2005 (still in use)
    with pytest.raises(
        ValueError,
        match="File is in use: usage_start = %s, you must desable its usage before removing'",
    ):
        db.remove_file(CalibrationType.DRS4_BASELINE, test_drs4_pedestal_file)

    doc = db.find_document_by_file(CalibrationType.DRS4_BASELINE, test_calibration_file)

    # remove drs4 file corresponding to run 2006 (not in use)
    doc_removed = db.remove_file(CalibrationType.DRS4_BASELINE, test_calibration_file)

    assert doc == doc_removed

    # search it again
    doc = db.find_document_by_file(CalibrationType.DRS4_BASELINE, test_calibration_file)
    assert doc is None


def test_defaults(clean_database):
    db = clean_database

    assert db._db_name_default() == "pixel_calibration_LSTN-01"

    assert db._data_tree_root_default() == Path(
        f"/fefs/onsite/data/lst-pipe/LSTN-{db.tel_id:02d}"
    )
