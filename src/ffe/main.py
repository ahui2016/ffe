from typing import cast
from ffe.model import Plan, Recipe, __recipes__, check_plan, dry_run
from ffe.util import ErrMsg
from . import (
    __version__,
    __package_name__,
    init_recipes,
)
import click
import tomli
import toml


@click.group()
@click.version_option(
    __version__,
    "-V",
    "--version",
    package_name=__package_name__,
    message="%(prog)s version: %(version)s",
)
def cli():
    # ctx.ensure_object(dict)
    # if file is not None:
    #     tasks = tomli.load(file)
    #     ctx.obj["tasks"] = tasks
    pass


# 以上是主命令
############
# 以下是子命令


def get_recipe(name: str) -> tuple[Recipe | None, ErrMsg]:
    if name in __recipes__:
        r: Recipe = __recipes__[name]()
        return r, ""
    return None, f"Not found recipe: {name}"


def print_recipe_help(name: str) -> None:
    r, err = get_recipe(name)
    if err:
        click.echo(f"{err}\n" 'Use "ffe list -a" to list out all recipes.')    
    if r:
        click.echo(r.help)


@cli.command()
@click.option(
    "all", "-a", "--all", is_flag=True, help="List out all registered recipes."
)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help="Show more information of the recipe.",
)
@click.pass_context
def list(ctx, all, recipe_name):
    """List out recipes, or show more information of a recipe."""

    if all:
        click.echo(f"All registered recipes: {', '.join(__recipes__.keys())}")
        click.echo('Use "ffe list -r <recipe>" to show more about a recipe.')
        ctx.exit()
    if not recipe_name:
        click.echo(ctx.get_help())
        ctx.exit()
    print_recipe_help(recipe_name)


@cli.command()
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.File("rb"),
    help="Specify a TOML file.",
)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help='Specify a recipe. Use "ffe list -a" to show all recipes.',
)
@click.pass_context
def dump(ctx, in_file, recipe_name):
    """Do not run tasks, but print the plan instead."""

    if (not in_file) and (not recipe_name):
        click.echo(ctx.get_help())
        ctx.exit()

    plan = Plan()

    if in_file:
        plan = cast(Plan, tomli.load(in_file))
    elif recipe_name:
        plan 

    err = check_plan(plan)
    if err:
        click.echo(err)
        ctx.exit()
    plan_toml = toml.dumps(plan)
    click.echo(plan_toml)


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

    plan = cast(Plan, tomli.load(in_file))
    err = check_plan(plan)
    if err:
        click.echo(err)
        ctx.exit()

    if is_dry is True:
        dry_run(plan)


# 初始化
init_recipes()

if __name__ == "__main__":
    cli(obj={})
