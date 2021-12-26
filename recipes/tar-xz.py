"""tar-xz: 打包压缩/解压缩文件

使用打包压缩功能时，需要先进入一个文件夹，用相对路径选择需要打包的文件/文件夹。
采用 lzma 压缩方法，打包压缩后的后缀名是 '.tar.xz'
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import tarfile
from pathlib import Path
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit  # get_bool, names_limit


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
使用打包压缩功能时，需要先进入一个文件夹，用相对路径选择需要打包的文件/文件夹。
采用 lzma 压缩方法，打包压缩后的后缀名是 '.tar.xz'
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            output="",
            wrap=True,
            mode=Mode.Auto.name,
            names=[],
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.output
        - self.wrap
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
        err = are_names_exist(names)
        if err:
            return err

        if len(names) == 1 and Path(names[0]).is_file() and names[0].endswith(suffix):
            self.mode = Mode.Unzip
        else:
            self.mode = Mode.Zip
        print(f"mode: {self.mode.name}")

        self.names = names

        if self.mode is Mode.Zip:
            output = options.get("output", "").strip()
            # 如果 options 里未指定 output 文件名，则用自动赋予一个合理的文件名。
            if not output:
                if len(self.names) == 1:
                    output = self.names[0]
                else:
                    output = Path.cwd().name
            if output.endswith(suffix):
                self.output = Path(output)
            else:
                # 如果 output 文件名后缀不是 '.tar.xz', 则自动添加后缀。
                self.output = Path(output).with_suffix(suffix)

        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        match self.mode:
            case Mode.Zip:
                if self.output.exists():
                    return f"File exists: '{self.output}'"
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        err = self.dry_run()
        if err:
            return err
        match self.mode:
            case Mode.Zip:
                with tarfile.open(self.output, 'w:xz') as tar:
                    for name in self.names:
                        tar.add(name)
        return ""


__recipe__ = TarXZ
