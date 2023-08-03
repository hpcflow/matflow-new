# Configuration file for the Sphinx documentation builder.

import copy
from pathlib import Path
import tempfile
from typing import Type

from ruamel.yaml import YAML
import tomlkit
from valida.datapath import DataPath, MapValue
from valida.schema import write_tree_html

from hpcflow.sdk.config.callbacks import callback_vars as config_callback_vars


def get_classmethods(cls: Type):
    """Get a list of class methods of a given class."""
    return sorted(
        [
            k
            for k, v in cls.__dict__.items()
            if callable(getattr(cls, k))
            and not k.startswith("_")
            and isinstance(v, classmethod)
        ]
    )


def _write_valida_tree_html(
    schema,
    path,
    from_path=None,
    anchor_root=None,
    heading_start_level=1,
    show_root_heading=True,
):
    tree = schema.to_tree(nested=True, from_path=from_path)
    path = Path(path).resolve()
    with path.open(mode="wt", encoding="utf-8") as fp:
        fp.write(
            write_tree_html(
                tree,
                anchor_root=anchor_root,
                heading_start_level=heading_start_level,
                show_root_heading=show_root_heading,
            )
        )
    return path


def generate_download_links_table():
    """Generate install/index.rst file programmatically, including binary download links."""
    EXE_PLAT_LOOKUP = {
        "win.exe": "Windows executable",
        "macOS": "macOS executable",
        "linux": "Linux executable",
        "win-dir.zip": "Windows folder",
        "linux-dir.zip": "Linux folder",
        "macOS-dir.zip": "macOS folder",
    }

    # Get just-released binaries:
    yaml = YAML()
    with Path("released_binaries.yml") as fh:
        bins_dat = yaml.load(fh)

    links_table = (
        '<table class="binary-downloads-table">'
        + "".join(
            f'<tr><td>{EXE_PLAT_LOOKUP["-".join(exe_name.split("-")[2:])]}</td><td><a href="{link}">{exe_name}</a></td></tr>'
            for exe_name, link in sorted(bins_dat.items())
        )
        + "</table>"
    )
    return links_table


def expose_variables(app):
    """Expose some variables' reprs as string variables to be used in the docs.

    See: https://stackoverflow.com/a/69211912/5042280

    """

    app_name = app.name
    variables_to_export = ["app", "app_name"]
    frozen_locals = dict(locals())
    rst_epilog = "\n".join(
        map(lambda x: f".. |{x}| replace:: {frozen_locals[x]}", variables_to_export)
    )
    del frozen_locals
    return rst_epilog


def generate_config_file_validation_schema(app):

    all_cfg_schema = app.config._file.file_schema

    # merge built-in schema with custom schemas:
    config_schema = app.config.config_schemas
    for s_i in config_schema[1:]:
        config_schema[0].add_schema(s_i)

    # merge config file schema with config schemas:
    all_cfg_schema.add_schema(
        config_schema[0], root_path=DataPath("configs", MapValue(), "config")
    )

    # write default config file example:
    config = copy.deepcopy(app.config._options.default_config)
    config["configs"]["default"]["config"]["machine"] = "HOSTNAME"
    log_file_path = config["configs"]["default"]["config"]["log_file_path"]
    config["configs"]["default"]["config"]["log_file_path"] = config_callback_vars(
        app.config, log_file_path
    )
    app.config._file._dump_config(
        config, Path("reference/_generated/default_config.yaml")
    )

    # write valida schema tree for config file:
    _write_valida_tree_html(
        all_cfg_schema,
        path="reference/_generated/config_validation.html",
        from_path=[MapValue("configs")],
        heading_start_level=2,
    )


def generate_parameter_validation_schemas(app):
    for param in app.parameters:
        schema = param._validation
        if schema:
            full_path = _write_valida_tree_html(
                schema=schema,
                path=f"reference/_generated/param_{param.typ}_validation.html",
                anchor_root=param.typ,
                show_root_heading=False,
                heading_start_level=2,
            )
            jinja_contexts["first_ctx"]["tree_files"][param.typ] = str(full_path)


def generate_dummy_environments(*env_names):
    """Add environments to a temporary file and add that file to the config's environment
    sources."""
    dummy_envs = [{"name": i} for i in env_names]
    tmp_dir = Path(tempfile.gettempdir())
    tmp_envs_file = tmp_dir / "temp_envs.yml"
    yaml = YAML()
    with tmp_envs_file.open("wt") as fp:
        yaml.dump(dummy_envs, fp)
    app.config.append("environment_sources", str(tmp_envs_file))


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

# allow loading task schemas without these envs defined:
generate_dummy_environments(
    "python_env", "matlab_env", "damask_env", "damask_parse_env", "formable_env"
)

# -------- app-specific content END ------------------------------------------------------
# ----------------------------------------------------------------------------------------
# -------- ...the remaining content can be identical for hpcflow and downstream apps -----


Path("./reference/_generated").mkdir(exist_ok=True)

# distribution name (i.e. name on PyPI):
with open("../../pyproject.toml") as fp:
    dist_name = tomlkit.load(fp)["tool"]["poetry"]["name"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx_jinja",
    "sphinx_copybutton",
    "sphinx_click",
    "sphinx_togglebutton",
    "sphinx_design",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    **additional_intersphinx,
}

html_context = {
    "github_user": github_user,
    "github_repo": github_repo,
    "github_version": "develop",
    "doc_path": "docs/source",
}

jinja_contexts = {
    "first_ctx": {
        "app_name": app.name,
        "app_version": app.version,
        "app_package_name": app.package_name,
        "app_module": app.module,
        "app_docs_import_conv": app.docs_import_conv,
        "dist_name": dist_name,
        "parameters": app.parameters,
        "task_schemas": app.task_schemas,
        "command_files": app.command_files,
        "environments": app.envs,
        "tree_files": {},
        "download_links_table_html": generate_download_links_table(),
        "github_user": github_user,
        "github_repo": github_repo,
    }
}

jinja_globals = {
    "get_classmethods": get_classmethods,
    "parameter_task_schema_map": app.get_parameter_task_schema_map(),
}

# see: https://stackoverflow.com/a/62613202/5042280 for autosummary strategy
autosummary_generate = True
autodoc_typehints = "description"
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 4

templates_path = ["_templates"]
exclude_patterns = []

text_newlines = "unix"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "external_links": [],
    "switcher": {
        "json_url": switcher_JSON_URL,
        # "url_template": "https://docs.matflow.io/v{version}/",  # TODO: update switcher.json to include this url
        "version_match": __version__,
    },
    "navbar_end": ["theme-switcher", "navbar-icon-links", "version-switcher"],
    "use_edit_page_button": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/{github_user}/{github_repo}",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": f"https://pypi.org/project/{PyPI_project}",
            "icon": "fas fa-box",  # TODO: icon is smaller than in https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html ?
        },
    ],
}

rst_epilog = expose_variables(app)
generate_config_file_validation_schema(app)
generate_parameter_validation_schemas(app)
