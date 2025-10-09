# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_pssh
#         Desc: 测试pssh模块
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 23:44
#=============================================================================
"""

from unittest import mock

from plum_tools.pssh import main


def test_main() -> None:
    mock_parser = mock.Mock()
    mock_args = mock.Mock(host="dev", type="default", identityfile="", user="", port=0)
    mock_parser.parse_args.return_value = mock_args
    with mock.patch("plum_tools.pssh.get_base_parser", return_value=mock_parser) as mock_argparse, mock.patch(
        "plum_tools.pssh.login"
    ) as mock_login:
        main()
        mock_argparse.assert_called_once_with()
        mock_parser.add_argument.assert_has_calls(
            [
                mock.call(dest="host", action="store", help="specify server"),
                mock.call(
                    "-t",
                    "--type",
                    action="store",
                    required=False,
                    dest="type",
                    default="default",
                    help="host type",
                ),
                mock.call(
                    "-i",
                    "--identityfile",
                    action="store",
                    required=False,
                    dest="identityfile",
                    default="",
                    help="ssh login identityfile path",
                ),
                mock.call(
                    "-u",
                    "--username",
                    action="store",
                    required=False,
                    dest="user",
                    default="",
                    help="ssh login username",
                ),
                mock.call(
                    "-p",
                    "--port",
                    action="store",
                    required=False,
                    dest="port",
                    type=int,
                    default=0,
                    help="ssh login port",
                ),
            ]
        )
        mock_parser.parse_args.assert_called_once_with()
        mock_login.assert_called_once_with("dev", mock_args.type, "", 0, "")
