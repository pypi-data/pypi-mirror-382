"""
Tool to compute Cat-A camera calibration coefficients (dc_to_pe and pedestals).

The estimation is performed with the F-factor method and based on flat-field and pedestal events.

.. code:: python

   lstcam_calib_create_calibration_file --help

"""
import copy

import numpy as np
from astropy.io import fits
from astropy.table import Table
from ctapipe.containers import (
    EventType,
    MonitoringCameraContainer,
    PixelStatusContainer,
)
from ctapipe.core import Provenance, Tool, ToolConfigurationError, traits
from ctapipe.io import EventSource, HDF5TableWriter
from ctapipe.io import metadata as meta
from ctapipe_io_lst import LSTEventSource
from tqdm.auto import tqdm
from traitlets import Bool, Float, Int

from lstcam_calib.io import OUTPUT_FORMATS, PROV_OUTPUT_ROLES
from lstcam_calib.io.calibration import CALIB_CONTAINERS
from lstcam_calib.io.metadata import (
    add_metadata_to_hdu,
    get_ctapipe_metadata,
    get_local_metadata,
)
from lstcam_calib.pixel.calibration_calculator import CalibrationCalculator

__all__ = ["CalibrationWriter"]


class CalibrationWriter(Tool):
    """Tool that generates a (h5 or fits) file with LST Cat-A camera calibration coefficients."""

    name = "CalibrationWriter"
    description = "Generate file with LST Cat-A camera calibration coefficients"

    one_event = Bool(False, help="Stop after first calibration event").tag(config=True)

    output_file = traits.Path(
        "calibration.h5",
        directory_ok=False,
        help="Name of the output file (allowed format: fits, fits.gz or h5)",
    ).tag(config=True)

    calibration_product = traits.create_class_enum_trait(
        CalibrationCalculator, default_value="LSTCalibrationCalculator"
    )

    events_to_skip = Int(
        1000, help="Number of first events to skip due to bad DRS4 pedestal correction"
    ).tag(config=True)

    mc_min_flatfield_adc = Float(
        2000,
        help="Minimum high-gain camera median charge per pixel (ADC) for flatfield MC events",
    ).tag(config=True)

    mc_max_pedestal_adc = Float(
        300,
        help="Maximum high-gain camera median charge per pixel (ADC) for pedestal MC events",
    ).tag(config=True)

    aliases = {
        ("i", "input-file"): "EventSource.input_url",
        ("m", "max-events"): "EventSource.max_events",
        ("o", "output-file"): "CalibrationWriter.output_file",
        ("p", "pedestal-file"): "LSTEventSource.LSTR0Corrections.drs4_pedestal_path",
        (
            "s",
            "systematics-file",
        ): "LSTCalibrationCalculator.systematic_correction_file",
        (
            "r",
            "run-summary-file",
        ): "LSTEventSource.EventTimeCalculator.run_summary_path",
        (
            "t",
            "time-calibration-file",
        ): "LSTEventSource.LSTR0Corrections.drs4_time_calibration_path",
        "events-to-skip": "CalibrationWriter.events_to_skip",
        "mc-min-flatfield-adc": "CalibrationWriter.mc_min_flatfield_adc",
        "mc-max-pedestal-adc": "CalibrationWriter.mc_max_pedestal_adc",
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

        self.eventsource = None
        self.processor = None
        self.writer = None
        self.simulation = False
        self.n_calib = 0
        self.mon_camera_container = None

        self.containers = {}
        for key in CALIB_CONTAINERS.keys():
            self.containers[key] = []

    def setup(self):
        """Initialize the tool components."""
        self.log.info("Opening file")

        # check output format
        if not any(self.output_file.name.endswith(end) for end in OUTPUT_FORMATS):
            raise ToolConfigurationError(
                f"Suffix of output file '{self.output_file.name}' not valid, it must be one of {OUTPUT_FORMATS} ",
            )
        self.eventsource = self.enter_context(EventSource(parent=self))

        self.processor = CalibrationCalculator.from_name(
            self.calibration_product, parent=self, subarray=self.eventsource.subarray
        )

        tel_id = self.processor.tel_id

        # if real data
        if isinstance(self.eventsource, LSTEventSource):
            if tel_id != self.eventsource.lst_service.telescope_id:
                raise ValueError(
                    f"Events telescope_id {self.eventsource.lst_service.telescope_id} "
                    f"different than CalibrationCalculator telescope_id {tel_id}"
                )
        else:
            self.simulation = True

        # setup monitoring camera container
        self.mon_camera_container = MonitoringCameraContainer()

    def start(self):
        """Calibration coefficient calculator."""
        tel_id = self.processor.tel_id
        new_ped = False
        new_ff = False
        count_ff = 0
        count_ped = 0

        self.log.debug("Start loop")
        self.log.debug("If not simulation, skip first %d events", self.events_to_skip)
        for count, event in enumerate(tqdm(self.eventsource, disable=None)):
            # if simulation use not calibrated and not gain selected R0 waveform
            if self.simulation:
                # estimate offset of each channel from the camera median pedestal value
                offset = np.median(
                    event.mon.tel[tel_id].calibration.pedestal_per_sample, axis=1
                ).round()
                event.r1.tel[tel_id].waveform = (
                    event.r0.tel[tel_id].waveform.astype(np.float32)
                    - offset[:, np.newaxis, np.newaxis]
                )

            if self.simulation:
                # initialize pixel status container
                if count == 0:
                    initialize_pixel_status(
                        self.mon_camera_container, event.r1.tel[tel_id].waveform.shape
                    )
                # set the event monitoring container
                event.mon.tel[tel_id] = self.mon_camera_container

            # skip first events which are badly drs4 corrected
            if not self.simulation and count < self.events_to_skip:
                continue

            # if pedestal event
            # (use a cut on the charge for MC events if trigger not defined)
            if self._is_pedestal(event, tel_id):
                if self.processor.pedestal.calculate_pedestals(event):
                    new_ped = True
                    count_ped = count + 1
                    self.log.info(
                        "Ready pedestal data at event n. %d stat = %d events",
                        count_ped,
                        event.mon.tel[tel_id].pedestal.n_events,
                    )

            # if flat-field event
            # (use a cut on the charge for MC events if trigger not defined)
            elif self._is_flatfield(event, tel_id):
                if self.processor.flatfield.calculate_relative_gain(event):
                    new_ff = True
                    count_ff = count + 1
                    self.log.info(
                        "Ready flatfield data at event n. %d stat = %d events",
                        count_ff,
                        event.mon.tel[tel_id].flatfield.n_events,
                    )

            # save the present version of the event monitoring
            self.mon_camera_container = event.mon.tel[tel_id]

            # collect flatfield results when enough statistics (also for pedestals)
            if new_ff and new_ped:
                new_ff = False
                new_ped = False

                # calculate calibration coefficients
                self.processor.calculate_calibration_coefficients(event)

                self.log.info(
                    "Ready calibration at event n. %d, event id %d",
                    count + 1,
                    event.index.event_id,
                )

                # collect data in lists (only the one used for the calibration event)
                self.containers["flatfield"].append(
                    copy.deepcopy(event.mon.tel[tel_id].flatfield)
                )
                self.containers["pedestal"].append(
                    copy.deepcopy(event.mon.tel[tel_id].pedestal)
                )
                self.containers["pixel_status"].append(
                    copy.deepcopy(event.mon.tel[tel_id].pixel_status)
                )
                self.containers["calibration"].append(
                    copy.deepcopy(event.mon.tel[tel_id].calibration)
                )

                self.n_calib += 1

                if self.one_event:
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
        ctapipe_metadata = get_ctapipe_metadata("Cat-A pixel calibration coefficients")
        if self.simulation:
            run_start = ""
        else:
            run_start = self.eventsource.run_start.iso
        local_metadata = get_local_metadata(
            self.processor.tel_id,
            str(self.provenance_log.resolve()),
            run_start,
        )

        # write in hdf5 format
        if self.output_file.name.endswith(".h5"):
            with HDF5TableWriter(self.output_file) as writer:
                for key in self.containers:
                    for container in self.containers[key]:
                        writer.write(f"tel_{self.processor.tel_id}/{key}", container)

                # add metadata
                meta.write_to_hdf5(ctapipe_metadata.to_dict(), writer.h5file)
                meta.write_to_hdf5(local_metadata.as_dict(), writer.h5file)

        # write in fits or fits.gz format
        elif self.output_file.name.endswith(".fits") or self.output_file.name.endswith(
            ".fits.gz"
        ):
            primary_hdu = fits.PrimaryHDU()
            add_metadata_to_hdu(ctapipe_metadata.to_dict(fits=True), primary_hdu)
            add_metadata_to_hdu(local_metadata.as_dict(), primary_hdu)

            hdul = fits.HDUList(primary_hdu)
            for key in self.containers:
                t = Table([container.as_dict() for container in self.containers[key]])

                # Workaround for astropy#17930, attach missing units
                for col, value in self.containers[key][0].items():
                    if unit := getattr(value, "unit", None):
                        t[col].unit = unit

                hdul.append(fits.BinTableHDU(t, name=key))

            hdul.writeto(self.output_file)

        Provenance().add_output_file(
            self.output_file, role=PROV_OUTPUT_ROLES["create_calibration_file"]
        )

    @staticmethod
    def _median_waveform_sum(event, tel_id):
        return np.median(np.sum(event.r1.tel[tel_id].waveform[0], axis=1))

    def _is_pedestal(self, event, tel_id=1):
        return (event.trigger.event_type == EventType.SKY_PEDESTAL) or (
            self.simulation
            and self._median_waveform_sum(event, tel_id) < self.mc_max_pedestal_adc
        )

    def _is_flatfield(self, event, tel_id):
        return (event.trigger.event_type == EventType.FLATFIELD) or (
            self.simulation
            and self._median_waveform_sum(event, tel_id) > self.mc_min_flatfield_adc
        )


def initialize_pixel_status(mon_camera_container, shape):
    """Initialize the pixel status container in the case of simulation events."""
    # (this should be done in the event source, but added here for the moment)

    # initialize the container
    status_container = PixelStatusContainer()
    status_container.hardware_failing_pixels = np.zeros(
        (shape[0], shape[1]), dtype=bool
    )
    status_container.pedestal_failing_pixels = np.zeros(
        (shape[0], shape[1]), dtype=bool
    )
    status_container.flatfield_failing_pixels = np.zeros(
        (shape[0], shape[1]), dtype=bool
    )

    mon_camera_container.pixel_status = status_container


def main():
    exe = CalibrationWriter()

    exe.run()


if __name__ == "__main__":
    main()
