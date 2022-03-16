These GitHub actions workflows are generated from Jinja templates from https://github.com/hpcflow-new/python-release-workflow.

The `generate_workflows.py` file is invoked like this to generate all of the workflow YAML file:

```yaml
cd .github/workflows
python generate_workflows.py . vars.jsonc
```
