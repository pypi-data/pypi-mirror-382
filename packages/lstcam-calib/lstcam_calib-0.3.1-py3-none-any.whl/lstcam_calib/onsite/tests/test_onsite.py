import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from lstcam_calib.conftest import test_data

test_r0_path = test_data / "real/R0/"
test_subrun1 = test_r0_path / "20200218/LST-1.1.Run02005.0000_first50.fits.fz"
test_subrun2 = test_r0_path / "20210215/LST-1.1.Run03669.0000_first50.fits.fz"

PRO = "pro"
BASE_DIR = test_data / "real"


def test_default_config():
    from lstcam_calib.onsite import DEFAULT_CONFIG_CAT_A

    assert DEFAULT_CONFIG_CAT_A.is_file()

    # test it's valid json
    with DEFAULT_CONFIG_CAT_A.open("rb") as f:
        yaml.safe_load(f)


def test_create_symlink_overwrite(tmp_path):
    from lstcam_calib.onsite import create_symlink_overwrite

    target1 = tmp_path / "target1"
    target1.open("w").close()

    target2 = tmp_path / "target2"
    target2.open("w").close()

    # link not yet existing case
    link = tmp_path / "link"
    create_symlink_overwrite(link, target1)
    assert link.resolve() == target1.resolve()

    # link points to the wrong target, recreate
    create_symlink_overwrite(link, target2)
    assert link.resolve() == target2.resolve()

    # link exists, points already to the target, this should be a no-op
    # but I didn't find a good way to verify that it really is one
    assert link.resolve() == target2.resolve()


def test_create_pro_link(tmp_path: Path):
    from lstcam_calib.onsite import create_pro_symlink

    v1 = tmp_path / "v1"
    v2 = tmp_path / "v2"
    pro = tmp_path / "pro"

    v1.mkdir()
    v2.mkdir()

    # test pro does not yet exist
    create_pro_symlink(v1)
    assert pro.exists()
    assert pro.resolve() == v1

    # test that prolink is relative, not absolute
    assert os.readlink(pro) == "v1"

    # test pro exists and points to older version
    create_pro_symlink(v2)
    assert pro.exists()
    assert pro.resolve() == v2


def test_find_r0_subrun(tmp_path):
    from lstcam_calib.onsite import find_r0_subrun

    tmp_r0 = tmp_path / "R0"
    correct = tmp_r0 / test_subrun1.parent.name
    correct.mkdir(parents=True)
    shutil.copy2(test_subrun1, correct / test_subrun1.name)

    # copy another run so we can make sure we really find the right one
    other = tmp_r0 / test_subrun2.parent.name
    other.mkdir(parents=True)
    shutil.copy2(test_subrun2, other / test_subrun2.name)

    path = find_r0_subrun(2005, 0, tmp_r0)
    assert path.resolve().parent == correct


def test_find_pedestal_file_from_data_tree():
    from lstcam_calib.onsite import find_pedestal_file_from_data_tree

    pedestal_file_name = "drs4_pedestal.Run02005.0000.h5"

    # find by run_id
    path = find_pedestal_file_from_data_tree(
        pro=PRO, pedestal_run=2005, base_dir=BASE_DIR, format="h5"
    )
    assert path.name == pedestal_file_name

    # find by night
    path = find_pedestal_file_from_data_tree(
        pro=PRO, date="20200218", base_dir=BASE_DIR, format="h5"
    )
    assert path.name == pedestal_file_name

    # if both are given, run takes precedence
    path = find_pedestal_file_from_data_tree(
        pro=PRO, pedestal_run=2005, date="20191124", base_dir=BASE_DIR, format="h5"
    )
    assert path.name == pedestal_file_name

    with pytest.raises(IOError, match="Pedestal file from run 2010 not found"):
        # wrong run
        find_pedestal_file_from_data_tree(pro=PRO, pedestal_run=2010, base_dir=BASE_DIR)


def test_find_pedestal_file_from_db(onsite_test_tree, onsite_database):
    from lstcam_calib.onsite import find_pedestal_file_from_db

    db = onsite_database

    path = find_pedestal_file_from_db(db, pro=PRO, pedestal_run=2005)
    assert path.name == "drs4_pedestal.Run02005.0000.h5"
    assert path.exists()

    data_date = datetime.strptime("20200219", "%Y%m%d")
    path = find_pedestal_file_from_db(db, pro=PRO, date=data_date)
    assert path.name == "drs4_pedestal.Run02005.0000.h5"
    assert path.exists()

    # test day before validity date of calibration time run (20200218)
    data_date = datetime.strptime("20200217", "%Y%m%d")
    with pytest.raises(
        OSError, match="No time calibration file found for date 2020-02-17 00:00:00"
    ):
        find_pedestal_file_from_db(db, pro=PRO, date=data_date)


def test_find_pedestal_file(onsite_test_tree, onsite_database):
    from lstcam_calib.onsite import find_pedestal_file

    pedestal_file_name = "drs4_pedestal.Run02005.0000.h5"
    db = onsite_database

    # find by tree
    path = find_pedestal_file(
        pro=PRO,
        pedestal_run=2005,
        date="20191124",
        base_dir=onsite_test_tree,
        db=None,
        format="h5",
    )
    assert path.name == pedestal_file_name

    # find by db
    path = find_pedestal_file(
        pro=PRO,
        pedestal_run=2005,
        date="20191124",
        base_dir=onsite_test_tree,
        db=db,
        format="h5",
    )
    assert path.name == pedestal_file_name


def test_find_run_summary():
    from lstcam_calib.onsite import find_run_summary

    # find by run_id
    path = find_run_summary(date="20200218", base_dir=BASE_DIR)
    assert path.name == "RunSummary_20200218.ecsv"

    path = find_run_summary(date="20201120", base_dir=BASE_DIR)
    assert path.name == "RunSummary_20201120.ecsv"

    with pytest.raises(IOError, match="Night summary file .* does not exist"):
        find_run_summary(date="20221120", base_dir=BASE_DIR)


def test_find_time_calibration_file_from_tree():
    from lstcam_calib.onsite import find_time_calibration_file_from_data_tree

    path = find_time_calibration_file_from_data_tree(
        pro=PRO, time_run=1625, base_dir=BASE_DIR
    )
    assert path.name == "time_calibration.Run01625.0000.h5"


def test_find_time_calibration_file_from_db(onsite_database):
    from lstcam_calib.onsite import find_time_calibration_file_from_db

    db = onsite_database

    path = find_time_calibration_file_from_db(db, pro=PRO, time_run=1625)
    assert path.name == "time_calibration.Run01625.0000.h5"

    assert path.exists()

    data_date = datetime.strptime("20200218", "%Y%m%d")
    path = find_time_calibration_file_from_db(db, pro=PRO, date=data_date)
    assert path.name == "time_calibration.Run01625.0000.h5"
    assert path.exists()

    # test day before validity date of calibration time run (20191124)
    data_date = datetime.strptime("20191123", "%Y%m%d")
    with pytest.raises(
        OSError, match="No time calibration file found for date 2019-11-23 00:00:00"
    ):
        find_time_calibration_file_from_db(db, pro=PRO, date=data_date)


def test_find_systematics_correction_file_from_data_tree():
    from lstcam_calib.onsite import find_systematics_correction_file_from_data_tree

    # no sys date
    path = find_systematics_correction_file_from_data_tree(
        pro=PRO, date="20200218", base_dir=BASE_DIR
    )
    assert path.name == "scan_fit_20200725.0000.h5"

    path = find_systematics_correction_file_from_data_tree(
        pro=PRO, date="20200218", sys_date="20200725", base_dir=BASE_DIR
    )
    assert path.name == "scan_fit_20200725.0000.h5"

    with pytest.raises(
        IOError, match="F-factor systematics correction file .* does not exist"
    ):
        # nonexistent sys date
        find_systematics_correction_file_from_data_tree(
            pro=PRO, date="20200218", sys_date="20190101", base_dir=BASE_DIR
        )


def test_find_systematics_correction_file_from_db(onsite_test_tree, onsite_database):
    from lstcam_calib.onsite import find_systematics_correction_file_from_db

    db = onsite_database

    # use the data date
    data_date = datetime.strptime("20200818", "%Y%m%d")
    path = find_systematics_correction_file_from_db(db, pro=PRO, date=data_date)
    assert path.name == "scan_fit_20200725.0000.h5"

    # search a specific date = validity start date
    sys_date = datetime.fromisoformat("2020-07-26 01:25:53.000")
    path = find_systematics_correction_file_from_db(db, pro=PRO, sys_date=sys_date)
    assert path.name == "scan_fit_20200725.0000.h5"


def test_rglob_symlinks(tmp_path):
    from lstcam_calib.onsite import rglob_symlinks

    # create a test structure similar to the real data
    r0 = tmp_path / "R0"
    r0g = tmp_path / "R0G"

    paths = [
        r0 / "20220101/run1.dat",
        r0 / "20220101/run2.dat",
        r0 / "20220102/run3.dat",
        r0 / "20220102/run4.dat",
        r0g / "20220103/run5.dat",
        r0g / "20220103/run6.dat",
    ]
    for path in paths:
        path.parent.mkdir(exist_ok=True, parents=True)
        path.open("w").close()
        if "R0G" in path.parts:
            # symlink R0G files to R0
            target = Path(str(path.parent).replace("R0G", "R0"))
            print(target, target.exists())
            if not target.exists():
                target.symlink_to(path.parent)

    # check "normal" file
    matches = rglob_symlinks(r0, "run1.dat")
    # check we get an iterator and not a list
    assert iter(matches) is iter(matches)
    assert list(matches) == [r0 / "20220101/run1.dat"]

    # check file in symlinked dir
    matches = rglob_symlinks(r0, "run5.dat")
    # check we get an iterator and not a list
    assert list(matches) == [r0 / "20220103/run5.dat"]

    # check multiple files
    matches = rglob_symlinks(r0, "run*.dat")
    # check we get an iterator and not a list
    assert len(list(matches)) == 6


def test_find_calibration_file_from_data_tree():
    from lstcam_calib.onsite import find_calibration_file

    # find by run_id
    path = find_calibration_file(
        pro=PRO, calibration_run=9506, base_dir=BASE_DIR, format="h5"
    )
    assert path.name == "calibration_filters_52.Run09506.0000.h5"

    # find by night
    path = find_calibration_file(
        pro=PRO, date="20200218", base_dir=BASE_DIR, format="h5"
    )
    assert path.name == "calibration_filters_52.Run02006.0000.h5"

    # if both are given, run takes precedence
    path = find_calibration_file(
        pro=PRO, calibration_run=2006, date="20191124", base_dir=BASE_DIR, format="h5"
    )
    assert path.name == "calibration_filters_52.Run02006.0000.h5"

    error = "Too many calibration files found for date 20221001: .*, choose one run"
    with pytest.raises(IOError, match=error):
        # if many calibration runs in one date
        find_calibration_file(pro=PRO, date="20221001", base_dir=BASE_DIR, format="h5")

    # find_calibration_file(pro=PRO, calibration_run=2010, base_dir=BASE_DIR)
    with pytest.raises(IOError, match="Calibration file from run .* not found"):
        # wrong run
        find_calibration_file(
            pro=PRO, calibration_run=2010, base_dir=BASE_DIR, format="h5"
        )
