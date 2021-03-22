---
title: "Graph Components, Centrality, and Link Analysis"
---

The [first post]({% post_url 2020-12-28-scratching-the-surface %})
on this blog introduced a graph with all the verses in the standard works
connected by their annotated cross-references. As I mentioned there, the graph
contains 41&nbsp;995 verses and 45&nbsp;985 cross-references. However, the graph
is composed of many disconnected components: most verses are impossible to reach
by following cross-references from any given starting verse.

## Graph Components

Consider the group of nodes shown here:

![](/assets/2020-12-31/small-component.png)

Most of the edges are reciprocal (that is, there are edges pointing in both
directions). However, there are no edges connecting to the larger graph—this is
the complete set of connections for these verses, and no verses in the standard
works outside this group reference any of the verses in this group. In graph
theory terminology, this is a *weakly connected component*
that is isolated from all other components in the graph.

The full cross-reference graph is actually mostly composed of disconnected
graphs like this one. In fact, more than 50% of verses are singletons that have
no incoming or outgoing edges—they do not reference any verses *and*
they are not referenced by any other verses. Here's a histogram showing the full
distribution of component sizes (note that both axes use a logarithmic scale):

![](/assets/2020-12-31/component-size.png)

The frequency of components with a given size drops rapidly as the size
increases. There are 22,243 singletons, 1159 two-node components, 342
three-node components, and so on. The bar on the far right is the one we're most
interested in; it represents a single component containing 15,004 nodes and
40,011 edges. This component contains 36% of the verses in the standard
works (76% of the verses that have any incoming or outgoing references) and 87%
of the cross-references.

*Since this component is by far the largest and most interesting subgraph,
subsequent analysis of the cross-reference graph is focused only on this
subgraph.*

## Which nodes are most important?

One way to think about the cross-reference graph is as an information network.
Verses contain information—explanations of doctrine, accounts of historical
events, prophecies, etc.—and cross-references are a mechanism for propagating
that information throughout the scriptures. If many authors cite the same verse,
we might assume that verse is more "important" than a verse that is rarely
referenced.

Before going further, I should clarify that we are talking about "importance"
in the graph theoretical sense. We certainly hope that the graph structure
approximates the doctrinal basis of the scriptures and highlights important
topics, events, and teachings (much like
the [scripture mastery](https://www.churchofjesuschrist.org/study/manual/doctrine-and-covenants-and-church-history-seminary-teacher-manual-2014/appendix/introduction-to-scripture-mastery?lang=eng)
program, which has manually chosen a set of important nodes according to those
criteria). However, this isn't guaranteed; sparsity and bias in the existing
references could leave us with significant gaps that future work to propose new
cross-references could help to address.

### Centrality

There are many ways of assessing the importance of nodes in graphs, variously
referred to as [*centrality metrics*](https://en.wikipedia.org/wiki/Centrality).
We have
[already explored]({% post_url 2020-12-28-scratching-the-surface %}) one of
these: *degree centrality*, which simply counts the number of incoming
references (technically this is "in-degree" centrality). More advanced methods
will also consider the importance of the referrers—a node can be important while
having few references if those references come from other important nodes. One
method in this class is
[PageRank](https://en.wikipedia.org/wiki/PageRank), which is used by Google to
rank web pages for serving search results.

The table below shows the most important verses as measured by degree and
PageRank centrality. While many of the same verses are ranked highly by both
methods, there are notable differences. The rank
correlation ([Kendall's 𝜏](https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient))
over all the nodes in the graph is 0.73 (with perfect correlation being 1.0).

<table>
<thead>
  <tr>
    <th>Verse</th>
    <th>Rank (Degree)</th>
    <th>Rank (PageRank)</th>
  </tr>
</thead>
<tbody>
  <tr class="dc">
    <td>D&amp;C 1:38</td>
    <td class="right">1</td>
    <td class="right">1</td>
  </tr>
  <tr class="dc">
    <td>D&amp;C 17:1</td>
    <td class="right">1</td>
    <td class="right">7</td>
  </tr>
  <tr class="bom">
    <td>1 Ne. 17:35</td>
    <td class="right">3</td>
    <td class="right">2</td>
  </tr>
  <tr class="bom">
    <td>Hel. 12:3</td>
    <td class="right">3</td>
    <td class="right">4</td>
  </tr>
  <tr class="dc">
    <td>D&amp;C 1:14</td>
    <td class="right">5</td>
    <td class="right">6</td>
  </tr>
  <tr class="pgp">
    <td>Moses 6:57</td>
    <td class="right">6</td>
    <td class="right">9</td>
  </tr>
  <tr class="bom">
    <td>2 Ne. 25:20</td>
    <td class="right">6</td>
    <td class="right">18</td>
  </tr>
  <tr class="bom">
    <td>1 Ne. 19:10</td>
    <td class="right">6</td>
    <td class="right">27</td>
  </tr>
  <tr class="dc">
    <td>D&amp;C 88:63</td>
    <td class="right">9</td>
    <td class="right">8</td>
  </tr>
  <tr class="dc">
    <td>D&amp;C 1:16</td>
    <td class="right">9</td>
    <td class="right">17</td>
  </tr>
  <tr class="bom">
    <td>2 Ne. 9:28</td>
    <td class="right">11</td>
    <td class="right">10</td>
  </tr>
  <tr class="bom">
    <td>Mosiah 4:26</td>
    <td class="right">22</td>
    <td class="right">3</td>
  </tr>
  <tr class="bom">
    <td>2 Ne. 9:37</td>
    <td class="right">112</td>
    <td class="right">5</td>
  </tr>
</tbody>
</table>

The disparity in ranks for 2&nbsp;Ne.&nbsp;9:37 is quite remarkable. Although it
has only 12 incoming references, it is ranked above 2&nbsp;Ne.&nbsp;9:28
(with 20 incoming references) by PageRank. This can be explained by noting that
the PageRank algorithm divides the influence of each node across all of its
outgoing connections. I like the example given by Mark Newman:

> For instance, websites like <i>Amazon</i> or <i>eBay</i> link to the web pages
of thousands of manufacturers and sellers; if I'm selling something on Amazon it
might link to me. Amazon is an important website, and would have high centrality
by any sensible measure, but should I therefore be considered important by
association? Most people would say not: I am only one of many that Amazon links
to and its contribution to the centrality of my page will get diluted as a
result. (Newman, Mark. <i>Networks</i>. Oxford University Press, 2018. p. 165.)

Similarly, we wouldn't expect that verses referenced by a verse with many other
connections would derive much benefit from that association. In the
cross-reference graph, 2&nbsp;Ne.&nbsp;9:28 is referenced by 2&nbsp;Ne.&nbsp;26:20.
Since 2&nbsp;Ne.&nbsp;26:20 is highly ranked (146th), we might expect it to
contribute significantly to the score of 2&nbsp;Ne.&nbsp;9:28. However,
2&nbsp;Ne.&nbsp;26:20 also references 16 other verses and therefore contributes
much less than we would otherwise expect.
(This feature of PageRank will be especially important as we begin proposing new
connections.)

### Hubs and Authorities

Another useful link analysis algorithm is
[hyperlink-induced topic search](https://en.wikipedia.org/wiki/HITS_algorithm)
(HITS). This algorithm introduces the concepts of *hubs* and
*authorities*; a hub is a node that points to many authoritative sources
(like an entry in the Topical Guide), while an authority is considered a source
of truth. In practice, these definitions are circular—authorities are recognized
because they are referenced by important hubs, and hubs emerge by pointing to
many authorities—and the algorithm iterates until it finds a self-consistent
solution. Note that these labels are not mutually exclusive; it's possible for a
node to be both a hub and an authority. Additionally, HITS does not compensate
for edge counts like PageRank does.

Running HITS on the cross-reference graph identifies a set of hubs and
authorities that we can compare to the nodes identified by degree centrality and
PageRank:

<table>
<thead>
  <tr>
    <th>Hubs</th>
    <th></th>
    <th>Authorities</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="bom">1 Ne. 19:10</td>
    <td></td>
    <td class="bom">Mosiah 7:19</td>
  </tr>
  <tr>
    <td class="bom">2 Ne. 26:12</td>
    <td></td>
    <td class="bom">1 Ne. 19:10</td>
  </tr>
  <tr>
    <td class="dc">D&amp;C 19:27</td>
    <td></td>
    <td class="bom">2 Ne. 25:20</td>
  </tr>
  <tr>
    <td class="bom">Mosiah 7:19</td>
    <td></td>
    <td class="bom">Mosiah 7:27</td>
  </tr>
  <tr>
    <td class="bom">1 Ne. 13:42</td>
    <td></td>
    <td class="bom">2 Ne. 26:12</td>
  </tr>
  <tr>
    <td class="bom">2 Ne. 19:6</td>
    <td></td>
    <td class="bom">Alma 11:39</td>
  </tr>
  <tr>
    <td class="dc">D&amp;C 8:3</td>
    <td></td>
    <td class="bom">2 Ne. 10:3</td>
  </tr>
  <tr>
    <td class="dc">D&amp;C 18:26</td>
    <td></td>
    <td class="bom">3 Ne. 11:14</td>
  </tr>
  <tr>
    <td class="bom">Moro. 7:22</td>
    <td></td>
    <td class="dc">D&amp;C 19:27</td>
  </tr>
  <tr>
    <td class="dc">D&amp;C 18:6</td>
    <td></td>
    <td class="bom">1 Ne. 13:42</td>
  </tr>
</tbody>
</table>

Several of these verses are considered to be both hubs and authorities:
1&nbsp;Ne.&nbsp;19:10, 2&nbsp;Ne.&nbsp;26:12, D&amp;C&nbsp;19:27, Mosiah&nbsp;7:
19, and 1&nbsp;Ne.&nbsp;13:42. Surprisingly, only two verses are repeated from
the earlier centrality analyses: 1&nbsp;Ne.&nbsp;19:10 and 2&nbsp;Ne.&nbsp;25:
20.

## Thus we see

There are definitely some strong themes in the verses we've highlighted in this
post. First of all, it's clear that the Book of Mormon and Doctrine and
Covenants make up the majority of the structurally important nodes in the
cross-reference graph; this isn't surprising, considering the role of those
volumes in the
[restoration of the gospel of Jesus Christ](https://www.churchofjesuschrist.org/study/manual/true-to-the-faith/restoration-of-the-gospel?lang=eng)
and the likely emphases of the people who compiled the original references (the
Old and New Testaments also have lower
[relative reference counts]({% post_url 2020-12-28-scratching-the-surface %})
than restoration scriptures). Despite the systematic differences between these
volumes (e.g. due to how they were created and compiled), I hope that future
work to propose new cross-references can help to reduce this bias.

Returning to the nodes we've identified, many of these verses refer to the role
of prophets and the mission of Jesus Christ. There is repeated emphasis on the
exodus of Israel from Egypt and the title of Jehovah as the God of Israel.
Notably, one of the authorities is
[3&nbsp;Ne.&nbsp;11:14](https://www.churchofjesuschrist.org/study/scriptures/bofm/3-ne/11.14?lang=eng#p14#14)
, where the Lord extends an invitation:

> Arise and come forth unto me, that ye may thrust your hands into my side, and also that ye may feel the prints of the nails in my hands and in my feet, that ye may know that I am the God of Israel, and the God of the whole earth, and have been slain for the sins of the world.

I'm delighted to see such fundamental doctrines highlighted by our analysis of
the cross-reference graph, and I hope that additional interesting and insightful
patterns will emerge as we continue digging.

{:.note}
The code used for the analysis and figures in this post is available
on [GitHub](https://github.com/skearnes/scripture-graph). Additional images were
generated with Cytoscape.

{:.note}
Updates:

* {:.note} **January 4,
  2021:** [Updated](https://github.com/skearnes/scripture-graph/pull/8)
  the reference parsing code to handle multiple verses in the same chapter
  (e.g. "1&nbsp;Ne.&nbsp;3:7,&nbsp;10" now creates edges to 1&nbsp;Ne.&nbsp;3:7
  and 1&nbsp;Ne.&nbsp;3:10). This changed the edge count from 45&nbsp;786 to
  45&nbsp;985 and resulted in multiple changes to the set and order of nodes
  chosen by the various node ranking algorithms.

[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)

{:.note}
© Copyright 2020 Steven Kearnes. This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).
