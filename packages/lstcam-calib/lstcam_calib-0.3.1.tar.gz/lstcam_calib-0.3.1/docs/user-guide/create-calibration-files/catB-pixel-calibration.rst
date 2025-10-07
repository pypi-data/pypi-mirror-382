.. _how-to-catB-calibration:

Cat-B Pixel Calibration
=======================


Input Data
..........

Interleaved flat-field and NSB pedestal events continuously acquired during the night at a frequency of 100 Hz.
The waveform of these events is stored by *lstchain* in *hdf5* files in the onsite directory

``/fefs/aswg/data/real/DL1/[date]/[lstchain_version]/interleaved``,

A statistics of 2,500 events (per trigger type) is required in order to collect enough
statistics per pixel and to guarantee a fast update of the interleaved calibration.


How To
......

The production of *one or many calibration files* is performed using the slurm batch system by the tool
:ref:`lstcam_onsite_create_cat_b_calibration_files_with_batch <onsite-pixel-cat-b--calibration-with-batch>` with the simple command:

    lstcam_calib_onsite_create_cat_b_calibration_files_with_batch -r [run_number_list]

In the case of one single run, the calibration coefficients can be produced interactively by the tool :ref:`onsite_create_calibration_file <onsite-pixel-calibration>`,
which can be run with the simple command:

    lstcam_calib_onsite_create_cat_b_calibration_file -r [run_number]


It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.

Output data
...........

Coefficients are written in a  *hdf5* format .

The data model and format is the same of Cat-A file:

    .. toctree::
        :maxdepth: 2

        ../notebooks/read_catA_pixel_calibration.ipynb
