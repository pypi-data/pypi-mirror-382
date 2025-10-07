"""
Tool to compute DRS4 time corrections on the base arrival time of flat-field events.

.. code:: python

    lstcam_calib_create_drs4_time_file --help

"""
import numpy as np
import tables
from astropy.io import fits
from ctapipe.core import Provenance, Tool, ToolConfigurationError, traits
from ctapipe.io import EventSource
from ctapipe.io import metadata as meta
from tqdm import tqdm

from lstcam_calib.drs4.time_correction_calculator import TimeCorrectionCalculator
from lstcam_calib.io import OUTPUT_FORMATS, PROV_OUTPUT_ROLES
from lstcam_calib.io.metadata import (
    add_metadata_to_hdu,
    get_ctapipe_metadata,
    get_local_metadata,
)

__all__ = ["DRS4TimeCorrection"]


class DRS4TimeCorrection(Tool):
    """Compute DRS4 time corrections."""

    name = "create_drs4_time_file"

    output_file = traits.Path(
        directory_ok=False,
        help="Path for the output hdf5 file of time corrections",
    ).tag(config=True)

    progress_bar = traits.Bool(
        help="Show progress bar during processing",
        default_value=True,
    ).tag(config=True)

    overwrite = traits.Bool(
        help=(
            "If true, overwrite output without asking,"
            " else fail if output file already exists"
        ),
        default_value=False,
    ).tag(config=True)

    aliases = {
        ("i", "input-file"): "EventSource.input_url",
        ("m", "max-events"): "EventSource.max_events",
        ("o", "output-file"): "DRS4TimeCorrection.output_file",
        ("p", "pedestal-file"): "LSTEventSource.LSTR0Corrections.drs4_pedestal_path",
        (
            "r",
            "run-summary-file",
        ): "LSTEventSource.EventTimeCalculator.run_summary_path",
    }

    flags = {
        **traits.flag(
            "overwrite",
            "DRS4TimeCorrection.overwrite",
            "Overwrite output file if it exists",
            "Fail if output file already exists",
        ),
        **traits.flag(
            "progress",
            "DRS4TimeCorrection.progress_bar",
            "Show a progress bar during event processing",
            "Do not show a progress bar during event processing",
        ),
        **traits.flag(
            "flatfield-heuristic",
            "LSTEventSource.use_flatfield_heuristic",
            "Use flatfield heuristic",
            "Do not use flatfield heuristic",
        ),
    }

    classes = (
        [EventSource, TimeCorrectionCalculator]
        + traits.classes_with_traits(TimeCorrectionCalculator)
        + traits.classes_with_traits(EventSource)
    )

    def setup(self):
        """Perform initial setup."""
        # check output format
        if not np.array(
            [self.output_file.name.endswith(end) for end in OUTPUT_FORMATS]
        ).any():
            raise ValueError(
                f"Suffix of output file '{self.output_file.name}' not valid, it must be one of {OUTPUT_FORMATS} ",
            )

        self.output_file = self.output_file.expanduser().resolve()
        if self.output_file.exists():
            if self.overwrite:
                self.log.warning("Overwriting %s", self.output_file)
                self.output_file.unlink()
            else:
                raise ToolConfigurationError(
                    f"Output file ({self.output_file}) exists, use the `overwrite` option or choose another `output_file` "
                )

        self.log.debug("output path: %s", self.output_file)

        self.source = EventSource(parent=self, pointing_information=False)

        self.processor = TimeCorrectionCalculator(
            parent=self, subarray=self.source.subarray
        )

    def start(self):
        """Run main event loop."""
        for event in tqdm(self.source, disable=not self.progress_bar):
            self.processor.calibrate_peak_time(event)

    def finish(self):
        """write-out calibration coefficients."""
        self.processor.finalize()

        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("DRS4 sampling time coefficients")
        local_metadata = get_local_metadata(
            self.processor.tel_id,
            str(self.provenance_log.resolve()),
            self.source.run_start.iso,
        )

        # write in hdf5 format
        if self.output_file.name.endswith(".h5"):
            with tables.open_file(
                self.output_file, mode="w", title="DRS4 time correction file"
            ) as hf:
                hf.create_array("/", "fan", self.processor.fan_array)
                hf.create_array("/", "fbn", self.processor.fbn_array)
                hf.root._v_attrs["n_events"] = self.processor.n_events_processed
                hf.root._v_attrs["n_harm"] = self.processor.n_harmonics

                # add metadata
                meta.write_to_hdf5(ctapipe_metadata.to_dict(), hf)
                meta.write_to_hdf5(local_metadata.as_dict(), hf)

        # write in fits or fits.gz format
        elif self.output_file.name.endswith(".fits") or self.output_file.name.endswith(
            ".fits.gz"
        ):
            primary_hdu = fits.PrimaryHDU()
            add_metadata_to_hdu(ctapipe_metadata.to_dict(fits=True), primary_hdu)
            add_metadata_to_hdu(local_metadata.as_dict(), primary_hdu)

            fan_hdu = fits.ImageHDU(data=self.processor.fan_array, name="fan")

            fan_hdu.header["n_events"] = self.processor.n_events_processed
            fan_hdu.header["n_harm"] = self.processor.n_harmonics

            fbn_hdu = fits.ImageHDU(data=self.processor.fbn_array, name="fbn")
            fbn_hdu.header["n_events"] = self.processor.n_events_processed
            fbn_hdu.header["n_harm"] = self.processor.n_harmonics

            hdul = fits.HDUList(
                [
                    primary_hdu,
                    fan_hdu,
                    fbn_hdu,
                ]
            )
            hdul.writeto(self.output_file)

        Provenance().add_output_file(
            str(self.output_file), role=PROV_OUTPUT_ROLES["create_drs4_pedestal_file"]
        )


def main():
    """Run the `DRS4TimeCorrection` tool."""
    tool = DRS4TimeCorrection()
    tool.run()


if __name__ == "__main__":
    main()
