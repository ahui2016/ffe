from pathlib import Path
from appdirs import AppDirs
import toml
import tomli

ErrMsg = str
"""只是一个描述错误内容的简单字符串而已"""

app_dirs = AppDirs("ffe", "github-ahui2016")
app_config_dir = Path(app_dirs.user_config_dir)
app_config_file = app_config_dir.joinpath("ffe-config.toml")
recipes_folder = "recipes_folder"
default_recipes_dir = Path(app_dirs.user_data_dir).joinpath("recipes")
default_settings = dict(recipes_folder=default_recipes_dir.__str__())
__recipes_folder__ = default_recipes_dir


def ensure_config_file() -> None:
    app_config_dir.mkdir(parents=True, exist_ok=True)
    if not app_config_file.exists():
        with open(app_config_file, "w") as f:
            toml.dump(default_settings, f)


def ensure_recipes_folder() -> None:
    with open(app_config_file, "rb") as f:
        settings = tomli.load(f)
        __recipes_folder__ = Path(settings.get(recipes_folder, default_recipes_dir))
        __recipes_folder__.mkdir(parents=True, exist_ok=True)
