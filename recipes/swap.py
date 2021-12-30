"""swap: 对调两个文件的文件名

只能用于不需要移动文件的情况，比如同一个文件夹（或同一个硬盘分区）内的文件可以操作，
而跨硬盘分区的文件则无法处理。

https://github.com/ahui2016/ffe/raw/main/recipes/swap.py
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

from pathlib import Path
from ffe.model import Recipe, ErrMsg, must_exist, get_bool, must_files, names_limit

suffix = "1"
"""临时文件名的后缀"""

suffix_limit = 20
"""限制最多可连续添加多少次 suffix, 避免文件名无限变长"""


# 每个插件都必须继承 model.py 里的 Recipe
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
names = []      # 只有当多个任务组合时才使用此项代替命令行输入

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
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # 检查选项，同时初始化选项，以便后续在 dry_run 和 exec 中使用。
        self.verbose, err = get_bool(options, "verbose")
        if err:
            return err

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        self.names, err = names_limit(names, 2, 2)
        if err:
            return err
        err = must_exist(self.names)
        if err:
            return err
        return must_files(self.names)

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        name1, name2 = Path(self.names[0]), Path(self.names[1])
        print(f"Start to swap {name1} and {name2}")
        temp, err = temp_name(name1)
        if err:
            return err
        print(f"-- found a safe temp name: {temp}")
        print(f"-- rename {name1} to {temp}")
        print(f"-- rename {name2} to {name1}")
        print(f"-- rename {temp} to {name2}")
        print(f"swap files OK: {name1} and {name2}")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"

        name1, name2 = Path(self.names[0]), Path(self.names[1])
        temp, err = temp_name(name1)
        if err:
            return err
        name1.rename(temp)
        name2.rename(name1)
        temp.rename(name2)

        # 这个插件本来不需要 verbose, 只是为了当作使用 options 的示例，因此简单处理。
        if self.verbose:
            self.dry_run()
        else:
            print(f"swap files OK: {name1} and {name2}")
        return ""


__recipe__ = Swap


def temp_name(name: Path) -> tuple[Path, ErrMsg]:
    for _ in range(suffix_limit):
        stem = name.stem + suffix
        name = name.with_stem(stem)
        if not name.exists():
            return name, ""
    return name, f"cannot find a proper temp name, last try: {name}"
