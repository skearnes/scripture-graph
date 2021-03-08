# Copyright 2020 Steven Kearnes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Installation script."""

from setuptools import find_packages
from setuptools import setup

if __name__ == '__main__':
    setup(name='scripture-graph',
          packages=find_packages(),
          install_requires=[
              'absl-py~=0.11.0',
              'cssselect~=1.1.0',
              'lxml~=4.6.2',
              'networkx~=2.5',
              'numpy~=1.18.5',
              'pandas~=1.1.3',
              'seaborn~=0.11.0',
          ])
