#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.2"


setup(
    name="appraiser",
    author="Gregory Rehm",
    version=__version__,
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    install_requires=[
        "cowboycushion",
        "flowzillow",
        "redis",
        "scrapezillow",
    ],
    entry_points={
        "console_scripts": [
            "appraiser=appraiser.main:main",
            "update_demographics=appraiser.update_demographics:main",
        ]
    }
)
