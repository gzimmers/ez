from setuptools import setup, find_packages
from ez_cmd import __version__

setup(
    name="ez-cmd",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ez=ez_cmd.cli:cli",
        ],
    },
    author="Greg Zimmers",
    description="A CLI tool for saving and replaying commands",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="cli, automation, command-line",
    python_requires=">=3.6",
)
