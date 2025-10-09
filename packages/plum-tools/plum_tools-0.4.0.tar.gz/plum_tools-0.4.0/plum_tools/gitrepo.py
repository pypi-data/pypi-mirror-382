"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: exceptions
#         Desc: 查找指定路径下所有被改动的git仓库
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-05 22:02
#=============================================================================
"""

import functools
import os
from multiprocessing import Pool
from typing import Generator, List

from .conf import Constant
from .utils.git import check_is_git_repository, check_repository_modify_status, check_repository_stash
from .utils.parser import get_base_parser
from .utils.printer import print_error, print_warn


def find_git_project_for_python(path: str) -> Generator[str, None, None]:
    """查找目录下所有的 git仓库

    :param path 要被检查的目录
    :example path "/tmp/git"

    >>> for path in find_git_project_for_python("/tmp"):
    ...    print path


    """
    for root, _, _ in os.walk(path):
        if check_is_git_repository(root):
            yield root


def check_project(path: str, stash: bool = True) -> dict:
    """检查git项目

    :param path 仓库路径
    :example path /tmp/git

    :param stash 是否显示储藏信息
    :example stash True

    :return result {
        path: 仓库路径
        output: 检查输出信息
        status:
            True 仓库有文件进行了修改或有储藏文件
            False 仓库没有和远程一致。且没有储藏文件
    }
    :example result {
        "path": "/tmp/git",
        "status": False,
        "output": ""
    }
    """
    result = {
        "path": path,
        "status": False,
    }
    # 检查文件是否改动
    status_result, status_out = check_repository_modify_status(path)
    if status_result:
        result["status"] = True
        result["output"] = status_out
        return result

    if not stash:
        return result
    # 检查是否有文件储藏
    stash_result, stash_out = check_repository_stash(path)
    if stash_result:
        result["status"] = True
        result["output"] = stash_out
    return result


def check_projects(projects: List[str], detail: bool, stash: bool = True) -> None:
    """检查指导目录下所有的仓库是否有修改

    当仓库中有内容被修改时，打印黄色警告信息

    :param projects 需要检查的目录列表
    :example ["/tmp"]

    :param detail 是否显示详细错误信息
    :example False

    :param stash 是否显示储藏信息
    :example False
    """
    targets = [path for project_path in projects for path in find_git_project_for_python(project_path)]
    with Pool(processes=Constant.processes_number) as pool:
        result = pool.map(functools.partial(check_project, stash=stash), targets)
    for item in result:
        # 仓库中文件没有被改动而且没有文件被储藏了
        if not item["status"]:
            continue
        print_warn(item["path"])

        # 打印详细错误信息
        if not detail:
            continue
        print_error(item["output"])


def main() -> None:
    """程序主入口"""
    parser = get_base_parser()
    parser.add_argument(
        "-p",
        "--path",
        action="store",
        required=False,
        dest="path",
        nargs="+",
        default=[os.environ["HOME"]],
        help="The directory path to check",
    )
    parser.add_argument(
        "-d",
        "--detail",
        action="store_true",
        required=False,
        dest="detail",
        default=False,
        help="display staged details",
    )
    parser.add_argument(
        "-s",
        "--stash",
        action="store_true",
        required=False,
        dest="stash",
        default=False,
        help="display stash details",
    )
    args = parser.parse_args()
    check_projects(args.path, args.detail, args.stash)
