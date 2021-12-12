from pathlib import Path
from typing import cast
from ffe.model import (
    ErrMsg,
    Plan,
    Recipe,
    Task,
    __recipes__,
    check_plan,
    dry_run,
    init_recipes,
)
from ffe.util import (
    Settings,
    app_config_file,
    ensure_config_file,
    ensure_recipes_folder,
)
from . import (
    __version__,
    __package_name__,
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
        click.echo(f"{err}\n" 'Use "ffe info -a" to list out all recipes.')
    if r:
        click.echo(r.help)


def show_dir(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"[ffe] {__file__}")
    click.echo(f"[config] {app_config_file}")
    click.echo(f"[recipes] {__recipes_folder__}")
    ctx.exit()


def set_recipes_dir(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    folder = cast(click.Path, value)
    with open(app_config_file, "rb") as f:
        settings = cast(Settings, tomli.load(f))
        folder_path = Path(folder.__str__()).resolve()
        settings["recipes_folder"] = folder_path.__str__()
    with open(app_config_file, "w") as f:
        toml.dump(settings, f)
    click.echo(f"OK\n[recipes] {settings['recipes_folder']}")
    ctx.exit()


@cli.command()
@click.option(
    "all", "-a", "--all-recipes", is_flag=True, help="List out all registered recipes."
)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help="Show description of the recipe.",
)
@click.option(
    "-dir",
    "--directories",
    is_flag=True,
    help="Show directories about ffe and recipes.",
    callback=show_dir,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--set-recipes",
    type=click.Path(exists=True),
    help="Change the location of the directory contains recipes.",
    callback=set_recipes_dir,
    expose_value=False,
)
@click.pass_context
def info(ctx, all, recipe_name):
    """Get or set information about recipes."""

    if all:
        if not __recipes__:
            click.echo("Cannot find any recipe.\n")
            click.echo(f"Please put some recipes in {__recipes_folder__}\n")
            click.echo(
                'Use "ffe info --set-recipes <DIRECTORY PATH>" to change the directory contains recipes.\n'
            )
            click.echo("Download example recipes at https://github.com/ahui2016/ffe\n")
            ctx.exit()
        click.echo(f"All registered recipes: {', '.join(__recipes__.keys())}")
        click.echo('Use "ffe info -r <recipe>" to show more about a recipe.')
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
    help='Specify a recipe. Use "ffe info -a" to show all recipes.',
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
    else:
        r, err = get_recipe(recipe_name)
        if err:
            click.echo(err)
            ctx.exit()
        if r:
            plan = Plan(
                tasks=[Task(recipe=r.name, names=[], options=r.default_options)]  # TODO
            )

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
ensure_config_file()
__recipes_folder__ = ensure_recipes_folder()
init_recipes(__recipes_folder__)

if __name__ == "__main__":
    cli(obj={})
