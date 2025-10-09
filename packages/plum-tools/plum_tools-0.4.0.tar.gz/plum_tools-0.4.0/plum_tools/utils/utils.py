"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: utils
#         Desc: 项目中工具包
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-05 22:02
#=============================================================================
"""

import os
import platform
import re
import signal
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import yaml

from ..conf import OsCommand, PathConfig
from ..exceptions import RunCmdError, RunCmdTimeout, SystemTypeError
from .printer import print_error, print_text


class cd:  # pylint: disable=invalid-name
    """进入目录执行对应操作后回到目录"""

    def __init__(self, new_path: str) -> None:
        """初始化

        :param new_path: 目标目录
        :example new_path "/tmp"

        >>> with cd("/tmp"):
        ...     print(run_cmd("pwd"))
        "/tmp"
        """
        self._new_path = new_path
        self._current_path = ""

    def __enter__(self) -> None:
        self._current_path = os.getcwd()
        os.chdir(self._new_path)

    def __exit__(self, exc_type: Any, exc_val: Exception, exc_tb: Any) -> None:
        os.chdir(self._current_path)


@dataclass
class SSHConf:
    user: str
    port: int
    identityfile: str


@dataclass
class ProjectConf:
    src: str
    desc: str
    dest: Optional[str]
    exclude: Optional[list]


@dataclass
class GlobalConf:
    default_ssh_conf: SSHConf
    ipmi_interval: int
    projects: List[ProjectConf]
    dynamic_data: dict

    def __init__(
        self, default_ssh_conf: SSHConf, ipmi_interval: int, projects: List[ProjectConf], **kwargs: Dict[str, str]
    ) -> None:
        self.default_ssh_conf = default_ssh_conf
        self.ipmi_interval = ipmi_interval
        self.projects = projects
        self.dynamic_data = kwargs

    def __post_init__(self) -> None:
        if not self.dynamic_data:
            return
        for key, value in self.dynamic_data.items():
            if not key.startswith("host_type_"):
                raise TypeError(f"key: {key} 必须以 type_ 开头")
            if not isinstance(value, str):
                raise TypeError(f"key:{key} value: {value} 必须为字符串")

    def get_data(self) -> dict:
        self.__post_init__()
        data = asdict(self)
        data.pop("dynamic_data")
        data.update(self.dynamic_data)
        return data


class YmlConfig:
    """解析yml配置"""

    _yml_data = {}  # type: ignore

    @classmethod
    def parse_config_yml(cls, yml_path: str) -> dict:
        """解析配置程序依赖的配置yml文件

        :param yml_path 项目依赖的yml配置文件路径
        :example yml_path ~/.plum_tools.yml

        :return yml配置文件内容
        """
        if cls._yml_data:
            return cls._yml_data
        try:
            with open(yml_path, encoding="utf-8") as f:
                try:
                    obj = GlobalConf(**yaml.safe_load(f.read()))
                    data = obj.get_data()
                except TypeError as e:
                    print_error(f"yml文件: {PathConfig.plum_yml_path} 格式错误, {e.args[0]}, 请参照以下格式进行修改")
                    with open(os.path.join(PathConfig.root, PathConfig.plum_yml_name), encoding="utf-8") as fp:
                        text = fp.read()
                    print_text(text)
                    sys.exit(1)
                else:
                    cls._yml_data = data
                    return cls._yml_data
        except OSError:
            print_error(f"yml文件: {PathConfig.plum_yml_path} 不存在")
            sys.exit(1)


def ensure_str(s: Any, encoding: str = "utf-8", errors: str = "strict") -> str:
    """Coerce *s* to `str`.

    - `str` -> `str`
    - `bytes` -> decoded to `str`
    """
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    raise TypeError(f"not expecting type '{type(s)}'")


def run_cmd(cmd: str, is_raise_exception: bool = True, timeout: Optional[int] = None) -> str:
    """执行系统命令

    :param cmd 系统命令
    :example cmd hostname

    :param is_raise_exception 执行命令失败是否抛出异常
    :example is_raise_exception False

    :param timeout 超时时间
    :example timeout 1

    >>> run_cmd("echo 1")
    '1\\n'

    >>> run_cmd("ls -l /tmp") #doctest: +ELLIPSIS
    'lrwxr-xr-x@ 1 root  wheel...'

    >>> run_cmd("aaa")
    Traceback (most recent call last):
    RunCmdError: run `aaa` fail

    >>> run_cmd("bbb")
    Traceback (innermost last):
    RunCmdError: run `bbb` fail

    :return 命令执行结果
    :example hostname

    :raise RunCmdError 命令执行失败
    :raise RunCmdTimeout 命令执行超时
    """

    def raise_timeout_exception(*_: Any) -> None:
        """通过抛出异常达到超时效果"""
        raise RunCmdTimeout(f"run `{cmd}` timeout, timeout is {timeout}")

    # 设置指定时间后出发handler
    if timeout:
        signal.signal(signal.SIGALRM, raise_timeout_exception)
        signal.alarm(timeout)

    with subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        out_msg = ensure_str(p.stdout.read())  # type: ignore[union-attr]
        err_msg = ensure_str(p.stderr.read())  # type: ignore[union-attr]
        exit_code = p.wait()

    # 解除触发handler
    if timeout:
        signal.alarm(0)

    if is_raise_exception and exit_code != 0:
        message = f"run `{cmd}` fail"
        raise RunCmdError(message, out_msg=out_msg, err_msg=err_msg)
    try:
        return ensure_str(out_msg)
    except UnicodeDecodeError:
        try:
            return ensure_str(out_msg, encoding="unicode_escape")
        except UnicodeDecodeError:
            print_text(f"Output: {out_msg!r}")
            raise


def get_file_abspath(path: str) -> str:
    """文件的相对路径

    :param path 文件路径
    :example path ~/.ssh/id_rsa

    :return abs_path 文件绝对路径
    :example abs_path /home/seekplum/.ssh/id_rsa
    """

    def replace_path(old_path: str) -> str:
        """替换路径中的空格"""
        return old_path.replace(r" ", r"\ ")

    # 系统直接可以找到
    if os.path.exists(path):
        return path

    # 通过系统命令stat查找真实路径
    path = replace_path(path)
    cmd = OsCommand.stat_command % path
    output = run_cmd(cmd)

    # 获取操作系统类型
    system_type = platform.system()
    if system_type == "Linux":
        pattern = re.compile(r"File: (.*)")
    # mac系统
    elif system_type == "Darwin":
        pattern = re.compile(r'"\s+\d+\s+\d+\s+\d+(.*)$')
    else:
        raise SystemTypeError("此项功能仅支持 Linux / Darwin(mac)")
    match = pattern.search(output)
    if match:
        abs_path = replace_path(match.group(1).strip())
        return abs_path
    raise FileNotFoundError(f"文件: {path} 不存在")
