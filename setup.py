#!/usr/bin/env python
#
# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0. 
# In applying this licence, ECMWF does not waive the privileges and immunities 
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import io
import os.path

from setuptools import setup, find_packages

import ecmwfapi

def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding='utf-8').read()

setup(
    name='ecmwf-api-client',
    version=ecmwfapi.__version__,
    description=ecmwfapi.__doc__,
    long_description=read('README.md'),
    author='European Centre for Medium-Range Weather Forecasts (ECMWF)',
    author_email='software.support@ecmwf.int',
    license='Apache License Version 2.0',
    url='https://github.com/ecmwf/ecmwf-api-client',
    long_description_content_type='text/markdown',

    packages=find_packages(),
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
)
