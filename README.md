# scripture-graph

# Quick start

```shell
# Install the package.
git clone https://github.com/skearnes/scripture-graph.git
cd scripture-graph
pip install -r requirements.txt
python setup.py install
# Download Standard Works EPUB files.
./download_epub.sh
# Generate a graph.
python scripture_graph/build_graph.py --input_pattern="*.epub" --output=scripture_graph.graphml
```

# Graph visualization

Generated graphs can be visualized interactively with various tools; see the
[recommendations](https://networkx.org/documentation/stable/reference/drawing.html#drawing)
from NetworkX.

# Things to do

Here are some of the things I'm thinking about:

* PageRank or other network analysis algorithms to identify structures such as
  hubs.
* Machine learning to embed each verse in a high-dimensional space. Assuming we
  can preserve the graph structure, we can do things like link prediction (i.e.
  what cross-references should exist but are not yet annotated?).
* Expand the Doctrine and Covenants so it's not treated as a single book :).
* Network visualization and exploration tools.  
* Lots and lots of testing to find all the bugs...
