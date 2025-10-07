.. _how-to-catA-calibration:

Cat-A Pixel Calibration
=======================


Input Data
..........

Events of a run of flat-field and NSB pedestal events (usually taken with a 1 kHz frequency).
These runs are tagged with ``run_type`` PEDCALIB in the run summary file. By default,
a statistics of 10,000 events (per trigger type) is required in order to collect enough
statistics per pixel.


How To
......

The production of *one or many calibration files* is performed using the slurm batch system by the tool
:ref:`lstcam_calib_onsite_create_calibration_files_with_batch <onsite-pixel-calibration-with-batch>` with the simple command:

    lstcam_calib_onsite_create_calibration_files_with_batch -r [run_number_list]

In the case of one single run, the calibration coefficients can be produced interactively by the tool :ref:`onsite_create_calibration_file <onsite-pixel-calibration>`,
which can be run with the simple command:

    lstcam_calib_onsite_create_calibration_file -r [run_number]


It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.

Output data
...........

Coefficients are written in a *fit*, *fits.gz* or *hdf5* format depending on the option ``--output-format``.

The data model and format are described below :

    .. toctree::
        :maxdepth: 2

        ../notebooks/read_catA_pixel_calibration.ipynb
