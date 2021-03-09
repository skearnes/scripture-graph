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

'use strict';

// Global Cytoscape object.
let cy = null;

// History handler to correctly process the back button.
window.onpopstate =
    function(event) {
    // NOTE(kearnes): Do not call updateQuery.
    updateGraph(event.state.verse);
    updateTable(event.state.verse);
}

/**
 * Fetches the neighborhood around a verse.
 * @param {string} verse
 * @return {!Promise<Object>}
 */
function getElements(verse) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/elements');
        xhr.responseType = 'json';
        xhr.onload = function() {
            if (xhr.status === 200) {
                resolve(xhr.response);
            } else {
                reject(verse);
            }
        };
        xhr.send(verse);
    });
}

/**
 * Updates the URL query string.
 * @param {string} verse
 */
function updateQuery(verse) {
    const queryParams = new URLSearchParams(window.location.search);
    queryParams.set('verse', verse);
    const state = {
        verse: verse,
    };
    history.pushState(state, verse, '?' + queryParams.toString());
}

/**
 * Initializes the Cytoscape viewer.
 * @param {string} verse
 */
function initGraph(verse) {
    // See https://js.cytoscape.org/#core/initialisation.
    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: getElements(verse),
        style: [
            {
                selector: 'node',
                css: {
                    'font-weight': 'normal',
                    'background-opacity': 1.0,
                    'font-size': 12,
                    'background-color': 'rgb(255,255,255)',
                    'border-opacity': 1.0,
                    'text-opacity': 1.0,
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'border-width': 0.0,
                    'border-color': 'rgb(204,204,204)',
                    'shape': 'roundrectangle',
                    'width': 'label',
                    'height': 'label',
                    'padding': '5px',
                    'content': 'data(id)'
                }
            },
            {
                selector: 'edge',
                css: {
                    'width': 1.0,
                    'text-opacity': 1.0,
                    'target-arrow-color': 'rgb(0,204,255)',
                    'line-color': 'rgb(0,204,255)',
                    'source-arrow-color': 'rgb(0,204,255)',
                    'line-style': 'solid',
                    'source-arrow-shape': 'none',
                    'opacity': 1.0,
                    'font-size': 10,
                    'target-arrow-shape': 'triangle',
                    'font-weight': 'normal',
                    'curve-style': 'straight'
                }
            }
        ],
        layout: {
            name: 'cola',
            animate: false,
        },
        autoungrabify: true,
        boxSelectionEnabled: false,
        userPanningEnabled: false,
        userZoomingEnabled: false,
    });
    cy.on('tap', 'node', function(event) {
        const verse = event.target.id();
        const queryParams = new URLSearchParams(window.location.search);
        if (queryParams.get('verse') !== verse) {
            updateGraph(verse);
            updateQuery(verse);
            updateTable(verse);
        }
    });
    updateQuery(verse);
}

/**
 * Updates the graph to focus on a new verse.
 * @param {string} verse
 * @param {boolean=} clear
 */
async function updateGraph(verse, clear = true) {
    const elements = await getElements(verse);
    if (clear) {
        cy.remove('*');
    }
    cy.add(elements);
    const layout = cy.layout({
        name: 'cola',
        animate: false,
    });
    layout.run();
}
