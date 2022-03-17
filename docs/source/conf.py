# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from pathlib import Path
from textwrap import indent

from ruamel.yaml import YAML

from matflow._version import __version__

# -- Project information -----------------------------------------------------

project = "MatFlow"
copyright = "2022, MatFlow developers"
author = "MatFlow developers"

# The full version, including alpha/beta/rc tags
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_jinja",
    "sphinx_copybutton",
]

autodoc_typehints = "description"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "logo_link": "https://matflow.io",
    "github_url": "https://github.com/hpcflow/matflow-new",
    "external_links": [],
    "switcher": {
        "json_url": "https://matflow.io/docs/switcher.json",
        "url_template": "https://matflow.io/docs/v{version}/",
        "version_match": __version__,
    },
    "navbar_end": ["version-switcher", "navbar-icon-links.html"],
    "use_edit_page_button": True,
}

html_context = {
    "github_user": "hpcflow",
    "github_repo": "matflow-new",
    "github_version": "develop",
    "doc_path": "docs/source",
}
html_logo = "_static/images/logo-50dpi.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["css/custom.css"]

text_newlines = "unix"

# Get just-released binaries:
yaml = YAML()
with Path("released_binaries.yml") as fh:
    bins_dat = yaml.load(fh)

# Generate install/index.rst file programmatically, including binary download links:

EXE_PLAT_LOOKUP = {"win.exe": "Windows", "macOS": "macOS", "linux": "Linux"}

get_links_table = (
    '<table class="binary-downloads-table">\n'
    + indent(
        text="\n".join(
            f'<tr><td>{EXE_PLAT_LOOKUP[exe_name.split("-")[-1]]}</td><td><a href="{link}">{exe_name}</a></td></tr>'
            for exe_name, link in sorted(bins_dat.items())
        ),
        prefix="  ",
    )
    + "\n</table>"
)

install_index = f"""
:orphan:

.. _install:

############
Installation
############

There are two methods to using MatFlow: via a binary executable file or via a Python package. 
Both methods allow the design and execution of workflows. If you want to use MatFlow on a 
cluster, using the binary executable file is recommended. If you want to design and explore
your workflows using the Python API, then you need the Python package. You can use both simultaneously if you wish!

********************************
Download binaries (v{release})
********************************

Release notes: `on GitHub <https://github.com/hpcflow/matflow-new/releases/tag/v{release}>`_

Click below to download the MatFlow binary for your platform (other binary releases are available by using the version switcher in the top-right corner):

.. raw:: html

{indent(get_links_table, '   ')}

**************************
Install the Python package
**************************

Use pip to install the Python package from PyPI::

  pip install matflow=={release}

"""
with Path("install/index.rst").open("w", newline="\n") as fh:
    fh.write(install_index)
