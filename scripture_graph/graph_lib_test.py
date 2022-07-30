# Copyright 2020-2022 Steven Kearnes
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
from collections import Counter

import pytest

from scripture_graph import graph_lib

@pytest.mark.parametrize("text,expected", [
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
    ('TG Israel, Judah, People of.', ['TG Israel, Judah, People of']),
    ('TG Self-mastery.', ['TG Self-mastery']),
    ('Prov. 22:1. TG Affliction; Blessing.',
     ['Prov. 22:1', 'TG Affliction', 'TG Blessing']),
    ('TG God, Gifts of; Record Keeping',
     ['TG God, Gifts of', 'TG Record Keeping']),
    ('Mosiah 1:2 (2-3); D&C 68:25 (25, 28). TG Honoring Father and Mother.',
     ['Mosiah 1:2', 'D&C 68:25', 'TG Honoring Father and Mother']),
    ('JST 1 Chr. 21:15 (Appendix).', []),
    ('Neh. 11:16, 22 (22-34), 33',
     ['Neh. 11:16', 'Neh. 11:22', 'Neh. 11:33'])])
def test_parse_reference(text, expected):
    assert Counter(graph_lib.parse_reference(text)) == Counter(expected)

@pytest.mark.parametrize("topics,references,expected", [
    (
        ['TG Lot'],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Lot')],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Lot')],
    ),
    (
        ['TG Lose, Lost'],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Lost')],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Lose, Lost')],
    ),
    (
        ['TG Transgress, Transgression'],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Transgress')],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Transgress, Transgression')],
    ),
    (
        ['TG Carnal Mind', 'TG Mind, Minded'],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Mind')],
        [graph_lib.Reference('1 Ne. 3:7', 'TG Mind, Minded')],
    )])
def test_correct_topic_references(topics, references, expected):
    assert Counter(graph_lib.correct_topic_references(['1 Ne. 3:7'], topics, references)) == Counter(expected)
