.. _create-calibration-files:

Create Calibration Files
========================

Calibration production is performed at the La Palma IT center by the
:ref:`Onsite Command-Line Tools <onsite-command-line-tools>` that permit to

- correctly retrieve the necessary input data and calibration files
- properly store the results in the calibration data-tree
- bookeep the file metadata in the calibration database.

.. note::
    The address of the metadata database must be set in the environment variable ``LSTCAM_CALIB_DB_URL``
    or given with the option ``--db-url`` (see :ref:`Database <data-base>`)


.. note::
    For offsite processing or tests it is possible to use directly the
    :ref:`Command-Line Tools <command-line-tools>`, which will require to give all the
    input files and output path as arguments.

.. note

List of Calibrations
--------------------

    .. toctree::
        :maxdepth: 1
        :titlesonly:

        drs4-baseline
        drs4-time-lapse
        drs4-time-sampling
        catA-pixel-calibration
        ffactor-systematics
        catB-pixel-calibration
