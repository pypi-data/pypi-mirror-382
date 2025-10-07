
.. _how-to-baseline:

DRS4 Baseline Correction
========================


Input Data
..........

Events of a run of dark pedestals (acquired with closed camera and random triggers).
These runs are tagged with ``run_type`` DRS4 in the run summary file. By default
minimum number of 20,000 events is required in order to collect enough statistics per
capacitor for the baseline estimation.

How To
......

The file with baseline and spikes' information is produced by the tool :ref:`lstcam_calib_onsite_create_drs4_pedestal_file <onsite-drs4-baseline>`,
which can be run with the simple command:

    lstcam_calib_onsite_create_drs4_pedestal_file -r [run_number]

It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.


Output data
...........

Coefficients are written in a *fit*, *fits.gz* or *hdf5* format depending on the option ``--output-format``.

The data model and format are described below :

    .. toctree::
        :maxdepth: 2

        ../notebooks/read_DRS4_baseline.ipynb
