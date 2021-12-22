"""swap: 对调两个文件的文件名

只能用于不需要移动文件的情况，比如同一个文件夹（或同一个硬盘分区）内的文件可以操作，
而跨硬盘分区的文件则无法处理。
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

from pathlib import Path
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit

suffix = "1"
"""临时文件名的后缀"""

suffix_limit = 20
"""限制最多可连续添加多少次 suffix, 避免文件名无限变长"""


# 关于具体如何实现一个 Recipe, 请参考项目源码中的 model.py
class Swap(Recipe):
    @property  # 注意: 必须有 @property
    def name(self) -> str:
        return "swap"

    @property  # 注意: 必须有 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "swap"  # 对调两个文件名
names = [        # 文件名数量必须是正好两个
  'file1.txt',
  'file2.txt',
]

[tasks.options]
verbose = true  # 显示或不显示程序执行的详细过程

# swap 只能用于不需要移动文件的情况，比如同一个文件夹 (或同一个硬盘分区)
# 内的文件可以操作，而跨硬盘分区的文件则无法处理。
"""

    @property  # 注意: 必须有 @property
    def default_options(self) -> dict:
        return dict(verbose=True)

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.names
        - self.verbose
        """

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        names, err = names_limit(names, 2, 2)
        if err:
            return err
        err = are_names_exist(names)
        if err:
            return err
        self.name1 = Path(names[0])
        self.name2 = Path(names[1])

        if self.name1.is_dir() or self.name2.is_dir():
            return f"{names[0]} and {names[1]} should be both files."

        # 检查选项，同时初始化选项，以便后续在 dry_run 和 exec 中使用。
        self.verbose = options.get("verbose", True)

        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        print(f"Start to swap {self.name1} and {self.name2}")
        temp, err = temp_name(self.name1)
        if err:
            return err
        print(f"-- found a safe temp name: {temp}")
        print(f"-- rename {self.name1} to {temp}")
        print(f"-- rename {self.name2} to {self.name1}")
        print(f"-- rename {temp} to {self.name2}")
        print(f"swap files OK: {self.name1} and {self.name2}\n")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"

        temp, err = temp_name(self.name1)
        if err:
            return err
        self.name1.rename(temp)
        self.name2.rename(self.name1)
        temp.rename(self.name2)

        # 这个插件本来不需要 verbose, 只是为了当作使用 options 的示例，因此简单处理。
        if self.verbose:
            self.dry_run()
        else:
            print(f"swap files OK: {self.name1} and {self.name2}\n")
        return ""


__recipe__ = Swap


def temp_name(name: Path) -> tuple[Path, ErrMsg]:
    for _ in range(suffix_limit):
        stem = name.stem + suffix
        name = name.with_stem(stem)
        if not name.exists():
            return name, ""
    return name, f"cannot find a proper temp name, last try: {name}"
