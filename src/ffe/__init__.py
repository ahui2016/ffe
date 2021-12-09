"""ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)"""

__package_name__ = "ffe"
__version__ = "0.0.1"

from pathlib import Path
import importlib.util
import sys
from .model import Recipe

__recipes_folder__ = "./recipes"
__recipes__: dict[str, Recipe] = {}


def register(r: Recipe):
    assert r.name in __recipes__, f"{r.name} already exists"
    __recipes__[r.name] = r


def init_recipes():
    recipes_files = Path(__recipes_folder__).glob("*.py")
    for file_path in recipes_files:
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        register(module.__recipe__)
