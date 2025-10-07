
.. _how-to-time-sampling:

DRS4 Time Sampling Correction
=============================

This correction is applied to the pixel pulse time by lstchain at present and (probably) by DPPS in future (TBD).

Input Data
..........

Events of a run of flat-field and NSB pedestal events.
These runs are tagged with ``run_type`` PEDCALIB in the run summary file. By default
minimum number of 20,000 events is required in order to collect enough statistics per
pixel.

How To
......

The file time lapse inform is produced by the tool :ref:`lstcam_calib_onsite_create_drs4_time_file <onsite-drs4-time-sampling>`,
which can be run with the simple command:

    lstcam_calib_onsite_create_drs4_time_file -r [run_number]

It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.


Output data
...........

The time correction as function of capacitors is described by a Fourier series.
Coefficients are written in a *fit*, *fits.gz* or *hdf5* format depending on the option ``--output-format``.

The models of the output file are the following :

    .. toctree::
        :maxdepth: 2

        ../notebooks/read_DRS4_time_sampling.ipynb
