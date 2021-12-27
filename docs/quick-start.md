# ffe

ffe: File/Folder Extensible manipulator  
可轻松地用 Python 来写插件的文件操作工具

Chinese readme (中文说明，更详细): [quick-start.md](docs/quick-start.md) [details.md](docs/details.md)

## Install ffe

```
python -m pip install ffe
```

## Install recipes

Ffe by it self can do nothing, you can write recipes yourself or download recipes written by others.

Please always inspect the recipe before installing it. For example,

Use `ffe install --peek https://github.com/ahui2016/ffe/raw/main/recipes/swap.py` to read a short description of the recipe.

Use `ffe install -d https://github.com/ahui2016/ffe/raw/main/recipes/swap.py` to download it, the content will be print to the screen, you can also use `ffe install -d http://example.com/recipe.py > recipe.py` to create a file.

After inspection, use `ffe install -i https://github.com/ahui2016/ffe/raw/main/recipes/swap.py` to install it.

Now, you can use `ffe info -a` to list out all installed recipes, and use `ffe info -r swap` the read more about the recipe (change swap to another recipe's name as you want).


## Use a recipe

Use `ffe info -r <recipe>` the read more about a recipe, or use `ffe dump -r <recipe> <files...>` to generate a plan of tasks, for example

```
ffe dump -r swap file1.txt file2.txt > swap.toml
```

will generate a TOML file as below:
```
[[tasks]]
recipe = "swap"
names = [ "file1.txt", "file2.txt",]

[tasks.options]
verbose = true
```

And then, use `ffe run -f swap.toml` to do the job. You can also run `ffe run -r swap file1.txt file2.txt`, but without a TOML file you cannot set options.

It is recommended to use a **--dry-run** flag when you are not familiar with the recipe yet. for example `ffe run -dry -f swap.toml`.


