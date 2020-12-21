"""Builds a scripture graph."""

import glob

from absl import app
from absl import flags
from absl import logging

from scripture_graph import graph_lib

FLAGS = flags.FLAGS
flags.DEFINE_string('input_pattern', None, 'Input EPUB pattern.')


def main(argv):
    del argv  # Only used by app.run().
    verses = {}
    references = []
    for filename in glob.glob(FLAGS.input_pattern):
        logging.info(filename)
        this_verses, this_references = graph_lib.read_epub(filename)
        logging.info(
            f'Found {len(this_verses)} verses and'
            f' {len(this_references)} references')
        verses.update(this_verses)
        references.extend(this_references)
    logging.info(
        f'Found {len(verses)} verses and {len(references)} references')


if __name__ == '__main__':
    flags.mark_flag_as_required('input_pattern')
    app.run(main)
