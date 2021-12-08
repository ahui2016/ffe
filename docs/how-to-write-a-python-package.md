# 从零开始做一个 Python 软件

我以前曾学过 Python, 但用得不算多, 后来有几年完全没有使用 Python, 现在已经忘得差不多了. 趁着这次重新使用 Python, 顺便把这个 "复习+学习" 的过程记录下来.

## 1. 变量的作用域非常重要

因此, 复习的时候, 我首先就找变量作用域的教程来看, 主要搞懂 nonlocal 和 global 就可以了, 不需要研究得太深.

## 2. 如何引用模块

如何引用 (import), 以及怎样组织代码 (packages and sub-packages), 也是了解个大概就可以了.

## 3. 类(class)

受到 Go 的影响 (最近几年我用 Go 比较多), 我会尽量不去使用 "继承" 的特性, 但 class 对于更有条理地组织代码是很有帮助的.

同样是 Go 的影响, 我寻找类似 interface 的东西, 找到了 Abstract Base Classes, 另外再了解 classmethod 与 staticmethod 这两个重要概念, 我认为暂时就够用了.

## 4. 库(libraries)

这次我用 Python, 是想写一个可以轻松写插件的文件/文件夹操作工具, 是个纯命令行程序, 并且用 YAML 或 TOML 来方便用户输入参数.

在实际动手写程序之前, 我习惯先找一下相关的库, 确定项目的可行性, 如果找不到相关的库, 或者看起来很不好用, 我就要考虑换语言了.

结果找到 importlib, Click, tomli 等库, 看起来都很不错.

## 5. 为发布软件做准备

以前我写程序不考虑发布出去给别人用, 但后来 GitHub 流行了, 恰巧用 Go 写的软件只需要发布在 GitHub 即可, 我就顺便发布了. 因此现在写程序已经习惯了考虑如何发布.

Python 程序的发布中心是 pypi.org, 为了避免用户名或程序名与别人冲突, 到时写好程序才发现可能就要改名, 因此我先去 pypi 注册.

## 6. 正确的目录结构

发布到 pypi.org 的程序必须有正确的目录结构, 以及一些配置文件 (比如项目名称, 版本号等), 在这里有详细说明 https://packaging.python.org/tutorials/packaging-projects/

另外找到一个帮助打包的好东西 https://github.com/pypa/flit

## 7. 虚拟环境 (virtualenv)

对于 Python 来说，虚拟环境非常重要，因此 Python 里有很多工具帮助解决这个问题，官方也提供了工具。一般来说，官方的工具就够用了，详见官方文档 https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

## 8. 生成可执行命令

有的 Python 程序当作一个库来使用，那就正常写程序就行，而如果要当作一个命令行程序来运行，可采用这种方法 https://click.palletsprojects.com/en/8.0.x/setuptools/#setuptools-integration 

采用这个方法时要注意两点：
  - setup.cfg 里的 entry_points, 相当于 pyproject.toml 里的 project.scripts
  - 要注意目录结构，在上面的 click 网站链接里有说明，注意看就行。

采用上述方法后，可在项目根目录用命令 `pip install --editable .` 进行本地安装，只需要本地安装一次，修改代码无需再次安装。

## 9. 格式化, 语法检查

还是受到 Go 的影响, Go 从一开始就强调代码格式化的重要性并且官方自带 formatter (当然, 只是说我受到 Go 的影响, 事实上各种语言都很重视这方面的工具), 很高兴在 Python 这边也找到了优秀的工具: Black 和 Flake8

