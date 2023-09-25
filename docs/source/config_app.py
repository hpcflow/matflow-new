# Configuration file for the Sphinx documentation builder -- App specific content

# -------- app-specific content START ----------------------------------------------------

from matflow import __version__
from matflow import app

project = "MatFlow"
copyright = "2023, MatFlow developers"
author = "MatFlow developers"
release = __version__

github_user = "hpcflow"
github_repo = "matflow-new"
PyPI_project = "matflow-new"

switcher_JSON_URL = "https://docs.matflow.io/switcher.json"

html_logo = "_static/images/logo-50dpi.png"

additional_intersphinx = {"hpcflow": ("https://hpcflow.github.io/docs/stable", None)}

# -------- app-specific content END ------------------------------------------------------

