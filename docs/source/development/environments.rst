Environments
############

`matlab_env`
~~~~~~~~~~~

Example environment definition (non-compiled script)
----------------------------------------------------

* MTEX tasks have a `compile` input parameter, which is `False` by default. When `compile` is `False`, the `run_mtex` executable must be defined in the `matlab_env`, as shown below.
* The MATLAB `-batch` switch is used, and is documented here for `Windows <https://uk.mathworks.com/help/matlab/ref/matlabwindows.html>`_, `MacOS <https://uk.mathworks.com/help/matlab/ref/matlabmacos.html>`_, and `Linux <https://uk.mathworks.com/help/matlab/ref/matlablinux.html>`_.
* So far, this is tested only on Windows.

.. code-block:: yaml

    - name: matlab_env
      executables:
        - label: run_mtex
          instances:
            - command: matlab -batch "<<script_name_no_ext>> <<args>>"
              num_cores: 1
              parallel_mode: null

Example environment definition (compiled script)
----------------------------------------------------

* MTEX tasks have a `compile` input parameter, which is `False` by default. When `compile` is `True`, both the `compile_mtex` and `run_compiled_mtex` executables must be defined in the `matlab_env`, as shown below.
* So far, this is tested only on Linux.

.. code-block:: yaml

  - name: matlab_env
    setup: |
      # set up commands (e.g. `module load ...`)
    executables:
      - label: compile_mtex
        instances:
          - command: compile-mtex <<script_name>> <<args>> # steps to compile the script
            num_cores: 1
            parallel_mode: null

      - label: run_compiled_mtex
        instances:
          - command: ./run_<<script_name>>.sh $MATLAB_HOME <<args>>
            num_cores: 1
            parallel_mode: null


`damask_parse`
~~~~~~~~~~~~~~

We used our CentOS docker image (https://github.com/orgs/hpcflow/packages/container/package/centos7-poetry) to produce a "relocatable" conda environment for the `damask_parse` MatFlow environment, using conda-pack. Using the CentOS image is required because of glibc compatibilities.

In the container:

* Install Miniconda via the bash installation script: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
* Initialise conda for use in the shell: :code:`conda init`
* Reload .bashrc: :code:`source ~/.bashrc`
* Install conda pack: :code:`conda install conda-pack`
* Create a new conda environment that contains :code:`damask-parse` and :code:`matflow`: :code:`conda create -n matflow_damask_parse_v3a7_env python=3.10`
* Install :code:`libGL` for VTK (required by the damask python package) :code:`yum install mesa-libGL`
* Activate the environment: :code:`conda activate matflow_damask_parse_v3a7_env`
* Add packages via pip: :code:`pip install matflow-new damask-parse`
* Deactivate the environment: :code:`conda deactivate`
* Pack the environment into a tarball: :code:`conda pack matflow_damask_parse_v3a7_env`
* Save the resulting compressed file outside of the container and transfer to the target machine

On the target machine:

* Unpack the environment:
  
  .. code-block:: bash
    
      mkdir matflow_damask_parse_v3a7_env
      tar -xzf matflow_damask_parse_v3a7_env.tar.gz -C matflow_damask_parse_v3a7_env

* Activate the environment: :code:`source matflow_damask_parse_v3a7_env/bin/activate`
* Run: :code:`conda-unpack`
* The environment can now be activated as normal using the :code:`source` command above.

Resources:

* https://conda.github.io/conda-pack/index.html
* https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
* https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands
* https://github.com/conda/conda-pack/issues/160


Example environment definition
------------------------------

.. code-block:: yaml

    name: damask_parse_env
    setup: |    
      conda activate matflow_damask_parse_env
    executables:
      - label: python
        instances:
          - command: python
            num_cores: 1
            parallel_mode: null

`damask`
~~~~~~~~

Example environment definition
------------------------------

.. code-block:: yaml

    name: damask_env
    executables:
      - label: damask_grid
        instances:
          - command: docker run --rm --interactive --volume ${PWD}:/wd --env OMP_NUM_THREADS=1 eisenforschung/damask-grid:3.0.0-alpha7
            parallel_mode: null
            num_cores: 1
