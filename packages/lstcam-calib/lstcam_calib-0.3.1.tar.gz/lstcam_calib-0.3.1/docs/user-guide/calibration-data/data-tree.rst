.. _data-tree:

Data-tree
=========
The onsite data-tree is placed in the root directory :

.. exec_code::
    :linenos:


    # --- hide: start ---
    from lstcam_calib.onsite import DEFAULT_BASE_PATH

    print(f"lstcam_calib.onsite.DEFAULT_BASE_PATH = {DEFAULT_BASE_PATH}")
    # --- hide: stop ---

Cat-A calibration files are stored in the sub-directory |onsite_catA_path| :

.. exec_code::
    :linenos:

    # --- hide: start ---

    from lstcam_calib.onsite import PIXEL_DIR_CAT_A, DEFAULT_BASE_PATH
    import subprocess

    print(f"Onsite Cat-A dir = {DEFAULT_BASE_PATH}/{PIXEL_DIR_CAT_A}")
    # --- hide: stop ---

This directory contains the following sub-directories,
each related to specific calibration data:

.. exec_code::
    :linenos:

    # --- hide: start ---
    from doc_utils import tree
    from lstcam_calib.onsite import PIXEL_DIR_CAT_A, DEFAULT_BASE_PATH
    tree(f"test_data/real/{PIXEL_DIR_CAT_A}", level=1, limit_to_directories=True)
    # --- hide: stop ---

Each directory has a sub-directory structure of type ``[date]\[version]\log``, where

    * ``[date]`` corresponds (generally) to the date of the data acquisition.
    * ``[version]`` corresponds to the lstcam_calib version used for the calibration production.
    * The calibration files are placed in the ``[version]`` directory.
    * A software link ``pro`` is pointing to the last ``[version]`` directory produced.
    * In the ``log`` directory are stored the log files with the output messages, the pdf files with the check plots and eventually the automatically produced batch scripts.

Here below you can see the example of the calibration  tree used for the CI tests.

.. exec_code::
    :linenos:

    # --- hide: start ---
    from doc_utils import tree
    from lstcam_calib.onsite import PIXEL_DIR_CAT_A
    tree(f"test_data/real/{PIXEL_DIR_CAT_A}", level=4, limit_to_directories=True)
    # --- hide: stop ---
