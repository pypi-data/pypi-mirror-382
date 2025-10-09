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

import io
import os
import re
import sys
from distutils.command.build_ext import build_ext
from shutil import copytree, copy, rmtree, move

from setuptools import setup, Extension

if sys.version_info < (3, 8):
    print("Python versions prior to 3.8 are not supported for PyFlink.",
          file=sys.stderr)
    sys.exit(-1)


def remove_if_exists(file_path):
    if os.path.exists(file_path):
        if os.path.islink(file_path) or os.path.isfile(file_path):
            os.remove(file_path)
        else:
            assert os.path.isdir(file_path)
            rmtree(file_path)

this_directory = os.path.abspath(os.path.dirname(__file__))

TEMP_PATH = "deps"
SCRIPTS_TEMP_PATH = os.path.join(TEMP_PATH, "bin")
PYFLINK_TEMP_PATH = os.path.join(TEMP_PATH, "pyflink")
FLINK_SOURCE_PATH = os.path.join(TEMP_PATH, "source")
SCRIPTS_PATH = os.path.join(this_directory, "bin")
PYFLINK_OVERRIDES_PATH = os.path.join(this_directory, "pyflink")

FLINK_ARTIFACT_URL = "https://dlcdn.apache.org/flink/flink-1.20.0/flink-1.20.0-src.tgz"
FLINK_ARTIFACT_PYTHON_PATH = "flink-1.20.0/flink-python/pyflink"

in_flink_source = os.path.isfile("../confluent-flink-table-api-java-plugin/src/main/java/io/confluent/flink/plugin/ConfluentSettings.java")
if in_flink_source:
  version_file = os.path.join(this_directory, 'pyflink/version.py')
else:
  version_file = os.path.join(this_directory, 'deps/pyflink/version.py')

try:
  exec(open(version_file).read())
except IOError:
  print("Failed to load PyFlink version file for packaging. '%s' not found!" % version_file, file=sys.stderr)
  sys.exit(-1)
VERSION = __version__  # noqa

def download_python_files():
  try:
    from urllib.request import urlopen
    import tarfile
    from io import BytesIO

    r = urlopen(FLINK_ARTIFACT_URL)
    t = tarfile.open(name=None, fileobj=BytesIO(r.read()))
    members = [ x for x in t.getmembers() if x.name.startswith(FLINK_ARTIFACT_PYTHON_PATH)]
    t.extractall(members = members, path = FLINK_SOURCE_PATH)
    t.close()
    move(os.path.join(FLINK_SOURCE_PATH, FLINK_ARTIFACT_PYTHON_PATH), PYFLINK_TEMP_PATH)
  except IOError:
    print("Failed to download PyFlink files for packaging.", file=sys.stderr)
    sys.exit(-1)

def prepare_dist():
  try:
    os.mkdir(TEMP_PATH)
  except:
    print("Temp path for symlink to parent already exists {0}".format(TEMP_PATH), file=sys.stderr)
    sys.exit(-1)

  if not os.path.isdir(PYFLINK_TEMP_PATH):
    download_python_files()

  try:
    os.symlink(SCRIPTS_PATH, SCRIPTS_TEMP_PATH)
  except BaseException:  # pylint: disable=broad-except
    copytree(SCRIPTS_PATH, SCRIPTS_TEMP_PATH)

  copytree(PYFLINK_OVERRIDES_PATH, os.path.join(PYFLINK_TEMP_PATH), dirs_exist_ok=True)

def setup_files():
  if re.search('dev.*$', VERSION) is not None:
    apache_flink_libraries_dependency = 'confluent-flink-jars==%s' % VERSION
  else:
    split_versions = VERSION.split('.')
    split_versions[-1] = str(int(split_versions[-1]) + 1)
    NEXT_VERSION = '.'.join(split_versions)
    apache_flink_libraries_dependency = 'confluent-flink-jars>=%s,<%s' % \
                                        (VERSION, NEXT_VERSION)

  script_names = ["pyflink-shell.sh", "find-flink-home.sh"]
  scripts = [os.path.join("bin", script) for script in script_names]
  scripts.append("deps/pyflink/find_flink_home.py")

  PACKAGES = ['pyflink',
              'pyflink.table',
              'pyflink.table.confluent',
              'pyflink.util',
              'pyflink.datastream',
              'pyflink.datastream.connectors',
              'pyflink.datastream.formats',
              'pyflink.common',
              'pyflink.metrics',
              'pyflink.bin',
              'pyflink.testing']

  PACKAGE_DIR = {
    'pyflink': 'deps/pyflink',
    'pyflink.bin': 'bin'
  }

  PACKAGE_DATA = {
    'pyflink.bin': ['*']}

  install_requires = ['py4j==0.10.9.7',
                      'python-dateutil>=2.8.0,<3',
                      'cloudpickle>=2.2.0',
                      'pytz>=2018.3',
                      'requests>=2.26.0',
                      'pemja==0.4.1;''platform_system != "Windows"',
                      'httplib2>=0.19.0',
                      'ruamel.yaml>=0.18.4',
                      apache_flink_libraries_dependency]

  setup(
      name='confluent-flink-table-api-python-plugin',
      version=VERSION,
      packages=PACKAGES,
      include_package_data=True,
      package_dir=PACKAGE_DIR,
      package_data=PACKAGE_DATA,
      scripts=scripts,
      url='https://confluent.io',
      license='https://www.apache.org/licenses/LICENSE-2.0',
      author='Confluent',
      author_email='dev@confluent.io',
      python_requires='>=3.8',
      install_requires=install_requires,
      cmdclass={'build_ext': build_ext},
      description='Confluent Apache Flink Table API Python',
      long_description="Confluent Apache Flink Table API Python",
      long_description_content_type='text/markdown',
      zip_safe=False,
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
    if not os.path.isdir(SCRIPTS_TEMP_PATH):
      print("The flink core files are not found. Please make sure your installation package "
            "is complete, or do this in the flink-python directory of the flink source "
            "directory.")
      sys.exit(-1)
  setup_files()
finally:
    if in_flink_source:
        remove_if_exists(TEMP_PATH)
