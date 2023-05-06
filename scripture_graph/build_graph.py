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
"""Builds a scripture graph.

Usage:
    build_graph.py --input_pattern=<str> --output=<str> [--tree=<str> --topics --suggested --threshold=<float>]

Options:
    --input_pattern=<str>       Input EPUB pattern.
    --output=<str>              Output graph filename (usually *.graphml).
    --tree=<str>                Output tree filename.
    --topics                    Include topic nodes.
    --suggested                 Include suggested edges.
    --threshold=<float>         Similarity threshold [default: 0.77].
"""
import dataclasses
import logging
import glob
import json

import docopt
import networkx as nx

from scripture_graph import graph_lib

logger = logging.getLogger(__name__)


def write_graph(graph: nx.Graph, filename: str) -> None:
    """Writes a graph to disk."""
    if filename.endswith(".gml"):
        nx.write_gml(graph, filename)
    elif filename.endswith(".graphml"):
        nx.write_graphml(graph, filename)
    elif filename.endswith(".json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(nx.node_link_data(graph), f)
    else:
        raise NotImplementedError(filename)


def main(**kwargs) -> None:
    scripture_graph = graph_lib.ScriptureGraph()
    for filename in glob.glob(kwargs["--input_pattern"]):
        logger.info(filename)
        this_graph = graph_lib.read_epub(filename)
        scripture_graph.update(this_graph)
        logger.info(this_graph)
    logger.info(scripture_graph)
    graph = nx.DiGraph()
    for key, verse in scripture_graph.verses.items():
        volume = graph_lib.get_volume(verse.book)
        graph.add_node(key, kind="verse", volume=volume, **dataclasses.asdict(verse))
    if kwargs["--topics"]:
        for key, topic in scripture_graph.topics.items():
            volume = graph_lib.get_volume(topic.source)
            graph.add_node(key, kind="topic", volume=volume, **dataclasses.asdict(topic))
    references = graph_lib.correct_topic_references(
        verses=list(scripture_graph.verses.keys()),
        topics=list(scripture_graph.topics.keys()),
        references=scripture_graph.references,
    )
    duplicated_edges = 0
    for reference in references:
        if reference.source not in graph.nodes:
            raise KeyError(f"missing source for {reference}")
        if reference.target not in graph.nodes:
            raise KeyError(f"missing target for {reference}")
        if (reference.source, reference.target) in graph.edges:
            duplicated_edges += 1
        else:
            graph.add_edge(reference.source, reference.target)
    if duplicated_edges:
        logger.info(f"ignored {duplicated_edges} duplicated edges")
    logger.info(nx.info(graph))  # pylint: disable=no-member
    if kwargs["--suggested"]:
        graph_lib.add_jaccard_edges(graph)
        graph_lib.add_use_edges(graph, float(kwargs["--threshold"]))
        logger.info(nx.info(graph))  # pylint: disable=no-member
    write_graph(graph, kwargs["--output"])
    if kwargs["--tree"]:
        graph_lib.write_tree(graph, kwargs["--tree"])


if __name__ == "__main__":
    main(**docopt.docopt(__doc__))
