---
title: "Adding the Topical Guide and Index"
---

Our analysis so far has focused on cross-references between verses. This post
expands the cross-reference graph by including topics from the
[Topical Guide](https://www.churchofjesuschrist.org/study/scriptures/tg?lang=eng)
(TG)
and [Index to the Triple Combination](https://www.churchofjesuschrist.org/study/scriptures/triple-index?lang=eng)
(ITC).

For convenience, I am treating each topic as an additional node in the graph,
with edges pointing to and from specific verses. We could imagine doing
something more elaborate like creating edges between all pairs of verses
referenced by a topic, but that would exponentially increase the number of edges
and lose some of the structure provided by the topical organization.

There are 3512 entries in the Topical Guide, and a further 3059 entries in the
Index, for a total of 6571 topics. After adding these topics and their
references to the graph, we have:

<div class="center">
<table class="left" style="display: inline-block; vertical-align: top; padding-right: 3em;">
<thead>
  <tr>
    <th class="center" colspan="2">Nodes</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Verses</td>
    <td class="right">41,995</td>
  </tr>
  <tr>
    <td>TG</td>
    <td class="right">3512</td>
  </tr>
  <tr>
    <td>ITC</td>
    <td class="right">3059</td>
  </tr>
  <tr>
    <td></td>
    <td class="right" style="border-top: 1px solid black"><b>48,566</b></td>
  </tr>
</tbody>
</table>

<table class="left" style="display: inline-block; vertical-align: top;">
<thead>
  <tr>
    <th class="center" colspan="2">Edges</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Verse→Verse</td>
    <td class="right">45,985</td>
  </tr>
  <tr>
    <td>Topic→Verse</td>
    <td class="right">100,597</td>
  </tr>
  <tr>
    <td>Verse→Topic</td>
    <td class="right">22,223</td>
  </tr>
  <tr>
    <td>Topic→Topic</td>
    <td class="right">14,267</td>
  </tr>
  <tr>
    <td></td>
    <td class="right" style="border-top: 1px solid black"><b>183,072</b></td>
  </tr>
</tbody>
</table>
</div>

## Reference Counts

Although the number of topics is small compared to the number of verses, adding
the topic references nearly quadruples the number of edges in the graph. As a
result, the distribution of reference counts is dramatically shifted relative to
the original graph that did not include any topic nodes:

![](/assets/2021-01-18/count-cdf.png)

Notably, the proportion of singletons—verses that are never referenced—has
dropped from 56% to 31%, and there are significantly more highly-cited verses.
If we dive deeper into the absolute and relative reference counts for each
volume of scripture, we see an explosion in cross-reference coverage (the
original values from the verses-only graph are shown in blue and orange):

![](/assets/2021-01-18/count-bar.png)

The Pearl of Great Price retains its position as the volume with the highest
relative reference count with an average of more than nine references to each
verse. The Book of Mormon overtakes the Old Testament as the volume with the
highest number of references overall, with more than 43,000.

## Graph Components

Even with the additional nodes and edges from the Topical Guide and Index, many
of the nodes in the graph are singletons or part of very small components.
Isolating the largest component, as we did previously, leaves us with a subgraph
containing 68% of the verses in the full graph (the largest component in the
topic-free graph only covered 36% of verses):

<div class="center">
<table class="left" style="display: inline-block; vertical-align: top; padding-right: 3em;">
<thead>
  <tr>
    <th class="center" colspan="2">Nodes</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Verses</td>
    <td class="right">28,573</td>
  </tr>
  <tr>
    <td>TG</td>
    <td class="right">3180</td>
  </tr>
  <tr>
    <td>ITC</td>
    <td class="right">2986</td>
  </tr>
  <tr>
    <td></td>
    <td class="right" style="border-top: 1px solid black"><b>34,739</b></td>
  </tr>
</tbody>
</table>

<table class="left" style="display: inline-block; vertical-align: top;">
<thead>
  <tr>
    <th class="center" colspan="2">Edges</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Verse→Verse</td>
    <td class="right">45,070</td>
  </tr>
  <tr>
    <td>Topic→Verse</td>
    <td class="right">100,537</td>
  </tr>
  <tr>
    <td>Verse→Topic</td>
    <td class="right">22,223</td>
  </tr>
  <tr>
    <td>Topic→Topic</td>
    <td class="right">14,266</td>
  </tr>
  <tr>
    <td></td>
    <td class="right" style="border-top: 1px solid black"><b>182,096</b></td>
  </tr>
</tbody>
</table>
</div>

### Centrality

With our newly expanded graph, we can repeat the centrality analyses to identify
the most "important" nodes. The Topical Guide dominates here, due to a small
number of topics receiving many references from verses throughout the Standard
Works as well as other topics (via "see also" lists).

<table style="margin-left: auto; margin-right: auto;">
<thead>
  <tr>
    <th>Verse</th>
    <th>Rank<br>(Degree)</th>
    <th>Rank<br>(PageRank)</th>
  </tr>
</thead>
<tbody class="sh">
  <tr>
    <td>TG Faith</td>
    <td class="right">1</td>
    <td class="right">1</td>
  </tr>
  <tr>
    <td>TG Righteousness</td>
    <td class="right">1</td>
    <td class="right">2</td>
  </tr>
  <tr>
    <td>TG Repent, Repentance</td>
    <td class="right">3</td>
    <td class="right">11</td>
  </tr>
  <tr>
    <td>TG Prayer, Pray</td>
    <td class="right">4</td>
    <td class="right">5</td>
  </tr>
  <tr>
    <td>TG Obedience, Obedient, Obey</td>
    <td class="right">5</td>
    <td class="right">30</td>
  </tr>
  <tr>
    <td>TG Sin</td>
    <td class="right">6</td>
    <td class="right">27</td>
  </tr>
  <tr>
    <td>TG Jesus Christ, Prophecies about</td>
    <td class="right">7</td>
    <td class="right">4</td>
  </tr>
  <tr>
    <td>TG Jesus Christ, Atonement through</td>
    <td class="right">8</td>
    <td class="right">20</td>
  </tr>
  <tr>
    <td>TG Forgive, Forgiveness</td>
    <td class="right">9</td>
    <td class="right">12</td>
  </tr>
  <tr>
    <td>TG God, Spirit of</td>
    <td class="right">10</td>
    <td class="right">13</td>
  </tr>
  <tr>
    <td>TG Idolatry, Idol</td>
    <td class="right">11</td>
    <td class="right">3</td>
  </tr>
  <tr>
    <td>TG Treasure</td>
    <td class="right">11</td>
    <td class="right">8</td>
  </tr>
  <tr>
    <td>TG God, Omniscience of</td>
    <td class="right">14</td>
    <td class="right">9</td>
  </tr>
  <tr>
    <td>TG Grace</td>
    <td class="right">15</td>
    <td class="right">10</td>
  </tr>
  <tr>
    <td>TG Disobedience, Disobey</td>
    <td class="right">17</td>
    <td class="right">7</td>
  </tr>
  <tr>
    <td>TG Angels</td>
    <td class="right">29</td>
    <td class="right">6</td>
  </tr>
</tbody>
</table>

Since the most important nodes all come from the added topics, these results are
difficult to compare to the measurements for the verses-only graph. However, if
we ignore topics and instead focus on the top-ranked verses, we can examine
whether the underlying verse-to-verse structure has changed. In the table below,
each centrality rank is reported as both a raw value (with topics) and an
adjusted value (without topics).

<table style="margin-left: auto; margin-right: auto;">
<thead>
  <tr>
    <th>Verse</th>
    <th colspan="2">Rank<br>(Degree)</th>
    <th colspan="2">Rank<br>(PageRank)</th>
  </tr>
</thead>
<tbody>
<tr class="dc">
  <td>D&amp;C 132:19</td>
  <td class="right">146</td>
  <td class="right">1</td>
  <td class="right">566</td>
  <td class="right">41</td>
</tr>
<tr class="pgp">
  <td>Moses 6:57</td>
  <td class="right">151</td>
  <td class="right">2</td>
  <td class="right">386</td>
  <td class="right">6</td>
</tr>
<tr class="bom">
  <td>Mosiah 3:19</td>
  <td class="right">159</td>
  <td class="right">3</td>
  <td class="right">366</td>
  <td class="right">4</td>
</tr>
<tr class="bom">
  <td>1 Ne. 19:10</td>
  <td class="right">159</td>
  <td class="right">3</td>
  <td class="right">406</td>
  <td class="right">7</td>
</tr>
<tr class="dc">
  <td>D&amp;C 13:1</td>
  <td class="right">159</td>
  <td class="right">3</td>
  <td class="right">433</td>
  <td class="right">12</td>
</tr>
<tr class="dc">
  <td>D&amp;C 17:1</td>
  <td class="right">169</td>
  <td class="right">6</td>
  <td class="right">326</td>
  <td class="right">1</td>
</tr>
<tr class="bom">
  <td>1 Ne. 17:35</td>
  <td class="right">180</td>
  <td class="right">7</td>
  <td class="right">416</td>
  <td class="right">9</td>
</tr>
<tr class="bom">
  <td>Mosiah 3:5</td>
  <td class="right">180</td>
  <td class="right">7</td>
  <td class="right">523</td>
  <td class="right">28</td>
</tr>
<tr class="bom">
  <td>Mosiah 4:26</td>
  <td class="right">192</td>
  <td class="right">9</td>
  <td class="right">345</td>
  <td class="right">3</td>
</tr>
<tr class="dc">
  <td>D&amp;C 1:16</td>
  <td class="right">212</td>
  <td class="right">10</td>
  <td class="right">471</td>
  <td class="right">15</td>
</tr>
<tr class="dc">
  <td>D&amp;C 1:38</td>
  <td class="right">252</td>
  <td class="right">17</td>
  <td class="right">343</td>
  <td class="right">2</td>
</tr>
<tr class="dc">
  <td>D&amp;C 1:14</td>
  <td class="right">275</td>
  <td class="right">20</td>
  <td class="right">409</td>
  <td class="right">8</td>
</tr>
<tr class="bom">
  <td>2 Ne. 9:28</td>
  <td class="right">321</td>
  <td class="right">29</td>
  <td class="right">418</td>
  <td class="right">10</td>
</tr>
<tr class="bom">
  <td>Hel. 12:3</td>
  <td class="right">436</td>
  <td class="right">69</td>
  <td class="right">375</td>
  <td class="right">5</td>
</tr>
</tbody>
</table>

Ten of the 13 verses reported for the verse-only graph are repeated here; only 2
Ne. 9:37, 2 Ne. 25:20, and D&amp;C 88:63 are missing. Of these, 2 Ne. 25:20 (#13
by degree) and D&amp;C 88:63 (#14 by PageRank) are just below the top-ten
threshold, while 2 Ne. 9:37 is significantly downweighted in the expanded
graph (#1692 and #87 by degree and PageRank, respectively). Four new verses
appear in this: Mosiah 3:5, Mosiah 3:19, D&amp;C 13:1, and D&amp;C 132:19. Of
these, only Mosiah 3:19 is close to the threshold in the original verse-only
graph (#12 by PageRank).

### Hubs and Authorities

We can likewise repeat the HITS analysis from before to identify "hub" and
"authority" nodes in the expanded graph:

<table style="margin-left: auto; margin-right: auto;">
<thead>
  <tr>
    <th>Hubs</th>
    <th>Rank</th>
    <th>Authorities</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="sh">ITC God</td>
    <td class="center">1</td>
    <td class="bom">2 Ne. 31:21</td>
  </tr>
  <tr>
    <td class="sh">ITC Jesus Christ</td>
    <td class="center">2</td>
    <td class="pgp">Moses 6:57</td>
  </tr>
  <tr>
    <td class="sh">TG Spirit</td>
    <td class="center">3</td>
    <td class="ot">Isa. 9:6</td>
  </tr>
  <tr>
    <td class="sh">ITC Name of the Lord</td>
    <td class="center">4</td>
    <td class="dc">D&amp;C 68:25</td>
  </tr>
  <tr>
    <td class="sh">ITC Jesus Christ—Son of God</td>
    <td class="center">5</td>
    <td class="bom">Moro. 10:4</td>
  </tr>
  <tr>
    <td class="sh">TG Know, Knew, Known</td>
    <td class="center">6</td>
    <td class="bom">Jacob 4:5</td>
  </tr>
  <tr>
    <td class="sh">ITC Repentance, Repent</td>
    <td class="center">7</td>
    <td class="bom">2 Ne. 19:6</td>
  </tr>
  <tr>
    <td class="sh">ITC Spirit, Holy/Spirit of the Lord</td>
    <td class="center">8</td>
    <td class="dc">D&amp;C 13:1</td>
  </tr>
  <tr>
    <td class="sh">TG Power, Powerful</td>
    <td class="center">9</td>
    <td class="sh">TG Repent, Repentance</td>
  </tr>
  <tr>
    <td class="sh">ITC Faith</td>
    <td class="center">10</td>
    <td class="pgp">Moses 6:59</td>
  </tr>
</tbody>
</table>

All the hubs are from the Topical Guide or Index, which isn't surprising given
the number of outgoing edges for most topics. What is surprising, however, is
that <i>none</i> of the top authority nodes from the verse-only graph are
repeated; the highest rank for any previously identified authority node is 27
(Mosiah 7:27).

The newly identified authorities contain some of the most powerful prophecies of
the coming of the Messiah in all the Standard Works. For instance, both Isa. 9:6
and 2 Ne. 19:6 prophesy of his birth ("For unto us a child is born..."). Moses
6:57, Moses 6:59, and D&amp;C 68:25 lay out basic gospel principles and
emphasize teaching them to children. One topic is included as an authority on
this list, and it is one of the most doctrinally important topics of all:
repentance.

## Thus we see

Adding topics to the cross-reference graph significantly expands the number of
connections and gives us new insights into the graph structure of the full
Standard Works. In a sense, the Topical Guide and other study helps are
cross-reference appendices&mdash;places to store all the cross-references that
wouldn't fit on the pages of the printed scriptures. They also serve as an
abstraction of the scriptures over time and space, helping us to see patterns in
the Standard Works across many authors and cultural contexts.

Some readers may be concerned that the verses ranked "most important" can change
depending on the analysis method or whether topics are included in the graph. In
my opinion, this variability highlights rather than obscures the beauty of the
cross-references and their patterns. Just as individuals may approach the
scriptures from different angles and gain different insights from the same
verses, the various methods used here emphasize different aspects of the
connections between verses while consistently pointing to Jesus Christ and the
restoration of the gospel.

{:.note} 
The code used for the analysis and figures in this post is available on
[GitHub](https://github.com/skearnes/scripture-graph).

[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)

{:.note}
© Copyright 2021&ndash;2022 Steven Kearnes. This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/)
.
