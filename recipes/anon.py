"""anon: 上传文件到 AnonFiles (匿名文件分享)
dependencies = ["pyperclip"]

上传文件到 anonfiles.com 用于分享或暂存。

AnonFiles 的优点：
1.免费 2.容量大 3.保存时间长 4.国内可直接访问 5.有API 6.匿名

https://github.com/ahui2016/ffe/raw/main/recipes/anon.py
version: 2022-01-11
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import tomli
import requests
import pyperclip
from ffe.model import (
    Recipe,
    ErrMsg,
    Result,
    must_exist,
    get_bool,
    must_files,
    names_limit,
)
from ffe.util import app_config_file, get_proxies


# 每个插件都必须继承 model.py 里的 Recipe
class Anon(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "anon"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "anon"  # 上传文件到 AnonFiles
names = [        # 每次只能上传一个文件
    'file.jpg',
]

[tasks.options]
auto_copy = true  # 是否自动复制结果到剪贴板
key = ""          # AnonFiles 账号的 key
use_pipe = true   # 是否接受上一个任务的结果

# 每次只能上传 1 个文件，如果需要一次性上传多个文件，建议先压缩打包。
# 不设置 key 也可使用，如果注册了 AnonFiles 并且设置了 key, 可登入 AnonFiles 的账号查看已上传文件的列表。
# 也可在 ffe-config.toml 里设置 key (参考 https://github.com/ahui2016/ffe/blob/main/examples/ffe-config.toml)
# 你的 ffe-config.toml 文件位置可以用命令 `ffe info -cfg` 查看。
# version: 2022-01-11
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            auto_copy=True,
            key="",
            use_pipe=False,
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.filename
        - self.auto_copy
        - self.key
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        self.auto_copy, err = get_bool(options, "auto_copy")
        if err:
            return err

        self.key = options.get("key", "")
        if not self.key:
            self.key = get_config_key()

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        names, err = names_limit(names, 1, 1)
        if err:
            return err
        self.filename = names[0]

        err = must_exist(names)
        if err:
            return err
        return must_files(names)

    def dry_run(self) -> Result:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print("There is no dry run for this recipe.")
        print("本插件涉及第三方服务，因此无法提供 dry run.")
        return [], ""

    def exec(self) -> Result:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        url = "https://api.anonfiles.com/upload"
        if self.key:
            url += f"?token={self.key}"
        with open(self.filename, "rb") as f:
            print(f"uploading {self.filename} ......")
            resp = requests.post(url, files={"file": f}, proxies=get_proxies())

        resp.raise_for_status()
        result = resp.json()
        if not result["status"]:
            return result["error"]["message"]

        file_url = result["data"]["file"]["url"]["full"]
        print(file_url)
        if self.auto_copy:
            print("Auto copy to clipboard: True")
            pyperclip.copy(file_url)
        return [], ""


__recipe__ = Anon


def get_config_key() -> str:
    with open(app_config_file, "rb") as f:
        config = tomli.load(f)
    if config.get("anon", ""):
        return config["anon"].get("key", "")
    return ""
