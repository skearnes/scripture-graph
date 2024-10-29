# scripture-graph

See blog posts using this code at [Welding Links](https://welding-links.org/blog).

## Connection Explorer

Visit https://graph.welding-links.org to explore cross-references in an interactive web app.

## Quick start

```shell
# Install the package.
git clone https://github.com/skearnes/scripture-graph.git
cd scripture-graph
pip install .
# Download Standard Works EPUB files.
./download_epub.sh
# Generate a graph.
python scripture_graph/build_graph.py --input_pattern="*.epub" --output=scripture_graph.graphml
```

## Graph visualization

Generated graphs can be visualized interactively with various tools; see the
[recommendations](https://networkx.org/documentation/stable/reference/drawing.html#drawing)
from NetworkX.
