"""
Tool to perform the fit of an intensity/filter scan.

It computes the F-factor systematics corrections (quadratic noise term).

.. code:: python

   lstcam_calib_create_fit_intensity_scan_file --help


"""
import os
from functools import partial
from pathlib import Path

import numpy as np
import tables
from ctapipe.coordinates import EngineeringCameraFrame
from ctapipe.core import Provenance, Tool, traits
from ctapipe.io import metadata as meta
from ctapipe.visualization import CameraDisplay
from ctapipe_io_lst import constants, load_camera_geometry
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator
from scipy.optimize import curve_fit
from traitlets import Float, Int, List

from lstcam_calib.io import PROV_INPUT_ROLES, PROV_OUTPUT_ROLES
from lstcam_calib.io.calibration import get_metadata, read_calibration_file
from lstcam_calib.io.metadata import (
    get_ctapipe_metadata,
    get_local_metadata,
)

__all__ = ["FitIntensityScan"]

MIN_N_RUNS = 5


class FitIntensityScan(Tool):
    """Tool that generates a file with the results of the fit of an intensity scan.

    This is useful to estimate the quadratic noise term to include in the
    standard F-factor formula.
    """

    name = "FitFilterScan"
    description = "Tool to fit an intensity scan"

    signal_range = List(
        [[1500, 14000], [200, 14000]],
        help="Signal range to include in the fit for [HG,LG] (camera median in [ADC])",
    ).tag(config=True)

    gain_channels = List([0, 1], help="Gain channel to process (HG=0, LG=1)").tag(
        config=True
    )

    sub_run = Int(0, help="Sub run number to process").tag(config=True)

    run_list = List(
        help="List of runs",
    ).tag(config=True)

    input_dir = traits.Path(
        directory_ok=True,
        help="directory with the input files",
    ).tag(config=True)

    input_prefix = traits.Unicode(
        default_value="calibration",
        help="Prefix to select calibration files to fit",
    ).tag(config=True)

    output_path = traits.Path(
        directory_ok=False,
        default_value="filter_scan_fit.h5",
        help="Path the output hdf5 file",
    ).tag(config=True)

    plot_path = traits.Path(
        directory_ok=False,
        default_value="filter_scan_fit.pdf",
        help="Path to pdf file with check plots",
    ).tag(config=True)

    fit_initialization = List(
        [[100.0, 0.001], [6.0, 0.001]],
        help="Fit parameters initialization [gain (ADC/pe), B term] for HG and LG",
    ).tag(config=True)

    fractional_variance_error = Float(
        0.02,
        help="Constant fractional error assumed for the y fit coordinate (variance)",
    ).tag(config=True)

    squared_excess_noise_factor = Float(
        1.222, help="Excess noise factor squared: 1+ Var(gain)/Mean(Gain)**2"
    ).tag(config=True)

    aliases = {
        "signal-range": "FitIntensityScan.signal_range",
        "input-dir": "FitIntensityScan.input_dir",
        "output-path": "FitIntensityScan.output_path",
        "plot-path": "FitIntensityScan.plot_path",
        "sub-run": "FitIntensityScan.sub_run",
        "gain-channels": "FitIntensityScan.gain_channels",
        "run-list": "FitIntensityScan.run_list",
        "input-prefix": "FitIntensityScan.input_prefix",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for chan in self.gain_channels:
            if not self.signal_range[chan]:
                raise ValueError(
                    f"Trailet signal_range {self.signal_range} inconsistent with"
                    f"trailet {self.gain_channels}. \n"
                )

        self.unusable_pixels = [None, None]
        self.signal = [None, None]
        self.variance = [None, None]
        self.selected_runs = [[], []]
        self.fit_parameters = np.zeros((constants.N_GAINS, constants.N_PIXELS, 2))
        self.fit_cov_matrix = np.zeros((constants.N_GAINS, constants.N_PIXELS, 4))
        self.fit_error = np.zeros((constants.N_GAINS, constants.N_PIXELS))

        self.run_list.sort()
        self.tel_id = None

    def setup(self):
        """Read input data."""
        channel = ["HG", "LG"]

        input_files = []
        # loop on runs and memorize data
        for i, run in enumerate(self.run_list):
            file_list = sorted(
                Path(f"{self.input_dir}").glob(
                    f"{self.input_prefix}*.Run{run:05d}.{self.sub_run:04d}.*"
                )
            )

            if len(file_list) == 0:
                raise OSError(f"Input file for run {run} do not found. \n")

            if len(file_list) > 1:
                raise OSError(
                    f"Input file for run {run} is more than one: {file_list} \n"
                )

            inp_file = file_list[0]
            if os.path.getsize(inp_file) < 100:
                raise OSError("file size run %d is too short \n", run)

            self.log.debug("Read file %s", inp_file)

            # read metadata info for first valid run
            if self.tel_id is None:
                metadata = get_metadata(inp_file)
                self.tel_id = metadata["TEL_ID"]
                self.run_start = metadata["RUN_START"]

            if inp_file not in input_files:
                input_files.append(inp_file)

            mon = read_calibration_file(inp_file)

            for chan in self.gain_channels:
                # verify that the median signal is inside the asked range
                charges = np.ma.array(
                    mon.flatfield.charge_median[chan],
                    mask=mon.calibration.unusable_pixels[chan],
                )
                median_charge = np.ma.median(charges)

                if (
                    median_charge > self.signal_range[chan][1]
                    or median_charge < self.signal_range[chan][0]
                ):
                    self.log.debug(
                        "%s : skip run %d, signal out of range %6.1f ADC",
                        channel[chan],
                        run,
                        median_charge,
                    )
                    continue

                signal = (
                    mon.flatfield.charge_median[chan] - mon.pedestal.charge_median[chan]
                )
                variance = (
                    mon.flatfield.charge_std[chan] ** 2
                    - mon.pedestal.charge_std[chan] ** 2
                )

                if self.signal[chan] is None:
                    self.signal[chan] = signal
                    self.variance[chan] = variance
                    self.unusable_pixels[chan] = mon.calibration.unusable_pixels[chan]

                else:
                    self.signal[chan] = np.column_stack((self.signal[chan], signal))
                    self.variance[chan] = np.column_stack(
                        (self.variance[chan], variance)
                    )
                    self.unusable_pixels[chan] = np.column_stack(
                        (
                            self.unusable_pixels[chan],
                            mon.calibration.unusable_pixels[chan],
                        )
                    )
                self.selected_runs[chan].append(run)
                self.log.info(
                    "%s : select run %d, median charge %6.1f ADC\n",
                    channel[chan],
                    run,
                    median_charge,
                )
        # add input files in provenance
        for inp_file in input_files:
            Provenance().add_input_file(
                str(inp_file), role=PROV_INPUT_ROLES["fit_intensity_scan"]
            )

        # check to have enough selected runs
        for chan in self.gain_channels:
            if self.signal[chan] is None:
                raise OSError(f"--> Zero runs selected for channel {channel[chan]} \n")

            if self.signal[chan].size < MIN_N_RUNS * constants.N_PIXELS:
                raise OSError(
                    f"--> Not enough runs selected for channel {channel[chan]}: {int(self.signal[chan].size / constants.N_PIXELS)} runs \n"
                )

    def start(self):
        """Loop to fit each pixel."""
        # only positive parameters
        bounds = [0, 200]

        funfit = partial(quadratic_fit, f2=self.squared_excess_noise_factor)

        for pix in np.arange(constants.N_PIXELS):
            if pix % 100 == 0:
                self.log.debug("Pixel %d", pix)

            # loop over channel
            for chan in self.gain_channels:
                # fit parameters initialization
                p0 = np.array(self.fit_initialization[chan])

                mask = self.unusable_pixels[chan][pix]
                sig = np.ma.array(self.signal[chan][pix], mask=mask).compressed()
                var = np.ma.array(self.variance[chan][pix], mask=mask).compressed()

                # skip the pixel if not enough data
                if sig.shape[0] < MIN_N_RUNS:
                    self.log.debug(
                        "Not enough data in pixel %d and channel %d for the fit (%d runs)\n",
                        pix,
                        chan,
                        sig.shape[0],
                    )
                    self.fit_error[chan, pix] = 1
                    continue

                # we assume a constant fractional error
                sigma = self.fractional_variance_error * var

                try:
                    par, par_cov = curve_fit(
                        funfit, sig, var, bounds=bounds, sigma=sigma, p0=p0
                    )
                    self.fit_parameters[chan, pix] = par
                    self.fit_cov_matrix[chan, pix] = par_cov.reshape(4)

                except Exception as e:
                    self.log.exception("\n >>> Exception: %s", e)

                    self.log.error("Error for pixel %d and channel %d:\n", pix, chan)
                    self.log.error("signal %f \n", sig)
                    self.log.error("variance %f \n", var)

                    self.fit_error[chan, pix] = 1

    def finish(self):
        """Write fit results in h5 file and the check-plots in pdf file."""
        # prepare metadata
        ctapipe_metadata = get_ctapipe_metadata("FFactor systematics coefficients")
        local_metadata = get_local_metadata(
            self.tel_id,
            str(self.provenance_log.resolve()),
            self.run_start,
        )

        gain = np.ma.array(self.fit_parameters.T[0], mask=self.fit_error.T)
        quadratic_term = np.ma.array(self.fit_parameters.T[1], mask=self.fit_error.T)

        # give to the badly fitted pixel a median value for the B term
        median_quadratic_term = np.ma.median(quadratic_term, axis=0)

        fill_array = (
            np.ones((constants.N_PIXELS, constants.N_GAINS)) * median_quadratic_term
        )

        quadratic_term_corrected = np.ma.filled(quadratic_term, fill_array)

        with tables.open_file(
            self.output_path, mode="w", title="Fit of filter scan"
        ) as hf:
            hf.create_array("/", "gain", gain.T, "Pixel gain estimated by the fit")
            hf.create_array(
                "/",
                "B_term",
                quadratic_term_corrected.T,
                "Quadratic coefficient of F-factor formula, estimated by the fit",
            )
            hf.create_array(
                "/",
                "covariance_matrix",
                self.fit_cov_matrix,
                "Covariance matrix of the fit",
            )
            hf.create_array(
                "/", "bad_fit_mask", self.fit_error, "Mask of pixels with failing fit"
            )

            # remember the camera median and the variance per run
            channel = ["HG", "LG"]
            for chan in [0, 1]:
                if self.signal[chan] is not None:
                    hf.create_array(
                        "/",
                        f"signal_{channel[chan]}",
                        self.signal[chan],
                        f"{channel[chan]} signal charge used in fit",
                    )
                    hf.create_array(
                        "/",
                        f"variance_{channel[chan]}",
                        self.variance[chan],
                        f"{channel[chan]} signal variance used in fit",
                    )
                    hf.create_array(
                        "/",
                        f"runs_{channel[chan]}",
                        self.selected_runs[chan],
                        f"Runs used in {channel[chan]} fit ",
                    )

            hf.create_array("/", "runs", self.run_list, "Total list of Runs")
            hf.create_array("/", "sub_run", self.sub_run, "Considered sub-run")

            # add metadata
            meta.write_to_hdf5(ctapipe_metadata.to_dict(), hf)
            meta.write_to_hdf5(local_metadata.as_dict(), hf)

        Provenance().add_output_file(
            str(self.output_path),
            role=PROV_OUTPUT_ROLES["fit_intensity_scan"],
        )

        # plot open pdf
        with PdfPages(self.plot_path) as pdf:
            plt.rc("font", size=15)

            for chan in self.gain_channels:
                # plot the used runs and their median camera charge
                fig = plt.figure(figsize=(8, 20))
                fig.suptitle(f"{channel[chan]} channel", fontsize=25)
                ax = plt.subplot(2, 1, 1)
                ax.grid(True)
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                ax.yaxis.set_major_locator(plt.MultipleLocator(1))

                plt.plot(
                    np.nanmedian(self.signal[chan], axis=0),
                    self.selected_runs[chan],
                    "o",
                )
                plt.xlabel(r"$\mathrm{\overline{Q}-\overline{ped}}$ [ADC]")
                plt.ylabel(r"Runs used in the fit")

                plt.subplot(2, 1, 2)
                camera = load_camera_geometry()
                camera = camera.transform_to(EngineeringCameraFrame())
                disp = CameraDisplay(camera)
                image = self.fit_parameters.T[1].T * 100
                mymin = np.median(image[chan]) - 3 * np.std(image[chan])
                mymax = np.median(image[chan]) + 3 * np.std(image[chan])
                disp.set_limits_minmax(mymin, mymax)
                mask = np.where(self.fit_error[chan] == 1)[0]
                disp.highlight_pixels(mask, linewidth=2.5, color="green")
                disp.image = image[chan]
                disp.cmap = plt.cm.coolwarm
                plt.title(f"{channel[chan]} Fitted B values [%]")
                disp.add_colorbar()
                plt.tight_layout()
                pdf.savefig()

                # plot the fit results and residuals for four arbitrary  pixels
                fig = plt.figure(figsize=(11, 22))
                fig.suptitle(f"{channel[chan]} channel", fontsize=25)

                pad = 0
                for pix in [0, 600, 1200, 1800]:
                    pad += 1
                    plt.subplot(4, 2, pad)
                    plt.grid(which="minor")

                    mask = self.unusable_pixels[chan][pix]
                    sig = np.ma.array(self.signal[chan][pix], mask=mask).compressed()
                    var = np.ma.array(self.variance[chan][pix], mask=mask).compressed()
                    popt = self.fit_parameters[chan, pix]

                    # plot points
                    plt.plot(sig, var, "o", color="C0")

                    # plot fit
                    min_x = min(1000, np.min(sig) * 0.9)
                    max_x = max(10000, np.max(sig) * 1.1)
                    x = np.arange(np.min(sig), np.max(sig))

                    plt.plot(
                        x,
                        quadratic_fit(x, *popt),
                        "--",
                        color="C1",
                        label=f"Pixel {pix}:\ng={popt[0]:5.2f} [ADC/pe] , B={popt[1]:5.3f}",
                    )
                    plt.xlim(min_x, max_x)
                    plt.xlabel("Q-ped [ADC]")
                    plt.ylabel(r"$\mathrm{\sigma_Q^2-\sigma_{ped}^2}$ [$ADC^2$]")
                    plt.xscale("log")
                    plt.yscale("log")
                    plt.legend()

                    # plot residuals
                    pad += 1
                    plt.subplot(4, 2, pad)
                    plt.grid(which="both", axis="both")

                    popt = self.fit_parameters[chan, pix]
                    plt.plot(
                        sig,
                        (quadratic_fit(sig, *popt) - var) / var * 100,
                        "o",
                        color="C0",
                    )
                    plt.xlim(min_x, max_x)
                    plt.xscale("log")
                    plt.ylabel("fit residuals %")
                    plt.xlabel("Q-ped [ADC]")
                    plt.hlines(0, 0, np.max(sig), linestyle="dashed", color="black")

                plt.tight_layout()
                pdf.savefig()

            Provenance().add_output_file(
                str(self.plot_path),
                role="fit intensity check plots",
                add_meta=False,
            )


def quadratic_fit(t, b=1, c=1, f2=1.222):
    return b * f2 * t + c**2 * t**2


def main():
    exe = FitIntensityScan()

    exe.run()


if __name__ == "__main__":
    main()
