"""Onsite script for creating a Cat-B calibration file."""
#!/usr//bin/env python

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import lstcam_calib
import lstcam_calib.visualization.plot_calib as calib
from lstcam_calib.io import OUTPUT_FORMATS
from lstcam_calib.io.calibration import read_calibration_file
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    DEFAULT_CONFIG_CAT_B,
    PIXEL_DIR_CAT_B,
    create_pro_symlink,
    find_calibration_file,
    find_filter_wheels,
    find_interleaved_subruns,
    find_r0_subrun,
    find_systematics_correction_file,
    query_yes_no,
)

__all__ = []

MAX_SUBRUNS = 100000

# parse arguments
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
required = parser.add_argument_group("required arguments")
optional = parser.add_argument_group("optional arguments")

required.add_argument(
    "-r", "--run-number", help="Run number of interleaved data", type=int, required=True
)

version = lstcam_calib.__version__

optional.add_argument(
    "-c",
    "--catA-calibration-run",
    help="Cat-A calibration run to be used. If None, it looks for the calibration run of the date of the interleaved data.",
    type=int,
)
optional.add_argument(
    "-v", "--prod-version", help="Version of the production", default=f"v{version}"
)

optional.add_argument("--lstchain-version", help="lstchain version of the DL1 data.")
optional.add_argument(
    "-s",
    "--statistics",
    help="Number of events for the flat-field and pedestal statistics",
    type=int,
    default=2500,
)
optional.add_argument(
    "-b",
    "--base-dir",
    help="Root dir for the output directory tree",
    type=Path,
    default=DEFAULT_BASE_PATH,
)
optional.add_argument(
    "--r0-dir",
    help="Root dir for the input r0 tree. By default, <base_dir>/R0 will be used",
    type=Path,
)
optional.add_argument(
    "--dl1-dir",
    help="Root dir for the input r tree. By default, <base_dir>/DL1 will be used",
    type=Path,
)

optional.add_argument(
    "--sys-date",
    help=(
        "Date of systematic correction file (format YYYYMMDD). \n"
        "Default: automatically search the best date \n"
    ),
)
optional.add_argument(
    "--no-sys-correction",
    help="Systematic corrections are not applied. \n",
    action="store_true",
    default=False,
)
optional.add_argument(
    "--output-base-name",
    help="Base of output file name (change only for debugging)",
    default="calibration",
)

optional.add_argument(
    "--n-subruns",
    help="Number of subruns to be processed",
    type=int,
    default=MAX_SUBRUNS,
)

optional.add_argument("-f", "--filters", help="Calibox filters")

optional.add_argument(
    "--config", help="Config file", default=DEFAULT_CONFIG_CAT_B, type=Path
)
optional.add_argument(
    "--mongodb",
    help="Mongo data-base (CACO DB) connection.",
    default="mongodb://10.200.10.161:27018/",
)

optional.add_argument(
    "-y",
    "--yes",
    action="store_true",
    help="Do not ask interactively for permissions, assume true",
)
optional.add_argument(
    "--no-pro-symlink",
    action="store_true",
    help="Do not update the pro dir symbolic link, assume true",
)
optional.add_argument(
    "--catA-format",
    help="output format",
    default="fits.gz",
    choices=OUTPUT_FORMATS,
)


def main():
    args, remaining_args = parser.parse_known_args()
    run = args.run_number
    n_subruns = args.n_subruns
    prod_id = f"v{lstcam_calib.__version__}"
    stat_events = args.statistics

    sys_date = args.sys_date
    no_sys_correction = args.no_sys_correction
    config_file = args.config
    yes = args.yes
    pro_symlink = not args.no_pro_symlink
    r0_dir = args.r0_dir or args.base_dir / "R0"
    dl1_dir = args.dl1_dir or args.base_dir / "DL1"

    # looks for the filter values in the database if not given
    if args.filters is None:
        filters = find_filter_wheels(run, args.mongodb)
    else:
        filters = args.filters

    if filters is None:
        sys.exit(f"Missing filter value for run {run}. \n")

    print(
        f"\n--> Start calculating Cat-B calibration from run {run}, filters {filters}"
    )

    # verify config file
    if not config_file.exists():
        raise OSError(f"Config file {config_file} does not exists. \n")

    print(f"\n--> Config file {config_file}")

    # look in R0 to find the date
    r0_list = find_r0_subrun(run, 0, r0_dir)
    date = r0_list.parent.name

    # dl1 dir
    run_dl1_dir = dl1_dir / date
    if not run_dl1_dir.exists():
        print(
            f"\n--> DL1 dir {run_dl1_dir} does not exist. Set the correct directory with the dl1-dir trailet"
        )
        exit(1)

    # verify input files
    input_files = find_interleaved_subruns(run, run_dl1_dir, args.lstchain_version)
    input_path = input_files[0].parent
    print(f"\n--> Found {len(input_files)} interleaved subruns for run {run}")
    if n_subruns < MAX_SUBRUNS:
        print(f"--> Process {n_subruns} subruns")

    # verify output dir
    calib_dir = args.base_dir / PIXEL_DIR_CAT_B
    output_dir = calib_dir / "calibration" / date / prod_id
    if not output_dir.exists():
        print(f"\n--> Create directory {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    if pro_symlink:
        pro = "pro"
        create_pro_symlink(output_dir)
    else:
        pro = prod_id

    # make log dir
    log_dir = output_dir / "log"
    if not log_dir.exists():
        print(f"--> Create directory {log_dir}")
        log_dir.mkdir(parents=True, exist_ok=True)

    cat_a_calib_file = find_calibration_file(
        pro,
        args.catA_calibration_run,
        date=date,
        base_dir=args.base_dir,
        format=args.catA_format,
    )
    print(f"\n--> Cat-A calibration file: {cat_a_calib_file}")

    # define systematic correction file
    if no_sys_correction:
        systematics_file = None
    else:
        systematics_file = find_systematics_correction_file(
            pro, date, sys_date, args.base_dir
        )

    print(f"\n--> F-factor systematics correction file: {systematics_file}")

    # define charge file names
    print("\n***** PRODUCE CAT_B CALIBRATION FILE ***** ")

    if filters is not None:
        filter_info = f"_filters_{filters}"
    else:
        filter_info = ""

    input_file_pattern = f"interleaved_LST-1.Run{run:05d}.*.h5"
    output_name = f"cat_B_calibration{filter_info}.Run{run:05d}"

    output_file = output_dir / f"{output_name}.h5"
    print(f"\n--> Output file {output_file}")

    now = datetime.now().replace(microsecond=0).isoformat(sep="T")
    log_file = log_dir / f"{output_name}_{now}.log"
    print(f"\n--> Log file {log_file}")

    provenance_file = log_dir / f"{output_name}_{now}.provenance.log"

    if output_file.exists():
        remove = False

        if not yes and os.getenv("SLURM_JOB_ID") is None:
            remove = query_yes_no(
                ">>> Output file exists already. Do you want to remove it?"
            )

        if yes or remove:
            os.remove(output_file)

        else:
            print("\n--> Output file exists already. Stop")
            exit(1)

    #
    # produce ff calibration file
    #

    cmd = [
        "lstcam_calib_create_cat_B_calibration_file",
        f"--input-path={input_path}",
        f"--output-file={output_file}",
        f"--input-file-pattern={input_file_pattern}",
        f"--n-subruns={n_subruns}",
        f"--cat-a-calibration-file={cat_a_calib_file}",
        f"--LSTCalibrationCalculator.systematic_correction_file={systematics_file}",
        f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
        f"--PedestalIntegrator.sample_size={stat_events}",
        f"--config={config_file}",
        f"--log-file={log_file}",
        f"--provenance-log={provenance_file}",
        "--log-file-level=INFO",
        *remaining_args,
    ]

    print("\n--> RUNNING...")
    subprocess.run(cmd, check=True)

    # plot and save some results
    plot_file = f"{output_dir}/log/{output_name}.pdf"

    print(f"\n--> PRODUCING PLOTS in {plot_file} ...")
    mon = read_calibration_file(output_file)
    calib.plot_calibration_results(
        mon.pedestal, mon.flatfield, mon.calibration, run, plot_file, "Cat-B"
    )

    print("\n--> END")


if __name__ == "__main__":
    main()
