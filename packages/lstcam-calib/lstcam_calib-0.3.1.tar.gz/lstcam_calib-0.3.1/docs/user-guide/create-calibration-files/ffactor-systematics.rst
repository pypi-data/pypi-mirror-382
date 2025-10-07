
.. _how-to-ffactor-systematics:

F-Factor systematics Correction
===============================


Input Data
..........
Flat-field and NSB pedestal events (usually taken with a 1 kHz frequency) from
an intensity scan obtained changing the filters in front of the
Calibox laser. Each run corresponds to a different flat-field intensity.
These runs are tagged with ``run_type`` PEDCALIB in the run summary file. By default,
a statistics of 10,000 events (per trigger type) is required in order to collect enough
statistics per pixel.


How To
......

F-factor systematics corrections are obtained with two steps:
    1. All PEDCALIB runs from the filter scan are reconstructed as normal calibration runs with the tools used for the :ref:`pixel calibration <how-to-catA-calibration>`
    (in particular :ref:`lstcam_calib_onsite_create_calibration_files_with_batch <onsite-pixel-calibration-with-batch>`)

    2. The fit of the signal intensity per gain and per pixel is performed with the tool :ref:`lstcam_calib_onsite_create_fit_intensity_scan_file <onsite-fit-intensity-scan>`,
    which can be run with the simple command:

        lstcam_calib_onsite_create_fit_intensity_scan_file -d [date] --config [config_file]

    where :
        * [date] is the date of scan
        * [config_file] must include the list of runs as follow as in this :ref:`example of configuration file <intensity-fit-config>`:):

It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.


Output data
...........

Coefficients are written in a *fit*, *fits.gz* or *hdf5* format depending on the option ``--output-format``.

The data model and format are described below :

    .. toctree::
        :maxdepth: 2

        ../notebooks/read_ffactor_systematics.ipynb
