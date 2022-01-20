"""ibm-delete: 删除 IBM COS 中的文件
dependencies = ["arrow", "humanfriendly", "ibm-cos-sdk"] (另外还依赖 recipes/common_ibm.py)

本插件用于删除原本由 ibm-upload 上传到 IBM COS 中的文件。

https://github.com/ahui2016/ffe/raw/main/recipes/common_ibm.py
https://github.com/ahui2016/ffe/raw/main/recipes/ibm-delete.py
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import json
import arrow
from humanfriendly import format_size
from ffe.model import (
    Recipe,
    ErrMsg,
    Result,
    names_limit,
)
from ffe.util import get_proxies
from common_ibm import (
    FilesSummary,
    delete_items,
    files_summary_name,
    get_by_prefix,
    get_config,
    get_files_summary,
    get_ibm_client,
    get_ibm_resource,
    put_text_file,
)

# 每个插件都必须继承 model.py 里的 Recipe
class IBMDelete(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "ibm-delete"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "ibm-delete"  # 删除 IBM COS 中的文件
names = [              # 文件的前缀，每次最多只可填写 1 个前缀
    '20220115'         # 使用 ibm-upload 上传文件时会自动添加日期前缀
]                      # 如果 names 为空，则打印文件数量统计结果

[tasks.options]
use_pipe = true  # 是否接受上一个任务的结果

# 本插件与 ibm-upload 搭配使用，用于删除由 ibm-upload 上传的文件。
# 使用本插件前必须正确设置 ibm-upload, 具体方法请使用命令 'ffe info -r ibm-upload' 查看。
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            use_pipe=False,
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.prefix
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        # set self.prefix
        names, err = names_limit(names, 0, 1)
        if err:
            return err
        if names:
            self.prefix = names[0]
        else:
            self.prefix = ""

        return ""

    def dry_run(self, really_run: bool = False) -> Result:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        cfg_ibm = get_config()
        cos = get_ibm_resource(cfg_ibm, get_proxies())
        bucket_name = cfg_ibm["bucket_name"]

        # 如未指定前缀，则打印 files-summary
        if not self.prefix:
            print("Retrieving files summary...")
            summary: FilesSummary = get_files_summary(cos, bucket_name)
            total = 0
            for date, n in summary["date_count"].items():
                print(f"{arrow.get(date).format('YYYY-MM-DD')}  {n}")
                total += n
            print(f"\nTotal: {total} files")
            return [], ""

        objects = []
        for item in get_by_prefix(cos, bucket_name, self.prefix):
            objects.append(dict(Key=item.key))
            if not really_run:
                print(f"({format_size(item.size)}) {item.key}")

        if not objects:
            print(f"There's no item starts with '{self.prefix}'.")
            if self.prefix.find("-") >= 0:
                print(f"前缀通常是一个日期，没有短横线，例如: '20220101'.")
        else:
            if really_run:
                cos_client = get_ibm_client(cfg_ibm, get_proxies())
                deleted = delete_items(cos_client, bucket_name, objects)
                for item in deleted:
                    print(f"Delete {item['Key']}")
                if deleted:
                    print(f"Update files counter...")
                    summary = get_files_summary(cos, bucket_name)
                    n = summary["date_count"].get(self.prefix, 0)
                    n -= len(deleted)
                    if n <= 0:
                        # 如果一个日期没有文件了，就删除它。
                        del summary["date_count"][self.prefix]
                    else:
                        summary["date_count"][self.prefix] = n
                    summary_json = json.dumps(summary)
                    put_text_file(cos, bucket_name, files_summary_name, summary_json)
                    print("OK.")

        return [], ""

    def exec(self) -> Result:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        return self.dry_run(really_run=True)


__recipe__ = IBMDelete
