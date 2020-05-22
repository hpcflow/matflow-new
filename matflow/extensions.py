import functools
import pkg_resources
import warnings

from matflow.config import Config
from matflow.errors import MatflowExtensionError, ConfigurationError
from matflow.validation import validate_task_schemas


def load_extensions():

    Config.set_config(raise_on_set=True)
    Config.unlock_extensions()

    extensions_entries = pkg_resources.iter_entry_points('matflow.extension')
    if extensions_entries:
        print('Loading extensions...')
        for entry_point in extensions_entries:

            loaded = entry_point.load()
            unload = False

            if not hasattr(loaded, '__version__'):
                warnings.warn(f'Matflow extension "{entry_point.module_name}" has no '
                              f'`__version__` attribute. This extension will not be '
                              f'loaded.')
                unload = True

            if Config.get('software_versions').get(loaded.SOFTWARE) is None:
                msg = (f'Matflow extension "{entry_point.module_name}" does not register '
                       f'a function for getting software versions. This extension will '
                       f'not be loaded.')
                warnings.warn(msg)
                unload = True

            if unload:
                Config.unload_extension(entry_point.name)
                continue

            Config.set_extension_info(
                entry_point.name,
                {'module_name': entry_point.module_name, 'version': loaded.__version__},
            )
            print(f'  "{entry_point.name}" (software: "{loaded.SOFTWARE}") from '
                  f'{entry_point.module_name} (version {loaded.__version__})', flush=True)

        # Validate task schemas against loaded extensions:
        print('Validating task schemas against loaded extensions...', end='')
        try:
            Config.set_schema_validities(
                validate_task_schemas(
                    Config.get('task_schemas'),
                    Config.get('input_maps'),
                    Config.get('output_maps'),
                    Config.get('func_maps'),
                )
            )
        except Exception as err:
            print('Failed.', flush=True)
            raise err

        num_valid = sum(Config.get('schema_validity').values())
        num_total = len(Config.get('schema_validity'))
        print(f'OK! {num_valid}/{num_total} schemas are valid.', flush=True)

    else:
        print('No extensions found.')

    Config.lock_extensions()


def input_mapper(input_file, task, method, software):
    """Function decorator for adding input maps from extensions."""
    def _input_mapper(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        key = (task, method, software)
        Config.set_input_map(key, input_file, func_wrap)
        return func_wrap
    return _input_mapper


def output_mapper(output_name, task, method, software):
    """Function decorator for adding output maps from extensions."""
    def _output_mapper(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        key = (task, method, software)
        Config.set_output_map(key, output_name, func_wrap)
        return func_wrap
    return _output_mapper


def func_mapper(task, method, software):
    """Function decorator for adding function maps from extensions."""
    def _func_mapper(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        key = (task, method, software)
        Config.set_func_map(key, func_wrap)
        return func_wrap
    return _func_mapper


def cli_format_mapper(input_name, task, method, software):
    """Function decorator for adding CLI arg formatter functions from extensions."""
    def _cli_format_mapper(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        key = (task, method, software)
        Config.set_CLI_arg_map(key, input_name, func_wrap)
        return func_wrap
    return _cli_format_mapper


def software_versions(software):
    """Function decorator to register an extension function as the function that returns
    a dict of pertinent software versions for that extension."""
    def _software_versions(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        Config.set_software_version_func(software, func_wrap)
        return func_wrap
    return _software_versions


def sources_mapper(task, method, software, **sources_dict):
    """Function decorator to register an extension function that generate task source
    files."""
    def _sources_mapper(func):
        @functools.wraps(func)
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        key = (task, method, software)
        Config.set_source_map(key, func_wrap, **sources_dict)
        return func_wrap
    return _sources_mapper


def register_output_file(file_reference, file_name, task, method, software):
    key = (task, method, software)
    Config.set_output_file_map(key, file_reference, file_name)