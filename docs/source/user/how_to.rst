How-to guides
#############

Configuration
-------------

Get and set config items
~~~~~~~~~~~~~~~~~~~~~~~~

Using the config sub-command in the |app_name| CLI, we can get configuration items like this:

.. jinja:: first_ctx
    
    .. code-block:: console

        {{ app_package_name }} config get machine

    Items can be set like this:

    .. code-block:: console

        {{ app_package_name }} config set machine my-machine-name

    ------------

    In the Python API, we can interact with the |app_name| configuration as below. Note that we must call :meth:`config.save <hpcflow.sdk.config.config.Config.save>` to make the config changes persistent, otherwise any changes made will only be temporary.

    .. code-block:: python

        import {{ app_module }} as {{ app_docs_import_conv }}

        # print the value of the `machine` item:
        print({{ app_docs_import_conv }}.config.machine)

        # set the value of the `machine` item:
        {{ app_docs_import_conv }}.config.machine = "my-machine-name"

        # save the changes to the config file:
        {{ app_docs_import_conv }}.config.save()

    See the configuration :ref:`reference documentation <reference/config_file:Configuration file>` for a listing of configurable items.
