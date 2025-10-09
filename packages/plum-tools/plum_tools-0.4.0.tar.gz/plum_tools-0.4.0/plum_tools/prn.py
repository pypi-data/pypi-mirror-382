"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: prn
#         Desc: 上传文件到服务器
#               命令: prn -s plum -p plum
#               描述: 上传 ~/..yml 中指定项目的文件到ssh_config中配置的服务器
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 17:26
#=============================================================================
"""

import os
import subprocess
import sys
from typing import List, Optional, Union

from .conf import PathConfig
from .exceptions import RunCmdError, SystemTypeError
from .utils.parser import get_base_parser
from .utils.printer import print_error, print_ok, print_text
from .utils.sshconf import merge_ssh_config
from .utils.utils import YmlConfig, get_file_abspath, run_cmd


def get_project_conf(  # noqa: C901
    project: str,
    src: List[str],
    dest: List[str],
    delete: Optional[int],
    exclude: List[str],
    is_download: bool = False,
) -> dict:
    """查询项目信息

    :param project 指定的项目名
    :example project plum

    :param src 本地路径
    :example src /tmp

    :param dest 远程机器路径
    :example dest /tmp

    :param exclude 需要过滤的目录
    :example exclude [".git"]

    :param delete 是否删除远程机器目录下非本次上传的文件
    :example delete 0 0|1  0: 不删除 1: 删除

    :param is_download 是否下载文件
    :example is_download True True|False

    :return data 项目的配置信息
    {
        "src": 本地路径,
        "dest": 上传后的目录路径,
        "exclude": 需要过滤不上传的目录,
        "delete": 是否删除远程机器目录下非本次上传的文件
    }
    :example data {
        "src": "/tmp",
        "dest": "/tmp",
        "exclude": [".git"],
        "delete": 0
    }
    """
    yml_data = YmlConfig.parse_config_yml(PathConfig.plum_yml_path)
    data = {}
    try:
        data = yml_data["projects"][project]
    except KeyError:
        if not (src and dest):
            print_error(f"yml文件: {PathConfig.plum_yml_path} 中没有配置项目: {project} 的信息")
            sys.exit(1)

    # 设置默认值
    data.setdefault("exclude", [])
    data.setdefault("delete", 0)

    # 从命令行中更新对应值
    if src:
        data["src"] = src
    if dest:
        data["dest"] = dest
    if not isinstance(data["src"], list):
        data["src"] = [data["src"]]
    if not isinstance(data["dest"], list):
        data["dest"] = [data["dest"]]
    # 上传时对本地路径取绝对路径
    if not is_download:
        try:
            data["src"] = [get_file_abspath(path) for path in data["src"]]
        except RunCmdError:
            tmp_src = " ".join(data["src"])
            print_error(f"{tmp_src} 文件/目录不存在")
            sys.exit(1)
        except SystemTypeError as e:
            print_error(str(e))
            sys.exit(1)
    if delete is not None:  # 默认值为None
        data["delete"] = delete
    if exclude:
        data["exclude"] = exclude

    return data


def process_path(path: str, is_local: bool = False) -> str:
    # 本地端目录结尾需要有 /
    if is_local and not path.endswith("/") and os.path.isdir(path):
        path += "/"
    # 目标端目录结尾不能有 /
    if not is_local and path.endswith("/"):
        path = path[:-1]
    return path


def process_paths(paths: Union[str, List[str]], is_local: bool = False) -> str:
    if isinstance(paths, str):
        paths = [paths]
    return " ".join([process_path(path, is_local=is_local) for path in paths])

def process_remote_paths(paths: Union[str, List[str]], user: str, hostname: str, pv: str) -> str:
    if isinstance(paths, str):
        paths = [paths]
    return " ".join([f"{user}@{hostname}:{process_path(path, is_local=False)}{pv}" for path in paths])


class SyncFiles:  # pylint: disable=too-many-instance-attributes
    """上传文件到服务器"""

    # pylint: disable=R0913
    def __init__(
        self,
        hostname: str,
        user: str,
        port: int,
        identityfile: str,
        src: str,
        dest: str,
        exclude: List[str],
        delete: int,
        is_download: bool = False,
        is_debug: bool = False,
    ):
        """文件上传功能

        :param hostname 主机ip
        :example hostname 10.10.100.1

        :param user ssh登陆使用的用户名
        :example user 10.10.100.1

        :param port ssh登陆使用的端口号
        :example port 22

        :param identityfile 私钥文件路径
        :example identityfile ~/.ssh/id_rsa

        :param src 本地路径
        :example src /tmp

        :param dest 远程机器路径
        :example dest /tmp

        :param exclude 需要过滤的目录
        :example exclude [".git"]

        :param delete 是否删除远程机器目录下非本次上传的文件
        :example delete 0 0|1  0: 不删除 1: 删除

        :param is_download 是否是下载文件，默认是上传
        :example is_download False

        :param is_debug 是否打印详细信息
        :example is_debug False
        """
        self._hostname = hostname
        self._user = user
        self._port = port
        self._identity_file = identityfile
        self._src = src
        self._dest = dest
        self._exclude = exclude
        self._delete = delete
        self._is_download = is_download
        self._is_debug = is_debug

    def _get_sync_option(self) -> str:
        """组合出同步文件的命令"""
        option = ["rsync -rtv"]
        known_host = "UserKnownHostsFile=/dev/null"
        host_key = "StrictHostKeyChecking no"
        timeout = "ConnectTimeout=2"
        # 指定端口
        if self._port:
            ssh_cmd = f"ssh -p {self._port}"
        else:
            ssh_cmd = "ssh"
        directory = os.path.dirname(self._dest)
        if not directory:
            directory = self._dest
        option.append(f"'--rsync-path=mkdir -p {directory} && rsync'")
        option.append(f'-e \'{ssh_cmd} -i {self._identity_file} -o "{known_host}" -o "{host_key}" -o "{timeout}"\'')
        if self._delete:
            option.append(" --delete")
        for item in set(self._exclude):
            option.append(f"--exclude '{item}'")
        return " ".join(option)

    def translate(self) -> None:
        """文件上传功能"""
        # pv = "|pv -lep -s 117 >/dev/null"
        pv = ""

        if self._is_download:
            self._src, self._dest = process_remote_paths(self._dest, self._user, self._hostname, pv), process_paths(self._src)
        else:
            self._src, self._dest = process_paths(self._src, is_local=True), process_paths(self._dest)

        # 从远端下载文件到本地
        if self._is_download:
            src = self._src
            dest = self._dest
            text = f"从 {self._user}@{self._hostname} 服务器(端口: {self._port}) 下载 {self._src} 到本地 {self._dest} "
        # 从本地上传文件到远端
        else:
            src = self._src
            dest = f"{self._user}@{self._hostname}:{self._dest}{pv}"
            text = f"上传 {self._src} 到 {self._user}@{self._hostname} 服务器(端口: {self._port}) {self._dest} "

        rsync = self._get_sync_option()
        cmd = f"{rsync} {src} {dest}"
        try:
            if self._is_debug:
                print_text(cmd)
                subprocess.call(cmd, shell=True)
            else:
                run_cmd(cmd)
            print_ok(f"{text}成功")
        except RunCmdError as e:
            print_error(f"{text}失败, 失败原因: {e.err_msg}")


def sync_files(  # pylint: disable=too-many-arguments
    host_list: List[str],
    host_type: str,
    user: str,
    port: int,
    identity_file: str,
    projects_conf: List[dict],
    is_download: bool = False,
    is_debug: bool = False,
) -> None:
    """上传文件到服务器上

    :param host_list 服务器列表
    :example host_list [1, 2]

    :param host_type 主机类型
    :example host_type 1

    :param user ssh登陆用户名
    :example user root

    :param port ssh登陆端口
    :example port 22

    :param user ssh登陆用户名
    :example user root

    :param identity_file ssh登陆私钥文件路径
    :example identity_file ~/.ssh/id_rsa

    :param projects_conf 需要上传的项目配置列表
    :example pro_conf [{
        "src": "/tmp",
        "dest": "/tmp",
        "exclude": [".git"],
        "delete": 0
    }]

    :param is_download 是否是下载文件，默认是上传
    :example is_download False

    :param is_debug 是否打印详细信息
    :example is_debug False
    """
    for host in host_list:
        ssh_conf = merge_ssh_config(host, host_type, user, port, identity_file)
        ssh_conf.update({"is_download": is_download, "is_debug": is_debug})
        for pro_conf in projects_conf:
            pro_conf.update(ssh_conf)
            sync = SyncFiles(**pro_conf)
            sync.translate()


def main() -> None:  # pylint: disable=R0914
    """程序主入口"""
    parser = get_base_parser()
    parser.add_argument(
        "-s",
        "--servers",
        required=False,
        action="store",
        dest="servers",
        nargs="+",
        help="specify server",
    )
    parser.add_argument(
        "-p",
        "--projects",
        required=False,
        action="store",
        dest="projects",
        nargs="+",
        default=["default"],
        help="specify project",
    )

    parser.add_argument(
        "-t",
        "--type",
        action="store",
        required=False,
        dest="type",
        default="default",
        help="host type",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        required=False,
        dest="download",
        default=False,
        help="Download the file locally",
    )
    parser.add_argument(
        "-i",
        "--identityfile",
        action="store",
        required=False,
        dest="identity_file",
        default="",
        help="ssh login identityfile path",
    )
    parser.add_argument(
        "-u",
        "--username",
        action="store",
        required=False,
        dest="user",
        default="",
        help="ssh login username",
    )
    parser.add_argument(
        "--port",
        action="store",
        required=False,
        dest="port",
        type=int,
        default=0,
        help="ssh login port",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store",
        required=False,
        dest="local",
        nargs="+",
        default="",
        help="local path",
    )
    parser.add_argument(
        "-r",
        "--remote",
        action="store",
        required=False,
        dest="remote",
        nargs="+",
        default="",
        help="remote path",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store",
        required=False,
        dest="delete",
        type=int,
        default=None,
        help="delete remote path other file",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="store",
        nargs="+",
        required=False,
        dest="exclude",
        default=[],
        help="exclude file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        required=False,
        dest="debug",
        default=False,
        help="debug output from parser",
    )

    args = parser.parse_args()
    host_list, host_type, projects = args.servers, args.type, args.projects
    if not host_list:
        parser.print_help()
        return

    src, dest, delete, exclude = args.local, args.remote, args.delete, args.exclude
    if len(src) > 1 and len(dest) > 1:
        print_error("本地路径和目标路径不能同时传入多个值")
        return

    user, port, identity_file = args.user, args.port, args.identity_file

    is_download, is_debug = args.download, args.debug

    projects_conf = [get_project_conf(project, src, dest, delete, exclude, is_download) for project in projects]
    sync_files(
        host_list,
        host_type,
        user,
        port,
        identity_file,
        projects_conf,
        is_download,
        is_debug,
    )
