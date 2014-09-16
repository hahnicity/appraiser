#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="appraiser",
    author="Gregory Rehm",
    version=__version__,
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    install_requires=[
        "flowzillow"
    ],
)
