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
"""Tests for scripture_graph.graph_lib."""

from absl.testing import absltest
from absl.testing import parameterized

from scripture_graph import graph_lib


class GraphLibTest(parameterized.TestCase, absltest.TestCase):

    @parameterized.parameters(
        ('Prov. 22:1.', ['Prov. 22:1']),
        ('Prov. 22:1 (1-3)', ['Prov. 22:1']),
        ('Prov. 22:1 (1-3); 23:2; 24:3 (3-5)',
         ['Prov. 22:1', 'Prov. 23:2', 'Prov. 24:3']),
        ('Isa. 42:1 (1, 3-4)', ['Isa. 42:1']),
        ('D&C 13.', ['D&C 13:1']),
        ('Prov. 22:1; 23:2 (2-4); Mosiah 1:2; 3 Ne. 5:6 (6-8)',
         ['Prov. 22:1', 'Prov. 23:2', 'Mosiah 1:2', '3 Ne. 5:6']),
        ('TG Birthright.', ['TG Birthright']),
        ('TG Kingdom of God, on Earth.', ['TG Kingdom of God, on Earth']),
        ('Prov. 22:1. TG Affliction; Blessing.',
         ['Prov. 22:1', 'TG Affliction', 'TG Blessing']),
        ('TG God, Gifts of; Record Keeping',
         ['TG God, Gifts of', 'TG Record Keeping']),
        ('Mosiah 1:2 (2-3); D&C 68:25 (25, 28). TG Honoring Father and Mother.',
         ['Mosiah 1:2', 'D&C 68:25', 'TG Honoring Father and Mother']),
    )
    def test_parse_reference(self, text, expected):
        self.assertCountEqual(graph_lib.parse_reference(text), expected)


if __name__ == '__main__':
    absltest.main()
