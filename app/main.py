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
"""Flask application for serving the cross-reference graph."""
import enum
import itertools
import json
import logging
from typing import Union
from urllib import parse

import flask

import scripture_graph

app = flask.Flask(__name__)
logging.basicConfig(level=logging.INFO)

Elements = dict[str, list[dict[str, dict[str, str]]]]

URL_BASE = "https://www.churchofjesuschrist.org/study/scriptures/"

BOOK_ORDER = dict(
    zip(
        itertools.chain(
            scripture_graph.VOLUMES["Old Testament"],
            scripture_graph.VOLUMES["New Testament"],
            scripture_graph.VOLUMES["Book of Mormon"],
            scripture_graph.VOLUMES["Doctrine and Covenants"],
            scripture_graph.VOLUMES["Pearl of Great Price"],
        ),
        range(len(scripture_graph.BOOKS_SHORT)),
    )
)


class FilterMode(enum.Enum):
    """Edge filter mode."""

    ALL = enum.auto()
    INCOMING = enum.auto()
    OUTGOING = enum.auto()


def load_connections() -> dict[str, dict[str, Union[int, str, list[str]]]]:
    """Loads the static set of connections."""
    with open("data/connections.json") as f:
        return json.load(f)


CONNECTIONS = load_connections()


def get_edges(verse: str) -> tuple[set[str], set[str], set[str]]:
    """Fetches the incoming and outgoing edges for a verse."""
    data = CONNECTIONS[verse]
    incoming = data.get("incoming", [])
    outgoing = data.get("outgoing", [])
    suggested = data.get("suggested", [])
    return set(incoming), set(outgoing), set(suggested)


@app.route("/elements", methods=["POST"])
def get_elements() -> str:
    """Fetches the neighborhood around a verse."""
    data = flask.request.get_json()
    data["filter_mode"] = FilterMode[data["filter_mode"].upper()]
    elements = _get_elements(**data)
    num_nodes = len(elements["nodes"])
    num_edges = len(elements["edges"])
    app.logger.info(f"Fetched {num_nodes} nodes and {num_edges} edges for {data}")
    return flask.jsonify(elements)


def _get_elements(verse: str, filter_mode: FilterMode, include_suggested: bool) -> Elements:
    """Renders the neighborhood around a verse."""
    unique_nodes = {verse}
    incoming, outgoing, suggested = get_edges(verse)
    # NOTE(skearnes): We drop suggested nodes if they are not requested. Filtered-out nodes
    # are still drawn but are deemphasized for visual clarity.
    if not include_suggested:
        suggested.clear()
    unique_nodes.update(incoming | outgoing | suggested)
    nodes = []
    for node in unique_nodes:
        if (
            node == verse
            or (filter_mode == FilterMode.ALL and (node in incoming or node in outgoing))
            or (filter_mode == FilterMode.INCOMING and node in incoming)
            or (filter_mode == FilterMode.OUTGOING and node in outgoing)
            or (include_suggested and node in suggested)
        ):
            keep = True
        else:
            keep = False
        nodes.append({"data": {"id": node, "keep": keep}})
    in_only = incoming - outgoing
    out_only = outgoing - incoming
    both = incoming & outgoing
    edges = []
    for source in in_only:
        edges.append(
            {
                "data": {
                    "id": f"{verse} <- {source}",
                    "source": source,
                    "target": verse,
                    "kind": "incoming",
                    "keep": filter_mode in {FilterMode.ALL, FilterMode.INCOMING},
                }
            }
        )
    for target in out_only:
        edges.append(
            {
                "data": {
                    "id": f"{verse} -> {target}",
                    "source": verse,
                    "target": target,
                    "kind": "outgoing",
                    "keep": filter_mode in {FilterMode.ALL, FilterMode.OUTGOING},
                }
            }
        )
    for other in both:
        edges.append(
            {
                "data": {
                    "id": f"{verse} <-> {other}",
                    "source": verse,
                    "target": other,
                    "kind": "both",
                    "keep": True,
                }
            }
        )
    for node in suggested:
        edges.append(
            {
                "data": {
                    "id": f"{verse} <?> {node}",
                    "source": verse,
                    "target": node,
                    "kind": "suggested",
                    "keep": include_suggested,
                }
            }
        )
    # Use attribute presence for matching in CSS.
    for node in nodes:
        if not node["data"]["keep"]:
            node["data"]["hide"] = True
    for edge in edges:
        if not edge["data"]["keep"]:
            edge["data"]["hide"] = True
    return {"nodes": nodes, "edges": edges}


@app.route("/", methods=["GET"])
def root() -> str:
    """Shows the main graph exploration page."""
    return flask.render_template("index.html")


@app.route("/tree")
def get_tree() -> str:
    """Fetches the navigation tree for the sidebar."""
    with open("data/tree.json") as f:
        return flask.jsonify(json.load(f))


@app.route("/table", methods=["POST"])
def get_table() -> str:
    """Builds a cross-reference table for the given verse."""
    verse = flask.request.get_data(as_text=True)
    args = {
        "verse": verse.replace(" ", "\xa0"),  # Non-breaking space.
        "verse_url": get_verse_url(verse),
    }
    incoming, outgoing, suggested = get_edges(verse)
    args["incoming"] = [(source, get_verse_url(source)) for source in sort_verses(incoming)]
    args["outgoing"] = [(target, get_verse_url(target)) for target in sort_verses(outgoing)]
    args["suggested"] = [(node, get_verse_url(node)) for node in sort_verses(suggested)]
    return flask.jsonify(flask.render_template("table.html", **args))


@app.route("/_ah/warmup")
def warmup() -> None:
    """Handle warmup requests from App Engine."""
    return flask.make_response("", 200)


def get_verse_url(verse: str) -> str:
    """Creates a URL for the verse text."""
    node = CONNECTIONS[verse]
    volume = scripture_graph.VOLUMES_SHORT[node["volume"]].lower()
    if volume == "bom":
        volume = "bofm"
    elif volume == "d&c":
        volume = "dc-testament"
    elif volume == "pogp":
        volume = "pgp"
    book = node["book"].lower()
    book_replacements = {
        " ": "-",
        ".": "",
        "&": "",
        "—": "-",
    }
    for old, new in book_replacements.items():
        book = book.replace(old, new)
    if book == "d&c":
        book = "dc"
    chapter = node["chapter"]
    i = node["verse"]
    return parse.urljoin(URL_BASE, f"{volume}/{book}/{chapter}.{i}?lang=eng#p{i}#{i}")


def sort_verses(verses: list[str]) -> list[str]:
    """Sorts verses in Standard Works order."""
    return sorted(verses, key=_sort_verses)


def _sort_verses(verse: str) -> tuple[int, int, int]:
    """Key function for sort_verses."""
    node = CONNECTIONS[verse]
    return BOOK_ORDER[node["book"]], node["chapter"], node["verse"]


if __name__ == "__main__":
    # https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service.
    app.run(host="127.0.0.1", port=8080, debug=True)
