"""one-way-sync: 单向同步

可选择按日期 及/或 按内容对比文件。
新增(add), 更新(update), 删除(delete) 三种情况均可单独控制。
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit


class OneWaySync(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "one-way-sync"

    @property  # 必须设为 @property
    def help(self) -> str:
        return "coming soon... (本插件正在施工中)"

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            add=True,
            update=True,
            delete=False,
            by_date=False,
            by_content=True,
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.add
        - self.update
        - self.delete
        - self.by_date
        - self.by_content
        - self.ignore
        - self.dst_dir
        - self.names
        """
        names, err = names_limit(names, 1)
        if err:
            return err
        err = are_names_exist(names)
        if err:
            return err

        return ""

    def dry_run(self, really_move: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        return "coming soon... (本插件正在施工中)"

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return "coming soon... (本插件正在施工中)"


__recipe__ = OneWaySync
