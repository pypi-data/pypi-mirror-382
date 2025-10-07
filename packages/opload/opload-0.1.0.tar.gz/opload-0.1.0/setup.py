import os
from setuptools import setup, find_namespace_packages


CODEBASE_PATH = os.environ.get(
    "CODEBASE_PATH",
    default=os.path.join("src", "main"),
)

with open("requirements.txt", "r") as file:
    requirements = [line for line in file.read().splitlines() if line and not line.startswith("#")]

version_filepath = os.path.join(CODEBASE_PATH, "opload", "version")
with open(version_filepath, "r") as file:
    version = file.read().strip()

with open("README.md") as file:
    readme = file.read()

setup(
    name="opload",
    version=version,
    description="Opload: Open Loading Server",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://openstone.stonebase.mx/",
    author="OpenStone Software Foundation",
    author_email="fred@fahera.mx",
    packages=find_namespace_packages(where=CODEBASE_PATH),
    package_dir={
        "": CODEBASE_PATH
    },
    package_data={
        "": [
            version_filepath,
            "**/*.json",
            "**/*.yaml",
        ]
    },
    entry_points={
        "console_scripts": [
            "opload=opload.cli:CLI.cli_exec",
        ]
    },
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.12",
)
