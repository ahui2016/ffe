from pathlib import Path
from typing import TypedDict, cast
from appdirs import AppDirs
from requests.models import Response
import toml
import tomli
import requests


class Settings(TypedDict):
    recipes_folder: str
    http_proxy: str
    use_proxy: bool


app_dirs = AppDirs("ffe", "github-ahui2016")
app_config_dir = Path(app_dirs.user_config_dir)
app_config_file = app_config_dir.joinpath("ffe-config.toml")
default_recipes_dir = Path(app_dirs.user_data_dir).joinpath("recipes").__str__()
default_settings = Settings(
    recipes_folder=default_recipes_dir, http_proxy="", use_proxy=True
)


def tomli_load(file: str) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)


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


def get_config() -> Settings:
    with open(app_config_file, "rb") as f:
        settings = cast(Settings, tomli.load(f))
    return settings


def get_proxies() -> dict | None:
    settings = get_config()
    proxies = None
    if settings["use_proxy"] and settings["http_proxy"]:
        proxies = dict(
            http=settings["http_proxy"],
            https=settings["http_proxy"],
        )
    return proxies


def request(url: str, proxies: dict | None) -> requests.Response:
    """下载文件，如果用户设置了代理则采用代理"""
    resp = requests.get(url, proxies=proxies)
    resp.raise_for_status()
    return resp


def peek_lines(url: str, proxies: dict = None, resp: Response = None) -> None:
    print(url)
    if not resp:
        resp = request(url, proxies)
    n, max = 0, 5
    for line in resp.iter_lines():
        if n >= max:
            break
        n += 1
        if line:
            print(line.decode())  # Default encoding is 'utf-8'.
    print()
