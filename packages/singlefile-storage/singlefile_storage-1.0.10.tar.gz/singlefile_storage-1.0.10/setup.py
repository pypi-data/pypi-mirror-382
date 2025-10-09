#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: qicongsheng
from singlefile_storage import help
from setuptools import setup, find_packages

setup(
    name=help.get_name(),
    version=help.get_version(),
    keywords=help.get_name(),
    description='SingleFile Rest Storage for python.',
    license='MIT License',
    url=help.get_source_url(),
    author='qicongsheng',
    author_email='qicongsheng@outlook.com',
    packages=find_packages(),
    include_package_data=True,
    platforms=['any'],
    install_requires=[
        'flask',
        'flask_httpauth'
    ],
    entry_points={
        'console_scripts': [
            'singlefile-storage = singlefile_storage.__main__:main'
        ]
    }
)
