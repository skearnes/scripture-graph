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

"""Flask application for serving the cross-reference graph."""

from typing import Dict, List

from absl import logging
import flask
import networkx as nx

app = flask.Flask(__name__)

Elements = Dict[str, List[Dict[str, Dict[str, str]]]]


def load_graph() -> nx.Graph:
    """Loads the static cross-reference graph."""
    graph = nx.read_graphml('data/scripture_graph.graphml')
    # Drop topic nodes/references.
    logging.info('Dropping topic nodes')
    logging.info('Original graph has %d nodes and %d edges',
                 graph.number_of_nodes(), graph.number_of_edges())
    drop = set()
    for node in graph.nodes:
        if graph.nodes[node]['kind'] == 'topic':
            drop.add(node)
    for node in drop:
        graph.remove_node(node)
    logging.info('Updated graph has %d nodes and %d edges',
                 graph.number_of_nodes(), graph.number_of_edges())
    return graph


GRAPH = load_graph()


@app.route('/elements', methods=['POST'])
def get_elements() -> str:
    """Fetches the neighborhood around a verse."""
    verse = flask.request.get_data(as_text=True)
    return flask.jsonify(_get_elements(verse))


def _get_elements(verse: str) -> Elements:
    """Fetches the neighborhood around a verse."""
    unique_nodes = {verse}
    edges = []
    for source, target in GRAPH.in_edges(verse):
        assert target == verse
        unique_nodes.add(source)
        edges.append({
            'data': {
                'id': f'{source} -> {target}',
                'source': source,
                'target': target
            }
        })
    for source, target in GRAPH.out_edges(verse):
        assert source == verse
        unique_nodes.add(target)
        edges.append({
            'data': {
                'id': f'{source} -> {target}',
                'source': source,
                'target': target
            }
        })
    nodes = []
    for node in unique_nodes:
        nodes.append({'data': {'id': node}})
    return {'nodes': nodes, 'edges': edges}


@app.route('/')
@app.route('/<verse>')
def root(verse: str = 'John 3:16'):
    return flask.render_template('index.html', verse=verse)


if __name__ == '__main__':
    # https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service.
    app.run(host='127.0.0.1', port=8080, debug=True)
