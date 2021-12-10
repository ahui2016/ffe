from abc import ABC, abstractmethod

__default_max__ = 9999
"""默认处理文件数量的上限"""


class Recipe(ABC):
    def __init__(self) -> None:
        self.is_validated = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this recipe.

        注意，应返回一个便于命令行输入的名字，比如中间不要有空格。
        """
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help messages.

        方便在命令行查看每个 recipe 的用途。如果不写清楚，使用者（包括一段时间之后的作者自己）
        就需要查看源文件才能知道具体使用方法了。通常用一个带注释的 TOML 文件即可。
        """
        pass

    @property
    @abstractmethod
    def default_options(self) -> dict:
        pass

    @abstractmethod
    def validate(self, names: list[str], options: dict) -> None:
        """检查参数并进行初始化。

        注意：插件制作者必须保证 validate 是安全的，不可对文件进行任何修改。
             包括文件内容、日期、权限等等任何修改都不允许。
        """
        self.is_validated = True

    @abstractmethod
    def exec(self) -> None:
        assert not self.is_validated, "在执行 exec 之前必须先执行 validate"
