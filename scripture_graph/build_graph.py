"""Builds a scripture graph."""

from absl import app
from absl import flags

from scripture_graph import graph_lib

FLAGS = flags.FLAGS
flags.DEFINE_string('input', None, 'Input EPUB.')


def main(argv):
    del argv  # Only used by app.run().
    verses, references = graph_lib.read_epub(FLAGS.input)


if __name__ == '__main__':
    flags.mark_flag_as_required('input')
    app.run(main)
