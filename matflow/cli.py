import logging
import click

from matflow import MatFlow
import matflow.api

logger = logging.getLogger(__name__)


@MatFlow.CLI.group()
def parameter():  # matflow-only command group
    pass


@parameter.command("search")  # matflow-only command
def parameter_search():
    matflow.api.parameter_search()


if __name__ == "__main__":
    MatFlow.CLI()
