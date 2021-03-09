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

/**
 * Initializes the navigation sidebar.
 * @param {string} verse
 */
function initTree(verse) {
    // See https://wwwendt.de/tech/fancytree/demo/#sample-configurator.html.
    $('#tree').fancytree({
        source: {url: '/tree'},
        // Options.
        autoCollapse: true,
        autoScroll: true,
        clickFolderMode: 3,
        debugLevel: 3,
        icon: false,
        selectMode: 1,
        tabindex: '0',
        // Callbacks.
        init: function(event, data) {
            updateTree(verse);
        },
        activate: function(event, data) {
            updateGraph(data.node.key);
            updateTable(data.node.key);
        },
        beforeActivate: function(event, data) {
            if (data.node.isFolder()) {
                return false;  // Don't allow selection of parent nodes.
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
        node.setActive();
        node.makeVisible();
    }
}
