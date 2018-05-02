
# coding: utf-8

try:
    from . import setup
    from . import exporter
except:
    import setup, exporter

from IPython import get_ipython

import shutil, nbconvert.nbconvertapp, tempfile, wheel.bdist_wheel
from traitlets import *
from pathlib import Path
from itertools import chain
from distutils.errors import DistutilsError

try:
    from pip.commands import install as pip_installer
except:
    from pip._internal.commands import install as pip_installer


nbconvert.nbconvertapp.NbConvertApp.export_format.default_value = "exporter.BlackExporter" if __name__ == "__main__" else "black"


def move_files_with_parents(build_directory, root, *files, log=None):
    for file in map(Path, files):
        to = build_directory / file.relative_to(root)
        to.parent.mkdir(exist_ok=True)
        if to.exists():
            log and log.warning(
                """Skipping {file} copy because it has been created from a notebook and is already in the package""".format(
                    file=file
                )
            )
        else:
            shutil.copy(file, to)
            log and log.info("""Moving {file} to the package.""".format(file=file))


def create_modules(build_directory):
    for file in filter(Path.is_dir, build_directory.iterdir()):
        init = file / "__init__.py"
        init.exists() or init.touch()


def create_package_data(build_directory, package_data):
    from collections import defaultdict

    package_data = defaultdict(list)
    name = build_directory.stem
    for file in build_directory.rglob("*"):
        if file.is_file() and file.suffix != ".py":
            package_data[".".join(file.relative_to(build_directory).parent.parts)].append(str(file))
    return package_data


def install_wheel(wheel):
    install = pip_installer.InstallCommand(isolated=True)
    install.run(*install.parse_args("{} --no-cache-dir --upgrade".format(wheel).split()))


class Wheelie(nbconvert.nbconvertapp.NbConvertApp):
    name = Unicode(allow_none=True).tag(config=True)
    version = Unicode(default_value="""0.0.1""").tag(config=True)
    description = Unicode(default_value="""A Package automatically created from notebooks.""").tag(
        config=True
    )
    root = Unicode(default_value=".").tag(config=True)
    output = Unicode(".").tag(config=True)
    install = Bool(default_value=False).tag(config=True)
    python_files = List(default_value=[])
    package_data = List(default_value=[])
    test = Unicode(allow_none=True)

    def init_notebooks(self):
        super().init_notebooks()
        self.notebooks = list(
            filter(
                bool,
                (
                    file
                    if file.endswith(".ipynb")
                    else self.python_files.append(file)
                    if file.endswith(".py")
                    else self.package_data.append(file)
                    for file in self.notebooks
                ),
            )
        )

    def convert_notebooks(self):
        wheel.bdist_wheel.logger = self.log

        self.notebooks = [str(Path(self.root) / notebook) for notebook in self.notebooks]
        self.exporter = nbconvert.get_exporter(self.export_format)(config=self.config)
        self.initialize(argv=tuple())
        with tempfile.TemporaryDirectory() as path:
            path = Path(path)
            build_directory = path / self.name

            for notebook in self.notebooks:
                self.writer = nbconvert.writers.files.FilesWriter(
                    build_directory=str((build_directory / notebook).parent)
                )
                self.convert_single_notebook(notebook)

            move_files_with_parents(
                build_directory, self.root, *self.python_files, *self.package_data, log=self.log
            )
            create_modules(build_directory)

            opts = {}
            if self.test:
                opts["test_suite"] = self.test

            distribution = setup.setup(
                self.name,
                build_directory,
                wheel_dir=self.output,
                package_data=create_package_data(build_directory, self.package_data),
                version=self.version,
                description=self.description,
                **opts
            )
            if self.test:
                distribution.run_command("test")

            distribution.run_command("bdist_wheel")

        self.log.info("""Exporting {0}.""".format(distribution.wheel_info))

        if self.install:
            pip_installer.logger = self.log
            install_wheel(distribution.wheel_info)

        return distribution.wheel_info

    __call__ = convert_notebooks

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self()


main = Wheelie.launch_instance

if __name__ == "__main__":
    Path("wheelie.py").write_text(exporter.BlackExporter().from_filename("wheelie.ipynb")[0])


# ## Context Manager Configuration

#     with Wheelie() as package:
#         package.name='testable'
#         package.notebooks='*.ipynb *.py'.split()
#         package.output='somewhere'

# ## Function call configuration
#
#     Wheelie(name='testable', notebooks='*.ipynb *.py'.split(), output='somewhere', install=True)()

# ## Command Line configuration
