# Copyright 2021 Steven Kearnes
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
"""Precomputes connections for the Connection Explorer."""

import json

from absl import app
from absl import flags
import networkx as nx

from scripture_graph import graph_lib

FLAGS = flags.FLAGS
flags.DEFINE_string('input', None, 'Input GraphML filename.')
flags.DEFINE_string('output', None, 'Output JSON filename.')


def main(argv):
    del argv  # Only used by app.run().
    graph = nx.read_graphml(FLAGS.input)
    graph_lib.remove_topic_nodes(graph)
    connections = {}
    for verse in graph.nodes:
        incoming = set()
        outgoing = set()
        suggested = set()
        for source, target in graph.in_edges(verse):
            assert target == verse
            kind = graph.edges[(source, target)].get('kind')
            if kind:
                suggested.add(source)
            else:
                incoming.add(source)
        for source, target in graph.out_edges(verse):
            assert source == verse
            kind = graph.edges[(source, target)].get('kind')
            if kind:
                suggested.add(target)
            else:
                outgoing.add(target)
        data = graph.nodes[verse]
        connections[verse] = {
            'volume': data['volume'],
            'book': data['book'],
            'chapter': data['chapter'],
            'verse': data['verse'],
        }
        if incoming:
            connections[verse]['incoming'] = list(incoming)
        if outgoing:
            connections[verse]['outgoing'] = list(outgoing)
        if suggested:
            connections[verse]['suggested'] = list(suggested)
    with open(FLAGS.output, 'w') as f:
        json.dump(connections, f, indent=2)


if __name__ == '__main__':
    flags.mark_flags_as_required(['input', 'output'])
    app.run(main)
