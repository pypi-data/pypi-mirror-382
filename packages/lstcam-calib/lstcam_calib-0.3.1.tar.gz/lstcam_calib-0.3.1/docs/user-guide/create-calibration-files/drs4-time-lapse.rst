
.. _how-to-time-lapse:

DRS4 Time Lapse Correction
==========================

Input Data
..........

Events of a run of dark pedestals (acquired with closed camera and random triggers).
These runs are tagged with ``run_type`` DRS4 in the run summary file.

How To
......

The time lapse file is produced by the tool :ref:`lstcam_calib_onsite_create_drs4_timelapse_file <onsite-drs4-timelapse>`,
which can be run with the simple command:

    onsite_create_drs4_timelapse_file -r [run_number]


It is possible to write data in a not official data-tree with the option  ``-b [data-tree-root]``.

The script runs successively three tools:
    * :ref:`lstcam_calib_extract_drs4_timelapse_data <extract-drs4-timelapse-data>` : extracts baseline versus timelapse per capacitors
    * :ref:`lstcam_calib_aggregate_drs4_timelapse <aggregate-drs4-time-lapse-data>` : aggregates data to be fitted
    * :ref:`lstcam_calib_drs4_timelapse <drs4-timelapse>` : fits timelapse coefficients and output the final coefficients

It is possible to run only some of the tools setting specific input cards.
Presently, the time lapse coefficients are estimated per DRS4 batch type.


Output data
...........

The script outputs intermediate files in h5 format (*drs4_timelapse_histo.Run[run].[subrun].h5*, *drs4_timelapse_data.Run[run].[subrun].h5*).
The final coefficient file (*drs4_timelapse.Run[run].[subrun].h5*) is written in a *fit*, *fits.gz* or *hdf5* format depending on the option ``--output-format``.

The data model and format are described below :

.. toctree::
        :maxdepth: 2

        ../notebooks/read_DRS4_time_lapse.ipynb
