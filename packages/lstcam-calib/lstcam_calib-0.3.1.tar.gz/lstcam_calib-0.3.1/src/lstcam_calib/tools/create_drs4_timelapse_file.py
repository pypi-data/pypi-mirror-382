"""Tool to create drs4 timelapse calibration coefficient files."""
import gc

import matplotlib.pyplot as plt
import numpy as np
import tables
from astropy.io import fits
from ctapipe.core import Container, Field, Provenance, Tool
from ctapipe.core.traits import Bool, Float, Path, flag
from ctapipe.io import HDF5TableWriter, read_table
from ctapipe.io import metadata as meta
from ctapipe_io_lst.constants import N_CHANNELS_MODULE, N_GAINS, N_MODULES, N_PIXELS
from iminuit import Minuit
from iminuit.cost import LeastSquares
from matplotlib.backends.backend_pdf import PdfPages
from numba import vectorize
from tqdm.auto import tqdm
from traitlets.traitlets import CaselessStrEnum

from lstcam_calib.io.metadata import (
    add_metadata_to_hdu,
    get_ctapipe_metadata,
    get_local_metadata,
)

N_DRS4_CHIPS = N_MODULES * N_CHANNELS_MODULE

__all__ = [
    "DRS4TimelapseFitter",
]


def _combine_stats(data_a, data_b):
    """Combine two sets of statistics into one."""
    # See https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm
    n_a = data_a["hist"].sum(axis=1)
    n_b = data_b["hist"].sum(axis=1)
    n = n_a + n_b

    mean_a = np.nan_to_num(data_a["mean"], nan=0.0)
    mean_b = np.nan_to_num(data_b["mean"], nan=0.0)

    delta = mean_b - mean_a
    update = np.full_like(mean_a, np.nan)
    np.divide(delta * n_b, n, where=n > 0, out=update)
    mean = mean_a + update

    m2_a = n_a * np.nan_to_num(data_a["std"], nan=0.0) ** 2
    m2_b = n_b * np.nan_to_num(data_b["std"], nan=0.0) ** 2

    update = np.full_like(mean_a, np.nan)
    np.divide(delta**2 * n_a * n_b, n, where=n > 0, out=update)
    m2 = m2_a + m2_b + update
    std = np.sqrt(m2 / n)

    return {
        "hist": data_a["hist"] + data_b["hist"],
        "mean": np.where(n == 0, np.nan, mean),
        "std": np.where(n < 2, np.nan, std),
    }


@vectorize(cache=True)
def delta_t_correction(x, scale, exponent, t0):
    """DRS4 dt correction function, version 2.

    This function forces f(t0) == 0.
    """
    # this formulation of the drs4 pedestal function forces f(t0) == 0
    if x > t0:
        return 0.0
    return scale * (x / t0) ** (-exponent) - scale


def fit_timelapse(centers, mean, std, t0, t0_fixed):
    """Perform fit of the dt function to the data of a single pixel."""
    valid = np.isfinite(mean) & (centers < 200)
    cost = LeastSquares(centers[valid], mean[valid], std[valid], delta_t_correction)

    scale = 18.0
    exponent = 0.20

    m = Minuit(cost, scale=scale, exponent=exponent, t0=t0)
    m.limits["scale"] = (1e-30, None)
    m.limits["exponent"] = (1e-30, None)

    if t0_fixed:
        m.fixed["t0"] = True
    else:
        m.limits["t0"] = (1, 150)

    m.migrad()
    if not m.valid:
        raise ValueError("Invalid fit")
    return m


class TimeLapseCoefficients(Container):
    """DRS4 Timelapse correction coefficients."""

    default_prefix = ""

    scale = Field(np.nan, "Scale coefficient for timelapse formula")
    exponent = Field(np.nan, "exponent coefficient for timelapse formula")
    t0 = Field(np.nan, "t0 coefficient")
    chi2 = Field(np.nan, "Least Squares value of fit")
    mean_10ms = Field(
        np.nan, "Mean value at dt=10ms, used to determine new vs. old chip"
    )
    pixel_batch = Field(
        None,
        "The batch to which each channel/pixel combination belongs. Only filled in case of batch-wise processing",
    )


class DRS4TimelapseFitter(Tool):
    """
    Tool to fit the dt curve coefficients.

    This tool is the third and final tool used to perform dt curve fitting.
    It runs on the output of ``lstcam_calib_create_drs4_dt_file`` from
    which it computes the dt curve fit parameters, either for each
    individual pixel or per batch (old or new) of drs4 chips.
    """

    name = "lstcam_calib_create_drs4_dt_file"

    input_path = Path(directory_ok=False).tag(config=True)
    output_path = Path(
        directory_ok=False,
        help="Output file of drs4 time lapse correction (fits or hdf5 automatically selected dipending on suffix)",
    ).tag(config=True)
    plot_output_path = Path(
        None,
        help="PDF file with plots of baseline vs dt and fit results",
        allow_none=True,
        directory_ok=False,
    ).tag(config=True)
    progress = Bool(None, allow_none=True).tag(config=True)

    mean_threshold_old = Float(
        4,
        help="DRS4 chips with a higher mean value than this at dt=10ms are classified as 'old' chips",
    ).tag(config=True)

    t0_new = Float(
        9.0,
        help="Fixed t0 value for new batch DRS4 chips.",
    ).tag(config=True)

    t0_old = Float(
        55.0,
        help="Fixed t0 value for old batch DRS4 chips.",
    ).tag(config=True)

    t0_fixed = Bool(
        default_value=True,
        help="Whether to hold the t0 parameter fixed in the fit.",
    ).tag(config=True)

    group_by = CaselessStrEnum(
        ["pixel", "batch"],
        default_value="batch",
        help=(
            "This options determines how the fits are performed."
            " If 'pixel', one fit is performed per pixel/channel combination. (1855 * 2)."
            # TBD    " If 'chip', one fit is performed per drs4 chip (2120)."
            " If 'batch', one fit is performed per batch of drs4 chips (1 or 2)."
            " This also influences the output data format."
        ),
    ).tag(config=True)

    aliases = {
        ("i", "input-file"): "DRS4TimelapseFitter.input_path",
        ("o", "output-file"): "DRS4TimelapseFitter.output_path",
        ("p", "plot-output"): "DRS4TimelapseFitter.plot_output_path",
        "group-by": "DRS4TimelapseFitter.group_by",
        "t0-new": "DRS4TimelapseFitter.t0_new",
        "t0-old": "DRS4TimelapseFitter.t0_old",
    }

    flags = {
        **flag(
            "progress",
            "DRS4TimelapseFitter.progress",
            "show a progress bar during event processing",
            "don't show a progress bar during event processing",
        ),
        **flag(
            "t0-fixed",
            "DRS4TimelapseFitter.t0_fixed",
            "Keep t0 fixed for the timelapse fit",
            "Have t0 as free parameter in the timelapse fit",
        ),
    }

    def setup(self):  # noqa: D102
        self.h5file = self.enter_context(tables.open_file(self.input_path))
        Provenance().add_input_file(self.input_path, "r0/service/timelapse_data")

        node = next(self.h5file.root.r0.service.timelapse_data._f_iter_nodes())
        self.tel_id = int(node.name.removeprefix("tel_"))
        self.table = read_table(self.h5file, node._v_pathname)

        meta = node._v_attrs
        self.n_bins_dt = meta["dt_n_bins"]
        self.bins_dt = np.geomspace(meta["dt_min"], meta["dt_max"], self.n_bins_dt + 1)
        self.dt_center = (self.bins_dt[:-1] * self.bins_dt[1:]) ** 0.5
        self.bin_10ms = np.nonzero(self.dt_center > 10)[0][0]

        self.n_bins_values = meta["values_n_bins"]
        self.bins_values = np.linspace(
            meta["values_min"], meta["values_max"], self.n_bins_values + 1
        )

        if self.group_by == "pixel":
            self.scale = np.full((N_GAINS, N_PIXELS), np.nan, dtype=np.float32)
            self.exponent = np.full((N_GAINS, N_PIXELS), np.nan, dtype=np.float32)
            self.t0 = np.full((N_GAINS, N_PIXELS), np.nan, dtype=np.float32)
            self.chi2 = np.full((N_GAINS, N_PIXELS), np.nan, dtype=np.float32)
            self.mean_10ms = np.full((N_GAINS, N_PIXELS), np.nan, dtype=np.float32)
        elif self.group_by == "chip":
            self.scale = np.full(N_DRS4_CHIPS, np.nan, dtype=np.float32)
            self.exponent = np.full(N_DRS4_CHIPS, np.nan, dtype=np.float32)
            self.t0 = np.full(N_DRS4_CHIPS, np.nan, dtype=np.float32)
            self.chi2 = np.full(N_DRS4_CHIPS, np.nan, dtype=np.float32)
            self.mean_10ms = np.full(N_DRS4_CHIPS, np.nan, dtype=np.float32)
        elif self.group_by == "batch":
            self.scale = np.full(2, np.nan, dtype=np.float32)
            self.exponent = np.full(2, np.nan, dtype=np.float32)
            self.t0 = np.full(2, np.nan, dtype=np.float32)
            self.chi2 = np.full(2, np.nan, dtype=np.float32)
            self.mean_10ms = np.full(2, np.nan, dtype=np.float32)

        self.pdf = None
        self.fig = None

        if self.plot_output_path is not None:
            self.pdf = self.enter_context(PdfPages(self.plot_output_path))

            self.dt_plot = np.geomspace(0.01, 800, 100)

            if self.group_by != "batch":
                figsize = 16, 9
                n_rows = 7
                n_cols = 5
            else:
                figsize = 6, 4
                n_rows = 1
                n_cols = 1

            self.fig, axs = plt.subplots(
                n_rows, n_cols, figsize=figsize, dpi=100, layout="constrained"
            )
            axs = np.array(axs, ndmin=2)
            self.axs = axs.ravel()
            self.current_plot = 0
            self.hists = []
            self.labels = []
            self.fit_plots = []
            self.t0_bars = []

            self.errorbars = []

            for ax in axs[-1, :]:
                ax.set(xlabel="dt / ms")

            for ax in axs[:, 0]:
                ax.set(ylabel="adc value")

            for ax in self.axs:
                hist = ax.pcolormesh(
                    self.bins_dt,
                    self.bins_values,
                    np.zeros((self.n_bins_values, self.n_bins_dt)),
                    cmap="inferno",
                    norm="log",
                )
                hist.set_rasterized(True)
                self.hists.append(hist)
                errorbar = ax.errorbar(
                    self.dt_center,
                    np.ones_like(self.dt_center),
                    yerr=np.ones_like(self.dt_center),
                    marker=".",
                    markersize=3,
                    ls="",
                    color="lightgray",
                )
                markers, _, (yerr,) = errorbar.lines
                segments = np.array(yerr.get_segments())
                self.errorbars.append((markers, yerr, segments))

                self.fit_plots.append(
                    ax.plot(
                        self.dt_plot,
                        np.zeros_like(self.dt_plot),
                        zorder=3,
                    )[0]
                )

                self.t0_bars.append(ax.axvline(100.0, color="black"))

                self.labels.append(
                    ax.text(
                        0.99, 0.99, "", ha="right", va="top", transform=ax.transAxes
                    )
                )
                ax.set(xscale="log")
                ax.grid()

    def start(self):
        """Fit data of each pixel."""
        disable_progress = None if self.progress is None else not self.progress

        # determine batches by looking at mean at 10ms
        self.table["new_batch"] = (
            self.table["mean"][:, self.bin_10ms] < self.mean_threshold_old
        )

        if self.group_by == "pixel":
            self._process_pixels(disable_progress)
        elif self.group_by == "chip":
            self._process_chips(disable_progress)
        elif self.group_by == "batch":
            self._process_batches(disable_progress)

    def _process_pixels(self, disable_progress):
        for row in tqdm(self.table, disable=disable_progress):
            try:
                self._process_pixel(row)
            except Exception:
                self.log.exception(
                    "Error processing channel %d, pixel_id %d",
                    row["channel"],
                    row["pixel_id"],
                )

            if self.pdf is not None:
                self.current_plot = (self.current_plot + 1) % len(self.axs)
                if self.current_plot == 0:
                    self.pdf.savefig(self.fig)
                    gc.collect()

    def _process_chips(self, disable_progress):
        raise NotImplementedError("Not yet implemented")

    def _process_batches(self, disable_progress):
        by_batch = self.table.group_by("new_batch")

        for key, table in zip(by_batch.groups.keys, by_batch.groups):
            batch = int(key["new_batch"])
            self.log.info(
                "processing batch: %d with %d pixel/channel combinations",
                batch,
                len(table),
            )
            # merge stats of all pixels in the same batch
            stats = table[0]
            for other in table[1:]:
                stats = _combine_stats(stats, other)

            self._process_batch(stats, batch=batch)

            if self.pdf is not None:
                self.pdf.savefig(self.fig)

    def _process_batch(self, data, batch):
        mean = data["mean"]
        std = data["std"]
        hist = data["hist"]

        # we have two kinds of drs4 chips, newer ones have a faster
        # dt falloff reaching a flat curve already at ~10 ms instead of ~55 ms
        t0 = self.t0_new if batch == 1 else self.t0_old

        m = fit_timelapse(self.dt_center, mean, std, t0=t0, t0_fixed=self.t0_fixed)
        self.log.info("Fit result of batch %d: %s", batch, m.values)

        self.scale[batch] = m.values["scale"]
        self.exponent[batch] = m.values["exponent"]
        self.t0[batch] = m.values["t0"]
        self.chi2[batch] = m.fval
        self.mean_10ms[batch] = mean[self.bin_10ms]

        if self.pdf is not None:
            self._plot_batch(batch, hist, mean, std)

    def _process_chip(self, data):
        pass

    def _process_pixel(self, data):
        channel = data["channel"]
        pixel = data["pixel_id"]

        mean = data["mean"]
        std = data["std"]
        hist = data["hist"]
        new_batch = data["new_batch"]

        # we have two kinds of drs4 chips, newer ones have a faster
        # dt falloff reaching a flat curve already at ~10 ms instead of ~55 ms
        t0 = self.t0_new if new_batch else self.t0_old

        m = fit_timelapse(self.dt_center, mean, std, t0=t0, t0_fixed=self.t0_fixed)
        self.log.info(
            "Fit result of channel %d, pixel %d: %s", channel, pixel, m.values
        )

        self.scale[channel, pixel] = m.values["scale"]
        self.exponent[channel, pixel] = m.values["exponent"]
        self.t0[channel, pixel] = m.values["t0"]
        self.chi2[channel, pixel] = m.fval
        self.mean_10ms[channel, pixel] = mean[self.bin_10ms]

        if self.pdf is not None:
            self._plot_pixel(channel, pixel, hist, mean, std)

    def _plot_pixel(self, channel, pixel, hist, mean, std):
        if self.pdf is None:
            raise ValueError("Plotting not setup")

        plot = self.hists[self.current_plot]
        label = self.labels[self.current_plot]
        label.set_text(f"chan.: {channel}, pix.: {pixel: 4d}")

        # axis order of pcolormesh and hist is inverted, need to transpose
        plot.set_array(hist.T)
        plot.autoscale()

        # update the mean/std errorbars, this is a bit complex due to how
        # matplotlib stores the lines / markers of an errorbar plot
        markers, yerr, segments = self.errorbars[self.current_plot]
        markers.set_ydata(mean)
        segments[:, 0, 1] = mean - std
        segments[:, 1, 1] = mean + std
        yerr.set_segments(segments)

        # plot fit result
        t0 = self.t0[channel, pixel]
        y = delta_t_correction(
            self.dt_plot,
            self.scale[channel, pixel],
            self.exponent[channel, pixel],
            t0,
        )
        self.fit_plots[self.current_plot].set_ydata(np.where(self.dt_plot < t0, y, 0))
        self.t0_bars[self.current_plot].set_xdata([t0])

    def _plot_batch(self, batch, hist, mean, std):
        if self.pdf is None:
            raise ValueError("Plotting not setup")

        ax = self.axs[0]
        ax.set_title(f"batch: {batch}")
        plot = self.hists[self.current_plot]

        # axis order of pcolormesh and hist is inverted, need to transpose
        plot.set_array(hist.T)
        plot.autoscale()

        # update the mean/std errorbars, this is a bit complex due to how
        # matplotlib stores the lines / markers of an errorbar plot
        markers, yerr, segments = self.errorbars[self.current_plot]
        markers.set_ydata(mean)
        segments[:, 0, 1] = mean - std
        segments[:, 1, 1] = mean + std
        yerr.set_segments(segments)

        # plot fit result
        t0 = self.t0[batch]
        y = delta_t_correction(
            self.dt_plot,
            self.scale[batch],
            self.exponent[batch],
            t0,
        )
        self.fit_plots[self.current_plot].set_ydata(np.where(self.dt_plot < t0, y, 0))
        self.t0_bars[self.current_plot].set_xdata([t0])

    def finish(self):
        """Store output."""
        pixel_batch = None

        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("DRS4 time lapse coefficients")
        local_metadata = get_local_metadata(
            self.tel_id,
            str(self.provenance_log.resolve()),
            self.h5file.root._v_attrs.RUN_START,
        )

        if self.group_by == "batch":
            pixel_batch = np.zeros((N_GAINS, N_PIXELS), dtype=np.int8)
            for row in self.table:
                pixel_batch[row["channel"], row["pixel_id"]] = int(row["new_batch"])

        # write h5 format
        if self.output_path.name.endswith(".h5"):
            container = TimeLapseCoefficients(
                scale=self.scale,
                exponent=self.exponent,
                t0=self.t0,
                chi2=self.chi2,
                mean_10ms=self.mean_10ms,
                pixel_batch=pixel_batch,
                meta={"group_by": self.group_by},
            )

            with HDF5TableWriter(self.output_path) as writer:
                writer.write(
                    f"r0/service/timelapse_coefficients/tel_{self.tel_id:03d}",
                    container,
                )
                # add metadata
                meta.write_to_hdf5(ctapipe_metadata.to_dict(), writer.h5file)
                meta.write_to_hdf5(local_metadata.as_dict(), writer.h5file)
                writer.h5file.root._v_attrs["GROUPING"] = "BATCH"

        # write in fits or fits.gz format
        elif self.output_path.name.endswith(".fits") or self.output_path.name.endswith(
            ".fits.gz"
        ):
            primary_hdu = fits.PrimaryHDU()

            add_metadata_to_hdu(ctapipe_metadata.to_dict(fits=True), primary_hdu)
            add_metadata_to_hdu(local_metadata.as_dict(), primary_hdu)
            primary_hdu.header["GROUPING"] = "BATCH"

            scale_hdu = fits.ImageHDU(data=self.scale, name="scale")
            exponent_hdu = fits.ImageHDU(data=self.exponent, name="exponent")
            t0_hdu = fits.ImageHDU(data=self.t0, name="t0")
            chi2 = fits.ImageHDU(data=self.chi2, name="chi2")
            mean_10ms = fits.ImageHDU(data=self.mean_10ms, name="mean_10ms")

            hdul_list = [primary_hdu, scale_hdu, exponent_hdu, t0_hdu, chi2, mean_10ms]

            if self.group_by == "batch":
                pixel_batch_hdu = fits.ImageHDU(data=pixel_batch, name="pixel_batch")
                hdul_list.append(pixel_batch_hdu)

            hdul = fits.HDUList(hdul_list)
            hdul.writeto(self.output_path)
        else:
            path = self.output_path
            msg = f"Unsupported output file format '{path.suffix}': '{path}'"
            raise ValueError(msg)

        Provenance().add_output_file(
            self.output_path, "r0/service/timelapse_coefficients"
        )
        if self.fig is not None:
            plt.close(self.fig)


def main():
    """Start tool."""
    DRS4TimelapseFitter().run()


if __name__ == "__main__":
    main()
