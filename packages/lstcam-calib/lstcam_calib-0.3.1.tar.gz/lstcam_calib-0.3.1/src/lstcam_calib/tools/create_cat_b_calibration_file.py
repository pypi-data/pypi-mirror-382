"""
Tool to compute Cat-B camera calibration coefficients (dc_to_pe and pedestals).

The estimation is performed with the F-factor method and
based on interleaved flat-field and pedestal events.

The estimated coefficients are relative to the Cat-A calibration (i.e. in the
case of identical conditions : dc_to_pe = 1 and pedestals = 0)

.. code:: python

   lstcam_calib_create_cat_b_calibration_file --help

"""
from copy import deepcopy
from pathlib import Path

import numpy as np
from ctapipe.containers import EventType
from ctapipe.core import Provenance, Tool, traits
from ctapipe.instrument.subarray import SubarrayDescription
from ctapipe.io import EventSource, HDF5TableWriter
from ctapipe.io import metadata as meta
from tqdm.auto import tqdm
from traitlets import Bool, Integer, Unicode

from lstcam_calib.io import PROV_OUTPUT_ROLES
from lstcam_calib.io.calibration import read_calibration_file
from lstcam_calib.io.metadata import (
    get_ctapipe_metadata,
    get_local_metadata,
)
from lstcam_calib.pixel.calibration_calculator import CalibrationCalculator

__all__ = ["CatBCalibrationHDF5Writer"]


class CatBCalibrationHDF5Writer(Tool):
    """Tool that generates a HDF5 file with Cat-B camera calibration coefficients."""

    name = "CatBCalibrationHDF5Writer"
    description = "Generate a HDF5 file with camera calibration coefficients"

    one_event = Bool(False, help="Stop after first calibration event").tag(config=True)

    output_file = traits.Path("calibration.hdf5", help="Name of the output file").tag(
        config=True
    )

    input_path = Unicode(".", help="Path of input file").tag(config=True)

    input_file_pattern = Unicode(
        "interleaved_LST-1.Run*.*.h5",
        help="Pattern for searching the input files with interleaved events to be processed",
    ).tag(config=True)

    n_subruns = Integer(1000000, help="Number of subruns to be processed").tag(
        config=True
    )

    cat_a_calibration_file = traits.Path(
        "catA_calibration.hdf5", help="Name of category A calibration file"
    ).tag(config=True)

    calibration_product = traits.create_class_enum_trait(
        CalibrationCalculator, default_value="LSTCalibrationCalculator"
    )

    aliases = {
        ("i", "input-file"): "EventSource.input_url",
        ("m", "max-events"): "EventSource.max_events",
        ("o", "output-file"): "CatBCalibrationHDF5Writer.output_file",
        (
            "k",
            "cat-a-calibration-file",
        ): "CatBCalibrationHDF5Writer.cat_a_calibration_file",
        (
            "s",
            "systematics-file",
        ): "LSTCalibrationCalculator.systematic_correction_file",
        ("input-file-pattern"): "CatBCalibrationHDF5Writer.input_file_pattern",
        ("input-path"): "CatBCalibrationHDF5Writer.input_path",
        ("n-subruns"): "CatBCalibrationHDF5Writer.n_subruns",
    }

    flags = {
        **traits.flag(
            "flatfield-heuristic",
            "LSTEventSource.use_flatfield_heuristic",
            "Use flatfield heuristic",
            "Do not use flatfield heuristic",
        )
    }

    classes = (
        [EventSource, CalibrationCalculator]
        + traits.classes_with_traits(CalibrationCalculator)
        + traits.classes_with_traits(EventSource)
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.run_start = None
        self.processor = None
        self.writer = None
        self.n_calib = 0

    def setup(self):
        """Initialize the tool components."""
        self.input_paths = sorted(
            Path(f"{self.input_path}").rglob(f"{self.input_file_pattern}")
        )

        tot_subruns = len(self.input_paths)
        if tot_subruns == 0:
            self.log.critical(
                "No interleaved files found to be processed in %s" "with pattern %s",
                self.input_path,
                self.input_file_pattern,
            )
            self.exit(1)

        if self.n_subruns > tot_subruns:
            self.n_subruns = tot_subruns

        # keep only the requested subruns
        self.input_paths = self.input_paths[: self.n_subruns]

        self.log.info("Process %d subruns ", self.n_subruns)

        self.subarray = SubarrayDescription.from_hdf(self.input_paths[0])

        self.processor = CalibrationCalculator.from_name(
            self.calibration_product, parent=self, subarray=self.subarray
        )

        tel_id = self.processor.tel_id
        group_name = "tel_" + str(tel_id)

        self.log.info("Open output file %s ", self.output_file)

        self.writer = HDF5TableWriter(
            filename=self.output_file, group_name=group_name, overwrite=True
        )

        # initialize the monitoring data
        self.cat_a_monitoring_data = read_calibration_file(self.cat_a_calibration_file)

    def start(self):
        """Calibration coefficient calculator."""
        tel_id = self.processor.tel_id
        new_ped = False
        new_ff = False
        count_ped = 0
        count_ff = 0

        stop = False
        self.log.debug("Start loop")

        # initialize the monitoring data with the cat-A calibration
        monitoring_data = deepcopy(self.cat_a_monitoring_data)

        for path in self.input_paths:
            self.log.debug("read %s", path)

            with EventSource(path, parent=self) as eventsource:
                for count, event in enumerate(tqdm(eventsource)):
                    # initialize info for metadata
                    if self.run_start is None:
                        run_start = deepcopy(event.trigger.tel[tel_id].time)
                        run_start.format = "iso"
                        self.run_start = run_start

                    # initialize the event monitoring data for event (to be improved)
                    event.mon.tel[tel_id] = monitoring_data

                    # save the config, to be retrieved as data.meta['config']
                    if count == 0:
                        ped_data = event.mon.tel[tel_id].pedestal
                        ff_data = event.mon.tel[tel_id].flatfield
                        status_data = event.mon.tel[tel_id].pixel_status
                        calib_data = event.mon.tel[tel_id].calibration

                    # if pedestal event
                    if self._is_pedestal(event, tel_id):
                        if self.processor.pedestal.calculate_pedestals(event):
                            new_ped = True
                            count_ped = count + 1

                    # if flat-field event
                    elif self._is_flatfield(event, tel_id):
                        if self.processor.flatfield.calculate_relative_gain(event):
                            new_ff = True
                            count_ff = count + 1

                    # write flatfield results when enough statistics (also for pedestals)
                    if new_ff and new_ped:
                        self.log.info(
                            "Write calibration at event n. %d, event id %d",
                            count + 1,
                            event.index.event_id,
                        )

                        self.log.info(
                            "Ready flatfield data at event n. %d stat = % d events",
                            count_ff,
                            ff_data.n_events,
                        )

                        # write on file
                        self.writer.write("flatfield", ff_data)

                        self.log.info(
                            "Ready pedestal data at event n. %d stat = %d events",
                            count_ped,
                            ped_data.n_events,
                        )

                        # write only pedestal data used for calibration
                        self.writer.write("pedestal", ped_data)

                        new_ff = False
                        new_ped = False

                        # Then, calculate calibration coefficients
                        self.processor.calculate_calibration_coefficients(event)

                        # Set the time correction relative to the Cat-A calibration so to avoid to decalibrate (as for dc_to_pe)
                        calib_data.time_correction -= (
                            self.cat_a_monitoring_data.calibration.time_correction
                        )

                        # write calib and pixel status
                        self.log.info("Write pixel_status data")
                        self.writer.write("pixel_status", status_data)

                        self.log.info("Write calibration data")
                        self.writer.write("calibration", calib_data)
                        self.n_calib += 1

                        if self.one_event:
                            stop = True

                    if stop:
                        break

                    # store the monitoring data for the next event
                    monitoring_data = event.mon.tel[tel_id]

            if stop:
                break

    def finish(self):
        """Do final actions."""
        self.log.info("Written %d calibration events", self.n_calib)
        if self.n_calib == 0:
            self.log.critical("!!! No calibration events in the output file !!! : ")
            self.log.critical(
                "flatfield collected statistics = %d events",
                self.processor.flatfield.num_events_seen,
            )
            self.log.critical(
                "pedestal collected statistics = %d events",
                self.processor.pedestal.num_events_seen,
            )
            self.exit(1)

        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("Cat-B pixel calibration coefficients")
        local_metadata = get_local_metadata(
            self.processor.tel_id,
            str(self.provenance_log.resolve()),
            self.run_start.value,
        )
        # add metadata
        meta.write_to_hdf5(ctapipe_metadata.to_dict(), self.writer.h5file)
        meta.write_to_hdf5(local_metadata.as_dict(), self.writer.h5file)

        Provenance().add_output_file(
            self.output_file, role=PROV_OUTPUT_ROLES["create_cat_b_calibration_file"]
        )

        self.writer.close()

    @staticmethod
    def _median_waveform_sum(event, tel_id):
        return np.median(np.sum(event.r1.tel[tel_id].waveform[0], axis=1))

    def _is_pedestal(self, event, tel_id=1):
        return event.trigger.event_type == EventType.SKY_PEDESTAL

    def _is_flatfield(self, event, tel_id):
        return event.trigger.event_type == EventType.FLATFIELD


def main():
    exe = CatBCalibrationHDF5Writer()

    exe.run()


if __name__ == "__main__":
    main()
