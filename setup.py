from os import environ

from setuptools import find_namespace_packages, setup

setup(
    name='zimran-config',
    version=environ['GITHUB_REF_NAME'],
    packages=find_namespace_packages(include=['zimran.*']),
    install_requires=['pydantic'],
    python_requires='>=3.10',
    zip_file=False,
)
