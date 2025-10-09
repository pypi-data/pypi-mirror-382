#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@created: 25.03.2023
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com
"""Setup script for fastQuast."""
import os
from setuptools import setup, find_packages

# read the contents of your README file
this_directory = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(this_directory, "README.md")

with open(readme_path, 'r', newline='', encoding='utf-8') as readme_file:
	long_description = readme_file.read()
	long_description_content_type = 'text/markdown'


setup(
    name='fastQuast',
    version='1.2.0',
    description='Fast and simple Quality Assessment Tool for Large Genomes',
    long_description = long_description,
	long_description_content_type = long_description_content_type,
    author='Aleksey Komissarov',
    author_email='ad3002@gmail.con',
    url='https://github.com/aglabx/fastQuast',
    packages=find_packages(),
    install_requires=[
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'fastQuast=fastQuast.fastQuast:main',
            'fastquast=fastQuast.fastQuast:main',
        ],
    },
)
