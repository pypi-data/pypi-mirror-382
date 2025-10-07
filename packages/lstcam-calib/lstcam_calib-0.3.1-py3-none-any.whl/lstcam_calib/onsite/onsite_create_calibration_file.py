"""Onsite script for creating a Cat-A calibration file."""
#!/usr//bin/env python

import argparse
import os
import subprocess
import sys
from datetime import datetime
from importlib.resources import files
from pathlib import Path

import lstcam_calib
import lstcam_calib.visualization.plot_calib as calib
from lstcam_calib.io import OUTPUT_FORMATS
from lstcam_calib.io.calibration import read_calibration_file
from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    DEFAULT_CONFIG_CAT_A,
    PIXEL_DIR_CAT_A,
    create_pro_symlink,
    find_filter_wheels,
    find_pedestal_file,
    find_r0_subrun,
    find_run_summary,
    find_systematics_correction_file,
    find_time_calibration_file,
    query_yes_no,
)

__all__ = []

# parse arguments
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
required = parser.add_argument_group("required arguments")
optional = parser.add_argument_group("optional arguments")

required.add_argument(
    "-r",
    "--run-number",
    help="Run number if the flat-field data",
    type=int,
    required=True,
)
optional.add_argument(
    "-f",
    "--output-format",
    help="output format",
    default="fits.gz",
    choices=OUTPUT_FORMATS,
)
optional.add_argument(
    "-p",
    "--pedestal-run",
    help="Pedestal run to be used. If None, it looks for the pedestal run of the date of the FF data.",
    type=int,
)

version = lstcam_calib.__version__

optional.add_argument(
    "-v", "--prod-version", help="Version of the production", default=f"v{version}"
)
optional.add_argument(
    "-s",
    "--statistics",
    help="Number of events for the flat-field and pedestal statistics",
    type=int,
    default=10000,
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
    "--time-run",
    help="Run for time calibration. If None, search the last time run before or equal the FF run",
    type=int,
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

optional.add_argument("--sub-run", help="sub-run to be processed.", type=int, default=0)
optional.add_argument("--min-ff", help="Min FF intensity cut in ADC.", type=float)
optional.add_argument("--max-ff", help="Max FF intensity cut in ADC.", type=float)
optional.add_argument("--filters", help="Calibox filters")
optional.add_argument("--tel-id", help="telescope id. Default = 1", type=int, default=1)

optional.add_argument(
    "--config", help="Config file", default=DEFAULT_CONFIG_CAT_A, type=Path
)

optional.add_argument(
    "--filters-db-url",
    help="Mongo data-base connection for filter information (Caco DB as default)",
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
    "--flatfield-heuristic",
    action="store_const",
    const=True,
    dest="use_flatfield_heuristic",
    help=(
        "If given, try to identify flatfield events from the raw data."
        " Should be used only for data from before 2022"
    ),
)
optional.add_argument(
    "--no-flatfield-heuristic",
    action="store_const",
    const=False,
    dest="use_flatfield_heuristic",
    help=(
        "If given, do not to identify flatfield events from the raw data."
        " Should be used only for data from before 2022"
    ),
)
parser.add_argument(
    "--no-db",
    action="store_true",
    help="Do not write metadata in TCU data-base",
)
optional.add_argument(
    "--db-url",
    help="Connection to calibration data_base.",
)

parser.add_argument(
    "--apply-drs4-corrections",
    action="store_true",
    help="Apply offline DRS4 correction",
)

parser.add_argument(
    "--apply-pedestal-correction",
    action="store_true",
    help="Apply offline pedestal correction",
)

optional.add_argument("--db-name", help="Name of mongo calibration db.")


def main():
    """Call calibration tool and write file in calibration data tree."""
    args, remaining_args = parser.parse_known_args()
    run = args.run_number
    output_format = args.output_format

    prod_id = args.prod_version
    stat_events = args.statistics
    time_run = args.time_run
    sys_date = args.sys_date
    no_sys_correction = args.no_sys_correction
    output_base_name = args.output_base_name
    sub_run = args.sub_run
    config_file = args.config
    yes = args.yes
    pro_symlink = not args.no_pro_symlink

    db = None

    if not args.no_db:
        print("\n--> use calibration database")
        db_kwargs = {}
        if args.db_name is not None:
            db_kwargs["db_name"] = args.db_name
        if args.db_url is not None:
            db_kwargs["db_url"] = args.db_url
        db_kwargs["data_tree_root"] = args.base_dir
        db = CalibrationDB(**db_kwargs)

    # looks for the filter values in the database if not given
    if args.filters is None:
        filters = find_filter_wheels(run, args.filters_db_url)
    else:
        filters = args.filters

    if filters is None:
        sys.exit(f"Missing filter value for run {run}. \n")

    # define the FF selection cuts
    if args.min_ff is None or args.max_ff is None:
        min_ff, max_ff = define_ff_selection_range(filters)
    else:
        min_ff, max_ff = args.min_ff, args.max_ff

    print(f"\n--> Start calculating calibration from run {run}, filters {filters}")

    # verify config file
    if not config_file.exists():
        raise OSError(f"Config file {config_file} does not exists. \n")

    print(f"\n--> Config file {config_file}")

    # verify input file
    r0_dir = args.r0_dir or args.base_dir / "R0"
    input_file = find_r0_subrun(run, sub_run, r0_dir)
    date = input_file.parent.name
    print(f"\n--> Input file: {input_file}")

    # verify output dir
    calib_dir = args.base_dir / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "calibration" / date / prod_id
    if not output_dir.exists():
        print(f"--> Create directory {output_dir}")
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

    # search the summary file info
    run_summary_path = find_run_summary(date, args.base_dir)

    print(f"\n--> Use run summary {run_summary_path}")

    if args.apply_drs4_corrections:
        pedestal_file = find_pedestal_file(
            pro,
            args.pedestal_run,
            date=date,
            base_dir=args.base_dir,
            db=db,
            format=output_format,
        )
        print(f"\n--> Pedestal file: {pedestal_file}")

        # search for time calibration file
        time_file = find_time_calibration_file(
            pro,
            date=date,
            time_run=time_run,
            base_dir=args.base_dir,
            db=db,
        )
        print(f"\n--> Time calibration file: {time_file}")

        if not args.apply_pedestal_correction:
            print("\n--> Offline baseline correction not required")
    else:
        print("\n--> DRS4 corrections not required")
        pedestal_file = None
        time_file = None

    # define systematic correction file
    if no_sys_correction:
        systematics_file = None
    else:
        systematics_file = find_systematics_correction_file(
            pro,
            date=date,
            sys_date=sys_date,
            base_dir=args.base_dir,
            db=db,
        )

    print(f"\n--> F-factor systematics correction file: {systematics_file}")

    # define charge file names
    print("\n***** PRODUCE CHARGE CALIBRATION FILE ***** ")

    if filters is not None:
        filter_info = f"_filters_{filters}"
    else:
        filter_info = ""

    # remember there are no systematic corrections
    prefix = "no_sys_corrected_" if no_sys_correction else ""

    output_name = f"{prefix}{output_base_name}{filter_info}.Run{run:05d}.{sub_run:04d}"

    output_file = output_dir / f"{output_name}.{output_format}"
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
            # remove from DB if used
            if db is not None:
                db.remove_file(CalibrationType.CALIBRATION, output_file)

            os.remove(output_file)

        else:
            print("\n--> Output file exists already. Stop")
            exit(1)

    #
    # produce ff calibration file
    #

    cmd = [
        "lstcam_calib_create_calibration_file",
        f"--input-file={input_file}",
        f"--output-file={output_file}",
        "--LSTEventSource.default_trigger_type=tib",
        f"--EventSource.min_flatfield_adc={min_ff}",
        f"--EventSource.max_flatfield_adc={max_ff}",
        f"--LSTCalibrationCalculator.systematic_correction_file={systematics_file}",
        f"--LSTEventSource.EventTimeCalculator.run_summary_path={run_summary_path}",
        f"--LSTEventSource.use_flatfield_heuristic={args.use_flatfield_heuristic}",
        f"--FlasherFlatFieldCalculator.sample_size={stat_events}",
        f"--PedestalIntegrator.sample_size={stat_events}",
        f"--LSTEventSource.LSTR0Corrections.apply_drs4_pedestal_correction={args.apply_pedestal_correction}",
        f"--LSTEventSource.apply_drs4_corrections={args.apply_drs4_corrections}",
        f"--LSTEventSource.LSTR0Corrections.drs4_time_calibration_path={time_file}",
        f"--LSTEventSource.LSTR0Corrections.drs4_pedestal_path={pedestal_file}",
        f"--config={config_file}",
        f"--log-file={log_file}",
        f"--provenance-log={provenance_file}",
        "--log-file-level=INFO",
    ]

    cmd.extend(remaining_args)

    print(f"\n--> PRODUCING CALIBRATION DATA in {output_file}")

    subprocess.run(cmd, check=True)

    # store meta-data in data-base (paths relative to base_dir)
    if db is not None:
        db.add_calibration_file(
            path=output_file,
            provenance_path=provenance_file,
            obs_id=run,
            local_run_id=run,
            drs4_baseline_path=pedestal_file,
            drs4_time_sampling_path=time_file,
            ffactor_systematics_path=systematics_file,
        )
        print("\n--> meta-data written in db")

    # plot and save some results
    plot_file = f"{output_dir}/log/{output_name}.pdf"

    print(f"\n--> PRODUCING PLOTS in {plot_file} ...")
    mon = read_calibration_file(output_file)
    calib.plot_calibration_results(
        mon.pedestal, mon.flatfield, mon.calibration, run, plot_file, "Cat-A"
    )

    print("\n--> END")


def define_ff_selection_range(filters):
    """Return the range of charges to select the FF events."""
    try:
        if filters is None:
            raise ValueError("Filters are not defined")
        # give standard values if standard filters
        if filters == "52":
            min_ff = 3000
            max_ff = 12000

        else:
            # ... recuperate transmission value of all the filters
            transm_file = files("lstcam_calib").joinpath(
                "resources/filters_transmission.dat"
            )

            f = open(transm_file)
            # skip header
            f.readline()
            trasm = {}
            for line in f:
                columns = line.split()
                trasm[columns[0]] = float(columns[1])

            if trasm[filters] > 0.001:
                min_ff = 4000
                max_ff = 1000000

            elif trasm[filters] <= 0.001 and trasm[filters] > 0.0005:
                min_ff = 1200
                max_ff = 12000
            else:
                min_ff = 200
                max_ff = 5000

    except Exception as e:
        print(f"\n >>> Exception: {e}")
        raise OSError("--> No FF selection range information")

    return min_ff, max_ff


if __name__ == "__main__":
    main()
