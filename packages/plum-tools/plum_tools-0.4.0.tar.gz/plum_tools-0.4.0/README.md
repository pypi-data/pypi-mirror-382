# linux 小工具

[![LICENSE](https://img.shields.io/github/license/seekplum/plum_tools.svg)](https://github.com/seekplum/plum_tools/blob/master/LICENSE)[![travis-ci](https://travis-ci.org/seekplum/plum_tools.svg?branch=master)](https://travis-ci.org/seekplum/plum_tools)[![coveralls](https://coveralls.io/repos/github/seekplum/plum_tools/badge.svg?branch=master)](https://coveralls.io/github/seekplum/plum_tools?branch=master) [![pypi version](https://img.shields.io/pypi/v/plum_tools.svg)](https://pypi.python.org/pypi/plum_tools) [![pyversions](https://img.shields.io/pypi/pyversions/plum_tools.svg)](https://pypi.python.org/pypi/plum_tools)

## 目录结构

```text
➜  tree -L 1 -a
.
├── .bumpversion.cfg    # `bumpversion`工具的配置文件，用于自动更新版本
├── .env                # 环境变量配置,`不会提交到gitlab中`
├── .gitignore          # 维护git仓库需要忽略文件
├── .gitlab-ci.yml      # gitlab ci的配置文件
├── .pylintrc           # pylint 配置文件
├── CHANGELOG.md        # 记录模块的变化
├── MANIFEST.in         # 打包时添加文件或移除文件等的配置
├── Pipfile             # python依赖包版本文件
├── Pipfile.lock        # 根据Pipfile生成的版本锁文件
├── README.md           # 项目自述文件
├── VERSION             # 项目版本文件
├── bin                 # 项目二进制程序
├── docs                # 项目文档
├── plum_tools          # 核心代码模块
├── setup.cfg           # 安装配置文件
├── setup.py            # 安装脚本
├── tasks.py            # 任务执行脚本
└── tests               # 单元测试目录

```

## 安装环境依赖

1.安装 invoke

```bash
pip install invoke
```

2.安装项目依赖环境

```bash
uv sync
```

3.安装 Git hooks

由于钩子文件无法提交到 `.git` 中，所以在第一次 clone 项目中需要执行以下命令，把钩子放到指定位置，有两种方式，建议使用第一种

第一种

```bash
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

第二种

```bash
cp -r hooks/* .git/hooks/
```

## 运行单元测试

### 第一种

```bash
inv coverage
```

### 第二种

```bash
inv test
```

## 检查 Python 代码规范

```bash
inv lint
```

## 更新版本

```bash
# 小版本
bumpversion patch

# 中版本
bumpversion minor
```

## gitrepo

查找指定路径下所有被改动的 git 仓库

```bash
➜  ~ gitrepo -h
usage: gitrepo [-h] [-p--path PATH [PATH ...]] [-d--detail] [-t--test]

optional arguments:
  -h, --help            show this help message and exit
  -p--path PATH [PATH ...]
                        The directory path to check
  -d--detail            display error details
  -t--test              run the test function
```

## pssh

通过 ip 简写或别名快速登录机器

```bash
➜  ~ pssh -h
usage: pssh [-h] [-t--type TYPE] [-i--identityfile IDENTITYFILE]
            [-u--username USER] [-p--port PORT]
            host

positional arguments:
  host                  specify server

optional arguments:
  -h, --help            show this help message and exit
  -t--type TYPE         host type
  -i--identityfile IDENTITYFILE
                        ssh login identityfile path
  -u--username USER     ssh login username
  -p--port PORT         ssh login port
```

## gitstash

外部传入一个 branch，保存本地未提交的修改，然后切换到 branch，将上次该 branch 保存的未提交的结果 stash pop 出来

```bash
➜  ~ gitstash -h
usage: gitstash [-h] branch

positional arguments:
  branch      specify branch

optional arguments:
  -h, --help  show this help message and exit
```

## pipmi

对指定机器进行远程执行 ipmitool 相关操作

```bash
➜  ~ pipmi -h
usage: pipmi [-h] -l HOST -s SERVERS [SERVERS ...] [-u USER] [-pass PASSWORD]
             [-p--port PORT] [-i--identityfile IDENTITYFILE] [-t--type TYPE]
             [-U USERNAME] [-c COMMAND] [-P PASSWORD]

optional arguments:
  -h, --help            show this help message and exit
  -l HOST, --login HOST
                        specify login ip
  -s SERVERS [SERVERS ...], --servers SERVERS [SERVERS ...]
                        specify server
  -u USER, --username USER
                        specify username
  -pass PASSWORD, --password PASSWORD
                        specify password
  -p--port PORT         ssh login port
  -i--identityfile IDENTITYFILE
                        ssh login identityfile path
  -t--type TYPE         host type
  -U USERNAME, --Username USERNAME
                        specify ipmi username
  -c COMMAND, --command COMMAND
                        specify ipmi command
  -P PASSWORD, --Password PASSWORD
                        specify ipmi password
```

## prn

上传文件到服务器

```bash
➜  ~ prn -h
usage: prn [-h] -s SERVERS [SERVERS ...] [-p PROJECT] [-t--type TYPE]
           [-i--identityfile IDENTITYFILE] [-u--username USER] [-p--port PORT]
           [-l--local LOCAL] [-r--remote REMOTE] [-d--delete DELETE]
           [-e--exclude EXCLUDE [EXCLUDE ...]]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVERS [SERVERS ...], --servers SERVERS [SERVERS ...]
                        specify server
  -p PROJECT, --project PROJECT
                        specify project
  -t--type TYPE         host type
  -i--identityfile IDENTITYFILE
                        ssh login identityfile path
  -u--username USER     ssh login username
  -p--port PORT         ssh login port
  -l--local LOCAL       local path
  -r--remote REMOTE     remote path
  -d--delete DELETE     delete remote path other file
  -e--exclude EXCLUDE [EXCLUDE ...]
                        exclude file
```

## pping

ping 指定网段所有 ip 是否能 ping 通

```bash
➜  ~ pping -h
usage: pping [-h] [-t--type TYPE]

optional arguments:
  -h, --help     show this help message and exit
  -t--type TYPE  host type
```

## 详细文档

见[项目文档目录](docs/README.md)
