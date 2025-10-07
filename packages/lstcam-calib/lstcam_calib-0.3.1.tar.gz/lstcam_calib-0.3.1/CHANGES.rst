lstcam_calib v0.3.0 (2025-07-21)
--------------------------------



Bug Fixes
~~~~~~~~~

- In DB meta-data, the file path of used coefficients must be relative to the root of the data-tree [`!59 <https://gitlab.cta-observatory.org/cta-array-elements/lst/analysis/lstcam_calib/-/merge_requests/59>`__]


New Features
~~~~~~~~~~~~

- Add towncrier to better fill the changelog (see `CTAO DevDoc <http://cta-computing.gitlab-pages.cta-observatory.org/documentation/developer-documentation/languages/python/index.html#changelogL>`_) [`!56 <https://gitlab.cta-observatory.org/cta-array-elements/lst/analysis/lstcam_calib/-/merge_requests/56>`__]

- Change default base-path of the data-tree from /fefs/aswg/data/real to /fefs/onsite/data/lst-pipe/LSTN-01 [`!58 <https://gitlab.cta-observatory.org/cta-array-elements/lst/analysis/lstcam_calib/-/merge_requests/58>`__]

- Onsite scripts do not apply anymore DRS4 corrections and baseline subtraction by default.
  Add options --apply-drs4-corrections and --apply-pedestal-correction to apply them [`!60 <https://gitlab.cta-observatory.org/cta-array-elements/lst/analysis/lstcam_calib/-/merge_requests/60>`__]


Maintenance
~~~~~~~~~~~

- Update the version of ctapipe to ~=0.26.0 for compatibility with cta-lstchain [`!57 <https://gitlab.cta-observatory.org/cta-array-elements/lst/analysis/lstcam_calib/-/merge_requests/57>`__]


lstcam_calib v0.2.0 (2025-04-09)
--------------------------------

New Features
~~~~~~~~~~~~

- Add tool to create time lapse calibration coefficients
- Add CALIBRATION_SERVICE_ID collection in data-base
- Change default output file format from "h5" to "fits.gz"
- Change name of data-tree to */fefs/aswg/data/real/service/PixelCalibration*

lstcam_calib v0.1.1 (2025-02-13)
--------------------------------

Maintenance
~~~~~~~~~~~

- Update ctapipe_io_lst

lstcam_calib v0.1.0.post1 (2024-10-15)
--------------------------------------

Bug Fixes
~~~~~~~~~

- Add fix docs and release deployment (sdist)

lstcam_calib v0.1.0 (2024-10-14)
--------------------------------

New Features
~~~~~~~~~~~~

- Add all Cat-A and Cat-B component classes and tools extracted from cta-lstchain
- Add bookkeeping of calibration files metadata in Mongo database
- Add tools and component classes to interact with Mongo database
