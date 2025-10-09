"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: exceptions
#         Desc: 所有的异常类
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2018-07-05 22:02
#=============================================================================
"""


class RunCmdError(Exception):
    """执行命令异常"""

    def __init__(self, message: str, out_msg: str, err_msg: str) -> None:
        """初始化参数

        :param message: 错误提示信息
        :param out_msg: 执行命令输出结果
        :param err_msg: 执行命令错误信息
        """
        super().__init__(message)  # pylint: disable=R1725
        self.out_msg = out_msg
        self.err_msg = err_msg


class RunCmdTimeout(Exception):
    """执行系统命令超时"""


class SSHException(Exception):
    """ssh异常"""


class SystemTypeError(Exception):
    """系统类型异常"""
