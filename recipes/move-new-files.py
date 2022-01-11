"""move-new-files: 移动 n 个指定后缀的新文件。
dependencies = ["humanfriendly"]

只能用来移动一个文件夹内的第一层文件，不能移动文件夹，也不会递归处理子文件夹。

本插件用来移动新文件，通过 st_ctime 来对文件排序。
    st_ctime:
        the time of most recent metadata change on Unix,
        the time of creation on Windows, expressed in seconds.

使用 shutil.move 来移动文件，因此会先尝试改名，改名失败再进行复制和删除操作。

https://github.com/ahui2016/ffe/raw/main/recipes/move-new-files.py
# version: 2022-01-11
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

from humanfriendly import format_size
import shutil
from pathlib import Path
from ffe.model import (
    Recipe,
    ErrMsg,
    must_exist,
    get_bool,
    must_folders,
    names_limit,
)


# 每个插件都必须继承 model.py 里的 Recipe
class MoveNewFiles(Recipe):
    @property  # 注意: 必须设为 @property
    def name(self) -> str:
        return "move-new-files"

    @property  # 注意: 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "move-new-files"  # 转移最新的 n 个文件
names = [                 # names 必须是（不多不少）两个文件夹
    'target_dir',         # 第一个是目标文件夹
    'src_dir',            # 第二个是源头文件夹
]

[tasks.options]
n = 1              # 移动多少个最新的文件
suffix = ".jpg"    # 指定文件名的末尾，空字符串表示不限
overwrite = false  # 是否覆盖同名文件
copy_only = false  # 设为 true 则只是复制，不删除源头文件
names = []         # 只有当多个任务组合时才使用此项代替命令行输入

# 注意：本插件在设计上并未对移动大量文件的场景进行优化，建议只用来移动少量文件。
# version: 2022-01-11
"""

    @property  # 注意: 必须设为 @property
    def default_options(self) -> dict:
        return dict(n=1, suffix="", overwrite=False, copy_only=False, names=[])

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.target_dir
        - self.src_dir
        - self.n
        - self.suffix
        - self.overwrite
        - self.copy_only
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        names, err = names_limit(names, 2, 2)
        if err:
            return err
        err = must_exist(names)
        if err:
            return err
        err = must_folders(names)
        if err:
            return err

        self.target_dir = names[0]
        self.src_dir = names[1]

        self.n = options.get("n", 1)
        if self.n < 1:
            return '"n" should be 1 or larger'

        self.suffix = options.get("suffix", "").strip().lower()
        self.overwrite, err = get_bool(options, "overwrite")
        self.copy_only = options.get("copy_only", False)
        return err

    def dry_run(self, really_run: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        src_files, files_size, free_space = self.get_new_files()
        verb = "Copy" if self.copy_only else "Move"
        print(
            f"{verb} [{len(src_files)}] files from [{self.src_dir}] to [{self.target_dir}]"
        )

        print(
            f"files size: {format_size(files_size)}, free space: {format_size(free_space)}"
        )
        if free_space <= files_size:
            return f"Not enough space in {self.target_dir}"

        print_and_move(
            Path(self.target_dir), src_files, self.overwrite, self.copy_only, really_run
        )
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return self.dry_run(really_run=True)

    def get_new_files(self) -> tuple[list[Path], int, int]:
        src_files = Path(self.src_dir).glob("*")
        src_files = [
            x
            for x in src_files
            if x.is_file() and x.__str__().lower().endswith(self.suffix)
        ]
        src_files.sort(key=lambda x: x.lstat().st_ctime, reverse=True)
        src_files = src_files[: self.n]
        files_size = sum([x.lstat().st_size for x in src_files])
        free_space = shutil.disk_usage(self.target_dir).free
        return src_files, files_size, free_space


__recipe__ = MoveNewFiles


def print_and_move(
    dst_folder: Path,
    src_files: list[Path],
    overwrite: bool,
    copy_only: bool,
    really_run: bool = False,
) -> None:
    for src in src_files:
        dst = dst_folder.joinpath(src.name)
        dst_exists = dst.exists()

        # 优先、重点处理覆盖文件的情形。
        if dst_exists and overwrite:
            print(f"-- overwrite {dst}")
            if really_run:
                copy_or_move(src, dst, copy_only)
            continue

        # 不覆盖文件。
        if dst_exists and not overwrite:
            print(f"-- skip {dst}")
            continue

        # 此时 dst 必然不存在，正常移动文件即可。
        verb = "copy" if copy_only else "move"
        print(f"-- {verb} {dst}")
        if really_run:
            copy_or_move(src, dst, copy_only)


def copy_or_move(src: Path, dst: Path, copy_only: bool) -> None:
    if copy_only:
        shutil.copyfile(src, dst)
    else:
        shutil.move(src, dst)
