import sys
import importlib.util
from pathlib import Path
from typing import Type, TypedDict
from abc import ABC, abstractmethod

from ffe.util import ErrMsg, __recipes_folder__


__default_max__ = 9999
"""默认处理文件数量的上限"""


class Recipe(ABC):
    def __init__(self) -> None:
        self.is_validated = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this recipe.

        注意，应返回一个便于命令行输入的名字，比如中间不要有空格。
        """
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help messages.

        方便在命令行查看每个 recipe 的用途。如果不写清楚，使用者（包括一段时间之后的作者自己）
        就需要查看源文件才能知道具体使用方法了。通常用一个带注释的 TOML 文件即可。
        """
        pass

    @property
    @abstractmethod
    def default_options(self) -> dict:
        """默认选项，具体项目可根据需要自由决定。"""
        pass

    @abstractmethod
    def validate(self, names: list[str], options: dict) -> None:
        """检查参数并进行初始化。

        注意：插件制作者必须保证 validate 是安全的，不可对文件进行任何修改。
             包括文件内容、日期、权限等等任何修改都不允许。
        """
        self.is_validated = True

    @abstractmethod
    def dry_run(self) -> None:
        """在不修改文件的前提下尝试运行，尽可能多收集信息预测真实运行的结果。

        比如，检查文件是否存在、将被修改的文件名等等。注意，与 validate 方法一样，
        插件制作者必须保证 dry_run 是安全的，不可对文件进行任何修改。
        """
        assert not self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print(f"There's no dry_run for {self.name}.")

    @abstractmethod
    def exec(self) -> None:
        """只有这个方法才真正操作文件，其它方法一律不可操作文件。"""
        assert not self.is_validated, "在执行 exec 之前必须先执行 validate"


class Task(TypedDict, total=False):
    recipe: str
    names: list[str]
    options: dict


class Plan(TypedDict, total=False):
    """一个计划可包含一个或多个任务，可与 TOML 文件互相转换。

    global_names, global_options 的优先级高过 task.names, task.options,
    具体如何体现优先级请看 check_plan 函数。
    """

    global_names: list[str]
    global_options: dict
    tasks: list[Task]


Recipes = dict[str, Type[Recipe]]
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


def check_plan(plan: Plan) -> ErrMsg:
    """plan 会被直接修改，返回错误消息（空字符串表示无错误）"""

    if not plan.get("tasks"):  # 如果 tasks 不存在或是空列表
        return "no task"

    has_global_names = False if not plan.get("global_names") else True
    has_global_options = False if not plan.get("global_options") else True

    for i, task in enumerate(plan.get("tasks", [])):
        recipe = task.get("recipe")
        if not recipe:
            return "recipe cannot be empty"
        if recipe not in __recipes__:
            return f"not found recipe: {recipe}"

        # 上面已经检查过 key 的存在，因此可以 type:ignore
        if has_global_names:
            plan["tasks"][i]["names"] = plan["global_names"]  # type:ignore
            del plan["global_names"]
        if has_global_options:
            for k, v in plan["global_options"].items():  # type:ignore
                plan["tasks"][i]["options"][k] = v  # type:ignore
            del plan["global_options"]

    return ""


def dry_run(plan: Plan):
    """提醒：在执行该函数前，应先执行 check_plan 函数。"""
    for task in plan.get("tasks", []):
        # check_plan 函数已经检查过 key 的存在，因此可以 type:ignore
        r: Recipe = __recipes__[task["recipe"]]()  # type:ignore
        r.dry_run()
