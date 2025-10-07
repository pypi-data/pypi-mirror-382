"""
Tool to change database documents associated to calibration files.

.. code:: python

   lstcam_change_db_document --help

"""
from enum import Enum

from ctapipe.core import Tool, traits

from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import query_yes_no

__all__ = ["ChangeDataBaseDocument", "ChangeType"]


class ChangeType(Enum):
    """Type of change allowed in the database documents."""

    #: validate a calibration file after data quality check
    validate = "validate"

    #: invalidate a calibration file after data quality check
    invalidate = "invalidate"

    #: enable usage of a calibration file
    enable = "enable"

    #: disable usage of a calibration file
    disable = "disable"

    #: remove from database the document of a calibration file
    remove = "remove"


class ChangeDataBaseDocument(Tool):
    """Tool to change a database document."""

    input_file = traits.Path(
        exists=True,
        directory_ok=False,
        help="Calibration file of the document",
    ).tag(config=True)

    calibration_type = traits.UseEnum(
        CalibrationType,
        help="Type of calibration",
    ).tag(config=True)

    change_type = traits.UseEnum(
        ChangeType,
        help="Type of change to be performed",
    ).tag(config=True)

    yes = traits.Bool(
        default_value=False,
        help="If True, do not ask for confirmation.",
    ).tag(config=True)

    aliases = {
        ("i", "input"): "ChangeDataBaseDocument.input_file",
        ("t", "type"): "ChangeDataBaseDocument.calibration_type",
        ("b", "base-dir"): "CalibrationDB.data_tree_root",
        ("change"): "ChangeDataBaseDocument.change_type",
        ("db-url"): "CalibrationDB.db_url",
        ("db-name"): "CalibrationDB.db_name",
        ("tel-id"): "CalibrationDB.tel_id",
    }

    classes = [CalibrationDB]

    flags = {
        ("y", "yes"): (
            {"ChangeDataBaseDocument": {"yes": True}},
            "Do not ask for confirmation",
        ),
    }

    def start(self):
        """Validate a calibration file in the database."""
        with CalibrationDB(parent=self) as db:
            # search the corresponding document:
            doc = db.find_document_by_file(self.calibration_type, self.input_file)

            self.log.info("Document found:")
            for key, val in doc.items():
                self.log.info("%s %s", key, val)

            if self.yes or query_yes_no(f"Do you want to {self.change_type.value} it?"):
                if self.change_type == ChangeType.validate:
                    db.validate_file_quality(
                        self.calibration_type,
                        self.input_file,
                    )
                elif self.change_type == ChangeType.invalidate:
                    db.invalidate_file_quality(
                        self.calibration_type,
                        self.input_file,
                    )
                elif self.change_type == ChangeType.enable:
                    db.enable_file_usage(
                        self.calibration_type,
                        self.input_file,
                    )
                elif self.change_type == ChangeType.disable:
                    db.disable_file_usage(
                        self.calibration_type,
                        self.input_file,
                    )
                elif self.change_type == ChangeType.remove:
                    db.remove_file(
                        self.calibration_type,
                        self.input_file,
                    )
            else:
                self.log.warning("Not changing document")


def main(args=None):
    """Run the `ChangeDataBaseDocument` tool."""
    tool = ChangeDataBaseDocument()
    tool.run(args)


if __name__ == "__main__":
    main()
