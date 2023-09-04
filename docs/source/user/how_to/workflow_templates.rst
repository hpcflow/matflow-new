Workflow templates how-tos
--------------------------

Loading workflow templates
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. jinja:: first_ctx

    Workflow template YAML files can be loaded from remote sources by providing :func:`{{ app_package_name }}.app.WorkflowTemplate.from_YAML_file` with an fsspec URL. For example, to load a workflow template YAML file from a GitHub repository, use the following format:

    .. code-block:: python

        import {{ app_module }} as {{ app_docs_import_conv }}

        wkt = {{ app_docs_import_conv }}.WorkflowTemplate.from_YAML_file()
