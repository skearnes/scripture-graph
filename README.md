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
python scripture_graph/build_graph.py --input_pattern="*.epub" --output=scripture_graph.gml
```

# Graph visualization

Generated graphs can be visualized interactively with
[Cytoscape](https://cytoscape.org).
