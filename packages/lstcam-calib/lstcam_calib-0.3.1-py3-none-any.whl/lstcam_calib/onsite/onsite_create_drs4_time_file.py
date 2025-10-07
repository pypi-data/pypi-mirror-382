"""
Onsite script to create DRS4 time correction file.

It handles the interaction with the onsite data tree and the database.
"""
#!/usr//bin/env python

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

import lstcam_calib
from lstcam_calib.io import OUTPUT_FORMATS
from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    DEFAULT_CONFIG_CAT_A,
    PIXEL_DIR_CAT_A,
    create_pro_symlink,
    find_pedestal_file,
    find_r0_subrun,
    find_run_summary,
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
version = lstcam_calib.__version__
optional.add_argument(
    "-v", "--prod-version", help="Version of the production", default=f"v{version}"
)
optional.add_argument(
    "-p",
    "--pedestal-run",
    help="Pedestal run to be used. If None, it looks for the pedestal run of the date of the FF data.",
    type=int,
)

optional.add_argument(
    "-s",
    "--statistics",
    help="Number of events for the flat-field and pedestal statistics",
    type=int,
    default=20000,
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
optional.add_argument("--sub-run", help="sub-run to be processed.", type=int, default=0)

optional.add_argument(
    "--config", help="Config file", default=DEFAULT_CONFIG_CAT_A, type=Path
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

optional.add_argument(
    "--no-progress",
    action="store_true",
    help="Do not display a progress bar during event processing",
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
    """Run drs4 time calibration tool and write files in calibration data tree."""
    args, remaining_args = parser.parse_known_args()
    run = args.run_number
    output_format = args.output_format
    prod_id = args.prod_version
    stat_events = args.statistics
    base_dir = args.base_dir
    sub_run = args.sub_run
    config_file = args.config
    pro_symlink = not args.no_pro_symlink
    yes = args.yes

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

    print(f"\n--> Start calculating drs4 time corrections from run {run}")

    # verify config file
    if not config_file.exists():
        raise OSError(f"Config file {config_file} does not exists. \n")

    print(f"\n--> Config file {config_file}")

    # verify input file
    r0_dir = args.r0_dir or Path(args.base_dir) / "R0"
    input_file = find_r0_subrun(run, sub_run, r0_dir)
    date = input_file.parent.name
    print(f"\n--> Input file: {input_file}")

    # verify output dir
    calib_dir = base_dir / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_time_sampling_from_FF" / date / prod_id

    if not output_dir.exists():
        print(f"--> Create directory {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # make log dir
    log_dir = output_dir / "log"
    if not log_dir.exists():
        print(f"--> Create directory {log_dir}")
        log_dir.mkdir(parents=True, exist_ok=True)

    # update the default production directory
    if pro_symlink:
        pro = "pro"
        create_pro_symlink(output_dir)
    else:
        pro = prod_id

    run_summary_path = find_run_summary(date, args.base_dir)
    print(f"\n--> Use run summary {run_summary_path}")

    output_file = (
        output_dir / f"time_calibration.Run{run:05d}.{sub_run:04d}.{output_format}"
    )

    pedestal_file = None
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

        if not args.apply_pedestal_correction:
            print("\n--> Offline baseline correction not required")
    else:
        print("\n--> DRS4 corrections not required")

    now = datetime.now().replace(microsecond=0).isoformat(sep="T")
    provenance_file = (
        log_dir / f"time_calibration.Run{run:05d}.{sub_run:04d}_{now}.provenance.log"
    )

    if output_file.exists():
        remove = False

        if not yes:
            remove = query_yes_no(
                ">>> Output file exists already. Do you want to remove it?"
            )

        if yes or remove:
            # remove from DB if used
            if db is not None:
                db.remove_file(CalibrationType.DRS4_TIME_SAMPLING, output_file)

            os.remove(output_file)

        else:
            print("\n--> Output file exists already. Stop")
            exit(1)

    print(f"\n--> PRODUCING TIME CALIBRATION in {output_file} ...")
    cmd = [
        "lstcam_calib_create_drs4_time_file",
        f"--input-file={input_file}",
        f"--output-file={output_file}",
        f"--provenance-log={provenance_file}",
        f"--config={config_file}",
        f"--run-summary-file={run_summary_path}",
        f"--max-events={stat_events}",
        f"--LSTEventSource.LSTR0Corrections.apply_drs4_pedestal_correction={args.apply_pedestal_correction}",
        f"--LSTEventSource.apply_drs4_corrections={args.apply_drs4_corrections}",
        f"--LSTEventSource.LSTR0Corrections.drs4_pedestal_path={pedestal_file}",
    ]

    if args.use_flatfield_heuristic:
        cmd.append("--flatfield-heuristic")

    if args.no_progress:
        cmd.append("--no-progress")

    cmd.extend(remaining_args)

    print(f"\n--> PRODUCING TIME SAMPLING DATA in {output_file}")

    subprocess.run(cmd, check=True)

    # store meta-data in data-base (paths relative to base_dir)
    if db is not None:
        db.add_drs4_time_sampling_file(
            path=output_file,
            provenance_path=provenance_file,
            drs4_baseline_path=pedestal_file,
            obs_id=run,
            local_run_id=run,
        )
        print("\n--> meta-data written in db")

    print("\n--> END")


if __name__ == "__main__":
    main()
