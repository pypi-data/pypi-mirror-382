import { jsonPost } from "./util.js";

const downloadForm = /** @type {HTMLFormElement} */ (document.getElementById('download-form'));
const downloadUrl = /** @type {HTMLInputElement} */ (document.getElementById('download-url'));
const downloadPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('download-playlist'));
const downloadButton = /** @type {HTMLButtonElement} */ (document.getElementById('download-button'));
const downloadLoading = /** @type {HTMLDivElement} */ (document.getElementById('download-loading'));
const downloadLog = /** @type {HTMLTextAreaElement} */ (document.getElementById('download-log'));

downloadForm.addEventListener('submit', async event => {
    event.preventDefault();

    downloadButton.disabled = true;
    downloadLoading.hidden = false;

    downloadLog.style.backgroundColor = '';
    downloadLog.textContent = '';

    const decoder = new TextDecoder();

    /**
     * @param {ReadableStreamReadResult<Uint8Array<ArrayBufferLike>>} result
     */
    function handleResponse(result) {
        console.debug(result.value);
        const text = decoder.decode(result.value);
        console.debug(text);
        downloadLog.textContent += text;
        downloadLog.scrollTop = downloadLog.scrollHeight;
        if (text.endsWith("\nDone\n")) {
            downloadLog.style.backgroundColor = 'var(--background-success)';
        } else if (text.endsWith("\nFailed\n")) {
            downloadLog.style.backgroundColor = 'var(--background-error)';
        }
    }

    try {
        const response = await jsonPost('/download/ytdl', {playlist: downloadPlaylist.value, url: downloadUrl.value});
        if (response.body == null) throw new Error();
        const reader = response.body.getReader();
        let result;
        while (!(result = await reader.read()).done) {
            handleResponse(result);
        }
    } finally {
        downloadButton.disabled = false;
        downloadLoading.hidden = true;
    }
});
