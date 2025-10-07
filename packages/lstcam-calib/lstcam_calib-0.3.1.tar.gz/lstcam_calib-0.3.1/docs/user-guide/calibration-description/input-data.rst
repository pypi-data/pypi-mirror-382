.. _input-data:

Input Data
==========

DRS4 corrections and pixel calibrations are based on:

**Flat-field (FF) events** :
   Events produced by the Calibox :cite:`Palatiello:2019HK`, which uniformly
   illuminates the camera with the diffused light of a laser (𝜆 = 355 nm).
   Two filters in front of the laser permit to modulate the signal from 1
   pe till the LG channel saturation. Standard FF events signal correspond
   to ~80 pe/pixel (filters 52). Cat-A calibration event statistical values (as
   median charge or charge standard deviation, see :ref:`Pixel Calibration <pixel-calibration>`) are in general extracted from
   samples of 10,000 events.

**Pedestal events** :
   Events triggered without signal. We distinguish two types of pedestal events:

   * *Dark pedestals*: events from random triggers, taken with closed camera for DRS4 corrections
   * *NSB pedestals*: events from fixted frequency triggers, taken with open camera for evaluating NSB pedestals and dc_to_pe calibration.
