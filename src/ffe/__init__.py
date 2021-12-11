"""ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)"""

__package_name__ = "ffe"
__version__ = "0.0.1"

from pathlib import Path
import importlib.util
import sys
from typing import Type
from .model import Plan, Recipe

Recipes = dict[str, Type[Recipe]]

__recipes_folder__ = "./recipes"
__recipes__: Recipes = {}


def register(recipe: Type[Recipe]):
    name = recipe().name
    assert name not in __recipes__, f"{name} already exists"
    __recipes__[name] = recipe


def init_recipes():
    recipes_files = Path(__recipes_folder__).glob("*.py")
    for file_path in recipes_files:
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)

        assert spec is not None
        assert spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        register(module.__recipe__)


def dry_run(plan: Plan):
    for task in plan["tasks"]:
        r: Recipe = __recipes__[task["recipe"]]()
        r.dry_run()
