.. _drs4-corrections:

DRS4 Corrections
================

There are several types of DRS4 corrections, mostly of them are performed by the EventBuilder.
We present here a short description, see references  :cite:`2013NIMPA.723..109S`-:cite:`LowLevelCor` for more details.

Baseline correction
...................
   Each capacitor has a different baseline that must be aligned to a common offset
   by subtracting a proper ADC shift.

   .. figure:: ../figures/DRS4_baseline.png
      :scale: 50 %
      :alt: DRS4 baseline correction

      Example of baseline counts of individual capacitors for a single pixel :cite:`LowLevelCor`

   In short:
      * Input data :  dark pedestal events
      * Correction applied by : EventBuilder
      * Coefficient production: see :ref:`How to <how-to-baseline>`

Time-lapse correction
.....................
   The baseline of each capacitor depends on the delay from the time of last reading.
   This is a systematic time shift that must subtracted.

   .. figure:: ../figures/DRS4_time_lapse.png
      :scale: 40 %
      :alt: DRS4 time lapse correction

      Baseline of capacitors as function of the elapsed time from last reading (dt),
      before (left) and after time-lapse correction (right).

   * Input data :  dark pedestal events
   * Correction applied by : EventBuilder
   * Coefficient production: see :ref:`How to <how-to-time-lapse>`

Spikes correction
.................
   R0 waveform presents predictable spikes with maximum height of ~50 ADC that must be subtracted.

   .. figure:: ../figures/DRS4_spikes.png
      :scale: 80 %
      :alt: DRS4 spikes

      Example of waveform with spike and after correction.

   In short:
      * Input data :  dark pedestal events
      * Correction applied by : EventBuilder
      * Coefficient production: see :ref:`How to <how-to-baseline>`

Time sampling correction
........................
   The arrival time of a waveform depends (systematically)on the position of the readout window in the DRS4 capacitor ring.

   .. figure:: ../figures/DRS4_time_sampling.png
      :scale: 22 %
      :alt: DRS4 time sampling

      Example of time shift (in ns) as function of the capacitor number for a given pixel.

   In short:
      * Input data :  flat-field events
      * Correction applied by : to be defined
      * Coefficient production: see :ref:`How to <how-to-time-sampling>`
