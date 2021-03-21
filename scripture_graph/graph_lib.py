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
"""Utilities for parsing scriptures EPUB into verses and references."""

import collections
import dataclasses
import io
import json
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple
import zipfile

from absl import logging
from lxml import cssselect
from lxml import etree
import networkx as nx
import numpy as np
import pandas as pd

# pylint: disable=too-many-branches
# pylint: disable=too-many-locals

# Short names for books (used in references).
BOOKS_SHORT = {
    '1 Chronicles': '1 Chr.',
    '1 Corinthians': '1 Cor.',
    '1 John': '1 Jn.',
    '1 Kings': '1 Kgs.',
    '1 Peter': '1 Pet.',
    '1 Samuel': '1 Sam.',
    '1 Thessalonians': '1 Thes.',
    '1 Timothy': '1 Tim.',
    '2 Chronicles': '2 Chr.',
    '2 Corinthians': '2 Cor.',
    '2 John': '2 Jn.',
    '2 Kings': '2 Kgs.',
    '2 Peter': '2 Pet.',
    '2 Samuel': '2 Sam.',
    '2 Thessalonians': '2 Thes.',
    '2 Timothy': '2 Tim.',
    '3 John': '3 Jn.',
    'Acts': 'Acts',
    'Amos': 'Amos',
    'Colossians': 'Col.',
    'Daniel': 'Dan.',
    'Deuteronomy': 'Deut.',
    'Ecclesiastes': 'Eccl.',
    'Ephesians': 'Eph.',
    'Esther': 'Esth.',
    'Exodus': 'Ex.',
    'Ezekiel': 'Ezek.',
    'Ezra': 'Ezra',
    'Galatians': 'Gal.',
    'Genesis': 'Gen.',
    'Habakkuk': 'Hab.',
    'Haggai': 'Hag.',
    'Hebrews': 'Heb.',
    'Hosea': 'Hosea',
    'Isaiah': 'Isa.',
    'James': 'James',
    'Jeremiah': 'Jer.',
    'Job': 'Job',
    'Joel': 'Joel',
    'John': 'John',
    'Jonah': 'Jonah',
    'Joshua': 'Josh.',
    'Jude': 'Jude',
    'Judges': 'Judg.',
    'Lamentations': 'Lam.',
    'Leviticus': 'Lev.',
    'Luke': 'Luke',
    'Malachi': 'Mal.',
    'Mark': 'Mark',
    'Matthew': 'Matt.',
    'Micah': 'Micah',
    'Nahum': 'Nahum',
    'Nehemiah': 'Neh.',
    'Numbers': 'Num.',
    'Obadiah': 'Obad.',
    'Philemon': 'Philem.',
    'Philippians': 'Philip.',
    'Proverbs': 'Prov.',
    'Psalms': 'Ps.',
    'Revelation': 'Rev.',
    'Romans': 'Rom.',
    'Ruth': 'Ruth',
    'Song of Solomon': 'Song.',
    'Titus': 'Titus',
    'Zechariah': 'Zech.',
    'Zephaniah': 'Zeph.',
    '1 Nephi': '1 Ne.',
    '2 Nephi': '2 Ne.',
    '3 Nephi': '3 Ne.',
    '4 Nephi': '4 Ne.',
    'Alma': 'Alma',
    'Enos': 'Enos',
    'Ether': 'Ether',
    'Helaman': 'Hel.',
    'Jacob': 'Jacob',
    'Jarom': 'Jarom',
    'Mormon': 'Morm.',
    'Moroni': 'Moro.',
    'Mosiah': 'Mosiah',
    'Omni': 'Omni',
    'Words of Mormon': 'W of M',
    'Doctrine and Covenants': 'D&C',
    'Articles of Faith': 'A of F',
    'Abraham': 'Abr.',
    'Joseph Smith—Matthew': 'JS—M',
    'Joseph Smith—History': 'JS—H',
    'Moses': 'Moses',
}

# Volumes of scripture.
VOLUMES = {
    'Old Testament': [
        'Gen.', 'Ex.', 'Lev.', 'Num.', 'Deut.', 'Josh.', 'Judg.', 'Ruth',
        '1 Sam.', '2 Sam.', '1 Kgs.', '2 Kgs.', '1 Chr.', '2 Chr.', 'Ezra',
        'Neh.', 'Esth.', 'Job', 'Ps.', 'Prov.', 'Eccl.', 'Song.', 'Isa.',
        'Jer.', 'Lam.', 'Ezek.', 'Dan.', 'Hosea', 'Joel', 'Amos', 'Obad.',
        'Jonah', 'Micah', 'Nahum', 'Hab.', 'Zeph.', 'Hag.', 'Zech.', 'Mal.'
    ],
    'New Testament': [
        'Matt.', 'Mark', 'Luke', 'John', 'Acts', 'Rom.', '1 Cor.', '2 Cor.',
        'Gal.', 'Eph.', 'Philip.', 'Col.', '1 Thes.', '2 Thes.', '1 Tim.',
        '2 Tim.', 'Titus', 'Philem.', 'Heb.', 'James', '1 Pet.', '2 Pet.',
        '1 Jn.', '2 Jn.', '3 Jn.', 'Jude', 'Rev.'
    ],
    'Book of Mormon': [
        '1 Ne.', '2 Ne.', 'Jacob', 'Enos', 'Jarom', 'Omni', 'W of M', 'Mosiah',
        'Alma', 'Hel.', '3 Ne.', '4 Ne.', 'Morm.', 'Ether', 'Moro.'
    ],
    'Doctrine and Covenants': ['D&C'],  # Note that 'OD' is excluded.
    'Pearl of Great Price': ['Moses', 'Abr.', 'JS—M', 'JS—H', 'A of F'],
    'Study Helps': ['BD', 'HC', 'JST', 'TG', 'ITC'],
}
VOLUMES_SHORT = {
    'Old Testament': 'OT',
    'New Testament': 'NT',
    'Book of Mormon': 'BoM',
    'Doctrine and Covenants': 'D&C',
    'Pearl of Great Price': 'PoGP',
}


def get_volume(book: str) -> str:
    """Returns the containing volume for a book."""
    for volume, books in VOLUMES.items():
        if book in books:
            return volume
    raise ValueError(f'unrecognized book: {book}')


@dataclasses.dataclass(frozen=True)
class Verse:
    """A single verse of scripture."""
    book: str
    chapter: int
    verse: int


@dataclasses.dataclass(frozen=True)
class Reference:
    """A directed reference from one verse to another."""
    source: str
    target: str


@dataclasses.dataclass(frozen=True)
class Topic:
    """A topic that cites many scriptures."""
    source: str
    title: str


@dataclasses.dataclass
class ScriptureGraph:
    """A collection of verses, topics, and references.

    Attributes:
        verses: Dict of `Verse`s keyed by reference form (e.g. "1 Ne. 3:7").
        topics: Dict of `Topic`s keyed by reference form (e.g. "TG Aaron").
        references: List of `Reference`s.
    """
    verses: Dict[str, Verse] = dataclasses.field(default_factory=dict)
    topics: Dict[str, Topic] = dataclasses.field(default_factory=dict)
    references: List[Reference] = dataclasses.field(default_factory=list)

    def update(self, other):
        """Updates the current graph with `other`."""
        self.verses.update(other.verses)
        self.topics.update(other.topics)
        self.references.extend(other.references)

    def __repr__(self):
        return ('ScriptureGraph:\n'
                f'\t{len(self.verses)} verses\n'
                f'\t{len(self.topics)} topics\n'
                f'\t{len(self.references)} references')


def read_epub(filename: str) -> ScriptureGraph:
    """Reads an EPUB archive and parses topics, verses, and references.

    Args:
        filename: EPUB filename.

    Returns:
        ScriptureGraph.
    """
    graph = ScriptureGraph()
    skipped = ('abr_fac', 'bofm', 'cover', 'dc-testament', 'history-', 'od_',
               'pgp', 'triple-', 'triple_', 'bd', 'tg', 'bible-', 'bible_',
               'harmony.', 'jst', 'nt.', 'ot.', 'quad')
    with zipfile.ZipFile(filename) as archive:
        for info in archive.infolist():
            if not info.filename.endswith('.xhtml'):
                continue
            data = io.BytesIO(archive.read(info))
            tree = etree.parse(data, parser=etree.HTMLParser())
            basename = os.path.basename(info.filename)
            if basename.startswith('bd_'):
                continue
            if basename.startswith('tg_'):
                topic = get_title(tree)
                key = f'TG {topic}'
                graph.topics[key] = Topic(source='TG', title=topic)
                graph.references.extend(read_topic(tree, source=key))
                continue
            if basename.startswith('triple-index_'):
                topic = get_title(tree)
                key = f'ITC {topic}'
                graph.topics[key] = Topic(source='ITC', title=topic)
                graph.references.extend(read_topic(tree, source=key))
                continue
            if basename.startswith(skipped):
                continue
            book, chapter = read_headers(tree)
            if not chapter:
                continue
            graph.verses.update(read_verses(tree, book, chapter))
            if book == 'JS—H':
                continue  # JS—H has no references.
            graph.references.extend(read_references(tree, book, chapter))
    return graph


def get_title(tree) -> str:
    """Extracts the title from an ElementTree."""
    headers = cssselect.CSSSelector('title')(tree)
    if len(headers) != 1:
        raise ValueError(f'unexpected number of titles: {headers}')
    return headers[0].text


def read_headers(tree) -> Tuple[Optional[str], Optional[int]]:
    """Finds the book and chapter for the given document.

    Returns:
        book: Short name of the book (or None if not found).
        chapter: Chapter or section number (or None if not found).
    """
    title = get_title(tree)
    book = title.split('Chapter')[0].split('Section')[0].split(
        'Psalm ')[0].strip()
    book_short = BOOKS_SHORT[book]
    title_number = cssselect.CSSSelector('.titleNumber')(tree)
    if not title_number:
        return None, None  # Table of contents, etc.
    chapter = int(list(title_number[0].itertext())[0].split()[-1])
    return book_short, chapter


def read_verses(tree, book: str, chapter: int) -> Dict[str, Verse]:
    """Finds `Verse`s in the current document.

    Args:
        tree: ElementTree.
        book: Short name of the book.
        chapter: Chapter or section number.

    Returns:
        Dict of `Verse`s keyed by the reference form (e.g. "1 Ne. 3:7").
    """
    verses = {}
    for verse_element in cssselect.CSSSelector('.verse-first,.verse')(tree):
        verse = None
        for element in verse_element.iter():
            if element.get('class') == 'verseNumber':
                verse = int(list(element.itertext())[0])
            # Remove verse numbers and reference markers.
            if element.get('class') in ['verseNumber', 'marker']:
                element.clear()
        text = ''.join(verse_element.itertext())
        if not verse:
            if text.startswith(('After prayer',)):
                continue  # D&C 102:34.
            raise ValueError(
                f'could not find verse number for {book} {chapter}: {text}')
        key = f'{book} {chapter}:{verse}'
        verses[key] = Verse(book=book, chapter=chapter, verse=verse)
    return verses


def read_references(tree, book: str, chapter: int) -> List[Reference]:
    """Finds `Reference`s in the current document.

    Args:
        tree: ElementTree.
        book: Short name of the book.
        chapter: Chapter or section number.

    Returns:
        List of `Reference`s.
    """
    references = []
    # NOTE(kearnes): Verse numbers are not repeated for multiple references, so
    # we keep track of the current verse as we iterate.
    verse = None
    for reference_element in cssselect.CSSSelector('.listItem')(tree):
        targets = []
        for element in reference_element.iter():
            if element.get('class') == 'label-verse':
                verse = int(list(element.itertext())[0])
            # NOTE(kearnes): Most (but not all) references have the
            # "scriptureRef" class. This ambiguity means we have to resort to
            # regexes instead of simply walking through the tree.
            if element.tag == 'p' and 'class' not in element.attrib:
                targets.extend(parse_reference(''.join(element.itertext())))
        if not verse:
            raise ValueError(
                'could not find verse number for reference in '
                f'{book} {chapter}: {"".join(reference_element.itertext())}')
        source = f'{book} {chapter}:{verse}'
        for target in targets:
            if target == source:
                # Should never happen; if it does it's a bug.
                raise ValueError(f'self-reference: {source}')
            references.append(Reference(source=source, target=target))
    return references


def parse_reference(text: str) -> List[str]:
    """Parses a single reference.

    References have several forms:

      * Scripture: "Gen. 10:6 (6-8)", where the range is optional.
      * Study helps: "TG Adam".
      * Other: Hebrew/Greek translations, etc.

    Multiple references are separated by semicolons. This is a bit tricky
    since TG references are given as e.g. "TG Affliction; Blessing" and
    references in the same book are given as e.g. 1 Ne. 3:18; 5:4.

    Scripture and TG references are separated by periods. This is ambiguous
    since book names are often abbreviated.

    Note that verse ranges are excluded from the target when creating edges.

    Args:
        text: Reference text to be parsed.

    Returns:
        List of reference targets.
    """
    targets = []
    replacements = {
        r'D&C 13[\.;]': 'D&C 13:1',  # One-verse section.
        r'D&C 116[\.;]': 'D&C 116:1',  # One-verse section.
        u'\xa0': ' ',  # Non-breaking space.
        'Song ': 'Song. ',  # Inconsistent abbreviation.
        # Chapter references.
        'Lam. 1–5; ': '',
        'Heb. 11; ': '',
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
    matches = re.findall(
        r'((?:JST\s)?\d*\s?[a-zA-Z\s&—]+\.?)\s'
        r'((?:\d+:(?:\d+(?:\s\(\d+[-–,]\s?\d+\))?(?:,\s)?)+(?:;\s)?)+)', text)
    # NOTE(kearnes): This is a list of reference prefixes that don't fit the
    # standard syntax and that I have manually checked for exclusion.
    skipped = ('See ', 'see ', 'Note ', 'note ', 'IE ', 'a land', 'Recall',
               'in', 'The ', 'the ', 'also', 'and ', '7 and', 'Deuel',
               'Details', 'as ', '20 and', '19 and', 'which ')
    skipped += ('JST',)  # Skip JST references for now.
    for match in matches:
        for chapter_verse in match[1].split(';'):
            if not chapter_verse.strip():
                continue
            book = match[0].strip()
            if book not in BOOKS_SHORT.values():
                if not book.startswith(skipped):
                    raise ValueError(
                        f'unrecognized reference to book: "{book}" ({text})')
                continue
            chapter, verses = chapter_verse.split(':')
            submatches = re.findall(r'(\d+)(?:\s\(\d+[-–,]\s?\d+\))?,?', verses)
            for verse in submatches:
                verse = verse.split()[0]  # Remove verse ranges.
                targets.append(f'{book} {int(chapter)}:{int(verse)}')
    match = re.search(r'TG\s((?:(?:[a-zA-Z\s,-]+)(?:;\s)?)+)', text)
    if match:
        for topic in match.group(1).split(';'):
            targets.append(f'TG {topic.strip()}')
    # NOTE(kearnes): This is a list of reference prefixes that don't fit the
    # standard syntax and that I have manually checked for exclusion.
    allowed = ('BD', 'HEB', 'IE', 'See ', 'Comparison', 'The', 'Gnolaum', 'His',
               'OR', 'Bath-shua', 'GR', 'Aramaic', 'Septuagint', 'It', 'Greek',
               'In', 'What', 'This', 'More', 'Joab', 'Persian', 'According',
               'Some', 'Hebrew', 'Samaritan', 'Variant', 'A ', 'Probably',
               'All ', 'Progress', '“', 'Beginning', 'Isaiah chapters',
               'Arabian', 'Despite', 'Israel', 'Possibly', 'Here', 'Several',
               'Rabbinical', 'Other', 'Many', 'Syriac', 'Dogs', 'Wisdom',
               'Implying', 'Compare', 'An ', '4 Ne. heading', 'Mal. 3–4.',
               'D&C 74.', 'Matt. 24.', 'Apparently', 'Reference', 'Ezekiel',
               'Do not', 'Grandson', 'Bel and', 'Jesus', 'Perhaps', 'Joseph')
    allowed += skipped  # Skipped references often end up here again.
    allowed += ('JST',)  # Skip JST references for now.
    # Add introductions for all D&C sections.
    allowed += tuple(f'D&C {section}: Intro.' for section in range(1, 139))
    allowed += ('OD 1', 'OD 2')
    # Other manual fixes for ITC.
    allowed += ('3 Ne. 12–14; Matt. 5–7', 'D&C 2; 19; 22–23', 'D&C 22',
                'D&C 51; D&C 54: Intro.; D&C 56: Intro.', 'D&C 61', 'D&C 77',
                'D&C 89', 'D&C 100', 'D&C 108', 'D&C 111', 'D&C 116', 'D&C 121',
                'D&C 125', 'D&C 130–31', 'D&C 136', 'D&C 138',
                'Abr., fac. 2, fig. 2', 'Abr., fac. 3, fig. 6')
    if not targets and not text.startswith(allowed):
        raise ValueError(f'unrecognized reference syntax: "{text}"')
    return targets


def read_topic(tree, source) -> List[Reference]:
    """Parses a Topical Guide or Index section.

    The reference format here is slightly different than that used in the
    footnotes. For instance, multiple verses can be listed in a single entry
    (example from TG Abase): Matt. 23:12 (Luke 14:11; D&C 101:42; 112:3).

    The XHTML structure suggests that it might be easiest to remove the text
    snippets and pass the entire entry list to parse_reference.
    """
    references = []
    targets = []
    others = cssselect.CSSSelector('p.title')(tree)
    # NOTE(kearnes): Some topics have "see also" topics, others have "see also"
    # scriptures, and others have both or none. This is the best way I've come
    # up with for distinguishing between "see also" topics and scriptures.
    #
    # Most topics don't have numbers in them; the ones that do are usually of
    # the form "Mosiah2" (for the second "Mosiah" character).
    other_pattern = re.compile(r'\s\d')
    # Parse the "see also" topic list.
    prefix = source.split()[0]
    if others and not re.search(other_pattern, ''.join(others[0].itertext())):
        text = ''.join(others[0].itertext())
        text = re.sub(u'\xa0', ' ', text)
        match = re.fullmatch(r'See (?:also )?(.*?)\.?', text)
        if not match:
            raise ValueError(
                f'failed to parse topic references for {source}: "{text}"')
        for target in match.group(1).split(';'):
            target = target.strip()
            if target.startswith(('BD',)):
                break  # Any topics following this one are also in the BD.
            if target.startswith('Bible Chronology in the appendix'):
                continue
            if target.startswith('TG'):
                prefix = 'TG'
            if not target.startswith(prefix):
                target = f'{prefix} {target}'
            targets.append(target)
    # Parse the entries.
    entries = []
    skipped = ('revelation received at', 'revelations received at',
               'revelation designated as')
    for reference_element in cssselect.CSSSelector('.entry')(tree):
        if ''.join(reference_element.itertext()).startswith(skipped):
            continue
        for element in reference_element.iter():
            if element.get('class') == 'locator':
                text = ''.join(element.itertext()).strip()
                if text.endswith(';'):
                    text = text[:-1]
                entries.append(text)
    if entries:
        try:
            targets.extend(parse_reference('; '.join(entries)))
        except ValueError as error:
            raise ValueError(source) from error
    # Parse the "see also" scripture list.
    if others and re.search(other_pattern, ''.join(others[-1].itertext())):
        text = ''.join(others[-1].itertext())
        if text not in ['Summary', 'Compare also']:
            match = re.fullmatch(r'See (?:also )?(.*?)\.?', text)
            if not match:
                raise ValueError(
                    f'failed to parse extra references for {source}: "{text}"')
            targets.extend(parse_reference(match.group(1)))
    for target in targets:
        if target.startswith('BD'):
            raise ValueError(f'disallowed target for {source}: {target}')
        references.append(Reference(source=source, target=target))
    return references


def correct_topic_references(
        verses: Iterable[str], topics: Iterable[str],
        references: Iterable[Reference]) -> List[Reference]:
    """Corrects incomplete topic references.

    For instance, 1 Chr. 10:13 references 'TG Transgress'. However, the actual
    target is 'TG Transgress, Transgression'. Does not modify the original
    references.

    Args:
        verses: List of defined verses.
        topics: List of defined topics.
        references: List of current `Reference`s.

    Returns:
        List of updated `Reference`s.
    """
    nodes = set(verses).union(topics)
    updated_references = []
    count = 0
    for reference in references:
        if reference.source not in nodes:
            try:
                source = _translate_topic(reference.source, topics)
            except ValueError as error:
                raise ValueError(reference) from error
            count += 1
        else:
            source = reference.source
        if reference.target not in nodes:
            try:
                target = _translate_topic(reference.target, topics)
            except ValueError as error:
                raise ValueError(reference) from error
            count += 1
        else:
            target = reference.target
        updated_references.append(Reference(source=source, target=target))
    logging.info(f'made {count} topic translations')
    return updated_references


def _translate_topic(topic: str, topics: Iterable[str]) -> str:
    """Translates an incomplete topic reference."""
    manual = {
        'TG Bear [verb]': 'TG Bear, Bare, Born, Borne [verb]',
        'TG Light [adjective]': 'TG Light, Lighter [adjective]',
        'TG Close': 'TG Close [verb]',
        'ITC Work [noun]': 'ITC Work, Works [noun]',
        'ITC Meet [verb]': 'ITC Meet, Met, Meeting',
        'ITC Bear [verb]': 'ITC Bear, Bore, Borne',
        'ITC Spirit, Holy': 'ITC Spirit, Holy/Spirit of the Lord',
        'ITC Shiblom1': 'ITC Shiblom1 [or Shiblon]',
    }
    if topic in manual:
        return manual[topic]
    short_topic = ' '.join(topic.split()[1:])  # Remove the book name.
    for title in topics:
        short_title = ' '.join(title.split()[1:])
        if short_topic in short_title.split(', '):
            return title
    raise ValueError(f'no suitable translation for {topic}')


def remove_topic_nodes(graph: nx.Graph):
    """Drops topic nodes from the graph."""
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


def remove_suggested_edges(graph: nx.Graph):
    """Drops non-canonical edges from the graph."""
    logging.info('Dropping non-canonical edges')
    logging.info('Original graph has %d nodes and %d edges',
                 graph.number_of_nodes(), graph.number_of_edges())
    drop = set()
    for edge in graph.edges:
        if graph.edges[edge].get('kind'):
            drop.add(edge)
    for edge in drop:
        graph.remove_edge(*edge)
    logging.info('Updated graph has %d nodes and %d edges',
                 graph.number_of_nodes(), graph.number_of_edges())


def write_tree(graph: nx.Graph, filename: str):
    """Writes a JSON navigation tree."""
    graph = graph.copy()
    remove_topic_nodes(graph)
    source = []
    book_names = {value: key for key, value in BOOKS_SHORT.items()}
    for volume, books in VOLUMES.items():
        if volume not in VOLUMES_SHORT:
            continue
        volume_children = []
        for book_short in books:
            book = book_names[book_short]
            verses = get_verses(graph, book_short)
            book_children = []
            for chapter_number in sorted(verses):
                chapter = f'{book_short} {chapter_number}'
                chapter_children = []
                for verse_number in sorted(verses[chapter_number]):
                    verse = f'{book_short} {chapter_number}:{verse_number}'
                    chapter_children.append({
                        'title': verse,
                        'key': verse,
                    })
                book_children.append({
                    'title': chapter,
                    'key': chapter,
                    'folder': True,
                    'children': chapter_children
                })
            if len(book_children) == 1:
                book_children = book_children[0]['children']
            volume_children.append({
                'title': book,
                'key': book,
                'folder': True,
                'children': book_children
            })
        if len(volume_children) == 1:
            volume_children = volume_children[0]['children']
        source.append({
            'title': volume,
            'key': volume,
            'folder': True,
            'children': volume_children
        })
    with open(filename, 'w') as f:
        json.dump(source, f, indent=2)


def get_verses(graph: nx.Graph, book: str) -> Dict[int, List[str]]:
    """Returns a dict mapping chapter numbers to verse counts for a book."""
    verses = collections.defaultdict(list)
    for node in graph.nodes:
        data = graph.nodes[node]
        if data['book'] == book:
            verses[data['chapter']].append(data['verse'])
    return verses


def jaccard(graph: nx.Graph) -> np.ndarray:
    """Builds a pairwise Jaccard similarity matrix based on node neighbors.

    Note that self-similarity values are removed from the returned array.

    Args:
        graph: Graph to use for similarity calculations.

    Returns:
        N x N similarity matrix.
    """
    adjacency_matrix = nx.adjacency_matrix(graph)
    ab = adjacency_matrix @ adjacency_matrix.T
    assert ab.shape == (graph.number_of_nodes(), graph.number_of_nodes())
    aa = adjacency_matrix.sum(axis=1)
    assert aa.shape == (graph.number_of_nodes(), 1)
    bb = aa.T
    assert bb.shape == (1, graph.number_of_nodes())
    similarity = ab / (aa + bb - ab)
    np.nan_to_num(similarity, copy=False)
    similarity[np.diag_indices_from(similarity)] = 0.0
    return similarity


def add_suggested_edges(digraph: nx.DiGraph) -> pd.DataFrame:
    """Adds suggested edges to the graph.

    Keeps all nonzero similarity pairs with at least two shared neighbors. Note
    that the added edges are based on similarities in an undirected graph, and
    that suggested edges are added bidirectionally.

    Args:
        digraph: The original cross-reference graph.

    Returns:
        DataFrame containing unique pairs that were added to the graph.
    """
    graph = digraph.to_undirected()
    remove_topic_nodes(graph)
    similarity = jaccard(graph)
    nonzero = get_nonzero_edges(graph, similarity)
    mask = (~nonzero.exists) & (nonzero.intersection > 1)
    suggested = nonzero[mask]
    logging.info('Adding %d suggested edges', suggested.shape[0])
    for row in suggested.itertuples():
        digraph.add_edge(row.a, row.b, kind='jaccard')
        digraph.add_edge(row.b, row.a, kind='jaccard')
    return suggested


def get_nonzero_edges(graph: nx.Graph, similarity: np.ndarray) -> pd.DataFrame:
    """Builds a list of nonzero edges."""
    nodes = np.asarray(graph.nodes())
    mask = np.where(similarity > 0)
    rows = []
    for i, j in zip(*mask):
        order = sorted([nodes[i], nodes[j]])
        a = set(n[1] for n in graph.edges(order[0]))
        b = set(n[1] for n in graph.edges(order[1]))
        rows.append({
            'a': order[0],
            'b': order[1],
            'jaccard': similarity[i, j],
            'intersection': len(a & b),
            'union': len(a | b),
        })
    df = pd.DataFrame(rows)
    logging.info('All nonzero pairs: %s', df.shape)
    df = df.drop_duplicates(['a', 'b']).reset_index()
    logging.info('Unique nonzero pairs: %s', df.shape)
    # Annotate connections that already exist.
    keep = []
    for row in df.itertuples():
        try:
            _ = graph.edges[(row.a, row.b)]
            keep.append(False)
        except KeyError:
            keep.append(True)
    keep = np.asarray(keep, dtype=bool)
    df.loc[keep, 'exists'] = False
    df.loc[~keep, 'exists'] = True
    df['exists'] = df.exists.values.astype(bool)
    return df
