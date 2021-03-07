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
 * Fetches the cross-reference table.
 * @param {string} verse
 */
function getTable(verse) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/table');
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
 * Initializes the cross-reference table.
 * @param {string} verse
 */
async function updateTable(verse) {
    const table = await getTable(verse);
    $('#table').html(table);
}
