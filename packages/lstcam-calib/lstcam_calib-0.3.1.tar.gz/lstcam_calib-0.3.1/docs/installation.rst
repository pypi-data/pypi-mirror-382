Installation
============

User Installation
-----------------

``lstcam-calib`` is on PyPI, install using:

.. code:: text

   $ pip install lstcam-calib


Developer Setup
---------------

This repository stores test data using `git LFS <https://git-lfs.com/>`_.

Install it using your package manager or by downloading from the website.

Then run:

.. code:: text

    $ git lfs install

This is only required once per machine / user.

If you cloned the repository before setting up git LFS correctly, you need to run

.. code-block:: shell

   $ git lfs pull

in the cloned repository after installing git LFS.

Using conda
^^^^^^^^^^^

Using the `miniforge3 <https://github.com/conda-forge/miniforge?tab=readme-ov-file#miniforge3>`_ distribution and ``mamba`` is recommended.

Clone the repository, create the conda environment, then install the package in development mode:

.. code-block:: shell

   $ git clone git@gitlab.cta-observatory.org:cta-array-elements/lst/analysis/lstcam_calib
   $ cd lstcam_calib
   $ mamba env create -f environment-dev.yaml
   $ mamba activate lstcam-calib-dev
   $ pip install -e '.[all]'

Using virtual environments
^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you have at least python 3.10, you can use `pyenv <https://github.com/pyenv/pyenv>`_ to install and use specific python versions.

As a developer, clone the repository, create a virtual environment
and then install the package in development mode:

.. code-block:: shell

   $ git clone git@gitlab.cta-observatory.org:cta-array-elements/lst/analysis/lstcam_calib
   $ cd lstcam_calib
   $ python -m venv venv
   $ source venv/bin/activate
   $ pip install -e '.[all]'

The same also works with conda, create and activate a conda env instead of a venv above.
