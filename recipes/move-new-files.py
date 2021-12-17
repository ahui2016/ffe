from humanfriendly import format_size
import shutil
from pathlib import Path
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit


"""
本插件用来移动新文件，通过 st_ctime 来对文件排序。
    st_ctime:
        the time of most recent metadata change on Unix,
        the time of creation on Windows, expressed in seconds.

使用 shutil.move 来移动文件，因此会先尝试改名，改名失败再进行复制和删除操作。
"""


class MoveNewFiles(Recipe):
    """移动 n 个指定后缀的新文件。

    只能用来移动一个文件夹内的第一层文件，不能移动文件夹，也不会递归处理子文件夹。
    """

    @property  # 注意: 必须有 @property
    def name(self) -> str:
        return "move-new-files"

    @property  # 注意: 必须有 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "move-new-files"  # 转移最新的 n 个文件
names = [                 # names 必须是（不多不少）两个文件夹
    'target_dir',         # 第一个是目标文件夹
    'src_dir',            # 第二个是源头文件夹
]

[tasks.options]
n = 1                   # 移动多少个最新的文件
suffix = ".jpg"         # 指定文件名的末尾，空字符串表示不限
overwrite = false       # 是否覆盖同名文件

# 注意：本插件在设计上并未对移动大量文件的场景进行优化，建议只用来移动少量文件。
# dependencies = ["humanfriendly"]
"""

    @property  # 注意: 必须有 @property
    def default_options(self) -> dict:
        return dict(n=1, suffix="", overwrite=False)

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.target_dir
        - self.src_dir
        - self.n
        - self.suffix
        - self.overwrite
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
        self.overwrite = options.get("overwrite", False)

        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True
        return ""

    def dry_run(self, really_move: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        print(f"Move files from [{self.src_dir}] to [{self.target_dir}]")

        src_files, files_size, free_space = self.get_new_files()
        print(
            f"files size: {format_size(files_size)}, free space: {format_size(free_space)}"
        )
        if free_space <= files_size:
            return f"Not enough space in {self.target_dir}"

        print_and_move(Path(self.target_dir), src_files, self.overwrite, really_move)
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        self.dry_run(really_move=True)
        return ""

    def get_new_files(self) -> tuple[list[Path], int, int]:
        src_files = Path(self.src_dir).glob("*")
        src_files = [
            x
            for x in src_files
            if x.is_file() and x.__str__().lower().endswith(self.suffix)
        ]
        src_files.sort(key=lambda x: x.lstat().st_ctime, reverse=True)
        files_size = sum([x.lstat().st_size for x in src_files])
        free_space = shutil.disk_usage(self.target_dir).free
        return src_files[: self.n], files_size, free_space


##
# 注意，这句代码重要，就是靠这句把 MoveNewFiles 传递给插件系统。
##
__recipe__ = MoveNewFiles


def print_and_move(
    dst_folder: Path, src_files: list[Path], overwrite: bool, move: bool = False
) -> None:
    for src in src_files:
        dst = dst_folder.joinpath(src.name)
        if dst.exists() and not overwrite:
            print(f"-- skip {dst}")
            continue

        if dst.exists():
            print(f"-- overwrite {dst}")
        else:
            print(f"-- move {dst}")

        if move:
            shutil.move(src, dst)
