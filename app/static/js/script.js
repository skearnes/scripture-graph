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
 * Initializes the entire page.
 */
function initExplorer() {
  // History handler to correctly process the back button.
  window.onpopstate = function(event) {
    const verse = event.state.verse;
    // NOTE(kearnes): Do not call updateQuery.
    updateGraph(verse);
    updateTree(verse);
    updateTable(verse);
  };
  const queryParams = new URLSearchParams(window.location.search);
  let verse;
  if (queryParams.has('verse')) {
    verse = queryParams.get('verse');
  } else {
    verse = 'John 3:16';
  }
  initTree(verse);
  initGraph(verse);
  updateTable(verse);
}

/**
 * Updates the URL query string.
 * @param {string} verse
 */
function updateQuery(verse) {
  const queryParams = new URLSearchParams(window.location.search);
  queryParams.set('verse', verse);
  const state = {
    verse : verse,
  };
  history.pushState(state, verse, '?' + queryParams.toString());
}

/**
 * Initializes the navigation sidebar.
 * @param {string} verse
 */
function initTree(verse) {
  // See https://wwwendt.de/tech/fancytree/demo/#sample-configurator.html.
  $('#tree').fancytree({
    source : {url : '/tree'},
    // Options.
    autoCollapse : true,
    autoScroll : true,
    clickFolderMode : 3,
    debugLevel : 3,
    icon : false,
    selectMode : 1,
    tabindex : '0',
    // Callbacks.
    init : function() { updateTree(verse); },
    activate : function(event, data) {
      updateGraph(data.node.key);
      updateTable(data.node.key);
      updateQuery(data.node.key);
    },
    beforeActivate : function(event, data) {
      if (data.node.isFolder()) {
        return false; // Don't allow selection of parent nodes.
      }
    }
  });
}

/**
 * Updates the selected node in the navigation sidebar.
 * @param {string} verse
 */
function updateTree(verse) {
  const tree = $.ui.fancytree.getTree('#tree');
  const node = tree.getNodeByKey(verse);
  if (node !== null) {
    const options = {
      noEvents : true,
    };
    node.setActive(true, options);
    node.makeVisible(options);
  }
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
 * Initializes the Cytoscape viewer.
 * @param {string} verse
 */
function initGraph(verse) {
  // See https://js.cytoscape.org/#core/initialisation.
  cy = cytoscape({
    container : document.getElementById('cy'),
    elements : getElements(verse),
    style : [
      {
        selector : 'node',
        css : {
          'font-weight' : 'normal',
          'background-opacity' : 1.0,
          'font-size' : 12,
          'background-color' : 'rgb(255,255,255)',
          'border-opacity' : 1.0,
          'text-opacity' : 1.0,
          'text-valign' : 'center',
          'text-halign' : 'center',
          'border-width' : 0.0,
          'border-color' : 'rgb(204,204,204)',
          'shape' : 'roundrectangle',
          'width' : 'label',
          'height' : 'label',
          'padding' : '5px',
          'content' : 'data(id)'
        }
      },
      {
        selector : 'edge',
        css : {
          'width' : 1.0,
          'text-opacity' : 1.0,
          'target-arrow-color' : 'rgb(0,204,255)',
          'line-color' : 'rgb(0,204,255)',
          'source-arrow-color' : 'rgb(0,204,255)',
          'line-style' : 'solid',
          'source-arrow-shape' : 'none',
          'opacity' : 1.0,
          'font-size' : 10,
          'target-arrow-shape' : 'triangle',
          'font-weight' : 'normal',
          'curve-style' : 'straight'
        }
      }
    ],
    layout : {
      name : 'cola',
      animate : false,
    },
    autoungrabify : true,
    boxSelectionEnabled : false,
    userPanningEnabled : false,
    userZoomingEnabled : false,
  });
  cy.on('tap', 'node', function(event) {
    const verse = event.target.id();
    const queryParams = new URLSearchParams(window.location.search);
    if (queryParams.get('verse') !== verse) {
      updateTree(verse);
      updateGraph(verse);
      updateTable(verse);
      updateQuery(verse);
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
    name : 'cola',
    animate : false,
  });
  layout.run();
}

/**
 * Fetches the cross-reference table.
 * @param {string} verse
 */
function getTable(verse) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/table');
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
 * Initializes the cross-reference table.
 * @param {string} verse
 */
async function updateTable(verse) {
  const table = await getTable(verse);
  $('#table').html(table);
}
