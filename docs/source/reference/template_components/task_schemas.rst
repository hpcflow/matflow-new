Task schemas
============

.. jinja:: first_ctx

   {% for i in task_schemas %}

   {{i.objective.name}}
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   Inputs:

   {% for inp in i.inputs %}

   * :ref:`reference/template_components/parameters:{{ inp.parameter.typ }}`

     * Labels: {{ inp.labels }}

   {% endfor %}

   Outputs:

   {% for out in i.outputs %}

   * :ref:`reference/template_components/parameters:{{ out.parameter.typ }}`

   {% endfor %}

   Actions:

   {% for act in i.actions %}

   * Action {{ loop.index0 }}

     {% set inp_types = act.get_input_types() %}
     {% set out_types = act.get_output_types() %}
     {% if inp_types %}
     * Inputs: {% for inp_type_i in inp_types -%}{{ inp_type_i }}{% if not loop.last %}, {% endif -%}{% endfor %}
     {% endif %}

     {% if out_types %}
     * Outputs: {% for out_type_i in out_types -%}{{ out_type_i }}{% if not loop.last %}, {% endif -%}{% endfor %}
     {% endif %}

     * Commands:

     {% for cmd in act.commands %}

       * Command:

         .. code-block:: console

            {{ cmd.command }}

       {% if cmd.stdout %}
       * Stdout:

         .. code-block:: console

            {{ cmd.stdout }}

       {% endif %}

       {% if cmd.stderr %}
       * Stderr:

         .. code-block:: console

            {{ cmd.stderr }}

       {% endif %}

     {% endfor %}

     * Environments:

     {% for cmd_env in act.environments %}

       * {{ cmd_env.scope.typ.name.lower() }}: :ref:`reference/template_components/environments:{{ cmd_env.environment.name }}`

     {% endfor %}

   {% endfor %}

   {% endfor %}
