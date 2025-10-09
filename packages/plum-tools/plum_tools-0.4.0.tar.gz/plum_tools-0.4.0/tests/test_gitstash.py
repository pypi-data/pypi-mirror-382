# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_gitstash
#         Desc: 测试gitstash模块
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 23:43
#=============================================================================
"""

from unittest import mock

from plum_tools.gitstash import main


def test_main() -> None:
    mock_parser = mock.Mock()
    mock_stash_instance = mock.Mock()
    mock_args = mock.Mock(branch="test")
    mock_parser.parse_args.return_value = mock_args
    with mock.patch("plum_tools.gitstash.get_base_parser", return_value=mock_parser) as mock_argparse, mock.patch(
        "plum_tools.gitstash.get_current_branch_name", return_value="master"
    ) as mock_current_branch, mock.patch(
        "plum_tools.gitstash.GitCheckoutStash", return_value=mock_stash_instance
    ) as mock_git_stash:
        main()
        mock_argparse.assert_called_once_with()
        mock_parser.add_argument.assert_called_once_with(dest="branch", action="store", help="specify branch")
        mock_parser.parse_args.assert_called_once_with()
        mock_current_branch.assert_called_once_with()
        mock_git_stash.assert_called_once_with("master", "test")
        mock_stash_instance.checkout.assert_called_once_with()
