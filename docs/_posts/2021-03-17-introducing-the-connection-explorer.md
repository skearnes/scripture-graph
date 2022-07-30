---
title: "Introducing the Connection Explorer"
---

I'm happy to present the *Connection Explorer*, an interactive tool for
exploring the cross-reference graph and other scriptural connections.

The tool can be accessed by clicking the 
[Connection Explorer](https://graph.welding-links.org) link here
or at the top of the page. Please give it a try!

## Overview

The Connection Explorer interface is divided into three sections:

![](/assets/2021-03-17/connection_explorer.png)

### Verse selector

The verse selector contains an entry for every verse in the Standard
Works. Click on any verse in the menu to refocus the graph
display on that verse.

### Graph display

The graph display shows the selected verse and its connections
in the cross-reference graph. Click on any of the verses shown in
the graph to refocus the graph on that verse.

### Source links

The source links section contains links to the text of the selected
verse and its connections. These links primarily point to the
online scriptures available at 
[ChurchofJesusChrist.org](https://www.churchofjesuschrist.org/study/scriptures?lang=eng).

## Other features

* The URL in the address bar is updated to reflect the currently
  selected verse. It can be copied and shared to return directly
  to that verse in the Connection Explorer.
* All three windows are kept in sync; a selection in the verse
  selector will update the graph display, and a selection in the 
  graph display will update the verse selector.
  
### Technical details

The Connection Explorer makes use of several third-party libraries:

* [Cytoscape.js](https://js.cytoscape.org/)
* [Fancytree](https://github.com/mar10/fancytree/)
* [WebCola](https://github.com/tgdwyer/WebCola)
* [cytoscape-cola](https://github.com/cytoscape/cytoscape.js-cola)
* [jQuery](https://jquery.com/)
  
{:.note}
The code for the Connection Explorer is available on
[GitHub](https://github.com/skearnes/scripture-graph). Images for this post were
generated with Google Drawings.
  
[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)

{:.note}
© Copyright 2020&ndash;2022 Steven Kearnes. This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).
