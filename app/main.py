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

import itertools
import json
import logging
from typing import Dict, Iterable, List, Tuple
from urllib import parse

import flask
import networkx as nx
from scripture_graph import graph_lib

app = flask.Flask(__name__)
logging.basicConfig(level=logging.INFO)

Elements = Dict[str, List[Dict[str, Dict[str, str]]]]

URL_BASE = 'https://www.churchofjesuschrist.org/study/scriptures/'

BOOK_ORDER = dict(
    zip(
        itertools.chain(graph_lib.VOLUMES['Old Testament'],
                        graph_lib.VOLUMES['New Testament'],
                        graph_lib.VOLUMES['Book of Mormon'],
                        graph_lib.VOLUMES['Doctrine and Covenants'],
                        graph_lib.VOLUMES['Pearl of Great Price']),
        range(len(graph_lib.BOOKS_SHORT))))


def load_graph() -> nx.DiGraph:
    """Loads the static cross-reference graph."""
    graph = nx.read_graphml('data/scripture_graph.graphml')
    graph_lib.remove_topic_nodes(graph)
    return graph


GRAPH = load_graph()


def get_edges(verse: str) -> Tuple[List[str], List[str]]:
    """Fetches the incoming and outgoing edges for a verse."""
    incoming = []
    for source, target in GRAPH.in_edges(verse):
        assert target == verse
        incoming.append(source)
    outgoing = []
    for source, target in GRAPH.out_edges(verse):
        assert source == verse
        outgoing.append(target)
    return incoming, outgoing


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
    incoming, outgoing = get_edges(verse)
    unique_nodes.update(incoming)
    unique_nodes.update(outgoing)
    nodes = []
    for node in unique_nodes:
        nodes.append({'data': {'id': node}})
    edges = []
    for node in incoming:
        edges.append({
            'data': {
                'id': f'{node} -> {verse}',
                'source': node,
                'target': verse,
            }
        })
    for node in outgoing:
        edges.append({
            'data': {
                'id': f'{verse} -> {node}',
                'source': verse,
                'target': node,
            }
        })
    return {'nodes': nodes, 'edges': edges}


@app.route('/', methods=['GET'])
def root() -> str:
    """Shows the main graph exploration page."""
    return flask.render_template('index.html')


@app.route('/tree')
def get_tree() -> str:
    """Fetches the navigation tree for the sidebar."""
    with open('data/tree.json') as f:
        return flask.jsonify(json.load(f))


@app.route('/table', methods=['POST'])
def get_table() -> str:
    """Builds a cross-reference table for the given verse."""
    verse = flask.request.get_data(as_text=True)
    args = {
        'verse': verse.replace(' ', '\xa0'),  # Non-breaking space.
        'verse_url': get_verse_url(verse),
        'incoming': [],
        'outgoing': [],
    }
    incoming, outgoing = get_edges(verse)
    args['incoming'] = [(source, get_verse_url(source))
                        for source in sort_verses(incoming)]
    args['outgoing'] = [(target, get_verse_url(target))
                        for target in sort_verses(outgoing)]
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


def sort_verses(verses: Iterable[str]) -> List[str]:
    """Sorts verses in Standard Works order."""
    return sorted(verses, key=_sort_verses)


def _sort_verses(verse: str) -> Tuple[int, int, int]:
    """Key function for sort_verses."""
    node = GRAPH.nodes[verse]
    return BOOK_ORDER[node['book']], node['chapter'], node['verse']


if __name__ == '__main__':
    # https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service.
    app.run(host='127.0.0.1', port=8080, debug=True)
