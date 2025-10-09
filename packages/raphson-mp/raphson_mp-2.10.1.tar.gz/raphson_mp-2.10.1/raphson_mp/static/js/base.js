// Base script included by all pages

import { durationToString, timestampToString, sendErrorReport } from "./util.js";

// Replace timestamp by formatted time string
(() => {
    for (const elem of document.getElementsByClassName('format-timestamp')) {
        if (!(elem instanceof HTMLElement) || elem.textContent == null) {
            continue;
        }
        elem.dataset.sort = elem.textContent;
        elem.textContent = timestampToString(parseInt(elem.textContent));
    }

    for (const elem of document.getElementsByClassName('format-duration')) {
        if (!(elem instanceof HTMLElement) || elem.textContent == null) {
            continue;
        }
        elem.dataset.sort =  elem.textContent;
        elem.textContent = durationToString(parseInt(elem.textContent));
    }
})();

window.addEventListener("error", sendErrorReport);
window.addEventListener("unhandledrejection", sendErrorReport);

// Table sorting
{
    /**
     * @param {HTMLTableSectionElement} tbody
     * @param {number} columnIndex
     */
    function sort(tbody, columnIndex) {
        // if the same column is clicked for a second time, sort in reverse
        const mod = tbody.currentSort == columnIndex ? -1 : 1;
        tbody.currentSort = mod == -1 ? undefined : columnIndex;
        console.info("sorting table by column", columnIndex, "order", mod);

        [...tbody.children]
            .sort((row1, row2) => {
                const a = /** @type {HTMLElement} */ (row1.children[columnIndex]);
                const b = /** @type {HTMLElement} */ (row2.children[columnIndex]);
                if (a.textContent == null || b.textContent == null) throw Error();
                const aVal = 'sort' in a.dataset ? parseInt(/** @type {string} */ (a.dataset.sort)) : a.textContent;
                const bVal = 'sort' in b.dataset ? parseInt(/** @type {string} */ (b.dataset.sort)) : b.textContent;
                return mod * (aVal > bVal ? 1 : -1);
            })
            .forEach(row => tbody.appendChild(row));
        // interesting behaviour of appendChild: if the node already exists, it is moved from its original location
    }

    for (const tempTable of document.querySelectorAll(".table")) {
        const table = tempTable;
        const thead = /** @type {HTMLTableSectionElement} */ (table.children[0]);
        const tbody = /** @type {HTMLTableSectionElement} */ (table.children[1]);

        if (thead.tagName != "THEAD" || tbody.tagName != "TBODY") {
            console.warn("ignoring invalid table", table);
            continue;
        }

        const tr = thead.children[0];
        for (let i = 0; i < tr.children.length; i++) {
            const columnIndex = i;
            const td = tr.children[i]
            if (!(td instanceof HTMLTableCellElement)) throw new Error();
            td.addEventListener("click", () => {
                sort(tbody, columnIndex)
            });
            td.style.cursor = 'pointer';
        }
    }
};

// Page close button
const closeButton = document.getElementById('page-heading-close');
if (closeButton) {
    if (window.opener == null) {
        // Closing not possible
        closeButton.remove();
    }

    closeButton.addEventListener('click', () => {
        window.close();
    });
}
