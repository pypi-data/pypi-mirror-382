lstcam_calib: LST Camera Calibration
====================================
**Date**: |today| **Version**: |version|

Python package to produce and bookkeep calibration coefficients for the pixels of the Larged-size Telescope (LST).

Data are stored in files (fits or hdf5 format), metadata in a Mongo database

.. This includes three main types of calibrations:

.. * **DRS4 corrections** : correction waveform baseline and time due to DRS4 systematic effects.

.. * **Cat-A pixel calibration** : ADC to photoelectron and NSB pedestals estimation, based on offline calibration data

.. * **Cat-B pixel calibration** : offline refinement of Cat-A calibration, based on interleaved calibration data.

.. toctree::
   :maxdepth: 1

   installation
   user-guide/index
   reference/index
   changelog
