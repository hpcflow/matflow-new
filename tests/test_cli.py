import pytest

from click.testing import CliRunner
from hpcflow._version import __version__ as hpcflow_version

from matflow._version import __version__ as matflow_version
from matflow.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, args="--version")
    assert result.output.strip() == f"matflow, version {matflow_version}"


def test_hpcflow_version():
    runner = CliRunner()
    result = runner.invoke(cli, args="hpcflow --version")
    assert result.output.strip() == f"hpcflow, version {hpcflow_version}"
