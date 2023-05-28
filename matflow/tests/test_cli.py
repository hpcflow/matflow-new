from click.testing import CliRunner
from hpcflow import __version__ as hpcflow_version

import matflow


def test_version():
    runner = CliRunner()
    result = runner.invoke(matflow.app.cli, args="--version")
    assert result.output.strip() == f"{matflow.app.name}, version {matflow.app.version}"


def test_hpcflow_version():
    runner = CliRunner()
    result = runner.invoke(matflow.app.cli, args="--hpcflow-version")
    assert result.output.strip() == f"hpcFlow, version {hpcflow_version}"
