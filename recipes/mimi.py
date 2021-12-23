"""mimi: 利用 cryptography 进行加密/解密
dependencies = ["cryptography"]

使用本插件时需要用明文保存密码，因此只适用于保密要求不高的情况。
比如发送文件给同事、朋友，或临时保存文件到网盘等，用户避免传输过程泄密或被服务商扫描。
建议使用新密码，不要使用平时的常用密码。
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import tomli
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, are_names_exist, names_limit
from ffe.util import app_config_file


class Method(Enum):
    Encrypt = auto()
    Decrypt = auto()


class Mimi(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "mimi"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
使用本插件时需要用明文保存密码，因此只适用于保密要求不高的情况。
比如发送文件给同事、朋友，或临时保存文件到网盘等，用户避免传输过程泄密或被服务商扫描。
建议使用新密码，不要使用平时的常用密码。
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            method=Method.Encrypt,
            password="",
            plain_file="",
            cipher_file="",
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.method
        - self.password
        - self.plain_file
        - self.cipher_file
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        # 优先采用 options 里设置, 方便多个任务组合。
        plain_file = options.get("plain_file", "")
        cipher_file = options.get("cipher_file", "")
        if plain_file:
            names[0] = plain_file
        if cipher_file:
            names[1] = cipher_file

        names, err = names_limit(names, 1, 1)
        if err:
            return err
        err = are_names_exist(names)
        if err:
            return err

        self.password = options.get("password", "")

        return ""


__recipe__ = Mimi


def get_config_key() -> str:
    with open(app_config_file, "rb") as f:
        config = tomli.load(f)
    if config.get("anon", ""):
        return config["anon"].get("key", "")
    return ""
