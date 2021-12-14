from pathlib import Path
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit


class MoveNewFiles(Recipe):
    """移动 n 个指定后缀的新文件。

    只能处理一个文件夹内的第一层文件，不会递归搜索子文件夹。
    """

    @property  # 注意: 必须有 @property
    def name(self) -> str:
        return "move-new-files"

    @property  # 注意: 必须有 @property
    def help(self) -> str:
        return ""

    @property  # 注意: 必须有 @property
    def default_options(self) -> dict:
        return dict(n=1, suffix="")

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.target_dir
        - self.src_dir
        - self.n
        - self.suffix
        """
        names, err = names_limit(names, 2, 2)
        if err:
            return err
        err = are_names_exist(names)
        if err:
            return err
        for name in names:
            if not Path(name).is_dir():
                return f"{name} should be a directory"
        self.target_dir = names[0]
        self.src_dir = names[1]

        self.n = options.get("n", 1)
        if self.n < 1:
            return '"n" should be 1 or larger'

        self.suffix = options.get("suffix", "").strip().lower()

        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        src_files = Path(self.src_dir).glob("*")
        src_files = filter(
            lambda f: f.is_file() and f.__str__().lower().endswith(self.suffix),
            src_files,
        )
        src_files = map(lambda f: f.__str__(), src_files)

        print("src_files:", list(src_files))
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"

        return ""


##
# 注意，这句代码重要，就是靠这句把 MoveNewFiles 传递给插件系统。
##
__recipe__ = MoveNewFiles
