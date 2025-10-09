import { checkResponseCode } from "./util.js";

const syncButton = /** @type {HTMLButtonElement} */ (document.getElementById('sync-button'));
const stopButton = /** @type {HTMLButtonElement} */ (document.getElementById('stop-button'));
const table = /** @type {HTMLTableElement} */ (document.getElementById('table'));
const log = /** @type {HTMLTableSectionElement} */ (document.getElementById('log'));
const wait = /** @type {HTMLParagraphElement} */ (document.getElementById('wait'));

const decoder = new TextDecoder();

/**
 * @param {import("./types.js").OfflineSyncLogEntry} entry
 * @returns {HTMLTableRowElement}
 */
function createRow(entry) {
    if (!entry.task) throw new Error("this method does not handle all_done")
    const tdTask = document.createElement('td');
    tdTask.textContent = entry.task;
    const tdIcon = document.createElement('td');
    if (entry.state == "done") {
        tdIcon.classList.add('icon', 'icon-check', 'icon-col');
    } else if (entry.state == "start") {
        tdIcon.classList.add('icon', 'icon-loading', 'spinning', 'icon-col');
    } else if (entry.state == "error") {
        tdIcon.classList.add('icon', 'icon-close', 'icon-col');
    }
    const row = document.createElement('tr');
    row.dataset.task = entry.task;
    row.append(tdTask, tdIcon);
    return row;
}

/**
 * @param {string} rawEntry
 */
function handleEntry(rawEntry) {
    console.debug('offline_sync: received value', rawEntry);

    if (rawEntry == "stopped") {
        syncButton.hidden = false;
        stopButton.hidden = true;
        wait.hidden = true;
        return;
    } else if (rawEntry == "running") {
        syncButton.hidden = true;
        stopButton.hidden = false;
        return;
    }

    table.hidden = false;
    wait.hidden = true;

    const entry = /** @type {import("./types.js").OfflineSyncLogEntry} */ (JSON.parse(rawEntry));
    if (entry.state == "all_done") {
        console.info('offline_sync: all done');
        // All done, any loading icons should be replaced by stop icon
        for (const elem of document.querySelectorAll('.icon-loading')) {
            elem.classList.remove('icon-loading', 'spinning');
            elem.classList.add('icon-close');
        }
    } else if (entry.state == "error") {
        console.info('offline_sync: error:', entry.task);
        for (const row of log.children) {
            if (row.dataset.task == entry.task) {
                row.replaceWith(createRow(entry));
            }
        }
    } else if (entry.state == "done") {
        console.info('offline_sync: done:', entry.task);
        // Task done
        // Remove loading row
        for (const row of log.children) {
            if (row.dataset.task == entry.task) {
                row.remove();
                break;
            }
        }

        // Insert done row after last loading row
        let lastLoadingRow = null;
        for (const row of log.children) {
            if (row.querySelector("td:nth-child(2)").classList.contains('icon-loading')) {
                lastLoadingRow = row;
            } else {
                break;
            }
        }
        const doneRow = createRow(entry);
        if (lastLoadingRow) {
            lastLoadingRow.after(doneRow);
        } else {
            log.prepend(doneRow);
        }
    } else if (entry.state == "start") {
        console.info('offline_sync: start:', entry.task);
        // Task start
        log.prepend(createRow(entry));

        if (log.children.length > 100) {
            log.children.item(log.children.length - 1).remove();
        }
    } else {
        console.warn('offline_sync: unknown state:', entry.state);
    }
}

/**
 * @param {ReadableStreamReadResult<Uint8Array<ArrayBufferLike>>} result
 */
async function handleResponse(result) {
    const values = decoder.decode(result.value);
    for (const value of values.split('\n')) {
        if (value) {
            handleEntry(value);
        }
    }
    return result;
}

syncButton.addEventListener('click', async () => {
    const response = await fetch('/offline/start', { method: 'POST' });
    checkResponseCode(response);
});

stopButton.addEventListener('click', async () => {
    const response = await fetch('/offline/stop', { method: 'POST' });
    checkResponseCode(response);
});

async function monitor() {
    try {
        const response = await fetch('/offline/monitor', { method: 'GET' });
        checkResponseCode(response);
        if (response.body == null) throw new Error();
        const reader = response.body.getReader();
        let result;
        while (!(result = await reader.read()).done) {
            await handleResponse(result);
        }
    } finally {
        wait.hidden = false; // status is not known
        setTimeout(monitor, 1000);
    }
}

monitor();
