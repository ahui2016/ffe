# ffe

ffe: File/Folder Extensible manipulator
可轻松地用 Python 来写插件的文件操作工具


## 项目灵感来源

最开始，我只是想写一个 "调换两个文件名" 的脚本，写好了又想写 "压缩加密上传一条龙" 的脚本，然后我就想，写一大堆脚本看起来一盘散沙，不整齐，而且对命令行的处理、对 TOML 文件的处理又有很多可以共用的代码。

于是我就想把这些脚本集合起来变成一个多功能软件，很自然就想到采用插件的方式比较合理，就这样做出了一个命令行插件工具，第一版是用 Go 语言做的 (看这里 https://v2ex.com/t/820116 ), 后来觉得还是用 Python 做比较合理，就有了这个项目。

### ffe 解决什么问题

在日常使用电脑的过程中，总有一些关于文件/文件夹的操作是有规律、有重复性的，比如：

- 对调两个文件的文件名
- 批量修改文件名
- 把指定文件备份到指定文件夹，并自动改名
- 把指定文件移动到指定文件夹，并自动删除超过 n 天的旧文件
- 复制文件并且在复制结束后校验文件完整性
- 压缩、加密、上传文件
- 按你喜欢的方式单向/双向同步两个文件夹（具体就看扩展代码怎样写了）
- ……等等


## ffe 本身的功能

ffe 本身不解决任何具体问题，比如对文件进行改名、复制、移动等操作全部交给插件去做。

ffe 为你提供以下服务：

- **install**: 你只需要把插件代码放在 github 或 gitee 之类的仓库中，任何人都能使用 ffe install 命令来安装你写的插件。
- **download**: 正式安装插件前可先下载代码，审查后再安装。
- **peek**: 下载或安装插件前阅读插件的简单介绍。
- **info**: 查看插件的帮助文档。
- **dump**: 在执行任务前查看任务计划，并且可生成 toml 文件。
- **dry run**: 在正式执行任务前，安全地（不修改文件）预测运行结果。
- **toml**: 通过 toml 文件来输入参数，一个 toml 文件可包含多个任务，用 `ffe run -f <recipe.toml>` 命令即可一次性按顺序执行多个任务。
- **proxy**: 涉及网络操作时，可设置代理。

对于插件作者来说，只需要专注于具体的业务逻辑即可，按照套路填写一些信息后就能获得以上全部功能。

对于用户来说，可以在安装前查看插件简介，可批量安装插件，不同的插件可以组合使用。

另外, CLI 与 TOML 的配合效果很不错, TOML 很直观，容易编辑，比纯 CLI 更直观，又比 GUI 更容易编程开发。(参考: [toml.io](https://toml.io))


## 安装方法

安装方法看这里 [usage.md](usage.md)


## 插件使用示例

- 以下内容假设你已经安装了 ffe, 并且已仔细阅读 [usage.md](usage.md) 的内容。
- 以下内容中涉及 github 的网址，如果遇到网络问题，可参照 [usage.md](usage.md) 里的说明设置 proxy, 或者使用这个文件 https://gitee.com/ipelago/ffe/raw/main/recipes/recipes-gitee.toml 里的网址来代替。

### 匿名上传分享文件(AnonFiles)

最近我发现了一个神奇的网站 anonfiles.com, 它的优点是：

1.免费   2.容量大   3.保存时间长   4.国内可直接访问   5.有API   6.匿名

其中有 API 是我最看重的优点，而且它的 API 非常简单易用。

我做了一个名为 anon 的插件，可使用以下命令安装该插件

```sh
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/anon.py
```

安装后，使用命令 `ffe run -r anon <file>` 即可匿名上传文件，上传成功后会自动复制分享地址到剪贴板。

使用命令 `ffe info -r anon` 可查看使用说明。

### 任务组合

有时，我希望先压缩文件，再加密文件，最后上传到 AnonFile, 本来可以把这些功能全都做到一个插件里，但为了作为一个“任务组合”的例子，我把这些功能拆分为几个插件了。

拆分也有好处，因为有时候只想加密，有时只想压缩打包，而且拆分后程序代码也变得更好理解。

- 打包压缩的插件是 https://github.com/ahui2016/ffe/raw/main/recipes/tar-xz.py
- 加密的插件是 https://github.com/ahui2016/ffe/raw/main/recipes/mimi.py

可逐个单独安装，也可以使用以下命令一次性安装我提供的全部插件：

```sh
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/recipes.toml
```

安装后，使用 dump 命令可以生成 TOML 文件，比如 `ffe dump -r mimi <file>`, 把多个任务的 TOML 内容复制到一个文件里，就可以形成一个组合，比如：

```toml
[[tasks]]
recipe = "mimi"    # 第一个任务：加密
names = [
  'file.txt',
]

[tasks.options]
suffix = ".mimi"
overwrite = false

[[tasks]]
recipe = "anon"    # 第二个任务：匿名上传
names = [
  'file.txt.mimi',
]

[tasks.options]
auto_copy = true
key = ""
names = []
```

然后使用命令 `ffe run -f mimi-anon.toml` 即可依次执行任务。如果有一个文件需要经常加密上传，这个任务组合就很方便了。还可以把打包压缩、删除文件等任务都添加进去，这甚至比 GUI 工具更灵活，编辑 TOML 文件也很直观。

### options

- 使用 `ffe dump -r <recipe>` 可查看一个插件的默认 options
- 使用 `ffe run -r <recipe>` 的方式执行任务时，只能使用默认的 options
- 如果想修改 options 就必须使用 TOML 文件
- 在 TOML 文件里可以填写 names, 然后用 `ffe run -f recipe.toml file1.jpg file2.jpg` 的方式来指定文件。
- 还可以用 `ffe dump -f recipe.toml file1.txt` 的方式来预览任务计划。

### 使用建议

- 使用 ffe 前请先认真阅读 [usage.md](usage.md)
- 对于不熟悉的插件，建议多使用 dump 和 install -dry 来预估运行结果。
