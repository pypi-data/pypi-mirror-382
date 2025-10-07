.. _data-base:

Database
========

The calibration database is hosted by the **TCU Mongo server**. All input/output actions must be
performed by specific onsite tools, through the functions of the :ref:`database <database-input-output>`
module (for more details see :ref:`Change Database Documents <act-on-database>`).

The address of the calibration data-base is automatically retrieved by the environment
variable ``LSTCAM_CALIB_DB_URL`` (if set) or it must be given with the option ``--db-url`` (the url name is with the format mongodb://x.y.z.k:w)

It is possible to disable the writing of the meta-data in the database with the option ``--no-db``

Meta-data are stored in **several collections**, one for each  ``CalibrationType`` :

    .. autoclass:: lstcam_calib.io.database.CalibrationType
        :members:
        :no-index:


Each document contains a set of fields that are common to all ``CalibrationType`` :

    * :class:`~lstcam_calib.io.database.CommonFields`


Then, each ``CalibrationType`` has its own specific fields, collected in the following classes :

    * :class:`~lstcam_calib.io.database.DRS4BaselineFile`
    * :class:`~lstcam_calib.io.database.DRS4TimeSamplingFile`
    * :class:`~lstcam_calib.io.database.CalibrationFile`
    * :class:`~lstcam_calib.io.database.FFactorSystematicsFile`

Finally, the last document of the collection ``CALIBRATION_SERVICE_ID`` contains the
path of the calibration files to be used in real time and the value of the
``calibration_service_id`` to insert in the R1 ``CameraConfiguration`` field :

    * :class:`~lstcam_calib.io.database.CalibrationServiceId`
