"""
Configuration file for the Sphinx documentation builder.

This module contains all the configuration settings for building the Quantify
documentation using Sphinx, including project information, extensions, theme settings,
and intersphinx mappings.
"""

import os
import re
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# add project root (quantify/) to sys.path so autodoc can find your modules
package_path = os.path.abspath("..")
sys.path.insert(0, package_path)

import quantify  # noqa: E402

release = quantify.__version__  # type: ignore
version = release.split("+", 1)[0]

# -- Project information -----------------------------------------------------

project = "Quantify"
author = "Quantify Consortium"
copyright = f"{datetime.now().year}, Qblox & Orange Quantum Systems"

# -- General configuration ---------------------------------------------------

# allow both .rst and .md source files
source_suffix = {".rst": "restructuredtext", ".md": "restructuredtext"}

# The master toctree document.
master_doc = "index"

# Sphinx extensions
extensions = [
    # "myst_parser",
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "myst_nb",
    "sphinx.ext.autodoc",  # auto document docstrings
    "sphinx.ext.napoleon",  # autodoc understands numpy docstrings
    # load after napoleon, improved compatibility with type hints annotations
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx-jsonschema",
    "sphinx.ext.mathjax",
    "sphinx_togglebutton",
    "jupyter_sphinx",
    # fancy type hints in docs and
    # solves the same issue as "sphinx_automodapi.smart_resolver"
    # however the smart_resolver seems to fail for external packages like `zhinst`
    "scanpydoc.elegant_typehints",
    "sphinxcontrib.bibtex",
    # documents parameters that are defined in the __init__ of `Instrument`s as
    # instance attributes
    "qcodes.sphinx_extensions.parse_parameter_attr",
    "sphinx_design",
    "autoapi.extension",
]

# automatically link section references
autosectionlabel_prefix_document = False

# paths that contain templates
templates_path = ["_templates"]

# patterns to ignore
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for autodoc -----------------------------------------------------

# show members in group order (init, methods, attributes)
autodoc_member_order = "groupwise"

# show type hints in the description
autodoc_typehints = "description"

autodoc_default_options = {
    # Ignore any __all__ that might be added accidentally by inexperienced developers
    # This is done to avoid nasty complications with sphinx and its extensions and
    # plenty of "reference target not found" warnings.
    # See also qualname_overrides above, which has to be used for external packages.
    "ignore-module-all": True,
    "member-order": "groupwise",
}

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_logo = "https://quantify-os.gitlab.io/_static/img/quantify_logo.svg"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_favicon = "images/QUANTIFY-FAVICON_16.png"
htmlhelp_basename = "quantifydoc"
html_context = {
    "display_gitlab": True,
    "gitlab_user": "quantify-os",
    "gitlab_repo": "quantify",
    "gitlab_version": "main/docs/",
}


html_theme_options = {
    "logo": {
        "link": "https://quantify-os.gitlab.io/quantify/",
        "image_light": "images/QUANTIFY_LANDSCAPE.svg",
        "image_dark": "images/QUANTIFY_LANDSCAPE_DM.svg",
    },
    "navbar_end": ["theme-switcher", "navbar-icon-links.html"],
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.com/quantify-os/quantify",
            "icon": "fab fa-gitlab",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/quantify",
            "icon": "fab fa-python",
        },
    ],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "header_links_before_dropdown": 6,
    "navbar_align": "left",
}

# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "lmfit": ("https://lmfit.github.io/lmfit-py/", None),
    "qcodes": ("https://microsoft.github.io/Qcodes/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "dateutil": ("https://dateutil.readthedocs.io/en/stable/", None),
    "uncertainties": (
        "https://uncertainties.readthedocs.io/en/latest/",
        None,
    ),
    "IPython": ("https://ipython.readthedocs.io/en/stable/", None),
}

# -- myst-parser -------------------------------------------------------------

# required to use sphinx_design in combination with myst
myst_enable_extensions = [
    "dollarmath",
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "substitution",
    "attrs_block",
    "amsmath",
    "linkify",
]
myst_heading_anchors = 3


# -- auto-api ----------------------------------------------------------------

# required for autoapi to use the same template
autoapi_template_dir = "_templates"
# see https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html

autoapi_type = "python"
autoapi_generate_api_docs = True
autoapi_dirs = ["../../quantify"]
ignore_module_all = True
autoapi_add_toctree_entry = False
autoapi_options = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
# displays docstrings inside __init__
autoapi_python_class_content = "class"
autoapi_keep_files = False


# -- bibtex ------------------------------------------------------------------

bibtex_bibfiles = ["refs.bib"]
bibtex_reference_style = "author_year"

# Configure pydata-sphinx-theme version switcher based on detected CI environment
# variables.
if (git_tag := os.environ.get("CI_COMMIT_TAG")) is not None and re.match(
    r"^v([0-9]+)\.([0-9]+)\.([0-9]+)((rc|a|b)([0-9]+))?$", git_tag
):
    switcher_version = git_tag
elif (
    (branch := os.environ.get("CI_COMMIT_BRANCH"))
    and (default_branch := os.environ.get("CI_DEFAULT_BRANCH"))
    and branch == default_branch
):
    switcher_version = "dev"
else:
    switcher_version = None

if switcher_version is not None:
    html_theme_options["switcher"] = {
        "json_url": "https://quantify-os.org/docs/quantify/switcher.json",
        "version_match": switcher_version,
    }
    html_theme_options["navbar_center"] = ["version-switcher", "navbar-nav"]
