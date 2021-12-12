from pathlib import Path
from typing import TypedDict, cast
from appdirs import AppDirs
import toml
import tomli

ErrMsg = str
"""只是一个描述错误内容的简单字符串而已"""


class Settings(TypedDict):
    # 暂时只有一个项目，后续根据需要再添加。
    recipes_folder: str


app_dirs = AppDirs("ffe", "github-ahui2016")
app_config_dir = Path(app_dirs.user_config_dir)
app_config_file = app_config_dir.joinpath("ffe-config.toml")
default_recipes_dir = Path(app_dirs.user_data_dir).joinpath("recipes").__str__()
default_settings = Settings(recipes_folder=default_recipes_dir)


def ensure_config_file() -> None:
    app_config_dir.mkdir(parents=True, exist_ok=True)
    if not app_config_file.exists():
        with open(app_config_file, "w") as f:
            toml.dump(default_settings, f)


def ensure_recipes_folder() -> str:
    with open(app_config_file, "rb") as f:
        settings = cast(Settings, tomli.load(f))
        r_folder = settings["recipes_folder"]
        Path(r_folder).mkdir(parents=True, exist_ok=True)
        return r_folder