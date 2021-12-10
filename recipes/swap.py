from ffe.model import Recipe

swap_suffix = "1"
"""临时文件名的后缀"""

swap_limit = 20
"""限制最多可连续添加多少次 swap_suffix, 避免文件名无限变长"""


class Swap(Recipe):
    """对调两个文件名

    只能用于不需要移动文件的情况，比如同一个文件夹（或同一个硬盘分区）内的文件可以操作，
    而跨硬盘分区的文件则无法处理。
    """

    def name(self) -> str:
        return "swap"

    def help(self) -> str:
        return """
对调两个文件名

只能用于不需要移动文件的情况，比如同一个文件夹（或同一个硬盘分区）内的文件可以操作，
而跨硬盘分区的文件则无法处理。
"""

    def default_options(self) -> dict:
        pass

    def validate(self, names: list[str], options: dict) -> None:
        pass

    def exec(self) -> None:
        pass


# 注意，这句代码重要，就是靠这句把 Swap 传递给插件系统。
__recipe__ = Swap
