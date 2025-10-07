"""Onsite script to create the Cat-B calibration files with batch jobs."""
#!/usr/bin/env python


import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import lstcam_calib
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    DEFAULT_CONFIG_CAT_B,
    PIXEL_DIR_CAT_B,
    find_interleaved_subruns,
    find_r0_subrun,
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
    "-r", "--run-list", help="Run numbers of intereleaved data", type=int, nargs="+"
)
optional.add_argument(
    "-f",
    "--filters-list",
    help="Filter list (same order as run list)",
    type=int,
    nargs="+",
)

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
    "--dl1-dir",
    help="Root dir for the input DL1 tree. By default, <base_dir>/DL1 will be used",
    type=Path,
)
optional.add_argument(
    "--r0-dir",
    help="Root dir for the input r0 tree. By default, <base_dir>/R0 will be used",
    type=Path,
)

optional.add_argument("--n-subruns", help="Number of subruns to be processed", type=int)

optional.add_argument(
    "--sys-date",
    help="Date of systematic corrections (format YYYYMMDD). \n"
    "Default: automatically search the best date \n",
)
optional.add_argument(
    "--no-sys-correction",
    help="Systematic corrections are not applied. \n",
    action="store_true",
    default=False,
)

optional.add_argument(
    "-y",
    "--yes",
    action="store_true",
    help="Do not ask interactively for permissions, assume true",
)

optional.add_argument("--lstchain-version", help="lstchain version of the DL1 data.")
optional.add_argument(
    "--no-pro-symlink",
    action="store_true",
    help="Do not update the pro dir symbolic link, assume true",
)

optional.add_argument(
    "--config", help="Config file", default=DEFAULT_CONFIG_CAT_B, type=Path
)


optional.add_argument("--queue", help="Slurm queue. Default: short ", default="short")


def main():
    args, remaining_args = parser.parse_known_args()
    run_list = args.run_list
    n_subruns = args.n_subruns

    filters_list = args.filters_list

    prod_id = f"v{lstcam_calib.__version__}"
    stat_events = args.statistics
    base_dir = args.base_dir

    config_file = args.config
    sys_date = args.sys_date
    no_sys_correction = args.no_sys_correction
    yes = args.yes
    queue = args.queue
    r0_dir = args.r0_dir or args.base_dir / "R0"
    dl1_dir = args.dl1_dir or args.base_dir / "DL1"

    calib_dir = base_dir / PIXEL_DIR_CAT_B

    if shutil.which("srun") is None:
        sys.exit(">>> This script needs a slurm batch system. Stop")

    print(f"\n--> Start to reconstruct runs {run_list}")

    # verify config file
    if not config_file.exists():
        sys.exit(f"Config file {config_file} does not exists. \n")

    print(f"\n--> Config file {config_file}")

    # for old runs or if the data-base is not available
    # it is possible to give the filter list
    if filters_list is not None and len(filters_list) != len(run_list):
        sys.exit("Filter list length must be equal to run list length. Verify \n")

    # loops over runs and send jobs
    filters = None
    for i, run in enumerate(run_list):
        print(f"\n--> Run {run} ")
        if filters_list is not None:
            filters = filters_list[i]

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
        print(f"--> Found {len(input_files)} interleaved subruns in {input_path}")

        if n_subruns:
            print(f"--> Process {n_subruns} subruns")

        # verify output dir
        output_dir = calib_dir / "calibration" / date / prod_id
        if not output_dir.exists():
            print(f"--> Create directory {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        # make log dir
        log_dir = output_dir / "log"
        if not log_dir.exists():
            print(f"--> Create directory {log_dir}")
            log_dir.mkdir(parents=True, exist_ok=True)

        # job file
        now = datetime.now().replace(microsecond=0).isoformat(sep="T")
        job_file = log_dir / f"run_{run}_date_{now}.job"

        with job_file.open(mode="w") as fh:
            fh.write("#!/bin/bash\n")
            fh.write("#SBATCH --job-name=%s.job\n" % run)
            fh.write("#SBATCH --output=log/run_%d_date_%s.out\n" % (run, now))
            fh.write("#SBATCH --error=log/run_%d_date_%s.err\n" % (run, now))
            fh.write("#SBATCH -p %s\n" % queue)
            fh.write("#SBATCH --cpus-per-task=1\n")
            fh.write("#SBATCH --mem-per-cpu=10G\n")
            fh.write("#SBATCH -D %s \n" % output_dir)

            cmd = [
                "srun",
                "lstcam_calib_onsite_create_cat_B_calibration_file",
                f"-r {run}",
                f"-v {prod_id}",
                f"--r0-dir {r0_dir}",
                f"--dl1-dir {dl1_dir}",
                f"-b {base_dir}",
                f"-s {stat_events}",
                f"--config={config_file}",
            ]

            if filters is not None:
                cmd.append(f"--filters={filters}")

            if sys_date is not None:
                cmd.append(f"--sys-date={sys_date}")

            if yes:
                cmd.append("--yes")

            if no_sys_correction:
                cmd.append("--no-sys-correction")

            if n_subruns:
                cmd.append(f"--n-subruns={n_subruns}")

            if args.no_pro_symlink is True:
                cmd.append("--no-pro-symlink")

            cmd.extend(remaining_args)

            # join command together with newline, line continuation and indentation
            fh.write(" \\\n  ".join(cmd))
            fh.write("\n")

        subprocess.run(["sbatch", job_file], check=True)


if __name__ == "__main__":
    main()
