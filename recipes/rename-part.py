import glob
from pathlib import Path
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit


class EditMethod(Enum):
    REPLACE = auto()
    START = auto()
    END = auto()


class RenamePart(Recipe):
    """批量改名：修改或删除文件名中的一部分。

    由于本插件专用于批量处理文件名中的一部分，因此可以自动选择需要处理的文件。
    """

    @property  # 必须设为 @property
    def name(self) -> str:
        return "rename-part"

    @property  # 必须设为 @property
    def help(self) -> str:
        return ""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            old='',
            method=EditMethod.REPLACE.name,
            auto=True,
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

        wrong_method = options.get('method', 'replace')
        method = wrong_method.upper()
        try:
            self.method = EditMethod[method]
        except KeyError:
            return f"KeyError: '{wrong_method}'\n"\
                "Please change the method to 'replace', 'start' or 'end'."

        self.old = options.get("old", '')
        self.new = options.get("new", '')
        self.auto = options.get("auto", True)
        self.use_glob = options.get("use_glob", False)
        if self.auto:
            names, err = names_limit(names, 1, 1)
            if err:
                return f'{err}\n当 auto=True 时要求 names 数量刚好等于 1'
            folder = Path(names[0])
            if not folder.is_dir:
                return f'{folder} 不是文件夹\n当 auto=True 时需要指定一个文件夹'
            all_names = folder.glob("*")
            self.names = [
                x
                for x in all_names
                if self.old in x.__str__()
            ]
        elif self.use_glob:
            names, err = names_limit(names, 1, 1)
            if err:
                return f'{err}\n当 use_glob=True 时要求 names 数量刚好等于 1'
            self.names = [Path(x) for x in glob.glob(names[0])]
        else:
            names, err = names_limit(names, 1)
            if err:
                return f'{err}\n当 auto=False 且 use_glob=False 时要求 names 数量大于等于 1'
            self.names = [Path(x) for x in names]
        return are_names_exist(self.names)

    def dry_run(self, really_move: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print("Before rename:")
        for name in self.names:
            print(name.__str__())

        print("\nAfter rename:")
        match self.method:
            case EditMethod.REPLACE:
                self.replace_names()

        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return ""

    def replace_names(self) -> None:
        for name in self.names:
            edited = name.__str__().replace(self.old, '')
            if not edited:
                print(f"Cannot rename '{name.__str__()}' to '{edited}'")
            else:
                print(edited)


##
# 注意，这句代码重要，就是靠这句把 OneWaySync 传递给插件系统。
##
__recipe__ = RenamePart
