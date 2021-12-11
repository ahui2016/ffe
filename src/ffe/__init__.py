"""ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)"""

__package_name__ = "ffe"
__version__ = "0.0.1"
__recipes_folder__ = "./recipes"

from pathlib import Path
import importlib.util
import sys

from ffe.model import register


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
