"""Schema and connection utilities for the calibration database."""
import json
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

import pymongo
from ctapipe.core import Component, traits
from pydantic import BaseModel, PlainSerializer
from traitlets.config import Config, default

from lstcam_calib.io import PROV_INPUT_ROLES

from .calibration import get_metadata

__all__ = [
    "CalibrationDB",
    "CalibrationType",
    "CalibrationStatus",
    "CalibrationServiceId",
    "CommonFields",
    "DRS4BaselineFile",
    "DRS4TimeSamplingFile",
    "DRS4TimeLapseFile",
    "CalibrationFile",
    "FFactorSystematicsFile",
    "PathStr",
]


PathStr = Annotated[Path, PlainSerializer(str, return_type=str)]


class CalibrationType(Enum):
    """Name of collections in the calibration database."""

    #: Collection of documents with meta-data of DRS4 baseline and spikes files
    DRS4_BASELINE = "drs4_baseline"
    #: Collection of documents with meta-data of DRS4 time sampling files
    DRS4_TIME_SAMPLING = "drs4_time_sampling"
    #: Collection of documents with meta-data of DRS4 timelapse files
    DRS4_TIME_LAPSE = "drs4_time_lapse"
    #: Collection of documents with meta-data of pixel calibration files
    CALIBRATION = "calibration"
    #: Collection of documents with meta-data of F-factor systematics files
    FFACTOR_SYSTEMATICS = "ffactor_systematics"


class CalibrationStatus(Enum):
    """Status of documents in the calibration database."""

    #: Calibration not yet verified by the data quality checks.
    NOT_VALIDATED = "not_validated"
    #: Calibration  not validated by the data quality checks.
    INVALID = "invalid"
    #: Calibration validated by the data quality checks.
    VALID = "valid"


CalibrationStatusStr = Annotated[
    CalibrationStatus, PlainSerializer(lambda s: s.value, return_type=str)
]


class CalibrationServiceId(BaseModel):
    """Pydantic schema with all paths of correction and calibration files."""

    #: Incremental id to be used in the CameraConfiguration of the R1 datamodel
    calibration_service_id: int

    #: Path to the DRS4 baseline file used to correct R0 input file
    drs4_baseline_path: PathStr

    #: Path to the DRS4 time lapse file used to correct R0 input file
    drs4_time_lapse_path: PathStr

    #: Path to the DRS4 time sampling file to be used to correct pulse time
    drs4_time_sampling_path: PathStr

    #: Path to the calibration file with dc_to_pe data
    calibration_path: PathStr

    #: Timestamp when this calibration document was last updated
    last_modified: datetime


class CommonFields(BaseModel):
    """Pydantic schema with fields common to all calibration files."""

    #: Provenance production id
    product_id: str
    #: Status of the file
    status: str
    #: Start time in which calibration is used
    usage_start: datetime | None = None
    #: End time in which calibration is used
    usage_stop: datetime | None = None
    #: Time of production of the calibration
    processing_time: datetime
    #: Path of the calibration file in the data-tree
    path: PathStr
    #: Path of the proveance file in the data-tree
    provenance_path: PathStr
    #: Version of lstcam_calib used for processing
    lstcam_calib_version: str
    #: Timestamp when this calibration document was last updated
    last_modified: datetime


class DRS4BaselineFile(CommonFields):
    """Pydantic model for a drs4 baseline file in the calibration db."""

    #: CTAO observation index of the R0/R1 data used for the calibration
    obs_id: int

    #: Local run index of R0/R1 data used for the calibration
    local_run_id: int


class DRS4TimeLapseFile(CommonFields):
    """Pydantic model for a drs4 time lapse file in the calibration db."""

    #: CTAO observation index of the R0/R1 data used for the calibration
    obs_id: int

    #: Local run index of R0/R1 data used for the calibration
    local_run_id: int


class DRS4TimeSamplingFile(CommonFields):
    """Pydantic model for a drs4 time sampling file in the calibration db."""

    #: CTAO observation index of the R0/R1 data used for the calibration
    obs_id: int

    #: Local run index of R0/R1 data used for the calibration
    local_run_id: int

    #: Path to the DRS4 baseline file used to correct R0 input file
    drs4_baseline_path: PathStr | None = None


class FFactorSystematicsFile(CommonFields):
    """Pydantic model for a ffactor systematics file in the calibration db."""

    #: List of paths to R1 input files
    calibration_paths: list


class CalibrationFile(CommonFields):
    """Pydantic model for a calibration file in the calibration db."""

    #: CTAO observation index of the R0/R1 data used for the calibration
    obs_id: int

    #: Local run index of R0/R1 data used for the calibration
    local_run_id: int

    #: Path to the DRS4 baseline file used to correct R0 input file
    drs4_baseline_path: PathStr | None = None

    #: Path to the DRS4 time file used to correct R0 input file
    drs4_time_sampling_path: PathStr | None = None

    #: Path to the F-factor systematics file to correct F-factor formula
    ffactor_systematics_path: PathStr | None = None


MODELS = {
    CalibrationType.DRS4_BASELINE: DRS4BaselineFile,
    CalibrationType.DRS4_TIME_SAMPLING: DRS4TimeSamplingFile,
    CalibrationType.DRS4_TIME_LAPSE: DRS4TimeLapseFile,
    CalibrationType.CALIBRATION: CalibrationFile,
    CalibrationType.FFACTOR_SYSTEMATICS: FFactorSystematicsFile,
}


class CalibrationDB(Component):
    """Archive calibration meta-data in mongo database."""

    tel_id = traits.Int(default_value=1, help="ID of telescope").tag(config=True)

    db_url = traits.Unicode(
        default_value=os.getenv("LSTCAM_CALIB_DB_URL", "mongodb://localhost:27017"),
        help=(
            "Url of mongo database. Default is localhost with standard port."
            " Can be overridden with the LSTCAM_CALIB_DB_URL environment variable"
        ),
    ).tag(config=True)

    db_name = traits.Unicode(
        help="The mongo database name, by default it will be pixel_calibration_tel_{tel_id:03d}"
    ).tag(config=True)

    data_tree_root = traits.Path(
        help=(
            "Root of the data tree. All paths will be stored"
            " relative to this root to allow moving data etc."
        ),
    ).tag(config=True)

    @default("data_tree_root")
    def _data_tree_root_default(self):
        return Path(f"/fefs/onsite/data/lst-pipe/LSTN-{self.tel_id:02d}")

    @default("db_name")
    def _db_name_default(self):
        return f"pixel_calibration_LSTN-{self.tel_id:02d}"

    def __init__(self, parent=None, config=None, **kwargs):
        super().__init__(parent=parent, config=config, **kwargs)

        self.client = pymongo.MongoClient(self.db_url)
        try:
            self.client.admin.command("ping")
        except Exception:
            raise ConnectionError("Error in connecting to calibration db.")

        self.db = self.client[self.db_name]
        self.collections = {
            calib_type: self.db[calib_type.name] for calib_type in CalibrationType
        }
        self.service_id_collection = self.db["CALIBRATION_SERVICE_ID"]

        parsed_url = urlparse(self.db_url)
        self.log.info(
            "Connected with host %s, port %s, user %s",
            parsed_url.hostname,
            parsed_url.port,
            parsed_url.username,
        )

    def disconnect(self):
        """Disconnect from mongo database."""
        self.client.close()

    def __enter__(self):
        """Enter function."""
        return self

    def __exit__(self, exc_class, exc_value, traceback):
        """Exit function."""
        self.disconnect()

    def relative_path(self, path: os.PathLike):
        """Return path relative to data_tree_root."""
        return Path(path).resolve().absolute().relative_to(self.data_tree_root)

    def find_document_by_file(self, type, path: Path):
        """Return the document of a given file."""
        try:
            rel_path = self.relative_path(path)
        except ValueError:
            raise ValueError(
                f"Given path '{path}' is not inside self.data_tree_root: '{self.data_tree_root}'"
            )

        # find collection
        col = self.collections[type]

        # search the file (unique index in the data base)
        doc = col.find_one({"path": str(rel_path)})

        if doc is None:
            self.log.debug("File %s not found in database", rel_path)
            return None

        # verify if file exists
        elif not path.is_file():
            raise ValueError(f"Path {path} does not exist.")

        return doc

    def find_document_by_run(
        self,
        type,
        run,
        used=True,
        valid=True,
        lstcam_calib_version=None,
    ):
        """
        Return document by local run id.

        If used = False, search also for files not in use.
        If valid = False search also for not validated files.
        If lstcam_calib_version is None, return the document
        corresponding to the last processed file.

        """
        # find collection
        col = self.collections[type]

        query = {"local_run_id": run}

        if valid:
            query["status"] = CalibrationStatus.VALID.value
        if used:
            query["usage_start"] = {"$ne": None}

        if lstcam_calib_version is not None:
            query["lstcam_calib_version"] = lstcam_calib_version

        # search for the query and sort for the last processed file
        # (equivalent to pro link in the data tree if lscam_calib_version
        # is not given)

        sort_by = [("processing_time", pymongo.DESCENDING)]
        doc = next(col.find(query).sort(sort_by).limit(1), None)

        if doc is None:
            raise ValueError("No document in use found in the db")

        return doc

    def find_document_by_usage_start(
        self,
        type,
        date: datetime,
        lstcam_calib_version=None,
    ):
        """Return document with usage_start equal to date ."""
        if not isinstance(date, datetime):
            raise ValueError(f"date {date} must be of type datetime")

        # find collection
        col = self.collections[type]

        query = {"status": CalibrationStatus.VALID.value, "usage_start": date}
        if lstcam_calib_version is not None:
            query["lstcam_calib_version"] = lstcam_calib_version

        sort_by = [("processing_time", pymongo.DESCENDING)]
        doc = next(col.find(query).sort(sort_by).limit(1), None)

        if doc is None:
            raise ValueError("No valid document in use found in the db")

        return doc

    def find_used_document_in_date(
        self,
        type,
        date: datetime,
        lstcam_calib_version=None,
    ):
        """Return document used in that date."""
        if not isinstance(date, datetime):
            raise ValueError(f"date {date} must be of type datetime")

        # find collection
        col = self.collections[type]

        query = {
            "$and": [
                {"status": CalibrationStatus.VALID.value},
                {"usage_start": {"$lte": date}},
                {
                    "$or": [
                        {"usage_stop": None},
                        {"usage_stop": {"$gt": date}},
                    ]
                },
            ]
        }

        if lstcam_calib_version is not None:
            query["lstcam_calib_version"] = lstcam_calib_version

        # search for the query and sort for the first  usage_stop
        # and for the last processed file
        sort_by = [
            ("usage_stop", pymongo.ASCENDING),
            ("processing_time", pymongo.DESCENDING),
        ]
        doc = next(col.find(query).sort(sort_by).limit(1), None)

        if doc is None:
            self.log.warning("No usable document found in db")

        return doc

    def add_drs4_baseline_file(
        self,
        path: Path,
        provenance_path: Path,
        **kwargs,
    ):
        """Add a drs4 baseline file in the database."""
        return self._add_file(
            type_=CalibrationType.DRS4_BASELINE,
            path=path,
            provenance_path=provenance_path,
            **kwargs,
        )

    def add_drs4_timelapse_file(
        self,
        path: Path,
        provenance_path: Path,
        **kwargs,
    ):
        """Add a drs4 time lapse file in the database."""
        return self._add_file(
            type_=CalibrationType.DRS4_TIME_LAPSE,
            path=path,
            provenance_path=provenance_path,
            **kwargs,
        )

    def add_drs4_time_sampling_file(
        self,
        path: Path,
        provenance_path: Path,
        drs4_baseline_path: Path,
        **kwargs,
    ):
        """Add a drs4 time sampling file in the database."""
        # verify drs4 baseline path
        if drs4_baseline_path:
            if (
                self.find_document_by_file(
                    CalibrationType.DRS4_BASELINE, drs4_baseline_path
                )
                is None
            ):
                raise ValueError(
                    f"drs4_baseline_path {drs4_baseline_path} is not in database"
                )
            else:
                drs4_baseline_path = self.relative_path(drs4_baseline_path)

        return self._add_file(
            type_=CalibrationType.DRS4_TIME_SAMPLING,
            path=path,
            provenance_path=provenance_path,
            drs4_baseline_path=drs4_baseline_path,
            **kwargs,
        )

    def add_ffactor_systematics_file(
        self,
        path: Path,
        provenance_path: Path,
        **kwargs,
    ):
        """Add a ffactor sytematics file in the database."""
        # retrieve calibration paths

        calibration_paths = []
        with open(provenance_path) as f:
            prov_log = Config(json.load(f)[0])
            for input in prov_log.input:
                if input["role"] == PROV_INPUT_ROLES["fit_intensity_scan"]:
                    cal_path = Path(input["url"])
                    calibration_paths.append(str(cal_path))

        return self._add_file(
            type_=CalibrationType.FFACTOR_SYSTEMATICS,
            path=path,
            provenance_path=provenance_path,
            calibration_paths=calibration_paths,
            **kwargs,
        )

    def add_calibration_file(
        self,
        path: Path,
        provenance_path: Path,
        drs4_baseline_path: Path,
        drs4_time_sampling_path: Path,
        ffactor_systematics_path: Path,
        **kwargs,
    ):
        """Add a calibration file in the database."""
        # verify drs4 baseline path

        if drs4_baseline_path:
            if (
                self.find_document_by_file(
                    CalibrationType.DRS4_BASELINE, drs4_baseline_path
                )
                is None
            ):
                raise ValueError(
                    f"drs4_baseline_path {drs4_baseline_path} is not in database"
                )
            else:
                drs4_baseline_path = self.relative_path(drs4_baseline_path)

        # verify drs4 time path
        if drs4_time_sampling_path:
            if (
                self.find_document_by_file(
                    CalibrationType.DRS4_TIME_SAMPLING, drs4_time_sampling_path
                )
                is None
            ):
                raise ValueError(
                    f"drs4_time_sampling_path {drs4_time_sampling_path} is not in database"
                )
            else:
                drs4_time_sampling_path = self.relative_path(drs4_time_sampling_path)

        # verify ffactor systematics path
        if ffactor_systematics_path:
            if (
                self.find_document_by_file(
                    CalibrationType.FFACTOR_SYSTEMATICS, ffactor_systematics_path
                )
                is None
            ):
                raise ValueError(
                    f"factor_sytematics_path {ffactor_systematics_path} is not in database"
                )
            else:
                ffactor_systematics_path = self.relative_path(ffactor_systematics_path)

        return self._add_file(
            type_=CalibrationType.CALIBRATION,
            path=path,
            provenance_path=provenance_path,
            drs4_baseline_path=drs4_baseline_path,
            drs4_time_sampling_path=drs4_time_sampling_path,
            ffactor_systematics_path=ffactor_systematics_path,
            **kwargs,
        )

    def _add_file(self, type_, path, provenance_path, **kwargs):
        """Add document related to a file in the database."""
        if not path.is_file():
            raise ValueError(f"path {path} is not an existing file")

        doc = self.find_document_by_file(type_, path)

        if doc is not None:
            raise ValueError("File %s is already in the database", path)

        if not provenance_path.is_file():
            raise ValueError(
                f"provenance_path {provenance_path} is not an existing file"
            )

        meta = get_metadata(path)
        product_id = meta["CTA PRODUCT ID"]
        lstcam_calib_version = meta["LSTCAM_CALIB_VERSION"]

        # read provenance info
        with open(provenance_path) as f:
            prov_log = Config(json.load(f)[0])
            processing_time = datetime.fromisoformat(prov_log.start["time_utc"])

        path = self.relative_path(path)
        provenance_path = self.relative_path(provenance_path)

        # initialize first modification date (use UTC time)
        last_modified = datetime.now(tz=timezone.utc)

        db_document = MODELS[type_](
            product_id=product_id,
            status=CalibrationStatus.NOT_VALIDATED.value,
            path=path,
            provenance_path=provenance_path,
            processing_time=processing_time,
            lstcam_calib_version=lstcam_calib_version,
            last_modified=last_modified,
            **kwargs,
        )

        col = self.collections[type_]
        doc = db_document.model_dump()
        res = col.insert_one(doc)

        self.log.debug("Written new entry in db \n %s", doc)

        return res

    def invalidate_file_quality(self, type, file):
        """Set the status of file's document to INVALID after check of data quality."""
        # find correct collection
        col = self.collections[type]

        doc = self.find_document_by_file(type, file)

        if doc is None:
            raise ValueError("File %s not found in database", file)

        if doc["usage_start"] is not None:
            raise ValueError(
                "File is in use: usage_start = %s, you must desable its usage before invalidating",
                doc["usage_start"],
            )

        # update the new file to valid
        query_new_doc = {"path": str(self.relative_path(file))}
        update = {
            "$set": {"status": CalibrationStatus.INVALID.value},
            "$currentDate": {"last_modified": True},
        }

        not_valid_doc = col.find_one_and_update(
            query_new_doc, update, return_document=pymongo.ReturnDocument.AFTER
        )
        self.log.debug("Updated new document \n %s", not_valid_doc)

        return not_valid_doc

    def validate_file_quality(self, type, file):
        """Validate file in database after check of data quality."""
        # find correct collection
        col = self.collections[type]

        doc = self.find_document_by_file(type, file)

        if doc is None:
            raise ValueError("File %s not found in database", file)

        # update the new file to valid
        query_new_doc = {"path": str(self.relative_path(file))}
        update = {
            "$set": {"status": CalibrationStatus.VALID.value},
            "$currentDate": {"last_modified": True},
        }

        new_valid_doc = col.find_one_and_update(
            query_new_doc, update, return_document=pymongo.ReturnDocument.AFTER
        )
        self.log.debug("Updated new document \n %s", new_valid_doc)

        return new_valid_doc

    def enable_file_usage(self, type, file):
        """
        Enable usage of file.

        Set the usage_start value and update the valid_stop of previous used file.

        """
        # find correct collection
        col = self.collections[type]

        doc = self.find_document_by_file(type, file)

        if doc is None:
            raise ValueError("File %s not found in database", file)

        if doc["status"] != CalibrationStatus.VALID.value:
            raise ValueError("File status is %s, it must be valid ", doc["status"])

        # find the usage_start date of the new document
        meta = get_metadata(file)
        usage_start = datetime.fromisoformat(meta["RUN_START"])

        # search last previous used file and
        # update its usage_stop to the new doc usage_start

        query_previous_doc = {
            "status": CalibrationStatus.VALID.value,
            "usage_start": {"$lt": usage_start},
        }

        previous_used_doc = col.find_one(query_previous_doc)

        if previous_used_doc is not None:
            update = {
                "$set": {"usage_stop": usage_start},
                "$currentDate": {"last_modified": True},
            }

            sort_by = [
                ("usage_start", pymongo.DESCENDING),
                ("processing_time", pymongo.DESCENDING),
            ]

            previous_used_doc = col.find_one_and_update(
                query_previous_doc,
                update,
                sort=sort_by,
                return_document=pymongo.ReturnDocument.AFTER,
            )

            self.log.debug("Updated previous document \n %s", previous_used_doc)

        # search next used file (if any)
        query_next_doc = {
            "status": CalibrationStatus.VALID.value,
            "usage_start": {"$gt": usage_start},
        }

        sort_by = [
            ("usage_start", pymongo.ASCENDING),
            ("processing_time", pymongo.DESCENDING),
        ]

        next_used_doc = next(col.find(query_next_doc).sort(sort_by).limit(1), None)

        # if any doc, update the new doc usage_end to the next usage_start
        usage_stop = None
        if next_used_doc is not None:
            usage_stop = next_used_doc["usage_start"]

        # set the usage_start and usage_stop of the new doc
        query_new_doc = {"path": str(self.relative_path(file))}
        update = {
            "$set": {"usage_start": usage_start, "usage_stop": usage_stop},
            "$currentDate": {"last_modified": True},
        }

        new_used_doc = col.find_one_and_update(
            query_new_doc, update, return_document=pymongo.ReturnDocument.AFTER
        )

        # update service_id collection
        self.add_calibration_service_id()

        self.log.debug("Updated new document \n %s", new_used_doc)

        return new_used_doc, previous_used_doc, next_used_doc

    def disable_file_usage(self, type, file, lstcam_calib_version=None):
        """Disable usage of file for calibration."""
        # find correct collection
        col = self.collections[type]

        doc = self.find_document_by_file(type, file)

        if doc is None:
            raise ValueError("File %s not found in database", file)

        if doc["usage_start"] is None:
            raise ValueError(
                "File is not in use, usage_start = %s, nothing to do.",
                doc["usage_start"],
            )

        # search next used file
        query_next_doc = {
            "status": CalibrationStatus.VALID.value,
            "usage_start": {"$gt": doc["usage_start"]},
        }
        if lstcam_calib_version is not None:
            query_next_doc["lstcam_calib_version"] = lstcam_calib_version

        # sort for the for the first usage_start and the
        # last processed file (equivalent to pro link in the data tree if
        # lscam_calib_version  is not given)

        sort_by = [
            ("usage_start", pymongo.ASCENDING),
            ("processing_time", pymongo.DESCENDING),
        ]
        next_doc = next(col.find(query_next_doc).sort(sort_by).limit(1), None)

        if next_doc is None:
            new_stop = None
        else:
            new_stop = next_doc["usage_start"]

        # search previous used file
        # and update its usage_stop to the next_doc usage_start

        query_previous_doc = {
            "status": CalibrationStatus.VALID.value,
            "usage_stop": doc["usage_start"],
        }
        if lstcam_calib_version is not None:
            query_previous_doc["lstcam_calib_version"] = lstcam_calib_version

        update = {
            "$set": {"usage_stop": new_stop},
            "$currentDate": {"last_modified": True},
        }

        previous_used_doc = col.find_one_and_update(
            query_previous_doc, update, return_document=pymongo.ReturnDocument.AFTER
        )
        if previous_used_doc:
            self.log.debug("Updated previous document \n %s", previous_used_doc)

        # set usage_start and usage_stope to None (i.e. disable its use)
        query_new_doc = {"path": str(self.relative_path(file))}
        update = {
            "$set": {"usage_start": None, "usage_stop": None},
            "$currentDate": {"last_modified": True},
        }

        disabled_doc = col.find_one_and_update(
            query_new_doc, update, return_document=pymongo.ReturnDocument.AFTER
        )
        self.log.debug("Updated new document \n %s", disabled_doc)

        # update service_id collection
        self.add_calibration_service_id()

        return disabled_doc, previous_used_doc

    def remove_file(self, type, file):
        """Remove document relative to a calibration_file."""
        doc = self.find_document_by_file(type, file)

        if doc is None:
            self.log.warning("File %s not found in database", file)
            return None

        if doc["usage_start"] is not None:
            raise ValueError(
                "File is in use: usage_start = %s, you must desable its usage before removing",
                doc["usage_start"],
            )

        # find correct collection
        col = self.collections[type]

        rel_path = self.relative_path(file)

        # query for (unique) path
        query = {"path": str(rel_path)}
        doc = col.find_one_and_delete(query)

        self.log.debug("Deleted document \n %s", doc)

        return doc

    def add_calibration_service_id(self, **kwargs):
        """Add new calibration_service_id document."""
        date = datetime.now().isoformat(" ")
        paths = {}

        for calib_type in CalibrationType:
            doc = self.find_used_document_in_date(
                calib_type, datetime.fromisoformat(date)
            )
            if doc is None:
                paths[calib_type.name] = "None"
            else:
                paths[calib_type.name] = self.data_tree_root / doc["path"]

        # initialize first modification date (use UTC time)
        last_modified = datetime.now(tz=timezone.utc)

        # define the index as the timestamp in ms
        new_index = int(last_modified.timestamp() * 1000)

        db_document = CalibrationServiceId(
            calibration_service_id=new_index,
            drs4_baseline_path=paths["DRS4_BASELINE"],
            drs4_time_sampling_path=paths["DRS4_TIME_SAMPLING"],
            drs4_time_lapse_path=paths["DRS4_TIME_LAPSE"],
            calibration_path=paths["CALIBRATION"],
            last_modified=last_modified,
        )

        doc = db_document.model_dump()
        res = self.service_id_collection.insert_one(doc)

        self.log.debug("Written new calibration_service_id entry in db \n %s", doc)

        return res
