"""
Onsite script to creates DRS4 baseline and spikes' height coefficients.

It handles the interaction with the onsite data tree and calibration database.
"""
#!/usr//bin/env python

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

import lstcam_calib
import lstcam_calib.visualization.plot_drs4 as drs4
from lstcam_calib.io import OUTPUT_FORMATS
from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    PIXEL_DIR_CAT_A,
    create_pro_symlink,
    find_r0_subrun,
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
    "-r", "--run-number", help="Run number with drs4 pedestals", type=int, required=True
)
version = lstcam_calib.__version__
optional.add_argument(
    "-f",
    "--output-format",
    help="output format",
    default="fits.gz",
    choices=OUTPUT_FORMATS,
)
optional.add_argument(
    "-v", "--prod-version", help="Version of the production", default=f"v{version}"
)
optional.add_argument(
    "-m",
    "--max-events",
    help="Number of events to be processed",
    type=int,
    default=20000,
)
optional.add_argument(
    "-b",
    "--base-dir",
    help="Base dir for the output directory tree",
    type=Path,
    default=DEFAULT_BASE_PATH,
)
optional.add_argument(
    "--r0-dir",
    help="Root dir for the input r0 tree. By default, <base_dir>/R0 will be used",
    type=Path,
)
optional.add_argument("--tel-id", help="telescope id. Default = 1", type=int, default=1)
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
parser.add_argument(
    "--no-progress",
    action="store_true",
    help="Do not display a progress bar during event processing",
)
parser.add_argument(
    "--no-db",
    action="store_true",
    help="Do not write in TCU data-base",
)
optional.add_argument(
    "--db-url",
    help="Connection to calibration data_base.",
)

optional.add_argument("--db-name", help="Name of mongo calibration db.")

optional.add_argument("--sub-run", help="sub-run to be processed.", type=int, default=0)


def main():
    """Run drs4 baseline calibration tool and write files in calibration data tree."""
    args, remaining_args = parser.parse_known_args()
    run = args.run_number
    output_format = args.output_format
    prod_id = args.prod_version
    max_events = args.max_events
    base_dir = args.base_dir
    tel_id = args.tel_id
    yes = args.yes
    pro_symlink = not args.no_pro_symlink
    sub_run = args.sub_run

    db = None

    if not args.no_db:
        print("\n--> use calibration database")
        db_kwargs = {}
        if args.db_name is not None:
            db_kwargs["db_name"] = args.db_name
        if args.db_url is not None:
            db_kwargs["db_url"] = args.db_url

        db_kwargs["data_tree_root"] = args.base_dir
        db_kwargs["tel_id"] = args.tel_id

        db = CalibrationDB(**db_kwargs)

    print(f"\n--> Start calculating DRS4 pedestals from run {run} \n")

    # verify input file
    r0_dir = args.r0_dir or Path(args.base_dir) / "R0"

    input_file = find_r0_subrun(run, sub_run=sub_run, r0_dir=r0_dir)
    date = input_file.parent.name

    # verify and make output dir
    calib_dir = base_dir / PIXEL_DIR_CAT_A
    output_dir = calib_dir / "drs4_baseline" / date / prod_id

    if not output_dir.exists():
        print(f"--> Create directory {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # update the default production directory
    if pro_symlink:
        create_pro_symlink(output_dir)

    # make log dir
    log_dir = output_dir / "log"
    if not log_dir.exists():
        print(f"--> Create directory {log_dir}")
        os.makedirs(log_dir, exist_ok=True)

    # define output file
    output_file = (
        output_dir / f"drs4_pedestal.Run{run:05d}.{sub_run:04d}.{output_format}"
    )

    now = datetime.now().replace(microsecond=0).isoformat(sep="T")
    provenance_file = (
        log_dir / f"drs4_pedestal.Run{run:05d}.{sub_run:04d}_{now}.provenance.log"
    )

    if output_file.exists():
        remove = False

        if not yes and os.getenv("SLURM_JOB_ID") is None:
            remove = query_yes_no(
                ">>> Output file exists already. Do you want to remove it?"
            )

        if yes or remove:
            # remove from DB if used
            if db is not None:
                db.remove_file(CalibrationType.DRS4_BASELINE, output_file)

            os.remove(output_file)

        else:
            print("\n--> Output file exists already. Stop")
            exit(1)

    # run script
    cmd = [
        "lstcam_calib_create_drs4_pedestal_file",
        f"--input-file={input_file}",
        f"--output-file={output_file}",
        f"--provenance-log={provenance_file}",
        f"--max-events={max_events}",
    ]

    if args.no_progress:
        cmd.append("--no-progress")

    cmd.extend(remaining_args)

    print(f"\n--> PRODUCING BASELINE DATA in {output_file}")

    subprocess.run(cmd, check=True)

    # store meta-data in data-base (paths relative to base_dir)

    if db is not None:
        db.add_drs4_baseline_file(
            path=output_file,
            provenance_path=provenance_file,
            obs_id=run,
            local_run_id=run,
        )
        print("\n--> meta-data written in db")

    # plot and save some results
    plot_file = f"{output_dir}/log/drs4_pedestal.Run{run:05d}.{sub_run:04d}.pdf"
    print(f"\n--> PRODUCING PLOTS in {plot_file} ...")
    drs4.plot_pedestals(
        input_file, output_file, run, plot_file, tel_id=tel_id, offset_value=400
    )

    print("\n--> END")


if __name__ == "__main__":
    main()
