# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_conf
#         Desc: 测试枚举
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-03 22:58
#=============================================================================
"""

import os
import unittest
from typing import Optional

import pytest
from plum_tools.conf import (
    ClsReadOnlyClass,
    Constant,
    GitCommand,
    OsCommand,
    PathConfig,
    ReadOnlyClass,
    SSHConfig,
    generate_test_class,
)


class TestClsReadOnlyClass:
    def test_bases_class(self) -> None:
        assert isinstance(ClsReadOnlyClass.__bases__[0], type)

    def test_variable_read_only(self) -> None:
        class MyClass(metaclass=ClsReadOnlyClass):
            name: Optional[str] = "test"
            value = "test"

            def __init__(self) -> None:
                self.name = None

        m = MyClass()
        m.name = "test2"
        m.new_name = "test2"  # type: ignore[attr-defined] # pylint: disable=attribute-defined-outside-init

        with pytest.raises(ValueError) as err:
            MyClass.name = "tes2"
        assert err.value.args[0] == "name is read-only"


class TestReadOnlyClass:
    def test_bases_class(self) -> None:
        assert ReadOnlyClass.__class__ is ClsReadOnlyClass

    def test_variable_read_only(self) -> None:
        class MyClass(ReadOnlyClass):
            name = "test"
            value = "test"

        with pytest.raises(ValueError) as err:
            m = MyClass()
            m.name = "test2"
        assert err.value.args[0] == "name is read-only"

        with pytest.raises(ValueError) as err:
            m = MyClass()
            m.new_name = "test2"  # pylint: disable=attribute-defined-outside-init
        assert err.value.args[0] == "new_name is read-only"

        with pytest.raises(ValueError) as err:
            MyClass.name = "tes2"
        assert err.value.args[0] == "name is read-only"


class TestGitCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.g = GitCommand

    def tearDown(self) -> None:
        del self.g

    def test_pull_keyword(self) -> None:
        assert self.g.pull_keyword == '"git pull"'

    def test_push_keyword(self) -> None:
        assert self.g.push_keyword == '"git push"'

    def test_git_checkout(self) -> None:
        assert self.g.git_checkout == "git checkout %s"

    def test_branch_abbrev(self) -> None:
        assert self.g.branch_abbrev == "git rev-parse --abbrev-ref HEAD"

    def test_stash_list(self) -> None:
        assert self.g.stash_list == "git stash list"

    def test_stash_pop(self) -> None:
        assert self.g.stash_pop == "git stash pop --index %s"

    def test_stash_save(self) -> None:
        assert self.g.stash_save == 'git stash save "%s"'

    def test_status_default(self) -> None:
        assert self.g.status_default == "git status"

    def test_status_short(self) -> None:
        assert self.g.status_short == "git status -s"


class TestOsCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.o = OsCommand

    def tearDown(self) -> None:
        del self.o

    def test_find_command(self) -> None:
        assert self.o.find_command == 'find %s -name ".git"'

    def test_ipmi_command(self) -> None:
        assert self.o.ipmi_command == "ipmitool -I lanplus -H %(ip)s -U %(user)s -P %(password)s %(command)s"

    def test_ping_command(self) -> None:
        assert self.o.ping_command == "ping -W 3 -c 1 %s"

    def test_stat_command(self) -> None:
        assert self.o.stat_command == "stat %s"


class TestSSHConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.s = SSHConfig

    def tearDown(self) -> None:
        del self.s

    def test_connect_timeout(self) -> None:
        assert self.s.connect_timeout == 3

    def test_default_ssh_port(self) -> None:
        assert self.s.default_ssh_port == 22


class TestConstant(unittest.TestCase):
    def setUp(self) -> None:
        self.c = Constant

    def tearDown(self) -> None:
        del self.c

    def test_command_timeout(self) -> None:
        assert self.c.command_timeout == 3

    def test_processes_number(self) -> None:
        assert self.c.processes_number == 100

    def test_stash_uuid(self) -> None:
        assert self.c.stash_uuid == "plum123456789987654321plum"


class TestPathConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.p = PathConfig

    def tearDown(self) -> None:
        del self.p

    def test_plum_yml_name(self) -> None:
        assert self.p.plum_yml_name == ".plum_tools.yaml"

    def test_ssh_config_name(self) -> None:
        assert self.p.ssh_config_name == ".ssh/config"

    def test_home(self) -> None:
        assert self.p.home == os.environ["HOME"]

    def test_plum_yml_path(self) -> None:
        assert self.p.plum_yml_path == os.path.join(self.p.home, self.p.plum_yml_name)

    def test_ssh_config_path(self) -> None:
        assert self.p.ssh_config_path == os.path.join(self.p.home, self.p.ssh_config_name)

    def test_root(self) -> None:
        current_path = os.path.dirname(os.path.abspath(__file__))
        assert self.p.root == os.path.join(os.path.dirname(current_path), "plum_tools")


def test_generate_test_class(capsys: pytest.CaptureFixture) -> None:
    context = """class TestConstant(unittest.TestCase):
    def setUp(self) -> None:
        self.c = Constant

    def tearDown(self) -> None:
        del self.c

    def test_command_timeout(self) -> None:
        assert self.c.command_timeout == '3'

    def test_processes_number(self) -> None:
        assert self.c.processes_number == '100'

    def test_stash_uuid(self) -> None:
        assert self.c.stash_uuid == 'plum123456789987654321plum'

"""
    generate_test_class(Constant, "c")
    captured = capsys.readouterr()
    output = captured.out
    assert output == context
