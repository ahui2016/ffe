# ffe

ffe: File/Folder Extensible manipulator  
可轻松地用 Python 来写插件的文件操作工具


## Install ffe

ffe 使用了 Python 3.10 的新特性，比如 type union operator, pattern matching 等，因此，如果你的系统中未安装 Python 3.10, 推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或 [miniconda](https://docs.conda.io/en/latest/miniconda.html) 来安装最新版本的 Python。

可使用以下命令进行安装 ffe:

```sh
pip install ffe
```

### 另一种安装方法

另外，还可以使用 pipx 来安装, pipx 会自动为 ffe 创建一个虚拟环境，不会污染系统环境，并且使用时不用管理虚拟环境，直接使用 ffe 命令即可。

pipx 的介绍及安装方法: https://pypa.github.io/pipx/

```sh
pipx install ffe
```

但是要注意，后续安装插件时，插件依赖的第三方库要用 pipx inject 命令来安装，比如 `pipx inject ffe humanfriendly`。


## Install recipes (安装插件)

ffe 本身不解决任何具体问题，比如对文件进行改名、复制、移动等操作全部交给插件去做。你可以自己写插件，或者直接安装别人做好的插件。

**每次安装插件前，请先审查代码**，因为一旦安装，执行任何 ffe 命令都会执行插件里的代码 (自动 import)。由于插件通常很简单, Python 代码也易于阅读，因此只是审查有无恶意代码应该是很轻松的。安装后，插件代码就在本地，只要不升级就不需要重新审查。

安装插件前，可用 --peek 参数阅读插件简介，可用 --donwload-only 参数下载插件代码，例如

```sh
ffe install -p https://github.com/ahui2016/ffe/raw/main/recipes/swap.py
```

```sh
ffe install -d https://github.com/ahui2016/ffe/raw/main/recipes/swap.py > swap.py
```

审查代码后，再正式安装

```sh
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/swap.py
```

### 批量安装

可以用 -p 参数一次性查看多个插件的简介，用 -i 参数批量安装多个插件，例如

```sh
ffe install -p https://github.com/ahui2016/ffe/raw/main/recipes/recipes.toml
```

```sh
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/recipes.toml
```

### 国内网络问题

如果遇到国内网络问题，可把以上示例中的网址改为 gitee 地址:

- `https://gitee.com/ipelago/ffe/raw/main/recipes/swap.py`
- `https://gitee.com/ipelago/ffe/raw/main/recipes/recipes-gitee.toml`

另外，也可以设置 proxy, 比如

```
ffe info --set-proxy http://127.0.0.1:1081
```


## 使用插件

安装插件后，可使用 `ffe info -a` 列出全部已安装的插件，使用 `ffe info -r swap` 查看该插件的详细用法 (其中 "swap" 是插件名称)。

使用 `ffe dump -r <recipe> <files...>` 可生成任务计划，例如

```sh
ffe dump -r swap file1.txt file2.txt > swap.toml
```

以上命令会生成一个内容如下所示的 TOML 文件:

```toml
[[tasks]]
recipe = "swap"
names = [ "file1.txt", "file2.txt",]

[tasks.options]
verbose = true
```

然后用 ffe run 命令，比如 `ffe run -f swap.toml` 即可执行任务，另外，也可以不使用 TOML 文件，直接运行 `ffe run -r swap file1.txt file2.txt`, 但必须使用 toml 文件才能设置 options, 而且一个 toml 文件内可包含多个任务，按顺序依次执行。

建议在不熟悉的时候多用 --dry-run 参数，比如 `ffe run -dry -f swap.toml` 可以在安全（不修改文件）的前提下尽量预测运行结果。

（dry run 具体如何预测运行结果，需要插件作者实现 dry_run 方法，但这个有套路，比如检查参数是否符合要求，文件是否真实存在等等，具体参考已经写好的插件代码。）


## 帮助信息

可以使用以下命令获取帮助信息：

- `ffe --help`
- `ffe info --help`
- `ffe info -r <recipe>` 等等

更详细的介绍看这里 [details.md](details.md)

另外，欢迎通过 issue 提交插件，我会不定期整理第三方插件列表。
