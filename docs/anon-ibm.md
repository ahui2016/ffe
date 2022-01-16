# 推荐两个免费、有API、国内可直接访问的文件储存/分享服务（以及相关Python脚本）

## 第一个是 anonfiles.com

优点：

1. 免费
2. 容量大
3. 保存时间长
4. 国内可直接访问
5. 有 API (且非常非常简单易用)
6. 匿名

缺点：

1. 只有上传 API, 没有获取文件列表、删除文件等 API
2. 登录页面不稳定（经常打不开）

## 第二个是 IBM Cloud 对象储存

https://www.ibm.com/cloud/object-storage 优点：

1. 有免费套餐
2. 国内可直接访问
3. 有 Smart Tier (一种方便好用且性价比高的计费方案)
4. 有 API (并且有多种语言的 SDK)
5. 功能强大

缺点：

1. 需要登记信用卡信息（但选择 COS Lite Plan 按理说是不会产生费用的）
2. 免费套餐有容量、次数的限制（每月恢复，一般够用，由于不登记信用卡因此超了也不怕产生费用）
3. 声称免费用户不活动 30 天就有可能删除资料（虽然我试过不活动 1 年也没事）
4. 设置比较麻烦

## 安装相关 Python 脚本

我写了几个脚本来方便上传文件，为了让脚本更容易管理、并且方便与压缩打包、加密等插件组合使用，我把脚本做成了 ffe 的插件，因此需要先安装 ffe (安装方法看这里: https://github.com/ahui2016/ffe/blob/main/docs/usage.md ) 但是当然也可以不安装 ffe, 参考源码稍稍修改一下就是个独立的脚本了。

安装了 ffe 之后，用以下命令安装相关脚本：

```sh
ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/anon-ibm.toml
```

如果遇到网络问题，也可以使用 gitee 地址：

```sh
ffe install -i https://gitee.com/ipelago/ffe/raw/main/recipes/anon-ibm-gitee.toml
```

最后安装依赖 `pip install pyperclip arrow humanfriendly ibm-cos-sdk`

完成。

## 使用方法

### AnonFiles

使用命令 `ffe run -r anon file.txt` 即可把 file.txt 匿名上传到 AnonFiles, 并且自动复制分享地址到剪贴板（也可设置不自动复制），任何人访问该分享地址均可下载文件。

如果你注册了 AnonFiles 账号，可以获得一个 key, 使用命令 `ffe info -r anon` 可以查看设置 key 的方法。关于 ffe 使用方法的详细说明请看 https://github.com/ahui2016/ffe/blob/main/docs/usage.md

### IBM COS

由于 IBM COS 的功能更强大，因此我为它写了两个脚本，其中一个专门负责上传。

使用命令 `ffe run -r ibm-upload file.txt` 即可上传文件 file.txt, 根据默认设定，在 IBM COS 里会自动为该文件添加前缀，因此在 IBM COS 里的文件名是像这个样子的 20220114184907-file.txt

由于对象储存对 “用文件名前缀进行检索” 进行了优化，因此后续可以非常方便地检索或删除某年、或某月、或精确到某天的全部文件。

但要注意，使用 ibm-upload 之前需要注册 IBM Cloud 账号并设置 ibm_api_key_id 等相关信息，具体方法请使用命令 `ffe info -r ibm-upload` 查看（设置这些信息比较麻烦，有任何问题可以问我）。

### ibm-delete

使用命令 `ffe run -r ibm-delete` 可以查看已经上传了多少文件，输出结果类似这样：

```txt
recipe: ibm-delete
Retrieving files summary...

2022-01-13  2
2022-01-14  3

Total: 5 files
```

使用命令 `ffe run -r ibm-delete 20220113 -dry` （注意一定要加 `-dry`）可以进一步查看具体的文件名。其中 20220113 意思是一月十三日的文件，也可以使用 202201 来指定一月的全部文件，或者用 2022011308 来指定 1月13日 08:00至09:00 之间的文件，非常灵活。

使用命令 `ffe run -r ibm-delete 20220113` 删除 IBM COS 里的文件，与上面查看文件名的命令的差别只是没有 `-dry`, `-dry` 在 ffe 里是 dry run 的意思，用来预估执行结果。

## 组合拳

ffe 的各个插件可以灵活组合使用。

使用命令 `ffe dump -r anon file.txt > anon.toml` 可以生成一个 TOML 文件，里面可以编辑各项参数。

把多个任务的 TOML 内容复制到一个文件里，就可以形成一个组合，比如：

```toml
[[tasks]]
recipe = "tar-xz"  # 第一个任务：打包压缩
names = [
  'file1.txt',
  'file2.txt',
]
[tasks.options]
output = "files"
auto_wrap = true
zip_overwrite = false

[[tasks]]
recipe = "anon"    # 第二个任务：匿名上传
names = [
  'files.tar.xz',
]
[tasks.options]
auto_copy = true
key = ""
```

然后使用命令 `ffe run -f tar-anon.toml` 即可一次性完成打包和上传。这个方法适用于一些需要经常重复操作的事情，写好 TOML 文件后就可以轻松打出一套组合拳。
