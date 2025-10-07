"""
Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Project information -----------------------------------------------------
import lstcam_calib
from lstcam_calib.onsite import DEFAULT_BASE_PATH, PIXEL_DIR_CAT_A

project = "lstcam_calib"
copyright = "2024, CTA-LST Project"
author = "CTA-LST Project"
version = lstcam_calib.__version__
# The full version, including alpha/beta/rc tags.
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_automodapi.automodapi",
    "sphinxarg.ext",
    "sphinx_design",
    "sphinxcontrib.bibtex",
    "nbsphinx",
    "sphinx.ext.mathjax",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_exec_code",
    "sphinx_changelog",
]

exec_code_working_dir = ".."
exec_code_source_folders = ["."]

# bibtex setup
bibtex_bibfiles = ["user-guide/references.bib"]
bibtex_default_style = "unsrt"
bibtex_reference_style = "label"

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.

exclude_patterns = ["build", "_build", "**.ipynb_checkpoints", "changes"]

# have all links automatically associated with the right domain.
default_role = "py:obj"


# intersphinx allows referencing other packages sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.10", None),
    "ctapipe": ("https://ctapipe.readthedocs.io/en/v0.19.3/", None),
    "traitlets": ("https://traitlets.readthedocs.io/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

numpydoc_show_class_members = False

nitpick_ignore = [
    ("py:class", "StrDict"),
    ("py:class", "ClassesType"),
    ("py:class", "Unicode"),
    ("py:class", "ctapipe.calib.camera.flatfield.FlatFieldCalculator"),
    ("py:class", "ctapipe.calib.camera.pedestals.PedestalCalculator"),
    ("py:class", "traitlets.traitlets.EventHandler"),
    ("py:class", "traitlets.utils.sentinel.Sentinel"),
    ("py:class", "traitlets.utils.sentinel.TraitType"),
    ("py:class", "traitlets.utils.bunch.Bunch"),
    ("py:class", "traitlets.traitlets.TraitType"),
    ("py:obj", "FieldInfo"),
    ("py:obj", "ComputedFieldInfo"),
    ("py:obj", "ConfigDict"),
    ("py:obj", "Model.__fields__"),
    ("py:obj", "inst"),
    ("py:obj", "handler"),
    ("py:obj", "remove"),
    ("py:class", "always"),
    ("py:class", "pathlib.Annotated"),
]

nitpick_ignore_regex = [
    ("py:class", r"pathlib\.Annotated\[.*\]"),
]

# -- Options for HTML output -------------------------------------------------
pages_url = "http://cta-array-elements.gitlab-pages.cta-observatory.org/lst/analysis/lstcam_calib"
html_theme = "pydata_sphinx_theme"
html_theme_options = dict(
    navigation_with_keys=False,
    show_nav_level=2,
    logo=dict(
        image_light="_static/1.MainVersion_CTAOLSTCollaboration_Logo_RGB_cropped.png",
        image_dark="_static/2.ReverseVersion_CTAOLSTCollaboration_Logo_RGB_cropped.png",
        alt_text="CTAO LST Collaboration",
    ),
    switcher=dict(
        json_url=f"{pages_url}/versions.json",  # noqa: E501
        version_match="latest" if ".dev" in version else f"v{version}",
    ),
    navbar_center=["version-switcher", "navbar-nav"],
)


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- import variables in doc ---------------------------------------------------

rst_epilog = f"""
.. |onsite_base_path| replace:: :code:`{DEFAULT_BASE_PATH}`
.. |onsite_catA_path| replace:: :code:`{PIXEL_DIR_CAT_A}`
"""
