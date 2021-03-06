/**
 * Copyright 2021 Steven Kearnes
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Core JS functionality for interactive graph visualization.
 */

// The full network is stored in a headless Cytoscape instance, and
// subgraphs are copied to the displayed instance as needed.
const network = cytoscape({
    elements: elements,
    // layout: {
    //     name: 'grid',  // Required to set initial positions.
    // },
});

const cy = cytoscape({
    container: document.getElementById('cy'),
    style: [
        {
            selector: 'node',
            style: {
                'background-color': '#666',
                'label': 'data(id)',
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 3,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        }
    ],
});

/**
 * Shows a verse and its neighbors.
 * @param {string} verse
 */
function showVerse(verse) {
    cy.remove('node');  // Clear the current graph.
    const sel = network.getElementById(verse);
    cy.add(sel.closedNeighborhood());
    cy.autolock(false);
    const layout = cy.layout({
        name: 'cose',
        animate: false,
        randomize: true,
    });
    layout.run();
    cy.autolock(true);
}

showVerse('John 1:1');