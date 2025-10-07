"""Onsite script to create a F-factor systematic correction file by fitting an intensity scan."""
#!/usr//bin/env python

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

import lstcam_calib
from lstcam_calib.io.database import CalibrationDB, CalibrationType
from lstcam_calib.onsite import (
    DEFAULT_BASE_PATH,
    PIXEL_DIR_CAT_A,
    create_pro_symlink,
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

required.add_argument("-d", "--date", help="Date of the scan (YYYYMMDD)", required=True)

# config file is mandatory because it contains the list of input runs
required.add_argument(
    "-c",
    "--config",
    type=Path,
    help="Config file (yaml format) with the list of runs",
    required=True,
)

version = lstcam_calib.__version__
optional.add_argument(
    "-v", "--prod-version", help="Version of the production", default=f"v{version}"
)
optional.add_argument(
    "-b",
    "--base-dir",
    help="Root dir for the output directory tree",
    type=Path,
    default=DEFAULT_BASE_PATH,
)
optional.add_argument("--sub-run", help="sub-run to be processed.", type=int, default=0)
optional.add_argument(
    "--input-prefix", help="Prefix of the input file names", default="calibration"
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
parser.add_argument(
    "--no-db",
    action="store_true",
    help="Do not write metadata in TCU data-base",
)
optional.add_argument(
    "--db-url",
    help="Connection to calibration data_base.",
)

optional.add_argument("--db-name", help="Name of mongo calibration db.")


def main():
    """Run filter scan fit tool and write files in calibration data tree."""
    args, remaining_args = parser.parse_known_args()
    date = args.date
    prod_id = args.prod_version
    base_dir = args.base_dir
    sub_run = args.sub_run
    config_file = args.config
    prefix = args.input_prefix
    yes = args.yes
    pro_symlink = not args.no_pro_symlink
    calib_dir = base_dir / PIXEL_DIR_CAT_A

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

    # verify config file
    if not config_file.exists():
        raise OSError(f"Config file {config_file} does not exists.")

    print(f"\n--> Config file {config_file}")

    # verify output dir
    output_dir = calib_dir / "ffactor_systematics" / date / prod_id
    if not output_dir.exists():
        print(f"--> Create directory {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    if pro_symlink:
        pro = "pro"
        create_pro_symlink(output_dir)
    else:
        pro = prod_id

    # verify input dir
    input_dir = calib_dir / "calibration" / date / pro
    if not input_dir.exists():
        raise OSError(f"Input directory {input_dir} not found")

    print(f"\n--> Input directory {input_dir}")

    # make log dir
    log_dir = output_dir / "log"
    if not log_dir.exists():
        print(f"--> Create directory {log_dir}")
        log_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now().replace(microsecond=0).isoformat(sep="T")

    # define output file names
    output_file = output_dir / f"scan_fit_{date}.{sub_run:04d}.h5"
    log_file = log_dir / f"scan_fit_{date}.{sub_run:04d}_{now}.log"
    plot_file = log_dir / f"scan_fit_{date}.{sub_run:04d}.pdf"
    provenance_file = log_dir / f"scan_fit_{date}.{sub_run:04d}_{now}.provenance.log"

    if output_file.exists():
        remove = False

        if not yes and os.getenv("SLURM_JOB_ID") is None:
            remove = query_yes_no(
                ">>> Output file exists already. Do you want to remove it?"
            )

        if yes or remove:
            # remove from DB if used
            if db is not None:
                db.remove_file(CalibrationType.FFACTOR_SYSTEMATICS, output_file)

            os.remove(output_file)

        else:
            print("\n--> Output file exists already. Stop")
            exit(1)

    print(f"\n--> Plot file {plot_file}")
    print(f"\n--> Log file {log_file}")

    #
    # produce intensity scan fit file
    #

    cmd = [
        "lstcam_calib_create_fit_intensity_scan_file",
        f"--config={config_file}",
        f"--input-dir={input_dir}",
        f"--output-path={output_file}",
        f"--plot-path={plot_file}",
        f"--sub-run={sub_run}",
        f"--input-prefix={prefix}",
        f"--log-file={log_file}",
        f"--provenance-log={provenance_file}",
        "--log-file-level=DEBUG",
        *remaining_args,
    ]

    print(f"\n--> PRODUCING SYSTEMATICS CORRECTION DATA in {output_file}")
    subprocess.run(cmd, check=True)

    # store meta-data in data-base (paths relative to base_dir)
    if db is not None:
        db.add_ffactor_systematics_file(
            path=output_file,
            provenance_path=provenance_file,
        )
        print("\n--> meta-data written in db")

    print("\n--> END")


if __name__ == "__main__":
    main()
