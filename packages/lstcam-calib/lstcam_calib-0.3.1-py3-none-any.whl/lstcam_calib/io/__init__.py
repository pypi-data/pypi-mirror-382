"""I/O functions."""
from contextlib import ExitStack

import tables

OUTPUT_FORMATS = ["fits.gz", "fits", "h5"]

PROV_INPUT_ROLES = {"fit_intensity_scan": "catA.r1.mon.tel.camera.intensity_scan"}

PROV_OUTPUT_ROLES = {
    "create_calibration_file": "catA.r1.mon.tel.camera.calibration",
    "create_drs4_pedestal_file": "catA.r0.mon.tel.camera.drs4_baseline",
    "create_drs4_time_file": "catA.r0.mon.tel.camera.drs4_time",
    "fit_intensity_scan": "catA.r0.mon.tel.camera.ffactor_systematics",
    "create_cat_b_calibration_file": "catB.r1.mon.tel.camera.calibration",
}


__all__ = ["get_dataset_keys"]


def get_dataset_keys(h5file):
    """
    Return a list of all dataset keys in a HDF5 file.

    Parameters
    ----------
    filename: str - path to the HDF5 file

    Returns
    -------
    list of keys
    """
    # we use exit_stack to make sure we close the h5file again if it
    # was not an already open tables.File
    exit_stack = ExitStack()

    with exit_stack:
        if not isinstance(h5file, tables.File):
            h5file = exit_stack.enter_context(tables.open_file(h5file, "r"))

        dataset_keys = [node._v_pathname for node in h5file.walk_nodes("/", "Table")]

    return dataset_keys
