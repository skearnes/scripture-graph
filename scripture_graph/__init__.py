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
# Short names for books (used in references).
"""Constants used in submodules."""

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
