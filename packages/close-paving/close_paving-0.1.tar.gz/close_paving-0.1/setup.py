#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: setup.py
# @time: 2025/10/8 23:31
# @Software: PyCharm


import os
from setuptools import find_packages
from close_paving import version
from astartool.setuptool import load_install_requires, get_version, setup, read_file

osp = os.path

setup(
    name='close-paving',
    version=get_version(version),
    description=(
        'toolkit for hexagonal grid'
    ),
    long_description=read_file('README.en.md', encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='A.Star',
    author_email='astar@snowland.ltd',
    maintainer='A.Star',
    maintainer_email='astar@snowland.ltd',
    license='Apache v2.0',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/hoops/close-paving',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=load_install_requires()
)
