#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

from setuptools import setup, find_packages


with open('%s/VERSION' % here) as f:
    __version__ = f.readline().strip()

setup(
    author='Frederik Petersen',
    author_email='frederik@the-imperfection.de',
    description='ahocorapy - Pure python ahocorasick implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    name='ahocorapy',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['future'],
    python_requires='>=2.7',
    url='https://github.com/FrederikP/ahocorapy',
    project_urls={
        'Source': 'https://github.com/FrederikP/ahocorapy'
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    keywords = ['keyword', 'search', 'purepython', 'aho-corasick', 'ahocorasick'],
    license='MIT',
    version=__version__
)
