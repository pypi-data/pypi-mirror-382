import { controlChannel, ControlCommand, ControlTopic, Track } from "./api.js";
import { initNowPlayingCards } from "./now_playing.js";
import { vars, timestampToString } from "./util.js";

/**
 * @param {Array<string>} contents
 * @returns
 */
function createTableRow(contents) {
    const row = document.createElement('tr');
    for (const content of contents) {
        const col = document.createElement('td');
        col.textContent = content;
        row.append(col);
    }
    return row;
}

/**
 * @param {import("./types").ControlServerPlayed} data
 * @returns {HTMLTableRowElement}
 */
function getHistoryRowHtml(data) {
    const track = new Track(data.track);
    return createTableRow([timestampToString(data.played_time), data.username, track.playlistName, track.displayText(false)]);
}

/**
 * @param {import("./types").ControlServerFileChange} data
 * @returns {HTMLTableRowElement}
 */
function getFileChangeRowHtml(data) {
    let text;
    if (data.action == "insert") {
        text = vars.tActivityFileAdded;
    } else if (data.action == "delete") {
        text = vars.tActivityFileDeleted;
    } else if (data.action == "update") {
        text = vars.tActivityFileModified;
    } else if (data.action == "move") {
        text = vars.tActivityFileMoved;
    } else {
        throw new Error("unexpected file action: " + data.action);
    }
    return createTableRow([timestampToString(data.change_time), data.username ? data.username : "", text, data.track]);
}

const nowPlayingDiv = /** @type {HTMLDivElement} */ (document.getElementById('now-playing'));
const historyTable = /** @type {HTMLTableSectionElement} */ (document.getElementById('tbody-history'));
const fileChangesTable = /** @type {HTMLTableSectionElement} */ (document.getElementById('tbody-changes'));

initNowPlayingCards(nowPlayingDiv, true);

/**
 * @param {import("./types").ControlServerPlayed} data
 */
function playedHandler(data) {
    historyTable.prepend(getHistoryRowHtml(data));
    while (historyTable.children.length > 10) {
        historyTable.children[historyTable.children.length - 1].remove();
    }
}
controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYED, playedHandler);

/**
 * @param {import("./types").ControlServerFileChange} data
 */
function fileChangeHandler(data) {
    fileChangesTable.prepend(getFileChangeRowHtml(data));
    while (fileChangesTable.children.length > 10) {
        fileChangesTable.children[fileChangesTable.children.length - 1].remove();
    }
}
controlChannel.registerMessageHandler(ControlCommand.SERVER_FILE_CHANGE, fileChangeHandler);

controlChannel.subscribe(ControlTopic.FILES);
controlChannel.subscribe(ControlTopic.PLAYING);
