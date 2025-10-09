import { createIconButton, vars } from "./util.js";

const UPLOAD_FILES_BUTTON = document.getElementById('upload-files-button');
const UPLOAD_FILES_FORM = document.getElementById('upload-files-form');
const CREATE_DIRECTORY_BUTTON = document.getElementById('create-directory-button');
const CREATE_DIRECTORY_FORM = document.getElementById('create-directory-form');
const FILES_TBODY = /** @type {HTMLTableSectionElement} */ (document.getElementById("tbody"));

if (UPLOAD_FILES_BUTTON && UPLOAD_FILES_FORM) {
    UPLOAD_FILES_BUTTON.addEventListener('click', () => {
        UPLOAD_FILES_BUTTON.setAttribute("disabled", "");
        UPLOAD_FILES_FORM.hidden = false;
    });
}

if (CREATE_DIRECTORY_BUTTON && CREATE_DIRECTORY_FORM) {
    CREATE_DIRECTORY_BUTTON.addEventListener('click', () => {
        CREATE_DIRECTORY_BUTTON.setAttribute("disabled", "");
        CREATE_DIRECTORY_FORM.hidden = false;
    });
}

/**
 * @param {HTMLButtonElement} button
 * @returns {HTMLTableDataCellElement}
 */
function tdIconButton(button) {
    const td = document.createElement("td");
    td.classList.add('button-col');
    td.append(button);
    return td;
}

for (const tr of FILES_TBODY.children) {
    if (!(tr instanceof HTMLTableRowElement)) continue;

    const path = tr.dataset.path;
    if (!path) throw new Error("path missing from dataset");

    const name = path.split("/").slice(-1)[0];

    // download button
    const downloadButton = createIconButton('download');
    downloadButton.addEventListener('click', () => {
        window.open('/files/download?path=' + encodeURIComponent(path));
    });
    tr.append(tdIconButton(downloadButton));

    // presence of upload button means user has write permissions
    if (UPLOAD_FILES_BUTTON) {
        // rename button
        const renameButton = createIconButton('rename-box');
        renameButton.addEventListener('click', () => {
            window.location.assign('/files/rename?path=' + encodeURIComponent(path));
        });
        tr.append(tdIconButton(renameButton));

        // trash or restore button
        const isTrash = window.location.href.endsWith("&trash"); // TODO properly examine query string
        const trashButton = createIconButton(isTrash ? 'delete-restore' : 'delete');
        trashButton.addEventListener('click', async () => {
            const formData = new FormData();
            formData.append("csrf", vars.csrfToken);
            formData.append("path", path);
            formData.append("new-name", isTrash ? name.substring(".trash.".length) : `.trash.${name}`);
            await fetch('/files/rename', {method: 'POST', body: formData});
            location.reload();
        });
        tr.append(tdIconButton(trashButton));
    }
}
