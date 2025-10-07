"""Tool to extract drs4 dt data for further processing."""
import numba
import numpy as np
import tables
from ctapipe.core import Tool
from ctapipe.core.traits import Integer, Path
from ctapipe.io import metadata as meta
from ctapipe.io.hdf5tableio import DEFAULT_FILTERS
from ctapipe_io_lst import LSTEventSource
from ctapipe_io_lst.calibration import (
    get_first_capacitors_for_pixels,
    get_spike_A_positions,
    update_last_readout_times,
)
from ctapipe_io_lst.constants import (
    CLOCK_FREQUENCY_KHZ,
    N_CAPACITORS_PIXEL,
    N_GAINS,
    N_PIXELS,
    N_PIXELS_MODULE,
    N_SAMPLES,
)
from tqdm import tqdm

from lstcam_calib.io.metadata import (
    get_ctapipe_metadata,
    get_local_metadata,
)

__all__ = [
    "DRS4Timelapse",
]


@numba.njit(cache=True)
def get_timelapse_data(
    first_capacitors,
    previous_first_capacitors,
    last_readout_time,
    local_clock_counter,
    pixel_id_map,
):
    """Fill stats object with current event data."""
    delta_t = np.full((N_GAINS, N_PIXELS, N_SAMPLES), np.nan, dtype=np.float32)
    capacitors = np.zeros((N_GAINS, N_PIXELS, N_SAMPLES), dtype=np.uint16)

    n_modules = len(pixel_id_map) // N_PIXELS_MODULE
    for gain in range(N_GAINS):
        for module in range(n_modules):
            time_now = local_clock_counter[module]

            for pixel_in_module in range(N_PIXELS_MODULE):
                pixel_index = module * N_PIXELS_MODULE + pixel_in_module
                pixel = pixel_id_map[pixel_index]

                fc = first_capacitors[gain, pixel]
                last_fc = previous_first_capacitors[gain, pixel]
                spike_positions = get_spike_A_positions(fc, last_fc)

                for sample in range(N_SAMPLES):
                    cap = (fc + sample) % N_CAPACITORS_PIXEL
                    capacitors[gain, pixel, sample] = cap

                    last_read = last_readout_time[gain, pixel, cap]

                    # ignore samples where we don't have a last readout time yet
                    if last_read == 0:
                        continue

                    # ignore spikes
                    if (
                        sample in spike_positions
                        or (sample - 1) in spike_positions
                        or (sample - 2) in spike_positions
                    ):
                        continue

                    delta_t[gain, pixel, sample] = (
                        time_now - last_read
                    ) / CLOCK_FREQUENCY_KHZ

    return delta_t, capacitors


class DRS4Timelapse(Tool):
    """
    Tool to write-out event-wise drs4 timelapse data.

    This tool essentially just converts the zfits event data
    to hdf5 in a way that allows loading all events but only
    for a specific pixel or chunks of pixels to reduce memory
    usage of the following step.

    This is the first tool to be run for performing computation of
    dt correction coefficients. The input must be a drs4 run
    without any corrections applied by EVB.

    The output of this tool is aggregated into histograms
    of the dt dependent charge by ``lstcam_calib_aggregate_drs4_dt_data``,
    which can then be fitted to produce coefficients by
    ``lstcam_calib_aggregate_drs4_dt_data``.
    """

    name = "lstcam_calib_extract_drs4_dt_data"

    output_path = Path(directory_ok=False).tag(config=True)
    skip_samples_front = Integer(default_value=10).tag(config=True)
    skip_samples_end = Integer(default_value=1).tag(config=True)

    aliases = {
        ("i", "input-file"): "LSTEventSource.input_url",
        ("o", "output-file"): "DRS4Timelapse.output_path",
        ("m", "max-events"): "LSTEventSource.max_events",
    }

    classes = [LSTEventSource]

    def setup(self):
        """Set up the tool."""
        self.source = LSTEventSource(
            parent=self,
            pointing_information=False,
            trigger_information=False,
            apply_drs4_corrections=False,
        )
        self.tel_id = self.source.tel_id

        shape = (N_GAINS, N_PIXELS, N_CAPACITORS_PIXEL)
        self.last_readout_time = np.zeros(shape, dtype=np.uint64)
        self.previous_first_capacitors = np.zeros((N_GAINS, N_PIXELS), dtype=int)

        self.h5file = self.enter_context(tables.open_file(self.output_path, "w"))
        self.h5file.root._v_attrs["obs_id"] = self.source.obs_ids[0]

        kwargs = dict(
            where="/",
            expectedrows=60000,
            shape=(0, N_GAINS, N_PIXELS, N_SAMPLES),
            chunkshape=None,  # (None, N_GAINS, N_PIXELS, N_SAMPLES),
            filters=DEFAULT_FILTERS,
            createparents=True,
        )

        self.capacitors = self.h5file.create_earray(
            name="capacitors",
            atom=tables.UInt16Atom(),
            **kwargs,
        )

        self.values = self.h5file.create_earray(
            name="values",
            atom=tables.Int16Atom(),
            **kwargs,
        )

        self.delta_t = self.h5file.create_earray(
            name="delta_t",
            atom=tables.Float32Atom(),
            **kwargs,
        )

    def start(self):
        """Run main event loop."""
        tel_id = self.tel_id
        pixel_id_map = self.source.pixel_id_map

        for event in tqdm(self.source):
            lst = event.lst.tel[tel_id]
            first_capacitors = get_first_capacitors_for_pixels(
                lst.evt.first_capacitor_id,
                lst.svc.pixel_ids,
            )

            delta_t, capacitors = get_timelapse_data(
                first_capacitors=first_capacitors,
                previous_first_capacitors=self.previous_first_capacitors,
                last_readout_time=self.last_readout_time,
                local_clock_counter=lst.evt.local_clock_counter,
                pixel_id_map=pixel_id_map,
            )

            if event.r1.tel[tel_id].waveform is not None:
                waveform = event.r1.tel[tel_id].waveform
            else:
                waveform = event.r0.tel[tel_id].waveform

            self._write(waveform, delta_t, capacitors)

            update_last_readout_times(
                lst.evt.local_clock_counter,
                first_capacitors,
                self.last_readout_time,
                pixel_id_map,
            )
            self.previous_first_capacitors = first_capacitors

    def finish(self):
        """Do final actions."""
        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("DRS4 extract time lapse data")
        local_metadata = get_local_metadata(
            self.source.tel_id,
            str(self.provenance_log.resolve()),
            self.source.run_start.iso,
        )
        # add metadata
        meta.write_to_hdf5(ctapipe_metadata.to_dict(), self.h5file)
        meta.write_to_hdf5(local_metadata.as_dict(), self.h5file)

    def _write(self, waveform, delta_t, capacitors):
        self.values.append(waveform[np.newaxis])
        self.delta_t.append(delta_t[np.newaxis])
        self.capacitors.append(capacitors[np.newaxis])


def main():
    """Run the timelapse data extraction tool."""
    tool = DRS4Timelapse()
    tool.run()


if __name__ == "__main__":
    main()
