from pathlib import Path
import setuptools

name = "wheelie"

__version__ = None

here = Path(__file__).parent

exec((here / name / "_version.py").read_text())

print(setuptools.find_packages())

setup_args = dict(
    name=name,
    version=__version__,
    author="deathbeds",
    author_email="tony.fast@gmail.com",
    description="Create a shareable wheel with nbconvert.",
    long_description="""(here / "readme.md").read_text()""",
#    long_description_content_type='text/markdown',
    url="https://github.com/deathbeds/wheelie",
    python_requires=">=3.6",
    license="BSD-3-Clause",
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=[
        "jupyter",
        "wheel",
        "black",
        "nbconvert",
        "pip",
    ],
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 4 - Beta",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'jupyter-wheelie = wheelie:main',
        ],
        'nbconvert.exporters': [
            'black = wheelie.exporter:BlackExporter',
        ],
    },
)

if __name__ == "__main__":
    setuptools.setup(**setup_args)
