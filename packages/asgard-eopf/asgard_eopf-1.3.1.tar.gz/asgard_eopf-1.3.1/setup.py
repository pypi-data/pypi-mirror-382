#!/usr/bin/env python
# Copyright 2022 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This setup.py file is needed to build cython extensions (math).
The main configuration to build and install the package is done in the
pyproject.toml file.

Please do not run this file directly, use modern `pip wheel` or wheel's `build`.
They will install the package in an isolated environment, with the required
build-system dependencies.
* https://packaging.python.org/en/latest/discussions/setup-py-deprecated/
"""
import os
import shutil
import sysconfig
from warnings import warn

from Cython.Build.Dependencies import cythonize
from setuptools import Extension, setup

# Check "Python.h" for building cython extensions
# Give a hint if build fails in minimal environement
if not os.path.exists(f"{sysconfig.get_path('include')}/Python.h"):
    warn("Please install libpython3-dev. Cython needs Python header files.", RuntimeWarning)

# Check & set GCC for building cython extensions
path_to_gcc = shutil.which("gcc")
if path_to_gcc is None:
    warn("Please install gcc. Required to compile Cython module.", RuntimeWarning)
    path_to_gcc = "gcc"  # when trying to generate a source distribution (sdist)

os.environ["CC"] = path_to_gcc
os.environ["CFLAGS"] = "-pthread -fPIC -fwrapv -O3 -Wall -fno-strict-aliasing -m64 -fopenmp"

# Setup Cython extensions
extension = Extension("asgard.core.math", ["asgard/core/math.pyx"])
setup(ext_modules=cythonize([extension]))
