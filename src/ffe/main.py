from .__init__ import __version__, __package_name__, __recipes__, init_recipes
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


def print_recipes(ctx, param, value):
    click.echo(__recipes__.keys())
    ctx.exit()


def print_recipe_help(ctx, param, value):
    if value in __recipes__:
        r = __recipes__[value]()
        click.echo(r.help())
    else:
        click.echo(
            f"not found recipe: {value}\n"
            'use "-l" or "--list" to list out all registered recipes'
        )
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
    "-f",
    "--file",
    type=click.File("rb"),
    help="specify a TOML file",
    callback=print_tasks,
    # is_eager=True,
)
@click.option(
    "-l",
    "--list",
    is_flag=True,
    help="list out all registered recipes",
    callback=print_recipes,
    # is_eager=True,
)
@click.option(
    "-r",
    "--recipe",
    help="print a brief overview of the recipe",
    callback=print_recipe_help,
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


# 初始化
init_recipes()

if __name__ == "__main__":
    cli()
