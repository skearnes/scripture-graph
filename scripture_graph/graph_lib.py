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

import dataclasses
import io
import os
import re
from typing import Dict, List, Optional, Tuple
import zipfile

from lxml import cssselect
from lxml import etree

# Short names for books (used in references).
_BOOKS_SHORT = {
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
    'Study Helps': ['BD', 'HC', 'JST', 'TG'],
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
    head: str
    tail: str


def read_epub(filename: str) -> Tuple[Dict[str, Verse], List[Reference]]:
    """Reads an EPUB archive and parses verses and references.

    Args:
        filename: EPUB filename.

    Returns:
        verses: Dict of `Verse`s keyed by the reference form (e.g. "1 Ne. 3:7").
        references: List of `Reference`s.
    """
    verses = {}
    references = []
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
                continue
            if basename.startswith('triple-index_'):
                continue
            if basename.startswith(
                ('abr_fac', 'bofm', 'cover', 'dc-testament', 'history-', 'od_',
                 'pgp', 'triple-', 'triple_', 'bd', 'tg', 'bible-', 'bible_',
                 'harmony.', 'jst', 'nt.', 'ot.', 'quad')):
                continue
            book, chapter = read_headers(tree)
            if not chapter:
                continue
            this_verses = read_verses(tree, book, chapter)
            verses.update(this_verses)
            if book == 'JS—H':
                continue  # JS—H has no references.
            references.extend(read_references(tree, book, chapter))
    return verses, references


def read_headers(tree) -> Tuple[Optional[str], Optional[int]]:
    """Finds the book and chapter for the given document.

    Returns:
        book: Short name of the book (or None if not found).
        chapter: Chapter or section number (or None if not found).
    """
    headers = cssselect.CSSSelector('title')(tree)
    book = headers[0].text.split('Chapter')[0].split('Section')[0].split(
        'Psalm ')[0].strip()
    book_short = _BOOKS_SHORT[book]
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
            if text.startswith(('After prayer', )):
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
        tails = []
        for element in reference_element.iter():
            if element.get('class') == 'label-verse':
                verse = int(list(element.itertext())[0])
            # NOTE(kearnes): Most (but not all) references have the
            # "scriptureRef" class. This ambiguity means we have to resort to
            # regexes instead of simply walking through the tree.
            if element.tag == 'p' and 'class' not in element.attrib:
                tails.extend(parse_reference(''.join(element.itertext())))
        if not verse:
            raise ValueError(
                'could not find verse number for reference in '
                f'{book} {chapter}: {"".join(reference_element.itertext())}')
        head = f'{book} {chapter}:{verse}'
        for tail in tails:
            references.append(Reference(head=head, tail=tail))
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

    Note that verse ranges are excluded from the tail when creating edges.
    """
    tails = []
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
        r'(\d*\s?[a-zA-Z\s&—]+\.?)\s'
        r'((?:\d+:\d+(?:\s\(\d+[-–,]\s?\d+\))?(?:;\s)?)+)', text)
    # NOTE(kearnes): This is a list of reference prefixes that don't fit the
    # standard syntax and that I have manually checked for exclusion.
    skipped = ('See ', 'see ', 'Note ', 'note ', 'IE ', 'a land', 'Recall',
               'in', 'The ', 'the ', 'also', 'and ', '7 and', 'Deuel',
               'Details', 'as ', '20 and', '19 and', 'which ')
    skipped += ('JST', )  # Skip JST references for now.
    for match in matches:
        for chapter_verse in match[1].split(';'):
            if not chapter_verse.strip():
                continue
            book = match[0].strip()
            if book not in _BOOKS_SHORT.values():
                if not book.startswith(skipped):
                    raise ValueError(
                        f'unrecognized reference to book: "{book}" ({text})')
                continue
            tails.append(f'{book} {chapter_verse.split()[0]}')
    match = re.search(r'TG\s((?:(?:[a-zA-Z\s]+,?[a-zA-Z\s]*)(?:;\s)?)+)', text)
    if match:
        for topic in match.group(1).split(';'):
            tails.append(f'TG {topic.strip()}')
    # NOTE(kearnes): This is a list of reference prefixes that don't fit the
    # standard syntax and that I have manually checked for exclusion.
    allowed = ('BD', 'HEB', 'IE', 'See ', 'Comparison', 'The', 'Gnolaum',
               'His', 'OR', 'Bath-shua', 'GR', 'Aramaic', 'Septuagint', 'It',
               'Greek', 'In', 'What', 'This', 'More', 'Joab', 'Persian',
               'According', 'Some', 'Hebrew', 'Samaritan', 'Variant', 'A ',
               'Probably', 'All ', 'Progress', '“', 'Beginning',
               'Isaiah chapters', 'Arabian', 'Despite', 'Israel', 'Possibly',
               'Here', 'Several', 'Rabbinical', 'Other', 'Many', 'Syriac',
               'Dogs', 'Wisdom', 'Implying', 'Compare', 'An ', '4 Ne. heading',
               'Mal. 3–4.', 'D&C 74.', 'Matt. 24.', 'Apparently', 'Reference',
               'Ezekiel', 'Do not', 'Grandson', 'Bel and', 'Jesus', 'Perhaps',
               'Joseph')
    allowed += skipped  # Skipped references often end up here again.
    allowed += ('JST', )  # Skip JST references for now.
    if not tails and not text.startswith(allowed):
        raise ValueError(f'unrecognized reference syntax: "{text}"')
    return tails
