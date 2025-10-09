# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_gitrepo
#         Desc: 测试gitrepo模块
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 23:43
#=============================================================================
"""

import os
from unittest import mock

import pytest
from plum_tools.gitrepo import check_project, check_projects, find_git_project_for_python, main

from tests.common import MockPool


# @mock.patch("builtins.os")
@mock.patch(
    "plum_tools.gitrepo.check_is_git_repository",
    side_effect=[True, True, False, True, True],
)
def test_find_git_project_for_python(mock_check: mock.MagicMock) -> None:
    mock_os_result = [(f"/tmp/{i + 1}", None, None) for i in range(5)]

    with mock.patch("plum_tools.gitrepo.os") as mock_os:
        mock_os.walk.return_value = mock_os_result
        result = list(find_git_project_for_python("/tmp"))
        assert result == ["/tmp/1", "/tmp/2", "/tmp/4", "/tmp/5"]
    mock_os.walk.assert_called_once_with("/tmp")
    mock_check.assert_has_calls(
        [
            mock.call("/tmp/1"),
            mock.call("/tmp/2"),
            mock.call("/tmp/3"),
            mock.call("/tmp/4"),
            mock.call("/tmp/5"),
        ]
    )


def test_check_project_with_modify() -> None:
    with mock.patch(
        "plum_tools.gitrepo.check_repository_modify_status",
        return_value=(True, "test1"),
    ) as mock_modify:
        result = check_project("/tmp")
        assert result == {
            "path": "/tmp",
            "status": True,
            "output": "test1",
        }
        mock_modify.assert_called_with("/tmp")
    with mock.patch(
        "plum_tools.gitrepo.check_repository_modify_status",
        return_value=(False, "test1"),
    ) as mock_modify, mock.patch(
        "plum_tools.gitrepo.check_repository_stash", return_value=(True, "test2")
    ) as mock_stash:
        result = check_project("/tmp")
        assert result == {
            "path": "/tmp",
            "status": True,
            "output": "test2",
        }
        mock_modify.assert_called_with("/tmp")
        mock_stash.assert_called_with("/tmp")
    with mock.patch(
        "plum_tools.gitrepo.check_repository_modify_status",
        return_value=(False, "test1"),
    ) as mock_modify, mock.patch(
        "plum_tools.gitrepo.check_repository_stash", return_value=(False, "test2")
    ) as mock_stash:
        result = check_project("/tmp")
        assert result == {
            "path": "/tmp",
            "status": False,
        }
        mock_modify.assert_called_with("/tmp")
        mock_stash.assert_called_with("/tmp")


@mock.patch(
    "plum_tools.gitrepo.check_is_git_repository",
    side_effect=[True, True, False, True, True],
)
def test_check_projects(mock_check: mock.MagicMock, capsys: pytest.CaptureFixture) -> None:
    mock_os_result = [(f"/tmp/{i + 1}", None, None) for i in range(5)]

    with mock.patch("plum_tools.gitrepo.Pool", return_value=MockPool()) as mock_pool, mock.patch(
        "plum_tools.gitrepo.os"
    ) as mock_os, mock.patch(
        "plum_tools.gitrepo.check_repository_modify_status",
        side_effect=[
            (True, "test1"),
            (True, "test2"),
            (False, "test3"),
            (False, "test4"),
        ],
    ) as mock_modify, mock.patch(
        "plum_tools.gitrepo.check_repository_stash",
        side_effect=[(True, "test5"), (False, "test6")],
    ) as mock_stash:
        mock_os.walk.return_value = mock_os_result
        check_projects(["/tmp"], True)
    mock_pool.assert_called_once_with(processes=100)
    mock_os.walk.assert_called_once_with("/tmp")
    mock_check.assert_has_calls(
        [
            mock.call("/tmp/1"),
            mock.call("/tmp/2"),
            mock.call("/tmp/3"),
            mock.call("/tmp/4"),
            mock.call("/tmp/5"),
        ]
    )
    mock_modify.assert_has_calls(
        [
            mock.call("/tmp/1"),
            mock.call("/tmp/2"),
            mock.call("/tmp/4"),
            mock.call("/tmp/5"),
        ]
    )
    mock_stash.assert_has_calls([mock.call("/tmp/4"), mock.call("/tmp/5")])

    captured = capsys.readouterr()
    assert "/tmp/1" in captured.out
    assert "/tmp/2" in captured.out
    assert "/tmp/3" not in captured.out
    assert "/tmp/4" in captured.out
    assert "/tmp/5" not in captured.out
    assert "test5" in captured.out


@mock.patch(
    "plum_tools.gitrepo.check_is_git_repository",
    side_effect=[True, True, False, True, True],
)
def test_check_projects_with_not_detail(mock_check: mock.MagicMock, capsys: pytest.CaptureFixture) -> None:
    mock_os_result = [(f"/tmp/{i + 1}", None, None) for i in range(5)]

    with mock.patch("plum_tools.gitrepo.Pool", return_value=MockPool()) as mock_pool, mock.patch(
        "plum_tools.gitrepo.os"
    ) as mock_os, mock.patch(
        "plum_tools.gitrepo.check_repository_modify_status",
        side_effect=[
            (True, "test1"),
            (True, "test2"),
            (False, "test3"),
            (False, "test4"),
        ],
    ) as mock_modify, mock.patch(
        "plum_tools.gitrepo.check_repository_stash",
        side_effect=[(True, "test5"), (False, "test6")],
    ) as mock_stash:
        mock_os.walk.return_value = mock_os_result
        check_projects(["/tmp"], False)
    mock_pool.assert_called_once_with(processes=100)
    mock_os.walk.assert_called_once_with("/tmp")
    mock_check.assert_has_calls(
        [
            mock.call("/tmp/1"),
            mock.call("/tmp/2"),
            mock.call("/tmp/3"),
            mock.call("/tmp/4"),
            mock.call("/tmp/5"),
        ]
    )
    mock_modify.assert_has_calls(
        [
            mock.call("/tmp/1"),
            mock.call("/tmp/2"),
            mock.call("/tmp/4"),
            mock.call("/tmp/5"),
        ]
    )
    mock_stash.assert_has_calls([mock.call("/tmp/4"), mock.call("/tmp/5")])

    captured = capsys.readouterr()
    assert "/tmp/1" in captured.out
    assert "/tmp/2" in captured.out
    assert "/tmp/3" not in captured.out
    assert "/tmp/4" in captured.out
    assert "/tmp/5" not in captured.out
    assert "test5" not in captured.out


def test_main() -> None:
    mock_parser = mock.Mock()
    mock_args = mock.Mock(path="/tmp/test111", detail=True, stash=False)
    mock_parser.parse_args.return_value = mock_args
    with mock.patch("plum_tools.gitrepo.get_base_parser", return_value=mock_parser) as mock_argparse, mock.patch(
        "plum_tools.gitrepo.check_projects"
    ) as mock_check:
        main()
        mock_argparse.assert_called_once_with()
        mock_parser.add_argument.assert_has_calls(
            [
                mock.call(
                    "-p",
                    "--path",
                    action="store",
                    required=False,
                    dest="path",
                    nargs="+",
                    default=[os.environ["HOME"]],
                    help="The directory path to check",
                ),
                mock.call(
                    "-d",
                    "--detail",
                    action="store_true",
                    required=False,
                    dest="detail",
                    default=False,
                    help="display staged details",
                ),
                mock.call(
                    "-s",
                    "--stash",
                    action="store_true",
                    required=False,
                    dest="stash",
                    default=False,
                    help="display stash details",
                ),
            ]
        )
        mock_parser.parse_args.assert_called_once_with()
        mock_check.assert_called_once_with("/tmp/test111", True, False)
