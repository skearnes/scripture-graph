"""Utilities for parsing scriptures EPUB into verses and references."""

import dataclasses
import io
import os
import re
from typing import Dict, List, Tuple
import zipfile

from absl import logging
from lxml import cssselect
from lxml import etree

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
    'Song of Solomon': 'Song',
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
    'Moses': 'Moses',
}


@dataclasses.dataclass(frozen=True)
class Verse:
    book: str
    chapter: int
    verse: int
    text: str


@dataclasses.dataclass(frozen=True)
class Reference:
    head: str
    tail: str


def read_epub(filename: str) -> Tuple[Dict[str, Verse], List[Reference]]:
    verses = {}
    references = []
    with zipfile.ZipFile(filename) as archive:
        for info in archive.infolist():
            if not info.filename.endswith('.xhtml'):
                continue
            logging.info(info.filename)
            data = io.BytesIO(archive.read(info))
            tree = etree.parse(data, parser=etree.HTMLParser())
            basename = os.path.basename(info.filename)
            if basename.startswith('bd_'):
                continue
            elif basename.startswith('tg_'):
                continue
            elif basename.startswith('triple-index_'):
                continue
            else:
                this_verses, this_references = read_tree(tree)
            logging.info(f'Found {len(this_verses)} verses and '
                         f'{len(this_references)} references')
            verses.update(this_verses)
            references.extend(this_references)
    logging.info(f'Found {len(verses)} verses and {len(references)} references')
    return verses, references


def read_tree(tree) -> Tuple[Dict[str, Verse], List[Reference]]:
    verses = {}
    references = []
    headers = cssselect.CSSSelector('.runHead')(tree)
    if not headers:
        return verses, references  # Table of contents, etc.
    book = list(headers[0].itertext())[0]
    book_short = BOOKS_SHORT[book]
    chapter = int(
        list(cssselect.CSSSelector('.titleNumber')(tree)[0].itertext())
        [0].split()[1])
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
            raise ValueError(
                'could not find verse number for {book_short} {chapter}: {text}'
            )
        key = f'{book_short} {chapter}:{verse}'
        verses[key] = Verse(book=book_short,
                            chapter=chapter,
                            verse=verse,
                            text=text)
    for reference_element in cssselect.CSSSelector('.listItem')(tree):
        verse = None
        tails = []
        for element in reference_element.iter():
            if element.get('class') == 'label-verse':
                verse = int(list(element.itertext())[0])
            # NOTE(kearnes): Most (but not all) references have the
            # "scriptureRef" class. This ambiguity means we have to resort to
            # regexes instead of simply walking through the tree.
            if element.tag == 'p' and 'class' not in element.attrib:
                tails.extend(parse_reference(''.join(element.itertext())))
        head = f'{book_short} {chapter}:{verse}'
        for tail in tails:
            references.append(Reference(head=head, tail=tail))
    return verses, references


def parse_reference(text: str) -> List[str]:
    tails = []
    # References have several forms:
    #
    #   * Scripture: "Gen. 10:6 (6-8)", where the range is optional.
    #   * Study helps: "TG Adam".
    #   * Other: Hebrew/Greek translations, etc.
    #
    # Multiple references are separated by semicolons. This is a bit tricky
    # since TG references are given as e.g. "TG Affliction; Blessing" and
    # references in the same book are given as e.g. 1 Ne. 3:18; 5:4.
    #
    # Scripture and TG references are separated by periods. This is ambiguous
    # since book names are often abbreviated.
    #
    # I think pattern matching on the full string is the only way to go.
    #
    # NOTE(kearnes): Verse ranges are excluded from the tail when creating
    # edges in the graph.
    replacements = {
        'D&C 13.': 'D&C 13:1.',
        'D&C 74.': 'D&C 74:1 (1-7).'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    matches = re.findall(
        r'(\d*\s?[\w\s&]+\.?)\s'
        r'((?:\d+:\d+(?:\s\(\d+[-–,]\s?\d+\))?(?:;\s)?)+)', text)
    for match in matches:
        for chapter_verse in match[1].split(';'):
            if not chapter_verse.strip():
                continue
            tails.append(f'{match[0]} {chapter_verse.split()[0]}')
    match = re.search(r'TG\s((?:(?:[\w\s]+,?[\w\s]*)(?:;\s)?)+)', text)
    if match:
        for topic in match.group(1).split(';'):
            tails.append(f'TG {topic.strip()}')
    allowed = (
        'BD', 'HEB', 'IE', 'See ', 'Comparison', 'The', 'Gnolaum', 'His', 'OR',
        'Bath-shua', 'GR', 'Aramaic', 'Septuagint', 'It', 'Greek', 'In', 'What',
        'This', 'More', 'Joab', 'Persian', 'According', 'Some', 'Hebrew',
        'Samaritan', 'Variant', 'A ', 'Probably', 'All ', 'Progress', '“',
        'Beginning', 'Isaiah chapters', 'Arabian', 'Despite', 'Israel',
        'Possibly', 'Here', 'Several', 'Rabbinical', 'Other', 'Many', 'Syriac',
        'Dogs', 'Wisdom', 'Implying'
    )
    if not tails and not text.startswith(allowed):
        raise ValueError(f'unrecognized reference syntax: "{text}"')
    return tails
