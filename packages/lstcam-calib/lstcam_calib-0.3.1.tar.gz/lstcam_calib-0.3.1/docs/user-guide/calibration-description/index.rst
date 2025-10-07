.. _calibration_description:

Calibration Description
=======================

Introduction
------------

LST-1 PMT signals are :
   * amplified in two gain channels : High Gain  ~ 17 x Low Gain
   * buffered in 4096 capacitors per channel: 4 DRS4 rings of 1024 capacitors
   * read at 1 GHz: 40 capacitors/pixel per trigger and per channel

Hence, one raw (R0) waveform corresponds to 40 samples of 1 ns per channel for each channel.

**The R0 waveform must be :**

 1. corrected by several DRS4 systematics effects :cite:`2013NIMPA.723..109S`-:cite:`LowLevelCor`
 2. calibrated to photo-electron counts and flat-fielded in charge and time :cite:`Kobayashi:2021jc`.

We distinguish two categories of coefficients :
   1. **Cat-A coefficients** : are provided to the EventBuilder to correct and calibrate the R0 waverform in order to upgrade to R1 level
   2. **Cat-B coefficients** : are produced offline using interleaved calibration events and used by the offline code to improve the Cat-A calibration

**The target of this package is the production and bookkeeping of LST Cat-A pixel calibration data.**
It includes however also some preliminary tools for performing Cat-B calibrations, which will be in future provided by the DPPS system of CTAO.

Calibration coefficients are :
   1. Produced by command-line tools on the base of calibration data (flat-field and pedestal events)
   2. Stored in files (fits or hdf5 format) inside a structured data-tree
   3. Bookkept in a Mongo database, through the use of well targeted meta-data.

In the following sections we describe all types of corrections/calibrations
and how to produce and bookkeep them.


    .. toctree::
        :maxdepth: 1
        :titlesonly:

        input-data
        drs4-corrections
        pixel-calibration
