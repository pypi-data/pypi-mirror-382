"""Support Functions For Onsite Tools."""
import logging
import os
import re
import sys
import tempfile
from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum, auto
from glob import glob
from importlib.resources import files
from pathlib import Path

import pymongo
from astropy.time import Time
from ctapipe.utils.filelock import FileLock

from lstcam_calib.io.database import CalibrationType

__all__ = []

log = logging.getLogger(__name__)


DEFAULT_BASE_PATH = Path("/fefs/onsite/data/lst-pipe/LSTN-01")
DEFAULT_R0_PATH = Path("/fefs/onsite/data/R0/LSTN-01/lst-arraydaq/events")
DEFAULT_DL1_PATH = DEFAULT_BASE_PATH / "DL1"
PIXEL_DIR_CAT_A = "service/PixelCalibration/Cat-A"
PIXEL_DIR_CAT_B = "monitoring/PixelCalibration/Cat-B"

DEFAULT_CONFIG_CAT_A = files("lstcam_calib").joinpath(
    "resources/catA_camera_calibration_param.yml"
)
DEFAULT_CONFIG_CAT_B = files("lstcam_calib").joinpath(
    "resources/catB_camera_calibration_param.yml"
)
Run = namedtuple("Run", "tel_id run subrun stream")

CALIBRATION_RE = re.compile(
    r"(?:.*)"  # prefix
    r".Run(\d+)"  # run number
    r"(?:.(\d+))?"  # subrun number
)


def str_to_bool(answer):
    """Translate string yes/no to boolean."""
    if answer.lower() in {"y", "yes"}:
        return True

    if answer.lower() in {"n", "no"}:
        return False

    raise ValueError("Invalid choice, use one of [y, yes, n, no]")


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    Parameters
    ----------
    question: str
        question to the user

    default: str - "yes", "no" or None
        resumed answer if the user just hits <Enter>.
        "yes" or "no" will set a default answer for the user
        None will require a clear answer from the user

    Returns
    -------
    bool - True for "yes", False for "no"
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
        default = True
    elif default == "no":
        prompt = " [y/N] "
        default = False
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice == "" and default is not None:
            return default
        else:
            try:
                return str_to_bool(choice)
            except ValueError:
                print(
                    "Please respond with 'yes' or 'no' (or 'y' or 'n').",
                    file=sys.stderr,
                )


def parse_int(string):
    """Parse string to int."""
    if string is None:
        return None
    return int(string)


def parse_calibration_name(filename):
    """Return ntuple with run info."""
    m = CALIBRATION_RE.match(os.path.basename(filename))
    if m is None:
        raise ValueError(f"Filename {filename} does not match pattern {CALIBRATION_RE}")

    run, subrun = m.groups()
    return Run(tel_id=None, run=parse_int(run), subrun=parse_int(subrun), stream=None)


class DataCategory(Enum):
    """Define data category."""

    #: Real-Time data processing
    A = auto()
    #: Onsite processing
    B = auto()
    #: Offsite processing
    C = auto()


def is_date(s):
    """Verify date."""
    try:
        datetime.strptime(s, "%Y%m%d")
        return True
    except ValueError:
        return False


def is_datetime(s):
    """Verify date."""
    try:
        datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
        return True
    except ValueError:
        return False


def create_symlink_overwrite(link, target):
    """Create a symlink from link to target, replacing an existing link atomically."""
    if not link.exists():
        link.symlink_to(target)
        return

    if link.resolve() == target:
        # nothing to do
        return

    # create the symlink in a tempfile, then replace the original one
    # in one step to avoid race conditions
    tmp = tempfile.NamedTemporaryFile(
        prefix="tmp_symlink_",
        delete=True,
        # use same directory as final link to assure they are on the same device
        # avoids "Invalid cross-device link error"
        dir=link.parent,
    )
    tmp.close()
    tmp = Path(tmp.name)

    tmp.symlink_to(target)
    tmp.replace(link)


def create_pro_symlink(output_dir):
    """Create a "pro" symlink to the dir in the same directory."""
    output_dir = Path(output_dir)
    pro_link = output_dir.parent / "pro"

    with FileLock(str(pro_link) + ".lock"):
        # the pro-link should be relative to make moving / copying a tree easy
        create_symlink_overwrite(pro_link, output_dir.relative_to(pro_link.parent))


def rglob_symlinks(path, pattern):
    """Find R0G following symlinks."""
    # Same as Path.rglob
    # convert results back to path
    return (Path(p) for p in glob(f"{path}/**/{pattern}"))


def find_r0_subrun(run, sub_run, r0_dir=DEFAULT_R0_PATH):
    """Find the given subrun R0 file (i.e. globbing for the date part)."""
    file_list = rglob_symlinks(r0_dir, f"LST-1.1.Run{run:05d}.{sub_run:04d}*.fits.fz")
    # ignore directories that are not a date, e.g. "Trash"
    file_list = [p for p in file_list if is_date(p.parent.name)]

    if len(file_list) == 0:
        raise OSError(f"Run {run} not found in r0_dir {r0_dir} \n")

    if len(file_list) > 1:
        raise OSError(f"Found more than one file for run {run}.{sub_run}: {file_list}")

    return file_list[0]


def find_pedestal_file(
    pro,
    pedestal_run=None,
    date=None,
    base_dir=DEFAULT_BASE_PATH,
    db=None,
    format="fits.gz",
):
    """Find pedestal file from data tree or data-base."""
    if pedestal_run is None and date is None:
        raise ValueError("Must give at least `date` or `run`")

    if db is not None:
        # set the date in datetime and consider the full day as for the data tree (to be changed)
        if date is not None and is_date(date):
            date = datetime.strptime(date, "%Y%m%d") + timedelta(days=1)
        return find_pedestal_file_from_db(db, pro, pedestal_run, date)
    else:
        return find_pedestal_file_from_data_tree(
            pro, pedestal_run, date, base_dir, format
        )


def find_pedestal_file_from_db(db, pro=None, pedestal_run=None, date=None):
    """Find pedestal file searching in database."""
    if pedestal_run is None and date is None:
        raise ValueError("Must give at least `date` or `pedestal_run`")

    if pro == "pro":
        pro = None

    if pedestal_run is not None:
        # search a specific run
        doc = db.find_document_by_run(CalibrationType.DRS4_BASELINE, pedestal_run, pro)

        if doc is None:
            raise OSError(f"No baseline file found with run {pedestal_run}\n")

    else:
        if not isinstance(date, datetime):
            raise ValueError(f"date {date} must be of type datetime")

        doc = db.find_used_document_in_date(CalibrationType.DRS4_BASELINE, date, pro)

        if doc is None:
            raise OSError(f"No time calibration file found for date {date}\n")

    return db.data_tree_root / doc["path"]


def find_pedestal_file_from_data_tree(
    pro, pedestal_run=None, date=None, base_dir=DEFAULT_BASE_PATH, format="fits.gz"
):
    """Find pedestal file searching in the data tree."""
    # pedestal base dir
    ped_dir = Path(base_dir) / PIXEL_DIR_CAT_A / "drs4_baseline"

    if pedestal_run is None and date is None:
        raise ValueError("Must give at least `date` or `pedestal_run`")

    if pedestal_run is not None:
        # search a specific pedestal run
        file_list = sorted(
            ped_dir.rglob(f"*/{pro}/drs4_pedestal.Run{pedestal_run:05d}.0000.{format}")
        )

        if len(file_list) == 0:
            raise OSError(f"Pedestal file from run {pedestal_run} not found\n")

        return file_list[0].resolve()

    # search for a unique pedestal file from the same date
    file_list = sorted((ped_dir / date / pro).glob(f"drs4_pedestal*.0000.{format}"))

    if len(file_list) == 0:
        raise OSError(f"No pedestal file found for date {date}")

    if len(file_list) > 1:
        raise OSError(
            f"Too many pedestal files found for date {date}: {file_list}, choose one run\n"
        )

    return file_list[0].resolve()


def find_run_summary(date, base_dir=DEFAULT_BASE_PATH):
    """Find RunSummary file."""
    run_summary_path = base_dir / f"monitoring/RunSummary/RunSummary_{date}.ecsv"
    if not run_summary_path.exists():
        raise OSError(f"Night summary file {run_summary_path} does not exist\n")
    return run_summary_path


def find_time_calibration_file(
    pro, date=None, time_run=None, base_dir=DEFAULT_BASE_PATH, db=None
):
    """Find a time calibration file for given run."""
    if db is not None:
        # set the date in datetime and consider the full day as for the data tree (to be changed)
        if date is not None and is_date(date):
            date = datetime.strptime(date, "%Y%m%d") + timedelta(days=1)

        return find_time_calibration_file_from_db(db, pro, date, time_run)
    else:
        return find_time_calibration_file_from_data_tree(pro, date, time_run, base_dir)


def find_time_calibration_file_from_db(db, pro, date=None, time_run=None):
    """Find a time calibration file for a given run or date searching in database."""
    if time_run is None and date is None:
        raise ValueError("Must give at least `date` or `time_run`")

    if pro == "pro":
        pro = None

    if time_run is not None:
        # search a specific time calibration run
        doc = db.find_document_by_run(CalibrationType.DRS4_TIME_SAMPLING, time_run, pro)

        if doc is None:
            raise OSError(f"No time calibration file done with run {time_run}\n")

    # search the first document enabled in that date
    else:
        if not isinstance(date, datetime):
            raise ValueError(f"date {date} must be of type datetime")

        doc = db.find_used_document_in_date(
            CalibrationType.DRS4_TIME_SAMPLING, date, pro
        )

        if doc is None:
            raise OSError(f"No time calibration file found for date {date}\n")

    return db.data_tree_root / doc["path"]


def find_time_calibration_file_from_data_tree(
    pro, date=None, time_run=None, base_dir=DEFAULT_BASE_PATH
):
    """Find a time calibration file for given run searching in data tree."""
    if time_run is None and date is None:
        raise ValueError("Must give at least `run` or `time_run`")

    time_dir = Path(base_dir) / PIXEL_DIR_CAT_A / "drs4_time_sampling_from_FF"

    if time_run is None:
        # search the first time calibation file before or equal to that date
        dir_list = sorted(time_dir.rglob(f"*/{pro}/time_calibration.Run*"))
        if len(dir_list) == 0:
            raise OSError(
                f"No time calibration file found for production {pro} in {time_dir}\n"
            )

        time_date_list = sorted([path.parts[-3] for path in dir_list], reverse=True)
        selected_date = next(
            (day for day in time_date_list if day <= date), time_date_list[-1]
        )

        file_list = sorted(
            time_dir.rglob(f"{selected_date}/{pro}/time_calibration.Run*")
        )

        if len(file_list) == 0:
            raise OSError(
                f"No time calibration file found in the data tree for prod {pro}\n"
            )
        if len(file_list) > 1:
            raise OSError(
                f"Too many time calibration files found for date {date}: {file_list}, choose one run\n"
            )
    else:
        # if given, search a specific time file
        file_list = sorted(
            time_dir.rglob(f"*/{pro}/time_calibration.Run{int(time_run):05d}.0000.h5")
        )
        if len(file_list) == 0:
            raise OSError(f"Time calibration file from run {time_run} not found\n")

    return file_list[0].resolve()


def find_systematics_correction_file(
    pro, date=None, sys_date=None, base_dir=DEFAULT_BASE_PATH, db=None
):
    """Find a time calibration file for given run."""
    if db is not None:
        # set the date in datetime and consider the full day as for the data tree (to be changed)
        if date is not None and is_date(date):
            date = datetime.strptime(date, "%Y%m%d") + timedelta(days=1)

        # if a specific date is asked, it must correspond to the full validity_start datetime
        if sys_date is not None:
            sys_date = datetime.fromisoformat(sys_date)

        return find_systematics_correction_file_from_db(db, pro, date, sys_date)
    else:
        return find_systematics_correction_file_from_data_tree(
            pro, date, sys_date, base_dir
        )


def find_systematics_correction_file_from_data_tree(
    pro, date=None, sys_date=None, base_dir=DEFAULT_BASE_PATH
):
    """Find systematic correction file searching in data tree."""
    sys_dir = Path(base_dir) / PIXEL_DIR_CAT_A / "ffactor_systematics"

    # search in a specific date
    if sys_date is not None:
        path = (
            sys_dir / sys_date / pro / f"ffactor_systematics_{sys_date}.h5"
        ).resolve()
        if not path.exists():
            raise OSError(f"F-factor systematics correction file {path} does not exist")
        return path

    # search the first systematics file before "date"
    dir_list = sorted(sys_dir.rglob(f"*/{pro}/ffactor_systematics*"))

    if len(dir_list) == 0:
        raise OSError(
            f"No systematic correction file found for production {pro} in {sys_dir}\n"
        )

    sys_date_list = sorted([path.parts[-3] for path in dir_list], reverse=True)
    selected_date = next(
        (day for day in sys_date_list if day <= date), sys_date_list[-1]
    )

    return (
        sys_dir / selected_date / pro / f"ffactor_systematics_{selected_date}.h5"
    ).resolve()


def find_systematics_correction_file_from_db(db, pro, date=None, sys_date=None):
    """Find systematic correction file searching in db."""
    if sys_date is None and date is None:
        raise ValueError("Must give at least `date` or `time_run`")

    if pro == "pro":
        pro = None

    if sys_date is not None:
        if not isinstance(sys_date, datetime):
            raise ValueError(f"date {sys_date} must be of type datetime")

        doc = db.find_document_by_usage_start(
            CalibrationType.FFACTOR_SYSTEMATICS, sys_date, pro
        )

    else:
        if not isinstance(date, datetime):
            raise ValueError(f"date {date} must be of type datetime")

        # search the first document enabled in the requested date
        doc = db.find_used_document_in_date(
            CalibrationType.FFACTOR_SYSTEMATICS, date, pro
        )

    return db.data_tree_root / doc["path"]


def find_calibration_file(
    pro,
    calibration_run=None,
    date=None,
    base_dir=DEFAULT_BASE_PATH,
    category=DataCategory.A,
    db=None,
    format="fits.gz",
):
    """Find a time calibration file for given run."""
    if db is not None:
        return find_calibration_file_from_db(db, pro, date, calibration_run, category)
    else:
        return find_calibration_file_from_data_tree(
            pro, date, calibration_run, base_dir, category, format
        )


def find_calibration_file_from_db(
    db,
    pro,
    date=None,
    calibration_run=None,
    category=DataCategory.A,
):
    """Find a  calibration file for a given run or date searching in database."""
    if calibration_run is None and date is None:
        raise ValueError("Must give at least `date` or `calibration_run`")

    if category != DataCategory.A:
        raise ValueError("DB store only Cat-A data, while asked {category}")

    if pro == "pro":
        pro = None

    if calibration_run is not None:
        # search a specific time calibration run
        doc = db.find_enabled_document_by_run(
            CalibrationType.CALIBRATION, calibration_run, pro
        )

        if doc is None:
            raise OSError(f"No calibration file done with run {calibration_run}\n")

    else:
        # search the first document enabled in that date
        doc = db.find_used_document_in_date(CalibrationType.CALIBRATION, date, pro)

        if doc is None:
            raise OSError(f"No  calibration file found for date {date}\n")

    return db.data_tree_root / doc.path


def find_calibration_file_from_data_tree(
    pro,
    date=None,
    calibration_run=None,
    base_dir=DEFAULT_BASE_PATH,
    category=DataCategory.A,
    format="fits.gz",
):
    """Find calibration file from data tree."""
    if category == DataCategory.A:
        cal_dir = Path(base_dir) / PIXEL_DIR_CAT_A / "calibration"
    elif category == DataCategory.B:
        cal_dir = Path(base_dir) / PIXEL_DIR_CAT_B / "calibration"
    else:
        raise ValueError(
            f"Argument 'category' can be only 'DataCategory.A' or 'DataCategory.B', not {category}"
        )

    if calibration_run is None and date is None:
        raise ValueError("Must give at least `date` or `run`")

    if calibration_run is not None:
        # search a specific calibration run
        file_list = sorted(
            cal_dir.rglob(
                f"*/{pro}/calibration*.Run{calibration_run:05d}.0000.{format}"
            )
        )

        if len(file_list) == 0:
            raise OSError(f"Calibration file from run {calibration_run} not found\n")

        return file_list[0].resolve()

    # search for a unique calibration file from the same date
    file_list = sorted((cal_dir / date / pro).glob(f"calibration*.0000.{format}"))

    if len(file_list) == 0:
        raise OSError(f"No calibration file found for date {date}")

    if len(file_list) > 1:
        raise OSError(
            f"Too many calibration files found for date {date}: {file_list}, choose one run\n"
        )

    return file_list[0].resolve()


def find_interleaved_subruns(run, run_dl1_dir, lstchain_version=None):
    """Find the given subrun of interleaved file in onsite tree."""
    # look in R0 to find the date
    lstchain_version = (
        lstchain_version
        or sorted(
            [x.name.split("v")[-1] for x in list(run_dl1_dir.rglob("v*"))], reverse=True
        )[0]
    )

    # search the files
    interleaved_dir = run_dl1_dir / f"v{lstchain_version}/interleaved"

    file_list = sorted(interleaved_dir.rglob(f"interleaved_LST-1.Run{run:05d}.*.h5"))

    if len(file_list) == 0:
        raise OSError(f"Run {run} not found in interleaved dir {interleaved_dir}\n")

    return file_list


def find_filter_wheels(run, database_url):
    """Read the employed filters from mongodb."""
    # there was a change of Mongo DB data names on 5/12/2022
    new_db_names_date = Time("2022-12-04T00:00:00")

    filters = None
    try:
        myclient = pymongo.MongoClient(database_url)

        mydb = myclient["CACO"]
        mycol = mydb["RUN_INFORMATION"]
        mydoc = mycol.find({"run_number": {"$eq": run}})
        for x in mydoc:
            date = Time(x["start_time"])
            if date < new_db_names_date:
                w1 = int(x["cbox"]["wheel1 position"])
                w2 = int(x["cbox"]["wheel2 position"])
            else:
                w1 = int(x["cbox"]["CBOX_WheelPosition1"])
                w2 = int(x["cbox"]["CBOX_WheelPosition2"])

            filters = f"{w1:1d}{w2:1d}"

    except Exception as e:  # In the case the entry says 'No available'
        log.exception("\n >>> Exception: %s", e)
        raise OSError(
            "--> No mongo DB filter information."
            " You must pass the filters by argument: -f [filters]"
        )

    if filters is None:  # In the case the entry is missing
        raise OSError(
            "--> No filter information in mongo DB."
            " You must pass the filters by argument: -f [filters]"
        )

    return filters
