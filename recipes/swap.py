from pathlib import Path
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit

suffix = "1"
"""临时文件名的后缀"""

suffix_limit = 20
"""限制最多可连续添加多少次 suffix, 避免文件名无限变长"""


# 关于具体如何实现一个　Recipe, 请参考项目源码中的 model.py
class Swap(Recipe):
    """对调两个文件名

    只能用于不需要移动文件的情况，比如同一个文件夹（或同一个硬盘分区）内的文件可以操作，
    而跨硬盘分区的文件则无法处理。
    """

    @property  # 注意: 必须有 @property
    def name(self) -> str:
        return "swap"

    @property  # 注意: 必须有 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "swap"  # 对调两个文件名（或文件夹名）
names = [        # 文件名（或文件夹名）数量必须是正好两个
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
        self.names, err = names_limit(names, 2, 2)
        if err:
            return err
        err = are_names_exist(names)
        if err:
            return err

        # 检查选项，同时初始化选项，以便后续在 dry_run 和 exec 中使用。
        self.verbose = options.get("verbose", True)

        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        print(f"Start to swap {self.names[0]} and {self.names[1]}")
        temp, err = temp_name(self.names[0])
        if err:
            return err
        print(f"-- found a safe temp name: {temp}")
        print(f"-- rename {self.names[0]} to {temp}")
        print(f"-- rename {self.names[1]} to {self.names[0]}")
        print(f"-- rename {temp} to {self.names[1]}")
        print(f"swap files OK: {self.names[0]} and {self.names[1]}\n")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"

        if self.verbose:
            print(f"Start to swap {self.names[0]} and {self.names[1]}")

        temp, err = temp_name(self.names[0])
        if err:
            return err

        if self.verbose:
            print(f"-- found a safe temp name: {temp}")
            print(f"-- rename {self.names[0]} to {temp}")
        Path(self.names[0]).rename(temp)

        if self.verbose:
            print(f"-- rename {self.names[1]} to {self.names[0]}")
        Path(self.names[1]).rename(self.names[0])

        if self.verbose:
            print(f"-- rename {temp} to {self.names[1]}")
        temp.rename(self.names[1])

        print(f"swap files OK: {self.names[0]} and {self.names[1]}\n")
        return ""


##
# 注意，这句代码重要，就是靠这句把 Swap 传递给插件系统。
##
__recipe__ = Swap


def temp_name(name: str) -> tuple[Path, ErrMsg]:
    temp = Path(name)
    for _ in range(suffix_limit):
        stem = temp.stem + suffix
        temp = temp.with_stem(stem)
        if not temp.exists():
            return temp, ""
    return temp, f"cannot find a proper temp name, last try: {temp}"
