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
"""Builds a scripture graph.

Example usage:

# Download Standard Works EPUB files.
$ ../download_epub.sh
# Generate a graph.
$ python build_graph.py \
    --input_pattern="*.epub" \
    --output=scripture_graph.graphml
"""

import dataclasses
import glob

from absl import app
from absl import flags
from absl import logging
import networkx as nx

from scripture_graph import graph_lib

FLAGS = flags.FLAGS
flags.DEFINE_string('input_pattern', None, 'Input EPUB pattern.')
flags.DEFINE_string('output', None, 'Output graph filename.')


def main(argv):
    del argv  # Only used by app.run().
    scripture_graph = graph_lib.ScriptureGraph()
    for filename in glob.glob(FLAGS.input_pattern):
        logging.info(filename)
        this_graph = graph_lib.read_epub(filename)
        scripture_graph.update(this_graph)
        logging.info(this_graph)
    logging.info(scripture_graph)
    graph = nx.DiGraph()
    for key, verse in scripture_graph.verses.items():
        volume = graph_lib.get_volume(verse.book)
        graph.add_node(key,
                       kind='verse',
                       volume=volume,
                       **dataclasses.asdict(verse))
    for key, topic in scripture_graph.topics.items():
        volume = graph_lib.get_volume(topic.source)
        graph.add_node(key,
                       kind='topic',
                       volume=volume,
                       **dataclasses.asdict(topic))
    references = graph_lib.correct_topic_references(
        verses=scripture_graph.verses.keys(),
        topics=scripture_graph.topics.keys(),
        references=scripture_graph.references)
    duplicated_edges = 0
    for reference in references:
        if reference.source not in graph.nodes:
            raise KeyError(f'missing source for {reference}')
        if reference.target not in graph.nodes:
            raise KeyError(f'missing target for {reference}')
        if (reference.source, reference.target) in graph.edges:
            duplicated_edges += 1
        else:
            graph.add_edge(reference.source, reference.target)
    if duplicated_edges:
        logging.info(f'ignored {duplicated_edges} duplicated edges')
    logging.info(nx.info(graph))
    if FLAGS.output.endswith('.gml'):
        nx.write_gml(graph, FLAGS.output)
    elif FLAGS.output.endswith('.graphml'):
        nx.write_graphml(graph, FLAGS.output)
    elif FLAGS.output.endswith('.js'):
        graph_lib.write_cytoscape(graph, FLAGS.output)
    else:
        raise NotImplementedError(FLAGS.output)


if __name__ == '__main__':
    flags.mark_flags_as_required(['input_pattern', 'output'])
    app.run(main)
