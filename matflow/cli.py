import click

from matflow import MatFlow


cli = MatFlow.CLI


@cli.group()
def parameter():  # matflow-only command group
    pass


@parameter.command("search")  # matflow-only command
def param_search():
    click.echo("param_search")


if __name__ == "__main__":
    cli()
