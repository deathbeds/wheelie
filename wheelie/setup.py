
# coding: utf-8

import sys, nbconvert.nbconvertapp, tempfile, setuptools.command, wheel.bdist_wheel
from traitlets import *
from pathlib import Path
import json
import shutil
import os


def setup(name, dir, wheel_dir=None, defaults=dict(version="0.0.1", zip_safe=False), **dict):

    class bdist_wheel(wheel.bdist_wheel.bdist_wheel):

        def initialize_options(self):
            wheel.bdist_wheel.bdist_wheel.initialize_options(self)
            self.dist_dir = str(Path(wheel_dir))
            self.bdist_dir = str(dir.parent) + "/build"

        def run(self):
            wheel.bdist_wheel.bdist_wheel.run(self)
            self.distribution.wheel_info = str(
                Path(self.dist_dir) / (self.get_archive_basename() + ".whl")
            )

    return setuptools.Distribution(
        {
            **defaults,
            **dict,
            "name": name,
            "packages": setuptools.find_packages(where=dir.parent),
            "package_dir": {"": str(dir.parent)},
            "script_name": "python",
            "cmdclass": {"bdist_wheel": bdist_wheel},
        }
    )


if __name__ == "__main__":
    get_ipython().system("jupyter nbconvert --to python setup.ipynb")
