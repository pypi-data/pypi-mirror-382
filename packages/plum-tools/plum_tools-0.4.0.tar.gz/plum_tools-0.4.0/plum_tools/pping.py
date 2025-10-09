"""
#=============================================================================
#  ProjectName: plum_tools
#     FileName: pping
#         Desc: ping指定网段所有ip是否能ping通
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-07 10:26
#=============================================================================
"""

from multiprocessing import Pool
from typing import Optional

from .conf import Constant, OsCommand
from .exceptions import RunCmdError
from .utils.parser import get_base_parser
from .utils.printer import print_text
from .utils.sshconf import get_prefix_host_ip
from .utils.utils import run_cmd


def ping(ip: str) -> Optional[str]:
    """ping指定ip是否能ping通

    :param ip 主机ip
    :example ip 10.10.100.1
    """
    cmd = OsCommand.ping_command % ip
    try:
        run_cmd(cmd)
    except RunCmdError:
        return None
    return ip


def run(host_type: str, prefix_host: str) -> None:
    """打印IP段内所有能ping通的ip

    :param host_type ip类型,不同的ip类型，ip前缀不一样
    :example host_type default

    :param prefix_host: 主机前缀
    :example prefix_host 1.1.1
    """
    if not prefix_host:
        prefix_host = get_prefix_host_ip(host_type)

    mark = "."
    if not prefix_host.endswith(mark):
        prefix_host += mark

    targets = [f"{prefix_host}{i}" for i in range(1, 255)]
    with Pool(processes=Constant.processes_number) as pool:
        result = pool.map(ping, targets)
    for ip in result:
        if ip:
            print_text(ip)


def main() -> None:
    """程序主入口"""
    parser = get_base_parser()
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
        "-p",
        "--prefix-host",
        action="store",
        required=False,
        dest="prefix_host",
        default=None,
        help="host prefix",
    )

    args = parser.parse_args()
    run(args.type, args.prefix_host)
