import os
import re
from setuptools import setup, find_packages

name = "acspec"

with open(os.path.join(os.path.dirname(__file__), name + '/__init__.py')) as f:
    _versions = re.search(
        "^__version__ = ['|\"](\d\.\d+\.\d+((\.dev|rc)\d?)?)['|\"]$",
        f.read(), re.M
    )
    if not _versions:
        raise StandardError(
            "Please provide a version in your __init__.py corresponding to " +
            "the format: __version__ = '<version>'"
        )
    version = _versions.group(1)

tests_require = [
    'mock >= 1.0.1',
    'pytest >= 2.6.4',
    'pytest-cov >= 1.8.1'
]

extras_require = {}
extras_require['tests'] = tests_require

setup(
    name=name,
    version=version,
    description="Library to create schematics models from dicts or YAML",
    author="Michael Jurke",
    author_email="michael.jurke@retresco.de",
    url="http://www.retresco.de",
    license='MIT',
    packages=[
        name + "." + package for package in find_packages(name)
    ],
    include_package_data=True,
    install_requires=[
        'schematics >=1.1.0,<2.0.0',
        'futures',
        'pyyaml'
    ],
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'extract_specs = acspec.scripts.extract_specs:extract_specs'
        ]
    }
)
