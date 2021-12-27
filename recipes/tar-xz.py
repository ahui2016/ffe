"""tar-xz: 打包压缩/解压缩文件

使用打包压缩功能时，需要先进入一个文件夹，用相对路径选择需要打包的文件/文件夹。
采用 lzma 压缩方法，打包压缩后的后缀名是 '.tar.xz'
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import tarfile
from pathlib import Path
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, must_exist, names_limit


suffix = '.tar.xz'


class Mode(Enum):
    Auto = auto()
    Zip = auto()
    Unzip = auto()


class TarXZ(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "tar-xz"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "tar-xz"  # 打包压缩/解压缩文件
names = [          # 如果提供 1 个文件，并且后缀是 '.tar.xz',
    'file.tar.xz'  # 则自动进入解压缩模式，否则进入打包压缩模式。
]

[tasks.options]
output = ""       # 指定压缩后的文件名或解压缩时的目标文件夹，
                  # 如果留空，本插件会为你自动设置。
auto_wrap = true  # 解压缩出来不止一个文件时，用一个文件夹包裹它们
names = []        # 只有当多个任务组合时才使用此项代替命令行输入

使用打包压缩功能时，需要先进入一个文件夹，用相对路径选择需要打包的文件/文件夹。
采用 lzma 压缩方法，打包压缩后的后缀名是 '.tar.xz'
解压缩时每次只能解压缩一个文件。
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            output="",
            auto_wrap=True,
            names=[],
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.output
        - self.mode
        - self.names
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        names, err = names_limit(names, 1)
        if err:
            return err
        err = must_exist(names)
        if err:
            return err

        if len(names) == 1 and Path(names[0]).is_file() and names[0].endswith(suffix):
            self.mode = Mode.Unzip
        else:
            self.mode = Mode.Zip
        print(f"mode: {self.mode.name}")

        self.names = names
        output = options.get("output", "").strip()
        auto_wrap = options.get("auto_wrap", True)

        match self.mode:
            case Mode.Unzip:
                with tarfile.open(self.names[0]) as tar:
                    only_one = len(tar.getnames()) == 1

                if output:
                    # 如果指定了 output, 则必须确保那是一个存在的文件夹
                    self.output = Path.cwd().joinpath(output).resolve()
                else:
                    # 未指定 output，则解压缩到当前文件夹。
                    self.output = Path.cwd()

                # auto_wrap 为真并且不止一个文件时，利用压缩文件的文件名作为文件夹。
                if auto_wrap and not only_one:
                    folder = self.names[0].removesuffix(suffix)
                    self.output = self.output.joinpath(folder).resolve()

            case Mode.Zip:
                # 如果 options 里未指定 output 文件名，则自动赋予一个合理的文件名。
                if not output:
                    if len(self.names) == 1:
                        output = self.names[0]
                    else:
                        output = Path.cwd().name
                if output.endswith(suffix):
                    self.output = Path(output)
                else:
                    # 如果 output 文件名后缀不是 '.tar.xz', 则自动添加后缀。
                    self.output = Path(output + suffix)

        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        match self.mode:
            case Mode.Unzip:
                with tarfile.open(self.names[0]) as tar:
                    for name in tar.getnames():
                        f = self.output.joinpath(name).resolve()
                        if f.exists():
                            return f"Already Exists: '{f}'"
                        print(f)
            case Mode.Zip:
                if self.output.exists():
                    return f"File exists: '{self.output}'"
                print(f"Create '{self.output}'")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        err = self.dry_run()
        if err:
            return err
        match self.mode:
            case Mode.Unzip:
                with tarfile.open(self.names[0]) as tar:
                    tar.extractall(self.output)
            case Mode.Zip:
                with tarfile.open(self.output, 'w:xz') as tar:
                    for name in self.names:
                        tar.add(name)
        return ""


__recipe__ = TarXZ
