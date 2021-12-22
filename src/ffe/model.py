import sys
import importlib.util
from pathlib import Path
from typing import Any, Dict, Type, TypedDict, cast
from abc import ABC, abstractmethod

ErrMsg = str
"""一个描述错误内容的简单字符串，空字符串表示无错误。"""


__input_files_max__ = 99
"""默认文件/文件夹数量上限(不是实际处理数量，而是输入参数个数)"""


class Recipe(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this recipe.

        注意，应返回一个便于命令行输入的名称，比如中间不要有空格。
        名称稍长一点也没关系，因为 ffe 的主要使用场景是配合 toml 文件使用，
        不需要太频繁输入插件名称。
        """
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help messages.

        方便在命令行查看每个 recipe 的用途。如果不写清楚，使用者（包括一段时间之后的作者自己）
        就需要查看源文件才能知道具体使用方法了。通常用一个带注释的 TOML 文件即可。
        如果依赖第三方库，也可在这里注明。
        """
        pass

    @property
    @abstractmethod
    def default_options(self) -> dict:
        """默认选项，具体项目可根据需要自由决定。"""
        pass

    @abstractmethod
    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """检查参数并进行初始化。

        注意：插件制作者必须保证 validate 是安全的，不可对文件进行任何修改。
             包括文件内容、日期、权限等等任何修改都不允许。
        """
        self.is_validated = True  # 在 dry_run, exec 中确认已检查
        return ""

    @abstractmethod
    def dry_run(self) -> ErrMsg:
        """在不修改文件的前提下尝试运行，尽可能多收集信息预测真实运行的结果。

        比如，检查文件是否存在、将被修改的文件名等等。注意，与 validate 方法一样，
        插件制作者必须保证 dry_run 是安全的，不可对文件进行任何修改。
        """
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print(f"There's no dry_run for {self.name}.")
        return ""

    @abstractmethod
    def exec(self) -> ErrMsg:
        """只有这个方法才真正操作文件，其它方法一律不可操作文件。"""
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return ""


class Task(TypedDict):
    recipe: str
    names: list[str]
    options: dict


class Plan(TypedDict):
    """一个计划可包含一个或多个任务，可与 TOML 文件互相转换。

    global_names, global_options 的优先级高过 task.names, task.options,
    具体如何体现优先级请看 check_plan 函数。
    """

    global_names: list[str]
    global_options: dict
    tasks: list[Task]


def new_plan(obj: Dict[str, Any] = None) -> Plan:
    plan = Plan(global_names=[], global_options={}, tasks=[])
    if not obj:
        return plan

    plan["global_names"] = obj.get("global_names", [])
    plan["global_options"] = obj.get("global_options", {})
    if "tasks" in obj:
        for i, v in enumerate(obj["tasks"]):
            v = cast(dict, v)
            task = Task(recipe="", names=[], options={})
            task["recipe"] = v.get("recipe", "")
            task["names"] = v.get("names", [])
            task["options"] = v.get("options", {})
            obj["tasks"][i] = task
        plan["tasks"] = obj["tasks"]

    return plan


Recipes = dict[str, Type[Recipe]]
__recipes__: Recipes = {}


def register(recipe: Type[Recipe]):
    r = recipe()
    name = r.name

    # 由于 ABC@abstractmethod 不能确保一个方法是否被设置了 @property,
    # 因此只要手动检查。
    if not isinstance(name, str):
        name = r.name()  # type:ignore

    assert isinstance(r.name, str), f"{name}.name should be a property"
    assert isinstance(r.help, str), f"{name}.help should be a property"
    assert isinstance(
        r.default_options, dict
    ), f"{name}.default_options should be a property"

    assert name not in __recipes__, f"{name} already exists"
    __recipes__[name] = recipe


def init_recipes(folder: str) -> None:
    """注册 folder 里的全部插件。"""
    recipes_files = Path(folder).glob("*.py")
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

    if not plan["tasks"]:  # 如果 tasks 是空列表
        return "no task"

    has_global_names = False if not plan["global_names"] else True
    has_global_options = False if not plan["global_options"] else True

    for i, task in enumerate(plan["tasks"]):
        recipe = task["recipe"]
        if not recipe:
            return "recipe cannot be empty"
        if recipe not in __recipes__:
            return f"not found recipe: {recipe}"

        if has_global_names:
            plan["tasks"][i]["names"] = plan["global_names"]
        if has_global_options:
            for k, v in plan["global_options"].items():
                plan["tasks"][i]["options"][k] = v

    plan["global_names"] = []
    plan["global_options"] = {}
    return ""


def are_names_exist(names: list[str] | list[Path]) -> ErrMsg:
    """names 是文件/文件夹的路径，全部存在时返回空字符串。"""
    for name in names:
        if isinstance(name, str):
            name = Path(name)
        if not name.exists():
            return f"not found: {name}"
    return ""


def filter_files(names: list[Path]) -> list[Path]:
    """只要文件，不要文件夹"""
    return [x for x in names if x.is_file()]


def names_limit(
    names: list[str], min: int, max: int = __input_files_max__
) -> tuple[list[str], ErrMsg]:
    """清除 names 里的空字符串，并且限定其上下限。"""

    temp = map(lambda name: name.strip(), names)
    names = list(filter(lambda name: name != "", temp))
    msg = ""
    size = len(names)
    if min == max and size != min:
        msg = f"exactly {min} names"
    elif size < min:
        msg = f"names.length > {min}"
    elif size > max:
        msg = f"names.length <= {max}"

    if msg:
        msg = f"expected: {msg}, got: {names}"
        names = []
    return names, msg
