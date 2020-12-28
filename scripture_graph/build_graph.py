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
$ python build_graph.py --input_pattern="*.epub" --output=scripture_graph.graphml
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
    verses = {}
    references = []
    for filename in glob.glob(FLAGS.input_pattern):
        logging.info(filename)
        this_verses, this_references = graph_lib.read_epub(filename)
        logging.info(f'Found {len(this_verses)} verses and'
                     f' {len(this_references)} references')
        verses.update(this_verses)
        references.extend(this_references)
    logging.info(
        f'Found {len(verses)} verses and {len(references)} references')
    graph = nx.DiGraph()
    for key, verse in verses.items():
        volume = graph_lib.get_volume(verse.book)
        graph.add_node(key, volume=volume, **dataclasses.asdict(verse))
    for reference in references:
        if reference.head.startswith('TG'):
            continue  # Skip TG references for now (no nodes).
        if reference.tail not in verses:
            raise KeyError(reference.tail)
        if reference.head not in verses:
            raise KeyError(reference.head)
        graph.add_edge(reference.tail, reference.head)
    if FLAGS.output.endswith('.gml'):
        nx.write_gml(graph, FLAGS.output)
    elif FLAGS.output.endswith('.graphml'):
        nx.write_graphml(graph, FLAGS.output)
    else:
        raise NotImplementedError(FLAGS.output)


if __name__ == '__main__':
    flags.mark_flags_as_required(['input_pattern', 'output'])
    app.run(main)
