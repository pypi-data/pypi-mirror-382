# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys

import pytest


def main() -> None:
    curr_path = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        args = [curr_path]
    print("*" * 100)
    print("测试文件: ", args)
    print("*" * 100)

    pytest.main(args)


if __name__ == "__main__":
    main()
