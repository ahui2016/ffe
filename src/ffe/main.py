from pathlib import Path
from urllib.parse import urlparse
from typing import Any, cast
import os
from ffe.model import (
    ErrMsg,
    Recipe,
    Task,
    __recipes__,
    check_plan,
    init_recipes,
    new_plan,
)
from ffe.util import (
    Settings,
    app_config_file,
    ensure_config_file,
    ensure_recipes_folder,
    get_proxies,
    peek_lines,
    request,
    tomli_load,
)
from . import (
    __version__,
    __package_name__,
)
import click
import tomli
import toml

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def check(ctx: click.Context, err: ErrMsg) -> None:
    """检查 err, 有错误则打印并终止程序，无错误则什么都不用做。"""
    if err:
        click.echo(f"Error: {err}")
        ctx.exit()


@click.group()
@click.help_option("-h", "--help")
@click.version_option(
    __version__,
    "-V",
    "--version",
    package_name=__package_name__,
    message="%(prog)s version: %(version)s",
)
@click.option(
    "safe", "-s", "--safe-mode", is_flag=True, help="Safe mode: do not load recipes."
)
def cli(safe):
    """ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)

    https://pypi.org/project/ffe/
    """
    if not safe:
        init_recipes(__recipes_folder__)


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
        click.echo(f"Error: {err}\n" 'Use "ffe info -a" to list out all recipes.')
    if r:
        click.echo(r.help)


def show_config(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    with open(app_config_file, "rb") as f:
        settings = cast(Settings, tomli.load(f))

    click.echo(f"[ffe] {__file__}")
    click.echo(f"[config] {app_config_file}")
    click.echo(f"[recipes] {settings['recipes_folder']}")
    click.echo(f'[http_proxy] {settings["http_proxy"]}')
    click.echo(f'[use_proxy] {settings["use_proxy"]}')
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


def set_proxy(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    value = cast(str, value).lower()
    with open(app_config_file, "rb") as f:
        settings = cast(Settings, tomli.load(f))
        if value == "off":
            settings["use_proxy"] = False
        elif value == "on":
            settings["use_proxy"] = True
        else:
            settings["http_proxy"] = value
    with open(app_config_file, "w") as f:
        toml.dump(settings, f)
    click.echo("OK")
    click.echo(f"[http_proxy] {settings['http_proxy']}")
    click.echo(f'[use_proxy] {settings["use_proxy"]}')
    ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
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
    "-cfg",
    "--config",
    is_flag=True,
    help="Show configurations about ffe and recipes.",
    callback=show_config,
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
@click.option(
    "--set-proxy",
    help='Set the http_proxy for requests. You can set it to "ON" or "OFF" too.',
    callback=set_proxy,
    expose_value=False,
)
@click.pass_context
def info(ctx, all, recipe_name):
    """Get or set information about recipes."""

    if all:
        if not __recipes__:
            click.echo("Warning: Cannot find any recipe.\n")
            click.echo(f"Please put some recipes in {__recipes_folder__}\n")
            click.echo(
                'Use "ffe info --set-recipes <DIRECTORY>" to change the directory contains recipes.\n'
            )
            click.echo(
                'Use "ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/swap.py" to install an example recipe\n'
            )
            ctx.exit()
        click.echo(f"All registered recipes: {', '.join(__recipes__.keys())}")
        click.echo('Use "ffe info -r <recipe>" to show more about a recipe.')
        ctx.exit()
    if not recipe_name:
        click.echo(ctx.get_help())
        ctx.exit()
    print_recipe_help(recipe_name)
    ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "peek", "-p", "--peek", is_flag=True, help="Print the first few lines of a file."
)
@click.option(
    "download",
    "-d",
    "--download-only",
    is_flag=True,
    help="Download a file and print its content, do not install it.",
)
@click.option(
    "install",
    "-i",
    "--install",
    is_flag=True,
    help="Install the recipe. Warning: Please inspect before installing it.",
)
@click.option(
    "force", "-f", "--force", is_flag=True, help="Force install/update the recipe."
)
@click.argument("url", nargs=1)
@click.pass_context
def install(ctx, peek, download, install, force, url):
    """Install recipes from an url.

    [URL] is a url point to a ".py" or ".toml" file.

    Warning: Please download and inspect recipes before installing them.

    提醒：请先下载 url 指向的文件，检查没有恶意代码后再安装，因为一旦安装，下次执行任何 ffe 命令都会自动执行其代码（自动 import）。
    """

    if (not download) and (not peek) and (not install):
        click.echo('Error: Missing option "-d" or "-i"')
        click.echo('Try "ffe install --help" for help.')
        ctx.exit()

    proxies = get_proxies()
    file_path = Path(urlparse(url).path)
    suffix = file_path.suffix.lower()

    if peek:
        resp = request(url, proxies)
        match suffix:
            case ".toml":
                recipe_list = tomli.loads(resp.text).get("recipes", [])
                if not recipe_list:
                    click.echo(f"{url} has no recipes")
                    ctx.exit()
                for r_url in recipe_list:
                    peek_lines(r_url, proxies)
            case _:
                peek_lines(url, None, resp)
        ctx.exit()

    if download:
        resp = request(url, proxies)
        print(resp.text)
        ctx.exit()

    # if install:
    if not force and file_path.suffix not in [".py", ".toml"]:
        click.echo(
            'Warning: It seem not a python file, retry with "-f" to force install it.'
        )
        ctx.exit()

    dst = Path(__recipes_folder__).joinpath(file_path.name)
    if dst.exists() and not force:
        click.echo(
            f'Warning: {dst.stem} already exists, retry with "-f" to force install it.'
        )
        ctx.exit()

    resp = request(url, proxies)
    if suffix == ".py":
        with open(dst, "wb") as f:
            f.write(resp.content)
        click.echo("OK.")
        ctx.exit()

    if suffix == ".toml":
        click.echo("Start to install a list of recipes.")
        click.echo("提醒：安装前应先审查代码，如未审查则在安装后暂时不要使用任何 ffe 命令，审查完再使用。")
        recipe_list = tomli.loads(resp.text).get("recipes", [])
        if not recipe_list:
            click.echo(f"{url} has no recipes")
            ctx.exit()
        for r_url in recipe_list:
            filename = Path(urlparse(r_url).path).name
            dst = Path(__recipes_folder__).joinpath(filename)
            if dst.exists() and not force:
                click.echo(f"skip {r_url}")
            else:
                resp = request(r_url, proxies)
                click.echo(f"install {r_url}")
                with open(dst, "wb") as f:
                    f.write(resp.content)
    ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help="Specify a recipe to uninstall.",
)
@click.pass_context
def uninstall(ctx, recipe_name):
    """Remove a recipe.

    Example: ffe uninstall -r swap
    """
    filename = recipe_name + ".py"
    r_path = Path(__recipes_folder__).joinpath(filename)
    os.remove(r_path)
    click.echo(f"Uninstall OK: {r_path}")
    ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.Path(),
    help="Specify a TOML file.",
)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help='Specify a recipe. Use "ffe info -a" to show all recipes.',
)
@click.argument("names", nargs=-1, type=click.Path())
@click.pass_context
def dump(ctx, in_file, recipe_name, names):
    """Do not run tasks, but print the plan instead.

    [NAMES] are file/folder paths(zero or many).
    """

    if (not in_file) and (not recipe_name):
        click.echo(ctx.get_help())
        ctx.exit()

    names = cast(list[click.Path], names)
    names = [x.__str__() for x in names]
    plan = new_plan()

    if in_file:
        plan = new_plan(tomli_load(in_file))
    else:
        r, err = get_recipe(recipe_name)
        check(ctx, err)
        if r:
            plan["tasks"] = [
                Task(
                    recipe=r.name,
                    names=names,
                    options=r.default_options,
                )
            ]

    check(ctx, check_plan(plan))  # 这里会把 global_names 和 global_options 清空（放进 tasks 里）

    obj = cast(Any, plan)  # 无法删除 TypedDict 的 key, 因此转换成 Any
    del obj["global_names"]
    del obj["global_options"]

    # 这里的 replace 是为了优化格式，但也有可能因此产生 bug, 等有 bug 再想办法吧。
    plan_toml = toml.dumps(obj).replace("\n[[", "\n\n\n[[")
    click.echo(plan_toml)
    ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "in_file",
    "-f",
    "--file",
    type=click.Path(),
    help="Specify a TOML file.",
)
@click.option(
    "recipe_name",
    "-r",
    "--recipe",
    help='Specify a recipe. Use "ffe info -a" to show all recipes.',
)
@click.option(
    "is_dry",
    "-dry",
    "--dry-run",
    is_flag=True,
    help="Predict the results of a real run, based on a test run without modifying files.",
)
@click.argument("names", nargs=-1, type=click.Path())
@click.pass_context
def run(ctx, in_file, recipe_name, is_dry, names):
    """Run tasks by specifying a file or a recipe.

    [NAMES] are file/folder paths(zero or many).
    """

    if (not in_file) and (not recipe_name):
        click.echo(ctx.get_help())
        ctx.exit()

    plan = new_plan()
    if in_file:
        plan = new_plan(tomli_load(in_file))
        if names:
            # 用户通过命令输入的 names 拥有最高优先级
            plan["tasks"][0]["names"] = names
    else:
        rcp, err = get_recipe(recipe_name)
        check(ctx, err)
        if rcp:
            plan["tasks"] = [
                Task(
                    recipe=rcp.name,
                    names=list(map(lambda name: name.__str__(), names)),
                    options=rcp.default_options,
                )
            ]

    check(ctx, check_plan(plan))

    # 提醒：在执行以下代码之前，应先执行 check_plan 函数。
    if is_dry:
        click.echo("\n** It's a dry run, not a real run. **")

    # 用来把上一个任务的执行结果传递到下一个任务。
    pipe_names = []

    for task in plan["tasks"]:
        r: Recipe = __recipes__[task["recipe"]]()
        click.echo(f"\nrecipe: {r.name}")

        # 默认使用 pipe_names, 但同时还需要 pipe_names 有内容才会被使用。
        if task["options"].get("use_pipe", False) and pipe_names:
            task["names"] = pipe_names

        # 避免“隔代遗传”
        pipe_names = []

        err = r.validate(task["names"], task["options"])
        if err:
            click.echo(f"Error: {err}")
            click.echo('Use "ffe run --help" to show usages of this command.')
            click.echo('Use "ffe info -r <recipe>" to show details of the recipe.')
            ctx.exit()

        if is_dry:
            pipe_names, err = r.dry_run()
            check(ctx, err)
        else:
            pipe_names, err = r.exec()
            check(ctx, err)

    if is_dry:
        click.echo("\nThe dry run has been completed.\n")
    else:
        click.echo("\nAll tasks have been completed.\n")
    ctx.exit()


# 初始化
ensure_config_file()
__recipes_folder__ = ensure_recipes_folder()

if __name__ == "__main__":
    cli(obj={})
