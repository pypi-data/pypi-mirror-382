# -*- coding: utf-8 -*-

import os
import shutil

from plum_tools.conf import PathConfig
from setuptools import find_packages, setup


def install():
    setup(
        setup_requires=[],
        include_package_data=True,
        packages=find_packages(exclude=["tests", "docs"]),
    )


def init():
    if not os.path.exists(PathConfig.plum_yml_path):
        shutil.copy(os.path.join(PathConfig.root, PathConfig.plum_yml_name), PathConfig.home)


if __name__ == "__main__":
    install()
    init()
