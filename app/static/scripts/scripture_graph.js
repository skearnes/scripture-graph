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