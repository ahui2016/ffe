"""ibm-upload: 上传文件到 IBM COS
dependencies = ["arrow", "ibm-cos-sdk"] (另外还依赖 recipes/common_ibm.py)

IBM COS 的优点：
1.有免费套餐  2.不需要登记信用卡  3.国内可直接访问  4.有Smart Tier

缺点：免费用户 30 天不活动，数据有可能被删除。

https://github.com/ahui2016/ffe/raw/main/recipes/common_ibm.py
https://github.com/ahui2016/ffe/raw/main/recipes/ibm-upload.py
version: 2022-01-14
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import arrow
import json
from pathlib import Path
from ffe.model import (
    Recipe,
    ErrMsg,
    filesize_limit,
    get_bool,
    must_exist,
    must_files,
    names_limit,
    MB,
)
from ffe.util import get_proxies

from common_ibm import (
    default_limit,
    files_summary_name,
    get_config,
    get_files_summary,
    get_ibm_resource,
    put_text_file,
    upload,
)

# 每个插件都必须继承 model.py 里的 Recipe
class IBMUpload(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "ibm-upload"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "ibm-upload"  # 上传文件到 IBM COS
names = [              # 每次只能上传一个文件
    'file.tar.gz'      # 如果需要上传多个文件建议先打包
]

[tasks.options]
add_prefix = true  # 是否自动添加前缀
size_limit = 0     # 单位:MB, 设为 0 则采用默认上限
names = []  # 只有当多个任务组合时才使用此项代替命令行输入

# 使用本插件需要 IBM Cloud 账号：
# - 注册一个 cloud.ibm.com 账号
# - 启用 IBM Cloud Object Storage 并且创建一个 bucket https://cloud.ibm.com/objectstorage/create
# - pip install ibm-cos-sdk
# - 收集必要参数 https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-prereqs
# - 把相关信息填写到 ffe-config.toml (参考 https://github.com/ahui2016/ffe/blob/main/examples/ffe-config.toml)
# version: 2022-01-14
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            add_prefix=True,
            size_limit=0,
            names=[],
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.item_name
        - self.size_limit
        - self.filename
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # set self.size_limit
        limit = options.get("size_limit", 0)
        if not limit:
            limit = default_limit
        self.size_limit = limit

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        # set self.filename
        names, err = names_limit(names, 1, 1)
        if err:
            return err
        self.filename = names[0]

        err = must_exist(names)
        if err:
            return err
        err = must_files(names)
        if err:
            return err
        err = filesize_limit(self.filename, self.size_limit)
        if err:
            return err

        # set self.item_name
        add_prefix, err = get_bool(options, "add_prefix")
        if err:
            return err
        self.item_name = Path(self.filename).name
        if add_prefix:
            prefix = f"{arrow.now().format('YYYYMMDDHHmmss')}-"
            self.item_name = prefix + self.item_name

        return ""

    def dry_run(self, really_run: bool = False) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print(f"Upload file: {self.filename}")
        print(f"as name: {self.item_name} in IBM COS")
        print(f"file size: {Path(self.filename).lstat().st_size/MB:.4f} MB")
        if not really_run:
            print("本插件涉及第三方服务，因此无法继续预测执行结果。")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        self.dry_run(really_run=True)

        cfg_ibm = get_config()
        cos = get_ibm_resource(cfg_ibm, get_proxies())
        bucket_name = cfg_ibm["bucket_name"]
        upload(cos, bucket_name, self.item_name, self.size_limit, self.filename)

        # 更新计数器
        print(f"Update files counter...")
        summary = get_files_summary(cos, bucket_name, files_summary_name)
        today = self.item_name[:8]
        n = summary["date_count"].get(today, 0)
        summary["date_count"][today] = n + 1
        summary_json = json.dumps(summary)
        put_text_file(cos, bucket_name, files_summary_name, summary_json)
        print("OK.")
        return ""


__recipe__ = IBMUpload
