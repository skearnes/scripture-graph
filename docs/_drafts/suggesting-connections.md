---
title: "Suggesting Connections"
---

The Standard Works contain 41&nbsp;995 verses and 45&nbsp;985 cross-references
between verses. If we ignore the directionality of these references, there are
26&nbsp;946 connected verse pairs. These connections represent only a fraction
of the possible number of verse pairs (26&nbsp;946 / 881&nbsp;727&nbsp;020 =
0.003%). Of course, we know that not all verse pairs are
interesting&mdash;Joshua 18:25 and D&C 10:30 really don't have anything in
common&mdash;but there are definitely interesting connections that the existing
cross-references have missed.

This post explores several methods for *algorithmically* suggesting new
connections in the scriptures. There's no ground truth here; the validity of a
connection is mostly subjective. That said, with the hope of being useful and
revealing new insights, the Connection Explorer now includes an option to
display suggested connections beyond the existing cross-references.

## Similarity between verses

Connections between verses are fundamentally statements about their similarity.
Verses can be similar in any number of ways: perhaps they refer to the same
person or event, or discuss the same doctrinal principle, or contain the same
idiom or phrasing ("And it came to pass..."). Depending on what we are looking
for, different flavors of similarity will be more or less relevant.

Unfortunately, the existing cross-references do not have any notion of *kind*;
different notions of similarity are mixed and matched without any warning.
Resources like the Topical Guide help to organize references by the type of
similarity they share; usually these resources are scarcely more than
concordances, easily approximated by modern keyword searches.

Ideally we could use data science and machine learning to identify non-obvious
connections that go beyond existing tools. But before I bite off more than I can
chew, let's start with some simple approaches that can be used to expand the
existing set of connections (obvious or not).

### Verses as vectors

From a data science perspective, similarity calculations require two
ingredients: a representation and a metric. The most common representation is a
vector, where each component holds information about some property of the
object. For example,
a [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model)
representation of a document is simply the number of instances of each word from
a predefined vocabulary. Metrics are used to combine the representations for two
objects and return a similarity or distance value. In text processing tasks, two
of the most common metrics
are [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
and [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance). The
metric values can be used to identify the most similar pairs, either by imposing
an absolute cutoff or by considering only the top-ranked pairs.

### Looking at neighbors

One of the simplest ways to measure similarity between verses is to compare
their neighborhoods&mdash;the connections they have in common. In this case, the
vector representation of each verse is simply its corresponding row in
the [adjacency matrix](https://en.wikipedia.org/wiki/Adjacency_matrix) of the
undirected graph. There is an entry in the vector for each verse in the graph,
with a 1 where two verses are connected and a 0 otherwise. Conceptually, the
nonzero entries in this vector define a set of neighbors; for example, the
neighborhood set for Helaman 5:8 is {1 Ne. 15:36, Hel. 8:25, 3 Ne. 13:20}.

The [Jaccard coefficient](https://en.wikipedia.org/wiki/Jaccard_index) is a
common metric for comparing binary vectors or sets. It is defined as the set
intersection divided by the set union; in our case, this is the number of
neighbors two verses have in common divided by the total number of neighbors for
both verses (after removing duplicates).

Consider [2 Ne. 26:24](https://www.churchofjesuschrist.org/study/scriptures/bofm/2-ne/26.24?lang=eng#p24#24)
and [3 Ne. 9:14](https://www.churchofjesuschrist.org/study/scriptures/bofm/3-ne/9.14?lang=eng#p14#14),
which are not connected by any existing cross-references. The neighborhood
sets for these verses are, respectively, {John 3:16, John 12:32, 2 Ne. 2:27, 2
Ne. 9:5, Jacob 5:41, Alma 26:37} and {Isa. 59:16, John 3:16, 1 Ne. 1:14, 2 Ne.
1:15, 2 Ne. 26:25, Jacob 6:5, Alma 5:33, Alma 5:34, Alma 19:36}. These verses
have one neighbor in common (John 3:16) and 14 unique neighbors between them, so
the Jaccard similarity is 1 / 14 = 0.07.

Identifying connections this way has an interesting property: it is iterable.
If we take the top-ranked connections as truth, we can add them to the existing
set of connections and repeat the analysis to suggest another new set of
connections. If we had the patience, we could repeat this procedure until the
set of connections doesn't change anymore. It's rather time-consuming to run
each round of comparisons due to the size of the graph; one trick, borrowed from
cheminformatics, is to [fold](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2536658/)
the vectors into smaller representations to speed up the metric calculations. 
The simplest approach is to replace a vector A of length N with a vector B of 
length M where B[\i % M\] = OR(A\[i\], B\[i % M\]). Bit collisions can lead to 
unexpected connections, but these are likely to be rare since the average number
of bits set for each verse is small.

### Looking at the text
