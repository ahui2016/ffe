"""rename-part: 批量修改或删除文件名中的一部分。

由于本插件专用于批量处理文件名中的一部分，因此可以自动选择需要处理的文件。
对文件名的处理可选择三种模式: replace(替换字符), head(在开头添加字符), tail(在末尾添加字符)
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import glob
from pathlib import Path
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, are_names_exist, filter_files, names_limit


class EditMethod(Enum):
    REPLACE = auto()
    HEAD = auto()
    TAIL = auto()


new_filenames = set()


class RenamePart(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "rename-part"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "rename-part"  # 批量修改或删除文件名中的一部分
names = [ "." ]        # 一个文件夹 或 多个文件 或 使用通配符

[tasks.options]
old = ""             # 需要被删除或修改的内容
new = ""             # 新内容
method = "REPLACE"   # 有三种方法可选: replace / head / tail
auto = true          # 根据 old 自动选择文件，需要在 names 里指定一个文件夹
use_glob = false     # 此项设为 true 时, names 应该使用通配符，如 '*.jpg'

# 本插件的主要用法有两种：
# 1. 自动根据 old 选择文件，并且把 old 更改为 new, 如果 new 是空字符串则相当于删除 old。
# 2. method 设为 head 或 tail 时分别表示在文件名的开头或末尾添加 new 的内容。
# 由于本插件比较复杂，不熟悉时建议多用 'ffe run -dry' 模式预估运行结果，确认无误再真正执行。
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            old="",
            new="",
            method=EditMethod.REPLACE.name,
            auto=True,
            use_glob=False,
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.auto
        - self.use_glob
        - self.names
        - self.old
        - self.new
        - self.method
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        wrong_method = options.get("method", "replace")
        method = wrong_method.upper()
        try:
            self.method = EditMethod[method]
        except KeyError:
            return (
                f"KeyError: '{wrong_method}'\n"
                "Please change the method to 'replace', 'head' or 'tail'."
            )

        self.old = options.get("old", "")
        self.new = options.get("new", "")
        self.auto = options.get("auto", True)
        self.use_glob = options.get("use_glob", False)

        # auto 模式只适用于 EditMethod.REPLACE
        if self.method is not EditMethod.REPLACE:
            print("set auto to False because the method is not REPLACE")
            self.auto = False

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        # 优先采用 auto 模式，其次采用 use_glob 模式，当 auto 与 use_glob 都被设为 False 时
        # 才进入逐一指定具体文件的模式。
        if self.auto:
            print("auto: True")
            names, err = names_limit(names, 1, 1)
            if err:
                return f"{err}\n当 auto=True 时要求 names 数量刚好等于 1"
            folder = Path(names[0])
            if not folder.is_dir():
                return f"{folder} 不是文件夹\n当 auto=True 时需要指定一个文件夹"
            all_names = folder.glob("*")
            self.names = [x for x in all_names if self.old in x.__str__()]
        elif self.use_glob:
            print("use_glob: True")
            names, err = names_limit(names, 1, 1)
            if err:
                return f"{err}\n当 use_glob=True 时要求 names 数量刚好等于 1"
            if names[0].find("**") >= 0:
                return "do not support the “**” pattern"
            self.names = [Path(x) for x in glob.glob(names[0])]
        else:
            print("auto: False, use_glob: False")
            names, err = names_limit(names, 1)
            if err:
                return f"{err}\n当 auto=False 且 use_glob=False 时要求 names 数量大于等于 1"
            self.names = [Path(x) for x in names]

        self.names = filter_files(self.names)
        return are_names_exist(self.names)

    def dry_run(self, really_run: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        print(f"method: {self.method.name}\n")
        print("Before rename:")
        for p in self.names:
            print(smart_resolve(p).__str__())

        print("\nAfter rename:")
        if self.method == EditMethod.REPLACE:
            self.names_replace(really_run)
        elif self.method == EditMethod.HEAD:
            self.names_add_head(really_run)
        elif self.method == EditMethod.TAIL:
            self.names_add_tail(really_run)

        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return self.dry_run(really_run=True)

    def names_replace(self, really_run: bool) -> None:
        for old_path in self.names:
            old_path = smart_resolve(old_path)
            new_name = old_path.name.replace(self.old, self.new)
            new_path = old_path.with_name(new_name)
            check_print_run(old_path, new_path, really_run)

    def names_add_head(self, really_run: bool) -> None:
        for old_path in self.names:
            old_path = smart_resolve(old_path)
            new_name = self.new + old_path.name
            new_path = old_path.with_name(new_name)
            check_print_run(old_path, new_path, really_run)

    def names_add_tail(self, really_run: bool) -> None:
        for old_path in self.names:
            old_path = smart_resolve(old_path)
            new_stem = old_path.stem + self.new
            new_path = old_path.with_stem(new_stem)
            check_print_run(old_path, new_path, really_run)


__recipe__ = RenamePart


def smart_resolve(p: Path) -> Path:
    """resolve p to its absolute path if necessary"""
    if p.__str__().startswith("."):
        return p.resolve()
    return p


def check_print_run(before: Path, after: Path, really_run: bool) -> None:
    before_str, after_str = before.__str__(), after.__str__()

    if not after_str:
        print(f"Cannot rename '{before_str}' to a blank filename.")
        return

    if after.exists() or after_str in new_filenames:
        print(f"Cannot rename '{before_str}' to '{after_str}'(exists)")
        return

    if really_run:
        before.rename(after)

    new_filenames.add(after_str)
    print(after_str)
