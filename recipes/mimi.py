"""mimi: 利用 cryptography 进行加密/解密
dependencies = ["cryptography"]

本插件加密时把随机生成的 key 混在加密后的数据里，因此加密、解密都不需要输入密码，
但只适用于保密要求不高的情况，比如发送文件给同事、朋友，或暂时保存文件到网盘等，
用于避免传输过程泄密或被服务商扫描，对于保密要求不高的情况已经够用了。
缺点：保密性不高；优点：非常方便，不需要密码。

https://github.com/ahui2016/ffe/raw/main/recipes/mimi.py
# version: 2022-01-11
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

from cryptography.fernet import Fernet
from pathlib import Path
from enum import Enum, auto
from ffe.model import Recipe, ErrMsg, get_bool, must_exist, must_files, names_limit


len_of_key = 43
len_of_head = 15
default_suffix = ".mimi"


class Method(Enum):
    Encrypt = auto()
    Decrypt = auto()


# 每个插件都必须继承 model.py 里的 Recipe
class Mimi(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "mimi"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """
[[tasks]]
recipe = "mimi"     # 秘密：加密/解密
names = [           # 每次只能处理一个文件
  'plain.txt.mimi'  # 后缀名 '.mimi' 表示需要解密，否则表示需要加密
]

[tasks.options]
suffix = ".mimi"   # 已加密文件的后缀名(如果省略，则默认为 '.mimi')
overwrite = false  # 如果文件名已存在，是否允许覆盖文件
names = [          # 只有当多个任务组合时才使用此项代替命令行输入
  'file.txt'
]

# 本插件加密时把随机生成的 key 混在加密后的数据里，因此加密、解密都不需要输入密码，
# 但只适用于保密要求不高的情况，比如发送文件给同事、朋友，或暂时保存文件到网盘等，
# 用于避免传输过程泄密或被服务商扫描，对于保密要求不高的情况已经够用了。
# version: 2022-01-11
"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict(
            suffix=default_suffix,
            overwrite=False,
            names=[],
        )

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：

        - self.method
        - self.plain_file
        - self.cipher_file
        - self.overwrite
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True

        self.overwrite, err = get_bool(options, "overwrite")
        if err:
            return err

        self.suffix = options.get("suffix", "")
        if not self.suffix:
            self.suffix = default_suffix

        # 优先采用 options 里的 names, 方便多个任务组合。
        options_names = options.get("names", [])
        if options_names:
            names = options_names

        names, err = names_limit(names, 1, 1)
        if err:
            return err
        filepath = Path(names[0])
        if filepath.suffix == self.suffix:
            self.method = Method.Decrypt
            self.cipher_file = filepath
            self.plain_file = filepath.with_suffix("")
        else:
            self.method = Method.Encrypt
            self.plain_file = filepath
            suffix = filepath.suffix + self.suffix
            self.cipher_file = filepath.with_suffix(suffix)

        match self.method:
            case Method.Encrypt:
                err = must_exist([self.plain_file])
                if err:
                    return err
                err = must_files([self.plain_file])
                if err:
                    return err
                if (not self.overwrite) and self.cipher_file.exists():
                    return f"Already Exists: {self.cipher_file}"
            case Method.Decrypt:
                err = must_exist([self.cipher_file])
                if err:
                    return err
                err = must_files([self.cipher_file])
                if err:
                    return err
                if (not self.overwrite) and self.plain_file.exists():
                    return f"Already Exists: {self.plain_file}"
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"

        if self.overwrite:
            print("overwrite: True")

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
                # https://cryptography.io/en/latest/fernet/
                key = Fernet.generate_key()
                with open(self.plain_file, "rb") as data, open(
                    self.cipher_file, "wb"
                ) as cipher_file:
                    token = Fernet(key).encrypt(data.read())
                    head, tail = token[:len_of_head], token[len_of_head:]
                    cipher_file.write(head + key[:-1] + tail)
            case Method.Decrypt:
                with open(self.cipher_file, "rb") as blob, open(
                    self.plain_file, "wb"
                ) as plain_file:
                    blob_bytes = blob.read()
                    head, key, tail = (
                        blob_bytes[:len_of_head],
                        blob_bytes[len_of_head : len_of_head + len_of_key] + b"=",
                        blob_bytes[len_of_head + len_of_key :],
                    )
                    plain_data = Fernet(key).decrypt(head + tail)
                    plain_file.write(plain_data)
        return self.dry_run()


__recipe__ = Mimi
