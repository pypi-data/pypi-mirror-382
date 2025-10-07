.. _pixel-calibration:

Pixel Calibration
=================

.. _pixel calibration:

After the correction of DRS4 systematic effects, the R0 waveform must be converted
from units in ADC to units in number of photo-electrons (pe) :

.. math::
   \mathrm{waveform_{pe}} = (\mathrm{waveform_{ADC}} - pedestal_{ADC}) \times dc\_to\_pe
   :label: calib

This step is generally
called \`Cat-A pixel calibration\` or \`DC to pe\`` conversion. In LST the estimation
of the calibration coefficients is performed offline
with so called \`F-factor\` (or \`photon statistics\`) method :cite:`BENCHEIKH1992349`, which
permits to estimate the coefficients *dc_to_pe* in eq. :eq:`calib`.
This method is however affected by some systematic deviations  that must be estimated and
corrected. In the next sections we briefly describe the methods, see :cite:`Kobayashi:2021jc` for more details.

F-factor method
...............

   This method permits to estimate the effective gain of the pixels, defined as *gain = 1/ dc_to_pe*.
   It makes use of the statistical correlation between the charge dispersion of a signal
   and the number of photo-electrons (:math:`{N_{pe}}`) originally produced by the light
   in the photo-cathode.

   In fact, in the case of an ideal poissonian detector, the integrated charge :math:`{Q}`
   produced by an incident light pulse on a PMT and its standard deviation, :math:`{\sigma_{Q}}` (when repeated several times)
   are related to the *gain* (*g*) by the following simple relations:


   .. math::
      \begin{eqnarray}
         Q  & = & g & \; \cdot & N_{pe} \\
         \sigma_{Q} & = & g & \; \cdot & \sqrt{N_{pe}}
      \end{eqnarray}
      :label: idealdet

   which permits to estimate the gain as

   .. math::
      \begin{eqnarray}
         g  & = & \frac{\sigma_{Q}^{2}}{Q}
      \end{eqnarray}
      :label: idealgain

   For a real detector the relation is more complicated due to added noise components.
   In particular, for LST, where :math:`{Q}` is produced by flat-field events, the
   variance :math:`{\sigma_{Q}^2}` is given by:

   .. math::
      \begin{eqnarray}
         \sigma_{Q}^2 = \sigma_{Q_{ped}}^2 + F^{2} g (Q-Q_{ped}) + B^2 (Q-Q_{ped})^2
      \end{eqnarray}
      :label: lst_variance

   where :math:`Q_{ped}` is the pedestal charge, :math:`\sigma_{Q_{ped}}^2` is its variance,
   :math:`F = \sqrt{1 + \sigma_{spe}}` is called \`excess noise factor\`
   and depends on :math:`\sigma_{spe}`, which is the single photon electron width in pe, *B* is
   a quadratic noise term due to the DRS4 time sampling irregularity and the intrinsic
   pulse light dispersion of the laser (see :cite:`Kobayashi:2021jc` for more details).
   Hence, the formula used to estimate the gain in LST is :

   .. math::
      \begin{eqnarray}
         g  & = & \frac{\sigma_{Q}^{2}-\sigma_{ped}^{2}}{Q-Q_{ped}} \frac{1}{F^2} - \frac{B^2}{F^2} (Q-Q_{ped})
      \end{eqnarray}
      :label: lst_gain

   In short:
      * Input data :  flat-field and NSB pedestal events
      * Correction applied by : EventBuilder
      * Coefficient production : see :ref:`How to <how-to-catA-calibration>`


F-factor systematics correction
...............................

   The systematic term B in eq. :eq:`lst_variance` is estimated, per pixel, by the fit of the
   charge variance of an intensity scan obtained by changing the Calibox filters in front of the laser.

   .. figure:: ../figures/FFactor_corrections.png
      :scale: 60 %
      :alt: FFactor systematics

      Example of intensity scan fit, based on eq. :eq:`lst_variance`, for both channels of one pixel.


   In short:
      * Input data :  flat-field and NSB pedestal events from an intensity scan
      * Correction applied by : lscam_calib
      * Coefficient production : see :ref:`How to <how-to-ffactor-systematics>`


Cat-B pixel calibration
.......................

   This calibration is performed in order to improve the Cat-A calibration (based on fixed coefficients for the full night)
   with a continuous estimation of the camera gain during the night based on interleaved calibration events.
   In this case, the F-factor method is applied to calibrated waveforms, the estimated Cat-B gain is then relative
   to the Cat-A gain. Therefore, if no changes are present during the night, the Cat-B gain is expected to be
   one. In general, smooth changes of less then 2% are observed.

   .. figure:: ../figures/Cat_B_gain.png
      :scale: 60 %
      :alt: Cat-B gain

      Example of Cat-B gain estimation for some runs of a night.


   In short:
      * Input data :  interleaved (calibrated) flat-field and NSB pedestals events
      * Correction applied by : lscam_calib
      * Coefficient production : see :ref:`How to <how-to-catB-calibration>`
