"""Tool aggregate the extracted drs4 timelapse data into histograms and mean/std per dt bin."""

import numpy as np
import tables
from ctapipe.core import Container, Field, Provenance, Tool
from ctapipe.core.traits import Bool, Float, Path, flag
from ctapipe.io import HDF5TableWriter
from ctapipe.io import metadata as meta
from ctapipe_io_lst.constants import N_CAPACITORS_PIXEL, N_GAINS, N_PIXELS
from scipy.stats import binned_statistic
from tqdm.auto import tqdm

from lstcam_calib.io.metadata import (
    get_ctapipe_metadata,
    get_local_metadata,
)
from lstcam_calib.statistics import OnlineStats

__all__ = [
    "TimelapsePixelHist",
    "DRS4TimelapseAggregator",
]


class TimelapsePixelHist(Container):
    """dt histogram, mean and std for one pixel."""

    default_prefix = ""

    channel = Field(-1, "Channel")
    pixel_id = Field(-1, "pixel_id")
    hist = Field(None, "baseline-subtracted value vs. dt histogram")
    mean = Field(None, "mean of values for each dt bin")
    std = Field(None, "std of values for each dt bin")


class DRS4TimelapseAggregator(Tool):
    """
    Tool to create dt histograms and compute mean/std per bin.

    This tool is the second tool used to perform dt curve fitting.
    It runs on the output of ``lstcam_calib_extract_drs4_dt_data``
    and provides the input for ``lstcam_calib_create_drs4_dt_file``.
    """

    name = "lstcam_calib_aggregate_drs4_dt_data"

    input_path = Path(directory_ok=False).tag(config=True)
    output_path = Path(directory_ok=False).tag(config=True)
    progress = Bool(None, allow_none=True).tag(config=True)

    min_dt_baseline = Float(
        default_value=80,
        help="minimum dt to include values in baseline computation",
    ).tag(config=True)

    aliases = {
        ("i", "input-file"): "DRS4TimelapseAggregator.input_path",
        ("o", "output-file"): "DRS4TimelapseAggregator.output_path",
        "min-dt-baseline": "DRS4TimelapseAggregator.min_dt_baseline",
    }

    flags = {
        **flag(
            "progress",
            "DRS4TimelapseAggregator.progress",
            "show a progress bar during event processing",
            "don't show a progress bar during event processing",
        ),
    }

    def setup(self):  # noqa: D102
        self.h5file = self.enter_context(tables.open_file(self.input_path))
        Provenance().add_input_file(self.input_path, "drs4 data")

        self.writer = self.enter_context(HDF5TableWriter(self.output_path))
        Provenance().add_output_file(self.output_path, "r0/service/timelapse_data")

        self.tel_id = self.h5file.root._v_attrs["TEL_ID"]

        # 15 bins per decade
        low = 0.01
        high = 1000
        self.n_bins_dt = 15 * int(np.log10(high) - np.log10(low))
        self.bins_dt = np.geomspace(low, high, self.n_bins_dt + 1)
        self.centers = 0.5 * (self.bins_dt[:-1] + self.bins_dt[1:])
        self.bin_10ms = np.nonzero(self.centers > 10)[0][0]

        self.bins_values = np.arange(-30, 92) - 0.5
        self.n_bins_values = len(self.bins_values) - 1

    def start(self):
        """Compute histogram, mean, std of data for each pixel."""
        # it would be fastest to just load all data at once into RAM
        # to minimize RAM usage, we are reading chunks of pixels
        # 1855 = 53 * 7 * 5, so the natural chunk choices are kind of limited
        # 265 happens to be the number of modules, but we do nothing particular
        # to modules.
        chunk_size = 265
        n_chunks = int(np.ceil(N_PIXELS / chunk_size))

        disable = None if self.progress is None else not self.progress
        with tqdm(total=N_GAINS * N_PIXELS, disable=disable) as bar:
            for channel in range(N_GAINS):
                for chunk in range(n_chunks):
                    self.log.info("Reading next chunk of %d pixels", chunk_size)
                    start = chunk * chunk_size
                    stop = start + chunk_size

                    capacitors = self.h5file.root.capacitors[:, channel, start:stop, :]
                    values = self.h5file.root.values[:, channel, start:stop, :]
                    delta_t = self.h5file.root.delta_t[:, channel, start:stop, :]

                    self.log.info("done")

                    for i in range(chunk_size):
                        pixel = start + i

                        try:
                            self._process_pixel(
                                channel,
                                pixel,
                                capacitors[:, i],
                                values[:, i],
                                delta_t[:, i],
                            )
                        except Exception:
                            self.log.exception(
                                "Error processing channel %d, pixel_id %d",
                                channel,
                                pixel,
                            )
                        bar.update(1)

    def _process_pixel(self, channel, pixel, capacitors, values, delta_t):
        # remove first three and last sample and flatten
        capacitors = capacitors[:, 3:-1].ravel()
        delta_t = delta_t[:, 3:-1].ravel()
        values = values[:, 3:-1].ravel()

        # subtract baseline of each cap
        mask = delta_t > self.min_dt_baseline

        stats = OnlineStats(N_CAPACITORS_PIXEL)
        stats.add_values_at_indices(capacitors[mask], values[mask])

        n_low_stats = np.count_nonzero(stats.counts < 10)
        if n_low_stats > 0:
            self.log.warning(
                "%d capacitors of channel %d, pixel %d have less then 10 entries for computing baseline",
                n_low_stats,
                channel,
                pixel,
            )
        baseline = stats.mean.astype(np.float32)
        values = values.astype(np.float32) - baseline[capacitors]

        # the capacitors at (positions % 32) == 0 show spikes which disturb the fitting.
        # we ignore them here
        valid = np.isfinite(delta_t) & np.isfinite(values) & ((capacitors % 32) != 0)
        kwargs = dict(x=delta_t[valid], values=values[valid], bins=self.bins_dt)
        mean = binned_statistic(**kwargs, statistic="mean").statistic
        std = binned_statistic(**kwargs, statistic="std").statistic

        # store individual output
        hist, _, _ = np.histogram2d(
            delta_t[valid],
            values[valid],
            bins=(self.bins_dt, self.bins_values),
        )
        container = TimelapsePixelHist(
            channel=channel,
            pixel_id=pixel,
            hist=hist,
            mean=mean,
            std=std,
            meta={
                "dt_min": self.bins_dt[0],
                "dt_max": self.bins_dt[-1],
                "dt_n_bins": self.n_bins_dt,
                "values_min": self.bins_values[0],
                "values_max": self.bins_values[-1],
                "values_n_bins": self.n_bins_values,
            },
        )
        self.writer.write(
            f"r0/service/timelapse_data/tel_{self.tel_id:03d}",
            container,
        )

    def finish(self):
        """Store metadata."""
        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("DRS4 aggregate dt data")
        local_metadata = get_local_metadata(
            self.tel_id,
            str(self.provenance_log.resolve()),
            self.h5file.root._v_attrs.RUN_START,
        )

        # add metadata
        meta.write_to_hdf5(ctapipe_metadata.to_dict(), self.writer.h5file)
        meta.write_to_hdf5(local_metadata.as_dict(), self.writer.h5file)


def main():
    """Start tool."""
    DRS4TimelapseAggregator().run()


if __name__ == "__main__":
    main()
