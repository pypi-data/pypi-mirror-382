################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################
from __future__ import print_function

import glob
import io
import os
import platform
import subprocess
import sys
from shutil import copytree, copy, rmtree

from setuptools import setup
from xml.etree import ElementTree as ET

def remove_if_exists(file_path):
  if os.path.exists(file_path):
    if os.path.islink(file_path) or os.path.isfile(file_path):
      os.remove(file_path)
    else:
      assert os.path.isdir(file_path)
      rmtree(file_path)

this_directory = os.path.abspath(os.path.dirname(__file__))
TEMP_PATH = "deps"

in_flink_source = os.path.isfile("../../confluent-flink-table-api-java-plugin/src/main/java/io/confluent/flink/plugin/ConfluentSettings.java")
if in_flink_source:
  version_file = os.path.join(this_directory, '../pyflink/version.py')
else:
  version_file = os.path.join(TEMP_PATH, 'pyflink/version.py')

try:
    exec(open(version_file).read())
except IOError:
    print("Failed to load PyFlink version file for packaging. " +
          "'%s' not found!" % version_file,
          file=sys.stderr)
    sys.exit(-1)
VERSION = __version__  # noqa

LIB_TEMP_PATH = os.path.join(TEMP_PATH, "lib")
VERSION_FILE_TEMP_PATH = os.path.join(TEMP_PATH, "pyflink/version.py")
LIB_PATH = os.path.join(this_directory, "target/dependency")

def prepare_dist():
  try:
    os.mkdir(TEMP_PATH)
  except:
    print("Temp path for symlink to parent already exists {0}".format(TEMP_PATH), file=sys.stderr)
    sys.exit(-1)

  if not os.path.isdir(LIB_PATH):
    print("Build the java module first")
    sys.exit(-1)

  try:
    os.symlink(LIB_PATH, LIB_TEMP_PATH)
    support_symlinks = True
  except BaseException:  # pylint: disable=broad-except
    support_symlinks = False

  os.mkdir(os.path.join(TEMP_PATH, "pyflink"))
  if support_symlinks:
    os.symlink(version_file, VERSION_FILE_TEMP_PATH)
  else:
    copytree(LIB_PATH, LIB_TEMP_PATH)
    copy(version_file, VERSION_FILE_TEMP_PATH)


def setup_files():
  PACKAGES = ['pyflink.lib']

  PACKAGE_DIR = {'pyflink.lib': LIB_TEMP_PATH}
  PACKAGE_DATA = {
    'pyflink': ['version.py'],
    'pyflink.lib': ['*.jar']
  }

  setup(
      name='confluent-flink-jars',
      version=VERSION,
      packages=PACKAGES,
      include_package_data=True,
      package_dir=PACKAGE_DIR,
      package_data=PACKAGE_DATA,
      url='https://confluent.io',
      license='https://www.apache.org/licenses/LICENSE-2.0',
      author='Confluent',
      author_email='dev@confluent.io',
      python_requires='>=3.8',
      description='Confluent Apache Flink Jars',
      long_description="Confluent Apache Flink Jars",
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'],
  )

try:
  if in_flink_source:
    prepare_dist()
  else:
    if not os.path.isdir(LIB_TEMP_PATH):
      print("The flink core files are not found. Please make sure your installation package "
            "is complete, or do this in the flink-python directory of the flink source "
            "directory.")
      sys.exit(-1)
  setup_files()
finally:
  if in_flink_source:
    remove_if_exists(TEMP_PATH)
