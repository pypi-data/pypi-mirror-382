"""
Tool to find the calibration files to be used in a given date.

It prints the database documents associated to the calibration files.

.. code:: python

    lstcam_calib_find_enabled_calibration_files --help

"""
from datetime import datetime

from ctapipe.core import Tool, traits

from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import is_datetime

__all__ = ["FindEnabledCalibrationFiles"]


class FindEnabledCalibrationFiles(Tool):
    """Find the calibration files to be used in a given date."""

    calibration_type = traits.UseEnum(
        CalibrationType,
        help="Type of calibration to search (if None search for all)",
        default_value=None,
        allow_none=True,
    ).tag(config=True)

    datetime = traits.Unicode(
        datetime.now().isoformat(" "),
        help="Date for which calibration files are searched (format: 2025-07-02 03:28:17.986227)",
    ).tag(config=True)

    aliases = {
        ("b", "base-dir"): "CalibrationDB.data_tree_root",
        ("db-url"): "CalibrationDB.db_url",
        ("db-name"): "CalibrationDB.db_name",
        ("d", "datetime"): "FindEnabledCalibrationFiles.datetime",
        ("t", "calibration_type"): "FindEnabledCalibrationFiles.calibration_type",
    }

    classes = [CalibrationDB]

    def setup(self):
        """Set up tool."""
        if self.calibration_type is None:
            self.calibration_types = CalibrationType
        else:
            self.calibration_types = [self.calibration_type]

        if not is_datetime(self.datetime):
            raise ValueError(f"Date {self.datetime} not in isoformat %Y-%m-%d %H:%M.%f")

    def start(self):
        """Search in db active files for datetime."""
        with CalibrationDB(parent=self) as db:
            print(f"\n-*-*- Search in database for datetime {self.datetime} -*-*-")

            for calib_type in self.calibration_types:
                print(f"\n--> {calib_type.name} calibration type:")
                doc = db.find_used_document_in_date(
                    calib_type, datetime.fromisoformat(self.datetime)
                )
                if doc is not None:
                    for item in doc.items():
                        print(f"   {item}")


def main(args=None):
    """Run the `FindEnabledCalibrationFiles` tool."""
    tool = FindEnabledCalibrationFiles()
    tool.run(args)


if __name__ == "__main__":
    main()
