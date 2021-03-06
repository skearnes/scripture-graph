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
        xhr.onload = function () {
            if (xhr.status === 200) {
                resolve(xhr.response);
            } else {
                reject(verse);
            }
        }
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
    history.pushState({'verse': verse}, verse, '?' + queryParams.toString());
}

/**
 * Initializes the Cytoscape viewer.
 * @param {string} verse
 */
function initGraph(verse) {
    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: getElements(verse),
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
        layout: {
            name: 'cose',
            animate: false,
        },
    });
    updateQuery(verse);
}

/**
 * Updates the graph to focus on a new verse.
 * @param {string} verse
 */
async function updateGraph(verse) {
    const elements = await getElements(verse);
    cy.remove('*');  // Clear the current graph.
    cy.add(elements);
    const layout = cy.layout({
        name: 'cose',
        animate: false,
    });
    layout.run();
    updateQuery(verse);
}
