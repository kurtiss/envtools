#!/usr/bin/env python
# encoding: utf-8
"""
setup.py
"""

from setuptools import setup, find_packages
import os

execfile(os.path.join('src', 'envtools', 'version.py'))

setup(
    name = 'envtools',
    version = VERSION,
    description = 'envtools is a productivity suite for virtualenv-based projects',
    author = 'Kurtiss Hare',
    author_email = 'kurtiss@gmail.com',
    url = 'http://www.github.com/kurtiss/envtools',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    scripts = [],
    entry_points = {
        "console_scripts" : [
            "addwork = envtools:addwork",
            "rmwork = envtools:rmwork",
            "lswork = envtools:lswork",
        ]
    
    },
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe = False
)
