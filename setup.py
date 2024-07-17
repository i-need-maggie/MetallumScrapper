import os, io, setuptools
from typing import List, Optional, Union

ROOT_DIR = os.path.dirname(__file__)

def pull_path(*path) -> str:
    return os.path.join(ROOT_DIR, *path)

def read_long_desc(filename:str='README.md') -> str:
    """Read long description from ReadMe file

    Args:
        filename (str, optional): name of read me file. Defaults to 'README.md'.

    Returns:
        str: long description
    """
    desc_path = pull_path(*filename)
    return io.open(desc_path, 'r', encoding='utf-8').read()

def pull_requirements(filename:str='requirements.txt') -> List[str]:
    """Pull Python package dependencies from requirement file

    Args:
        filename (str, optional): name of requirements file. Defaults to 'requirements.txt'.

    Returns:
        List[str]: list of dependencies
    """
    req_path = pull_path(*filename)
    return io.open(req_path).read().strip().split('\n')

setuptools.setup(
    name="MetallumScrapper",
    version="0.1",
    author="i-need-maggie",
    license="MIT license",
    description=("Metal Archive scrapping implementation"),
    long_description=read_long_desc('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT license",
    ],
    packages=setuptools.find_packages(exclude=("benchmarks", "docs",
                                               "examples", "tests")),
    python_requires=">=3.8",
    install_requires=pull_requirements('requirements.txt'),
)
