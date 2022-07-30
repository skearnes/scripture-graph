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

setup(
    name="scripture-graph",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "cssselect>=1.1.0",
        "lxml>=4.6.2",
        "networkx>=2.5",
        "numpy>=1.19.2",
        "pandas>=1.1.5",
        "seaborn>=0.11.1",
        "tensorflow>=2.4.1",
        "tensorflow-hub>=0.11.0",
    ],
    extras_require={
        "tests": [
            "black[jupyter]>=22.3.0",
            "coverage>=5.2.1",
            "pylint>=2.13.9",
            "pytest>=7.1.1",
            "pytest-cov>=3.0.0",
            "pytype>=2022.5.19",
        ],
    },
)
