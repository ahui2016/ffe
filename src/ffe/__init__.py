"""ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)"""

__package_name__ = "ffe"
__version__ = "0.0.1"

from pathlib import Path
import importlib.util
import sys
from .model import Recipe

__recipes_folder__ = "./recipes"
__recipes__: dict[str, Recipe] = {}


def register(recipe: Recipe):
    name = recipe().name()  # recipe is a class, recipe() is an instance
    assert name not in __recipes__, f"{name} already exists"
    __recipes__[name] = recipe


def init_recipes():
    recipes_files = Path(__recipes_folder__).glob("*.py")
    for file_path in recipes_files:
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        register(module.__recipe__)


# AllTasks 的结构如下所示
"""
Task: {
    recipe: str,
    names: list[str],
    options: dict
}
AllTasks: {
    global-names: list[str],
    global-options: dict,
    tasks: list[Task]
}
"""


def check_tasks(all_tasks) -> tuple[dict, str]:
    """返回错误消息"""
    if not all_tasks.get("tasks"):  # 如果 tasks 不存在或是空列表
        return {}, "no task"

    has_global_names = False if not all_tasks.get("global-names") else True
    has_global_options = False if not all_tasks.get("global-options") else True
    for i, task in enumerate(all_tasks["tasks"]):
        recipe = task.get("recipe")
        if not recipe:
            return {}, "recipe cannot be empty"
        if recipe not in __recipes__:
            return {}, f"not found recipe: {recipe}"
        if has_global_names:
            all_tasks["tasks"][i]["names"] = all_tasks["global-names"]
            all_tasks["global-names"] = []
        if has_global_options:
            for k, v in all_tasks["global-options"].items():
                all_tasks["tasks"][i]["options"][k] = v
            all_tasks["global-options"] = {}

    return all_tasks, ""


def dry_run(all_tasks) -> str:
    for task in all_tasks["tasks"]:
        r: Recipe = __recipes__[task["recipe"]]()
        r.dry_run()
