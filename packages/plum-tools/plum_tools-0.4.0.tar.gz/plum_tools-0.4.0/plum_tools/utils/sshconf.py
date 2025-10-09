"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: sshconf
#         Desc: 解析ssh配置函数
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 17:45
#=============================================================================
"""

import re
import sys

from ..conf import PathConfig
from .utils import YmlConfig, print_error


class SSHConf:
    """SSH相关配置"""

    def __init__(self, user: str, port: int, identityfile: str) -> None:
        """初始

        :param user ssh登陆使用的用户名
        :example user 10.10.100.1

        :param port ssh登陆使用的端口号
        :example port 22

        :param identityfile 主机ip
        :example identityfile ~/.ssh/id_rsa
        """
        self._user = user
        self._port = port
        self._identityfile = identityfile

    def get_ssh_conf(self, host: str) -> dict:
        """查询默认的ssh登陆信息

        :param host: 主机ip
        :example host 10.10.100.1

        :return ssh_conf ssh主机信息
        :example ssh_conf
        {
            'identityfile': '~/.ssh/seekplum',
            'hostname': 'github.com',
            'user': 'seekplum',
            'port': 22
        }
        """
        yml_config = YmlConfig.parse_config_yml(PathConfig.plum_yml_path)
        ssh_conf = yml_config["default_ssh_conf"]
        if self._user:
            ssh_conf["user"] = self._user
        if self._port:
            ssh_conf["port"] = self._port
        if self._identityfile:
            ssh_conf["identityfile"] = self._identityfile
        ssh_conf["hostname"] = host
        return ssh_conf

    def merge_ssh_conf(self, alias_conf: dict) -> dict:
        """合并ssh配置信息

        :param alias_conf 在./ssh/config配置文件中的ssh主机信息
        :example alias_conf
        {
            'identityfile': '~/.ssh/seekplum',
            'hostname': 'github.com',
            'user': 'seekplum',
            'port': 22
        }

        :return ssh_conf 和输入信息合并后的ssh主机信息
        :example ssh_conf
        {
            'identityfile': '~/.ssh/seekplum',
            'hostname': 'github.com',
            'user': 'seekplum',
            'port': 22
        }
        """
        yml_config = YmlConfig.parse_config_yml(PathConfig.plum_yml_path)
        default_ssh_conf = yml_config["default_ssh_conf"]
        ssh_conf = {
            "identityfile": self._identityfile or alias_conf.get("identityfile", default_ssh_conf["identityfile"]),
            "hostname": alias_conf["hostname"],
            "user": self._user or alias_conf.get("user", default_ssh_conf["user"]),
            "port": int(self._port or alias_conf.get("port", default_ssh_conf["port"])),
        }
        return ssh_conf


def get_prefix_host_ip(host_type: str) -> str:
    """查询不同类型的前三段IP

    :param host_type ip类型,不同的ip类型，ip前缀不一样
    :example host_type default

    :return prefix_host IP前三段值
    :example prefix_host 10.10.100
    """
    type_key = f"host_type_{host_type}"
    try:
        yml_config = YmlConfig.parse_config_yml(PathConfig.plum_yml_path)
        prefix_host = yml_config[type_key]
    except KeyError:
        print_error(f"yml文件: {PathConfig.plum_yml_path} 中缺少key: {type_key}")
        sys.exit(1)
    return prefix_host


def get_host_ip(host: str, host_type: str) -> str:
    """查询主机的ip

    :param host: ip的简写
    :example host 1

    :param host_type ip类型,不同的ip类型，ip前缀不一样
    :example host_type default

    :return 完整的主机ip
    """
    prefix_host = get_prefix_host_ip(host_type)
    mark = "."
    # 处理输入的前两位的情况
    point_count = host.count(mark)
    # 标准ip中点的数量
    normal_point = 3
    if point_count < normal_point:
        prefix_host = mark.join(prefix_host.split(mark)[: (normal_point - point_count)])
        host = f"{prefix_host}.{host}"
    return host


def get_ssh_alias_conf(host: str) -> dict:
    """解析~/.ssh/config配置信息

    :return ssh_conf ssh主机信息
    :example ssh_conf
    {
        'identityfile': '~/.ssh/seekplum',
        'hostname': 'github.com',
        'user': 'seekplum',
        'port': 22
    }
    """
    begin = False
    # 查询默认的ssh信息
    ssh_conf = {}
    with open(PathConfig.ssh_config_path, encoding="utf-8") as f:
        for line in f:
            data = line.split()
            # config配置都是两列
            if len(data) != 2:
                continue

            key = data[0].lower()
            value = data[1]

            # 多个主机信息已 Host 进行分隔
            if key == "host":
                if begin:  # pylint: disable=R1723
                    break
                elif value == host:
                    begin = True
                else:
                    continue

            if begin:
                ssh_conf[key] = value

    if not begin:
        print_error(f"未在 {PathConfig.ssh_config_path} 中配置主机 {host} 的ssh登陆信息")
        sys.exit(1)
    return ssh_conf


def merge_ssh_config(host: str, host_type: str, user: str, port: int, identityfile: str) -> dict:
    """合并ssh配置信息

    :param host: ip的简写或者主机的别名
    :example host 1

    :param host_type ip类型,不同的ip类型，ip前缀不一样
    :example host_type default

    :param user ssh登陆用户名
    :example user root

    :param port ssh登陆端口
    :example port 22

    :param user ssh登陆用户名
    :example user root

    :param identityfile ssh登陆私钥文件路径
    :example identityfile ~/.ssh/id_rsa

    :return ssh_conf ssh主机信息
    :example ssh_conf
    {
        'identityfile': '~/.ssh/seekplum',
        'hostname': 'github.com',
        'user': 'seekplum',
        'port': 22
    }
    """
    pattern = re.compile(r"^(?:\d+\.){0,3}\d+$")
    match = pattern.match(host)
    conf_obj = SSHConf(user, port, identityfile)
    # 传入的是ip的简写
    if match:
        host = get_host_ip(host, host_type)
        ssh_conf = conf_obj.get_ssh_conf(host)
    else:
        alias_conf = get_ssh_alias_conf(host)
        ssh_conf = conf_obj.merge_ssh_conf(alias_conf)
    return ssh_conf
