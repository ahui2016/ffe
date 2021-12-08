from .__init__ import __version__, __package_name__
import click
import tomli


def print_tasks(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(param)
    click.echo(value)
    tasks = tomli.load(value)
    click.echo(tasks)
    ctx.exit()


@click.group()
@click.version_option(
    __version__,
    "-V",
    "--version",
    package_name=__package_name__,
    message="%(prog)s version: %(version)s",
)
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.File("rb"),
    help="specify a TOML file",
    callback=print_tasks,
    is_eager=True,
)
def cli():
    pass


@cli.command()
def ver():
    """the version of ffe"""
    click.echo(f"ffe {__version__}")


@cli.command()
def dropdb():
    click.echo("Dropped the database")


if __name__ == "__main__":
    cli()
