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

import gzip
import json
import logging
from typing import Dict, List
from urllib import parse

import flask
import networkx as nx
from scripture_graph import graph_lib

app = flask.Flask(__name__)
logging.basicConfig(level=logging.INFO)

Elements = Dict[str, List[Dict[str, Dict[str, str]]]]

URL_BASE = 'https://www.churchofjesuschrist.org/study/scriptures/'


def load_graph() -> nx.DiGraph:
    """Loads the static cross-reference graph."""
    graph = nx.read_graphml('data/scripture_graph.graphml')
    graph_lib.drop_topic_nodes(graph)
    return graph


GRAPH = load_graph()


@app.route('/elements', methods=['POST'])
def get_elements() -> str:
    """Fetches the neighborhood around a verse."""
    verse = flask.request.get_data(as_text=True)
    elements = _get_elements(verse)
    num_nodes = len(elements['nodes'])
    num_edges = len(elements['edges'])
    app.logger.info(
        f'Fetched {num_nodes} nodes and {num_edges} edges for {verse}')
    return flask.jsonify(elements)


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


@app.route('/', methods=['GET'])
def root() -> str:
    """Shows the main graph exploration page."""
    verse = flask.request.args.get('verse', type=str, default='John 3:16')
    app.logger.info(f'Received request for {verse}')
    return flask.render_template('index.html', verse=verse)


@app.route('/tree')
def get_tree() -> str:
    """Fetches the navigation tree for the sidebar."""
    with gzip.open('data/tree.json.gz') as f:
        return flask.jsonify(json.load(f))


@app.route('/table', methods=['POST'])
def get_table() -> str:
    """Builds a cross-reference table for the given verse."""
    verse = flask.request.get_data(as_text=True)
    args = {
        'verse': verse,
        'verse_url': get_verse_url(verse),
        'incoming': [],
        'outgoing': [],
    }
    for source, target in GRAPH.in_edges(verse):
        assert target == verse
        args['incoming'].append((source, get_verse_url(source)))
    for source, target in GRAPH.out_edges(verse):
        assert source == verse
        args['outgoing'].append((target, get_verse_url(target)))
    return flask.jsonify(flask.render_template('table.html', **args))


def get_verse_url(verse: str) -> str:
    """Creates a URL for the verse text."""
    node = GRAPH.nodes[verse]
    volume = graph_lib.VOLUMES_SHORT[node['volume']].lower()
    if volume == 'bom':
        volume = 'bofm'
    elif volume == 'd&c':
        volume = 'dc-testament'
    elif volume == 'pogp':
        volume = 'pgp'
    book = node['book'].lower()
    book_replacements = {
        ' ': '-',
        '.': '',
        '&': '',
        '—': '-',
    }
    for old, new in book_replacements.items():
        book = book.replace(old, new)
    if book == 'd&c':
        book = 'dc'
    chapter = node['chapter']
    i = node['verse']
    return parse.urljoin(URL_BASE,
                         f'{volume}/{book}/{chapter}.{i}?lang=eng#p{i}#{i}')


if __name__ == '__main__':
    # https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service.
    app.run(host='127.0.0.1', port=8080, debug=True)
