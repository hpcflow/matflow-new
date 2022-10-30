import numpy as np
from hpcflow.sdk import App, ConfigOptions

from matflow._version import __version__

config_options = ConfigOptions(
    directory_env_var="MATFLOW_CONFIG_DIR",
    default_directory="~/.matflow",
    sentry_DSN="https://2463b288fd1a40f4bada9f5ff53f6811@o1180430.ingest.sentry.io/6293231",
    sentry_traces_sample_rate=1.0,
    sentry_env="main" if "a" in __version__ else "develop",
)

MatFlow = App(
    name="matflow",
    version=__version__,
    description="Materials science workflow manager",
    config_options=config_options,
)

TaskSchema = MatFlow.TaskSchema
Task = MatFlow.Task
WorkflowTask = MatFlow.WorkflowTask
Workflow = MatFlow.Workflow
WorkflowTemplate = MatFlow.WorkflowTemplate
Action = MatFlow.Action
ActionScope = MatFlow.ActionScope
ActionScopeType = MatFlow.ActionScopeType
Environment = MatFlow.Environment
InputFile = MatFlow.InputFile
InputSource = MatFlow.InputSource
InputSourceType = MatFlow.InputSourceType
InputSourceMode = MatFlow.InputSourceMode
InputValue = MatFlow.InputValue
Command = MatFlow.Command
ActionEnvironment = MatFlow.ActionEnvironment
Parameter = MatFlow.Parameter
ValueSequence = MatFlow.ValueSequence
ZarrEncodable = MatFlow.ZarrEncodable


# temporarily used just to check correct inclusion of numpy in built exes:
a = np.random.random((10, 10))
