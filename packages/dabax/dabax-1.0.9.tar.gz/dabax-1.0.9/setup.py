# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2021 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["M Sanchez del Rio - ESRF"]
__license__ = "MIT"
__date__ = "22/10/2021"

import os
from setuptools import setup, find_packages

README_FILE = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(README_FILE).read()

setup(name='dabax',
    version='1.0.9',
    description='python access to DABAX files',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='M Sanchez del Rio',
    author_email='srio@esrf.eu',
    url='https://github.com/oasys-kit/dabax/',
    packages=find_packages(include=['dabax', 'dabax.*']),
    install_requires=[
        'numpy',
        'scipy',
        'silx',
        ],
    setup_requires=[
        'setuptools',
        ],
    )
