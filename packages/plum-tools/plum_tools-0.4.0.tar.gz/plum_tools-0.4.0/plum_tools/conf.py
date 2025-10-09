"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: conf
#         Desc: 相关常量配置信息
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-06 18:39
#=============================================================================
"""

import os
from typing import Any, Type

VERSION = "0.4.0"


class ClsReadOnlyClass(type):
    """类属性只读"""

    def __setattr__(cls, key: str, _: Any) -> None:
        """修改属性式抛出异常"""
        raise ValueError(f"{key} is read-only")


class ReadOnlyClass(metaclass=ClsReadOnlyClass):
    """所有属性只读"""

    def __init__(self) -> None:
        """初始化"""

    def __setattr__(self, key: str, _: Any) -> None:
        """修改属性式抛出异常"""
        raise ValueError(f"{key} is read-only")


class GitCommand(ReadOnlyClass):
    """git 相关命令"""

    stash_list = "git stash list"  # 检查是否有文件在储藏区
    status_default = "git status"  # 检查文件状态
    status_short = "git status -s"  # 检查文件状态，简短输出，只能看到文件是否有改动，无法确认是否落后、超前远程分支
    branch_abbrev = "git rev-parse --abbrev-ref HEAD"  # 查询当前分支名
    stash_save = 'git stash save "%s"'  # 保存修改的文件到储藏区
    stash_pop = "git stash pop --index %s"  # 把储藏的文件恢复
    git_checkout = "git checkout %s"  # 切换分支

    pull_keyword = '"git pull"'  # 落后远程分支关键字
    push_keyword = '"git push"'  # 超前远程分支关键字


class OsCommand(ReadOnlyClass):
    """系统 相关命令"""

    find_command = 'find %s -name ".git"'  # 通过系统命令查找文件路径
    ping_command = "ping -W 3 -c 1 %s"  # ping命令 -W 超时时间 -c 次数
    # ipmi命令
    ipmi_command = "ipmitool -I lanplus -H %(ip)s -U %(user)s -P %(password)s %(command)s"
    stat_command = "stat %s"


class SSHConfig(ReadOnlyClass):
    """ssh配置相关"""

    default_ssh_port = 22
    connect_timeout = 3


class Constant(ReadOnlyClass):
    """相关常量"""

    stash_uuid = "plum123456789987654321plum"
    command_timeout = 3  # 执行命令超时时间
    processes_number = 100  # 进程数量


class PathConfig(ReadOnlyClass):
    """相关配置文件"""

    home = os.environ["HOME"]
    root = os.path.dirname(os.path.abspath(__file__))
    plum_yml_name = ".plum_tools.yaml"  # 项目需要的配置文件名
    plum_yml_path = os.path.join(home, plum_yml_name)  # 项目需要的配置文件路径
    ssh_config_name = ".ssh/config"  # ssh配置文件名
    ssh_config_path = os.path.join(home, ssh_config_name)  # ssh配置文件路径


def generate_test_class(cls: Type[ReadOnlyClass], short: str) -> None:
    """生成测试代码

    :param cls: 只读属性的类
    :example cls OsCommand

    :param short: 类的简写
    :example short a
    """
    cls_name = cls.__name__
    print(f"class Test{cls_name}(unittest.TestCase):")
    print("    def setUp(self) -> None:")
    print(f"        self.{short} = {cls_name}")
    print()
    print("    def tearDown(self) -> None:")
    print(f"        del self.{short}")
    print()
    cls_variables = [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]
    for name in cls_variables:
        print(f"    def test_{name}(self) -> None:")
        print(f"        assert self.{short}.{name} == '{getattr(cls, name)}'")
        print()
