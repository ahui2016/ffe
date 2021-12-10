from ffe.model import Recipe
from .__init__ import (
    __version__,
    __package_name__,
    __recipes__,
    check_tasks,
    dry_run,
    init_recipes,
)
import click
import tomli
import toml


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
# @click.option(
#     "-f",
#     "--file",
#     type=click.File("rb"),
#     help="specify a TOML file",
# )
def cli():
    # ctx.ensure_object(dict)
    # if file is not None:
    #     tasks = tomli.load(file)
    #     ctx.obj["tasks"] = tasks
    pass


# 以上是主命令
############
# 以下是子命令


def print_recipe_help(ctx, param, value):
    if value in __recipes__:
        r: Recipe = __recipes__[value]()
        click.echo(r.help())
    else:
        click.echo(
            f"not found recipe: {value}\n"
            'use "-l" or "--list" to list out all registered recipes'
        )
    ctx.exit()


# def print_recipe_task(ctx, param, value):


@cli.command()
@click.pass_context
def list(ctx):
    """List out all registered recipes."""
    click.echo(__recipes__.keys())
    ctx.exit()


@cli.command()
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.File("rb"),
    help="Specify a TOML file.",
    required=True,
)
def dump(in_file):
    """Do not run tasks, but print messages instead."""
    tasks = toml.dumps(tomli.load(in_file))
    click.echo(tasks)


@cli.command()
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.File("rb"),
    help="Specify a TOML file.",
)
@click.option(
    "is_dry",
    "-dry",
    "--dry-run",
    is_flag=True,
    help="Predict the results of a real run, based on a test run without modifying files.",
)
@click.pass_context
def run(ctx, in_file, is_dry):
    """Run tasks by specifying a file or a recipe."""
    tasks = tomli.load(in_file)
    click.echo(tasks)

    _, err = check_tasks(tasks)
    click.echo(tasks)
    if err:
        click.echo(err)
        ctx.exit()

    if is_dry is True:
        dry_run(tasks)


# 初始化
init_recipes()

if __name__ == "__main__":
    cli(obj={})
