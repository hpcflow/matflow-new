from hpcflow.sdk import app as sdk_app
from hpcflow.sdk.config import ConfigOptions

from matflow._version import __version__
from matflow.param_classes import *

# provide access to app attributes:
__getattr__ = sdk_app.get_app_attribute

# ensure docs/help can see dynamically loaded attributes:
__all__ = sdk_app.get_app_module_all()
__dir__ = sdk_app.get_app_module_dir()

# set app-level config options:
config_options = ConfigOptions(
    directory_env_var="MATFLOW_CONFIG_DIR",
    default_directory="~/.matflow-new",
    sentry_DSN="https://2463b288fd1a40f4bada9f5ff53f6811@o1180430.ingest.sentry.io/6293231",
    sentry_traces_sample_rate=1.0,
    sentry_env="main" if "a" in __version__ else "develop",
)

# load built in template components:
template_components = sdk_app.App.load_builtin_template_component_data("matflow.data")

# initialise the App object:
app: sdk_app.App = sdk_app.App(
    name="MatFlow",
    version=__version__,
    module=__name__,
    docs_import_conv="mf",
    description="Materials science workflow manager",
    template_components=template_components,
    scripts_dir="data.scripts",  # relative to root package
    config_options=config_options,
)  #: |app|
