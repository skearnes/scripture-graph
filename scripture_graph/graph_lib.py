"""Utilities for parsing scriptures EPUB into verses and references."""

import dataclasses
import re
from typing import Dict, Iterable, List, Tuple
import zipfile

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
    'THE FIRST BOOK OF NEPHI': '1 Ne.',
    'THE SECOND BOOK OF NEPHI': '2 Ne.',
    'THIRD NEPHI': '3 Ne.',
    'FOURTH NEPHI': '4 Ne.',
    'THE BOOK OF ALMA': 'Alma',
    'THE BOOK OF ENOS': 'Enos',
    'THE BOOK OF ETHER': 'Ether',
    'THE BOOK OF HELAMAN': 'Hel.',
    'THE BOOK OF JACOB': 'Jacob',
    'THE BOOK OF JAROM': 'Jarom',
    'THE BOOK OF MORMON': 'Morm.',
    'THE BOOK OF MORONI': 'Moro.',
    'THE BOOK OF MOSIAH': 'Mosiah',
    'THE BOOK OF OMNI': 'Omni',
    'THE WORDS OF MORMON': 'W of M',
    'THE DOCTRINE AND COVENANTS': 'D&C',
    'THE ARTICLES OF FAITH': 'A of F',
    'THE BOOK OF ABRAHAM': 'Abr.',
    'JOSEPH SMITH—MATTHEW': 'JS—M',
    'BOOK OF MOSES': 'Moses',
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
            tree = etree.parse(info.filename, parser=etree.HTMLParser())
            this_verses, this_references = read_tree(tree)
            verses.update(this_verses)
            references.extend(this_references)
    return verses, references


def read_tree(tree) -> Tuple[Dict[str, Verse], List[Reference]]:
    verses = {}
    references = []
    book = list(cssselect.CSSSelector('.runHead')(tree)[0].itertext())[0]
    book_short = BOOKS_SHORT[book]
    chapter = int(list(cssselect.CSSSelector('.titleNumber')(tree)[0].itertext())[0].split()[1])
    for verse_element in cssselect.CSSSelector('.verse-first,.verse')(tree):
        verse = None
        for element in verse_element.iter():
            if element.get('class') == 'verseNumber':
                verse = int(list(element.itertext())[0])
            # Remove verse numbers and reference markers.
            if element.get('class') in ['verseNumber', 'marker']:
                verse_element.remove(element)
        text = ''.join(verse_element.itertext())
        if not verse:
            raise ValueError('could not find verse for {book_short} {chapter}: {text}')
        key = f'{book_short} {chapter}:{verse}'
        verses[key] = Verse(book=book_short, chapter=chapter, verse=verse, text=text)
    for reference_element in cssselect.CSSSelector('.listItem')(tree):
        verse = None
        tails = []
        for element in reference_element.iter():
            if element.get('class') == 'label-verse':
                verse = int(list(element.itertext())[0])
            # NOTE(kearnes): Most (but not all) references have the
            # "scriptureRef" class. This ambiguity means we have to resort to
            # regexes instead of simply walking through the tree.
            if 'class' not in element.attrib:
                tails.extend(parse_reference(element.itertext()))
        head = f'{book_short} {chapter}:{verse}'
        for tail in tails:
            references.append(Reference(head=head, tail=tail))
    return verses, references


def parse_reference(lines: Iterable[str]) -> List[str]:
    tails = []
    # Multiple references are separated by semicolons.
    lines = ''.join(lines).split(';')
    for line in lines:
        # References have several forms:
        #   * Scripture: "Gen. 10:6 (6-8)", where the range is optional.
        #   * Study helps: "TG Adam".
        #   * Other: Hebrew/Greek translations, etc.
        if line.startswith(('BD',)):
            continue
        # NOTE(kearnes): Verse ranges are excluded from the tail when creating
        # edges in the graph.
        match = re.fullmatch(r'(\w+\.?\s+\d+:\d+)(?:\s+\(\d+-\d+\))?\.?', line)
        if match:
            tails.append(match.group(1))
            continue
        match = re.fullmatch(r'(TG \w+)', line)
        if match:
            tails.append(match.group(1))
            continue
        raise ValueError(f'unrecognized reference syntax: {line}')
    return tails
