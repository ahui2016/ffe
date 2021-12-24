"""mimi: 利用 cryptography 进行加密/解密
dependencies = ["cryptography"]

使用本插件时需要用明文保存密码，因此只适用于保密要求不高的情况。
比如发送文件给同事、朋友，或临时保存文件到网盘等，用户避免传输过程泄密或被服务商扫描。
建议使用新密码，不要使用平时的常用密码。
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
import tomli
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, get_bool, names_limit
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
[[tasks]]
recipe = "mimi"   # 秘密：加密/解密
names = [
    'plain.txt',   # 第一个是待加密或解密后的文件（正常）
    'cipher.txt',  # 第二个是待解密或加密后的文件（乱码）
]

[tasks.options]
method = "encrypt"  # 选择 encrypt 或 decrypt
password = ""       # 密码
plain_file = ""     # 只有当多个任务组合时才使用此项代替命令行输入
cipher_file = ""    # 只有当多个任务组合时才使用此项代替命令行输入
overwrite = false   # 如果文件名已存在，是否允许覆盖文件

# 本插件用明文保存密码，因此只适用于保密要求不高的情况。
# 例如发送文件给同事、朋友，或临时保存文件到网盘等，用于避免传输过程泄密或被服务商扫描。
# 建议使用新密码，不要使用平时的常用密码。
# 也可在 ffe-config.toml 里设置 password (参考 https://github.com/ahui2016/ffe/blob/main/examples/ffe-config.toml)
# 你的 ffe-config.toml 文件位置可以用命令 `ffe info -cfg` 查看。
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            method=Method.Encrypt.name,
            password="",
            plain_file="",
            cipher_file="",
            overwrite=False,
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.method
        - self.password
        - self.plain_file
        - self.cipher_file
        - self.overwrite
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        self.overwrite, err = get_bool(options, "overwrite")
        if err:
            return err

        self.password = options.get("password", "")
        if not self.password:
            self.password = get_config_pwd()
        if not self.password:
            return "The password is empty."

        wrong_key = options.get("method", "encrypt")
        method = wrong_key.capitalize()
        try:
            self.method = Method[method]
        except KeyError:
            return (
                f"KeyError: '{wrong_key}'\n"
                "Please set the method to 'encrypt' or 'decrypt'."
            )

        # 优先采用 options 里设置, 方便多个任务组合。
        plain_file = options.get("plain_file", "")
        cipher_file = options.get("cipher_file", "")
        if plain_file:
            names[0] = plain_file
        if cipher_file:
            names[1] = cipher_file

        names, err = names_limit(names, 2, 2)
        if err:
            return err
        self.plain_file = Path(names[0])
        self.cipher_file = Path(names[1])

        match self.method:
            case Method.Encrypt:
                if not self.plain_file.exists():
                    return f"Not Exists: {self.plain_file.__str__()}"
                if (not self.overwrite) and self.cipher_file.exists():
                    return f"Already Exists: {self.cipher_file.__str__()}"
            case Method.Decrypt:
                if not self.cipher_file.exists():
                    return f"Not Exists: {self.cipher_file.__str__()}"
                if (not self.overwrite) and self.plain_file.exists():
                    return f"Already Exists: {self.plain_file.__str__()}"
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        match self.method:
            case Method.Encrypt:
                print(f"'{self.plain_file}' is encrypted to '{self.cipher_file}'")
            case Method.Decrypt:
                print(f"'{self.cipher_file}' is decrypted to '{self.plain_file}'")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        match self.method:
            case Method.Encrypt:
                # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=os.urandom(16),
                    iterations=390_000,
                )
                key = base64.urlsafe_b64encode(
                    kdf.derive(self.password.encode("utf-8"))
                )
                with open(self.plain_file, "rb") as data, open(
                    self.cipher_file, 'wb'
                ) as cipher_file:
                    token = Fernet(key).encrypt(data.read())
                    cipher_file.write(token)
        return self.dry_run()


__recipe__ = Mimi


def get_config_pwd() -> str:
    with open(app_config_file, "rb") as f:
        config = tomli.load(f)
    if config.get("mimi", ""):
        return config["mimi"].get("password", "")
    return ""
