# ffe

ffe: File/Folder Extensible manipulator
可轻松地用 Python 来写插件的文件操作工具

在日常使用电脑的过程中，总有一些关于文件/文件夹的操作是有规律、有重复性的，比如：

- 对调两个文件的文件名
- 批量修改文件名
- 把指定文件备份到指定文件夹，并自动改名
- 把指定文件移动到指定文件夹，并自动删除超过 n 天的旧文件
- 复制文件并且在复制结束后校验文件完整性
- 按你喜欢的方式单向/双向同步两个文件夹（具体就看扩展代码怎样写了）
- ……等等

dry_run 会尽量检查可能发生的错误，建议先 dry_run 一次。

Warning: Please download and inspect recipes before installing them.

提醒：请先下载 url 指向的文件，检查没有恶意代码后再安装，因为一旦安装，下次执行任何 ffe 命令都会自动执行其代码（自动 import）。

另外提供 recipes-gitee.toml

用户通过命令输入的 names 拥有最高优先级，但要注意一个 toml 文件包含多个任务，那么每个任务的 names 都会被命令行输入的 names 覆盖。

每个插件的简介里写明 dependencies, 另外专门做一个全部插件的 requirements.txt

处理 unicode 问题
