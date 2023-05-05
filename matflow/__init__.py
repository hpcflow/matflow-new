from hpcflow.sdk import App, ConfigOptions

from matflow._version import __version__
from matflow.parameters import Orientations

config_options = ConfigOptions(
    directory_env_var="MATFLOW_CONFIG_DIR",
    default_directory="~/.matflow-new",
    sentry_DSN="https://2463b288fd1a40f4bada9f5ff53f6811@o1180430.ingest.sentry.io/6293231",
    sentry_traces_sample_rate=1.0,
    sentry_env="main" if "a" in __version__ else "develop",
)

template_components = App.load_builtin_template_component_data("matflow.data")

MatFlow = App(
    name="MatFlow",
    version=__version__,
    description="Materials science workflow manager",
    template_components=template_components,
    scripts_dir="data.scripts",  # relative to root package
    config_options=config_options,
)

Action = MatFlow.Action
ActionEnvironment = MatFlow.ActionEnvironment
ActionScope = MatFlow.ActionScope
ActionScopeType = MatFlow.ActionScopeType
Command = MatFlow.Command
Environment = MatFlow.Environment
Executable = MatFlow.Executable
ExecutableInstance = MatFlow.ExecutableInstance
ExecutablesList = MatFlow.ExecutablesList
FileSpec = MatFlow.FileSpec
InputFile = MatFlow.InputFile
InputFileGenerator = MatFlow.InputFileGenerator
InputSource = MatFlow.InputSource
InputSourceType = MatFlow.InputSourceType
InputValue = MatFlow.InputValue
Parameter = MatFlow.Parameter
ResourceList = MatFlow.ResourceList
ResourceSpec = MatFlow.ResourceSpec
SchemaInput = MatFlow.SchemaInput
SchemaOutput = MatFlow.SchemaOutput
Task = MatFlow.Task
TaskObjective = MatFlow.TaskObjective
TaskSchema = MatFlow.TaskSchema
TaskSourceType = MatFlow.TaskSourceType
ValueSequence = MatFlow.ValueSequence
Workflow = MatFlow.Workflow
WorkflowTask = MatFlow.WorkflowTask
WorkflowTemplate = MatFlow.WorkflowTemplate
