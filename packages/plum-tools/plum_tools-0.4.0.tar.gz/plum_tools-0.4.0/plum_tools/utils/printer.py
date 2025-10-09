"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: printer
#         Desc: 按指定颜色打印信息
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-03 22:50
#=============================================================================
"""

from typing import Any


def get_color(c: int, s: Any) -> str:
    """获取带背景色的字符串

    :param c 前背景色
    :example c 1

    :param s 需要获取背景色的字符串
    :example s ok

    :return: 带颜色的字符串
    """
    return f"\033[3{c}m{s}\033[0m"


def get_red(s: Any) -> str:
    """获取红颜色字符串

    :param s 需要获取背景色的字符串
    :example s ok

    :return: 红色的字符串
    """
    return get_color(1, s)


def get_green(s: Any) -> str:
    """获取绿颜色字符串

    :param s 需要获取背景色的字符串
    :example s ok

    :return: 绿色的字符串
    """
    return get_color(2, s)


def get_yellow(s: Any) -> str:
    """获取黄颜色字符串

    :param s 需要获取背景色的字符串
    :example s ok

    :return: 黄色的字符串
    """
    return get_color(3, s)


def print_text(text: Any) -> None:
    """打印普通信息

    :param text 要打印的信息
    :example text "ok"
    """
    print(text)


def print_ok(text: Any) -> None:
    """打印正确信息,绿色

    :param text 要打印的信息
    :example text "ok"
    """
    fmt = get_green(text)
    print_text(fmt)


def print_warn(text: Any) -> None:
    """打印警告信息,黄色

    :param text 要打印的信息
    :example text "warn"
    """
    fmt = get_yellow(text)
    print_text(fmt)


def print_error(text: Any) -> None:
    """打印错误信息,红色

    :param text 要打印的信息
    :example text "error"
    """
    fmt = get_red(text)
    print_text(fmt)
