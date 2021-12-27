# ffe

ffe: File/Folder Extensible manipulator  
可轻松地用 Python 来写插件的文件操作工具


## Install ffe

可使用以下命令进行安装：

```
pip install ffe
```

### 另一种安装方法

另外，还可以使用 pipx 来安装, pipx 会自动为 ffe 创建一个虚拟环境，不会污染系统环境，并且使用时不用管理虚拟环境，直接使用 ffe 命令即可。

先安装 pipx https://pypa.github.io/pipx/

然后

```
pipx install ffe
```

但是要注意，后续安装插件时，插件依赖的第三方库要用 pipx inject 命令来安装，比如 `pipx inject ffe humanfriendly`。


## Install recipes (安装插件)

ffe 本身不解决任何具体问题，比如对文件进行改名、复制、移动等操作全部交给插件去做。你可以自己写插件，或者直接安装别人做好的插件。

**每次安装插件前，请先审查代码**，因为一旦安装，执行任何 ffe 命令都会执行插件里的代码 (自动 import)。由于插件通常很简单, Python 代码也易于阅读，因此只是审查有无恶意代码应该是很轻松的。安装后，插件代码就在本地，只要不升级就不需要重新审查。

安装插件前，可用 --peek 参数阅读插件简介，可用 --donwload-only 参数下载插件代码，例如

```
ffe install -p https://github.com/ahui2016/ffe/raw/main/recipes/swap.py
```

```
ffe install -d https://github.com/ahui2016/ffe/raw/main/recipes/swap.py > swap.py
```

审查代码后，再正式安装
```
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/swap.py
```

### 批量安装

可以用 -p 参数一次性查看多个插件的简介，用 -i 参数批量安装多个插件，例如
```
ffe install -p https://github.com/ahui2016/ffe/raw/main/recipes/recipes.toml
```

```
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/recipes.toml
```

国内如有网络问题，可把以上示例中的网址改为 gitee 地址:

- `https://gitee.com/ipelago/ffe/raw/main/recipes/swap.py`
- `https://gitee.com/ipelago/ffe/raw/main/recipes/recipes.toml`


## 使用插件

安装插件后，可使用 `ffe info -a` 列出全部已安装的插件，使用 `ffe info -r swap` 查看该插件的详细用法 (其中 "swap" 是插件名称)。

使用 `ffe dump -r <recipe> <files...>` 可生成任务计划，例如

```
ffe dump -r swap file1.txt file2.txt > swap.toml
```

以上命令会生成一个内容如下所示的 TOML 文件:
```
[[tasks]]
recipe = "swap"
names = [ "file1.txt", "file2.txt",]

[tasks.options]
verbose = true
```

And then, use `ffe run -f swap.toml` to do the job. You can also run `ffe run -r swap file1.txt file2.txt`, but without a TOML file you cannot set options.

It is recommended to use a **--dry-run** flag when you are not familiar with the recipe yet. for example `ffe run -dry -f swap.toml`.


