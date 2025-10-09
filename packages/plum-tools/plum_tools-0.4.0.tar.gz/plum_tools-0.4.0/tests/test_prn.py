# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_prn
#         Desc: 测试prn模块
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 16:24
#=============================================================================
"""

from typing import List, Optional
from unittest import mock

import pytest
from plum_tools.conf import PathConfig
from plum_tools.prn import SyncFiles, get_project_conf, main


@pytest.mark.parametrize(
    "project, src, dest, delete, exclude",
    [
        ("plum", "/tmp", "/tmp", 0, []),
        ("plum", "/tmp", "/tmp", 0, [".git"]),
        ("2", "/tmp", "/tmp", 1, [".git"]),
        ("1", "/tmp/1", "/tmp/2", 1, [".git", "*.pyc"]),
        ("1", "/tmp/1", "/tmp/2", None, [".git", "*.pyc"]),
        ("xxx", "/tmp/1", "/tmp/2", None, []),
    ],
)
def test_get_project_conf(project: str, src: str, dest: str, delete: Optional[int], exclude: List[str]) -> None:
    with mock.patch(
        "plum_tools.utils.utils.YmlConfig.parse_config_yml",
        return_value={
            "projects": {
                project: {
                    "src": "/tmp",
                    "dest": "/tmp",
                    "delete": None,
                    "exclude": [],
                }
            }
        },
    ) as p, mock.patch("plum_tools.prn.get_file_abspath", side_effect=lambda x: x):
        data = get_project_conf(project, [src], [dest], delete, exclude)
        assert data == {
            "exclude": exclude,
            "delete": delete,
            "src": [src],
            "dest": [dest],
        }
        p.assert_called_with(PathConfig.plum_yml_path)


def test_translate(capsys: pytest.CaptureFixture) -> None:
    hostname, user, port, identityfile, src, dest, delete = (
        "1.1.1.1",
        "user",
        22,
        "",
        "/tmp",
        "/tmp",
        0,
    )
    exclude: List[str] = []
    u = SyncFiles(hostname, user, port, identityfile, src, dest, exclude, delete)
    with mock.patch("plum_tools.prn.run_cmd") as m:
        u.translate()
        m.call_args(
            'rsync -rtv -e \'ssh -p 22 -i  -o "UserKnownHostsFile=/dev/null" '
            '-o "StrictHostKeyChecking no" -o "ConnectTimeout=2"\' /tmp user@1.1.1.:/tmp'
        )
        captured = capsys.readouterr()
        output = captured.out
        assert (
            output
            == "[32m上传 /tmp/ 到 user@1.1.1.1 服务器(端口: 22) /tmp 成功[0m\n"  # pylint: disable=invalid-character-esc
        )


def test_main() -> None:
    mock_parser = mock.Mock()
    mock_args = mock.Mock(
        servers=["test", "dev"],
        projects=["test", "python"],
        default="default",
        download=False,
        identity_file="",
        user="",
        port=0,
        local="",
        remote="",
        delete=None,
        exclude=[],
        debug=False,
        version=False,
    )
    mock_project_conf = mock.Mock()
    mock_parser.parse_args.return_value = mock_args
    with mock.patch("plum_tools.prn.get_base_parser", return_value=mock_parser) as mock_argparse, mock.patch(
        "plum_tools.prn.get_project_conf", return_value=mock_project_conf
    ) as mock_project, mock.patch("plum_tools.prn.sync_files") as mock_sync:
        main()
        mock_argparse.assert_called_once_with()
        mock_parser.add_argument.assert_has_calls(
            [
                mock.call(
                    "-s",
                    "--servers",
                    required=False,
                    action="store",
                    dest="servers",
                    nargs="+",
                    help="specify server",
                ),
                mock.call(
                    "-p",
                    "--projects",
                    required=False,
                    action="store",
                    dest="projects",
                    nargs="+",
                    default=["default"],
                    help="specify project",
                ),
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
                    "--download",
                    action="store_true",
                    required=False,
                    dest="download",
                    default=False,
                    help="Download the file locally",
                ),
                mock.call(
                    "-i",
                    "--identityfile",
                    action="store",
                    required=False,
                    dest="identity_file",
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
                    "--port",
                    action="store",
                    required=False,
                    dest="port",
                    type=int,
                    default=0,
                    help="ssh login port",
                ),
                mock.call(
                    "-l",
                    "--local",
                    action="store",
                    required=False,
                    dest="local",
                    nargs="+",
                    default="",
                    help="local path",
                ),
                mock.call(
                    "-r",
                    "--remote",
                    action="store",
                    required=False,
                    dest="remote",
                    nargs="+",
                    default="",
                    help="remote path",
                ),
                mock.call(
                    "-d",
                    "--delete",
                    action="store",
                    required=False,
                    dest="delete",
                    type=int,
                    default=None,
                    help="delete remote path other file",
                ),
                mock.call(
                    "-e",
                    "--exclude",
                    action="store",
                    nargs="+",
                    required=False,
                    dest="exclude",
                    default=[],
                    help="exclude file",
                ),
                mock.call(
                    "--debug",
                    action="store_true",
                    required=False,
                    dest="debug",
                    default=False,
                    help="debug output from parser",
                ),
            ]
        )
        mock_parser.parse_args.assert_called_once_with()
        mock_project.assert_has_calls([mock.call(project, "", "", None, [], False) for project in ["test", "python"]])
        mock_sync.assert_called_once_with(
            ["test", "dev"],
            mock_args.type,
            "",
            0,
            "",
            [mock_project_conf, mock_project_conf],
            False,
            False,
        )
