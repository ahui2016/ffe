"""anon: 上传文件到 AnonFiles (匿名文件分享)

上传文件到 anonfiles.com 用于分享或暂存。

AnonFiles 的优点：
1.免费 2.容量大 3.保存时间长 4.国内可直接访问 5.有API 6.匿名
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import requests
import pyperclip
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit
from ffe.util import get_proxies


class Anon(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "anon"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
# 每次只能上传 1 个文件，如果需要一次性上传多个文件，建议先压缩打包。
# dependencies = ["pyperclip"]
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            auto_copy=True,
            key="",
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.filename
        - self.auto_copy
        - self.key
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        self.key = options.get("key", "")
        self.filename = options.get("filename", "")  # 优先采用 options.filename, 方便多个任务组合。
        if not self.filename:
            names, err = names_limit(names, 1, 1)
            if err:
                return err
            self.filename = names[0]
        err = are_names_exist(names)
        if err:
            return err
        self.auto_copy = options.get("auto_copy", True)
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print("There is no dry run for this recipe.")
        print("本插件涉及第三方服务，因此无法提供 dry run.")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        url = "https://api.anonfiles.com/upload"
        if self.key:
            url += f"?token={self.key}"
        with open(self.filename, "rb") as f:
            file = {"file": f}
            print(f"uploading {self.filename} ......")
            resp = requests.post(url, file, proxies=get_proxies())

        resp.raise_for_status()
        result = resp.json()
        if not result["status"]:
            return result["error"]["message"]

        file_url = result["data"]["file"]["full"]
        print(file_url)
        if self.auto_copy:
            pyperclip.copy(file_url)
        return ""


__recipe__ = Anon
