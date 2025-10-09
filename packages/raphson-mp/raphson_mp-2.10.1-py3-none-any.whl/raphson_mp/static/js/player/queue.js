import { eventBus, MusicEvent } from "./event.js";
import { choice, durationToString, vars, createToast, prefetch, createIconButton, throttle } from "../util.js";
import { music, Track, controlChannel, ControlCommand } from "../api.js";
import { getTagFilter } from "./tag.js";
import { getImageQuality, Setting } from "./settings.js";
import { trackDisplayHtml } from "./track.js";
import { player, playlistCheckboxes } from "./player.js";
import { playerSync } from "./control.js";

const MAX_HISTORY_SIZE = 25;

/**
 * @param {string | null} currentPlaylist current playlist name
 * @returns {string | null} next playlist name
 */
function getNextPlaylist(currentPlaylist) {
    const playlists = playlistCheckboxes.getActivePlaylists();

    let playlist;

    if (playlists.length === 0) {
        // No one is selected
        console.warn('playlist: no playlists active');
        return null;
    } else if (currentPlaylist === null) {
        // No playlist chosen yet, choose random playlist
        playlist = choice(playlists);
    } else {
        const currentIndex = playlists.indexOf(currentPlaylist);
        if (currentIndex === -1) {
            // Current playlist is no longer active, we don't know the logical next playlist
            // Choose random playlist
            playlist = choice(playlists);
        } else {
            // Choose next playlist in list, wrapping around if at the end
            playlist = playlists[(currentIndex + 1) % playlists.length];
        }
    }

    return playlist;
}

export class QueuedTrack {
    /** @type {Track} */
    track;
    /** @type {boolean} */
    manual;

    /**
     * @param {Track} track
     * @param {boolean} manual
     */
    constructor(track, manual) {
        this.track = track;
        this.manual = manual;
    }
}

class Queue {
    #htmlCurrentQueueSize = /** @type {HTMLSpanElement} */ (document.getElementById("current-queue-size"));
    #htmlQueue = /** @type {HTMLTableElement} */ (document.getElementById("queue"));
    #htmlQueueBox = /** @type {HTMLTableElement} */ (document.getElementById("box-queue"));
    #previousPlaylist = /** @type {string|null} */ (null);
    #playlistOverrides = /** @type {Array<string>} */ ([]);
    previousTracks = /** @type {Array<Track>} */ ([]);
    queuedTracks = /** @type {Array<QueuedTrack>} */ ([]);
    currentTrack = /** @type {Track|null} */ (null);
    #filling = false;
    #fillDelay = 1000;

    constructor() {
        eventBus.subscribe(MusicEvent.METADATA_CHANGE, (/** @type {Track} */ updatedTrack) => {
            for (const queuedTrack of this.queuedTracks) {
                if (queuedTrack.track.path != updatedTrack.path) {
                    continue;
                }

                console.debug('queue: updating track in queue following a METADATA_CHANGE event', updatedTrack.path);
                queuedTrack.track = updatedTrack;
            }

            if (this.currentTrack != null && this.currentTrack.path == updatedTrack.path) {
                this.currentTrack = updatedTrack;
                console.debug('queue: updating current track following a METADATA_CHANGE event', updatedTrack.path);
            }
            // TODO update previousTracks
            eventBus.publish(MusicEvent.QUEUE_CHANGE);
        });

        // When playlist checkboxes are loaded, fill queue
        eventBus.subscribe(MusicEvent.PLAYLIST_CHANGE, () => queue.#fill());

        // Clear queue button
        const clearButton = /** @type {HTMLButtonElement} */ (document.getElementById('queue-clear'));
        clearButton.addEventListener('click', () => queue.clear());

        // Fill queue when size is changed
        Setting.QUEUE_SIZE.addEventListener('change', () => queue.#fill());

        eventBus.subscribe(MusicEvent.QUEUE_CHANGE, () => {
            this.#updateHtml();
            this.#fill();
        });
    };

    /**
     * Add track to queue
     * @param {Track} track
     * @param {boolean} manual True if this track is added manually by the user
     * @param {boolean} top True to add track to top of queue, e.g. for news
     */
    async add(track, manual, top = false) {
        if (!track) throw new Error();
        prefetch(track.getAudioURL(Setting.AUDIO_TYPE.value));
        const queuedTrack = new QueuedTrack(track, manual);
        if (top) {
            // add to top
            this.queuedTracks.unshift(queuedTrack);
        } else {
            if (manual) {
                // are there already manually added tracks?
                if (this.queuedTracks.some(track => track.manual)) {
                    // add after last manually added track
                    const i = this.queuedTracks.map(track => track.manual).lastIndexOf(true);
                    this.queuedTracks.splice(i + 1, 0, queuedTrack);
                } else {
                    // add to top
                    this.queuedTracks.unshift(queuedTrack);
                }
            } else {
                // add to end of queue
                this.queuedTracks.push(queuedTrack);
            }
        }

        eventBus.publish(MusicEvent.QUEUE_CHANGE);
    };


    /**
     * Play given track immediately
     * @param {Track} track
     */
    async playNow(track) {
        // Add current track to history
        if (this.currentTrack !== null) {
            this.previousTracks.push(this.currentTrack);
            // If history exceeded maximum length, remove first (oldest) element
            if (this.previousTracks.length > MAX_HISTORY_SIZE) {
                this.previousTracks.shift();
            }
        }

        // Replace current track with given track
        this.currentTrack = track;
        eventBus.publish(MusicEvent.TRACK_CHANGE);
    }

    /**
     * @param {number} index
     */
    remove(index) {
        const track = this.queuedTracks.splice(index, 1)[0];
        const removalBehaviour = Setting.QUEUE_REMOVAL_BEHAVIOUR.value;
        if (removalBehaviour === 'same') {
            // Add playlist to override array. Next time a track is picked, when #playlistOverrides contains elements,
            // one element is popped and used instead of choosing a random playlist.
            if (track.track instanceof Track) {
                this.#playlistOverrides.push(track.track.playlistName);
            }
        } else if (removalBehaviour !== 'roundrobin') {
            console.warn('queue: unexpected removal behaviour: ' + removalBehaviour);
        }
        eventBus.publish(MusicEvent.QUEUE_CHANGE);
    };

    /**
     * Remove all items from queue
     */
    clear() {
        // keep manually added tracks
        this.queuedTracks = this.queuedTracks.filter(track => track.manual);
        eventBus.publish(MusicEvent.QUEUE_CHANGE);
        createToast('playlist-remove', vars.tQueueCleared);
    }

    #getMinimumSize() {
        let minQueueSize = parseInt(Setting.QUEUE_SIZE.value);
        return isFinite(minQueueSize) ? minQueueSize : 1;
    }

    async #fill() {
        if (playerSync != null) {
            // Adding tracks to queue is handled by control.js
            return;
        }

        if (this.queuedTracks.length >= this.#getMinimumSize()) {
            console.debug('queue: full');
            return;
        }

        if (this.#filling) {
            console.debug('queue: already filling');
            return;
        }

        console.debug('queue: fill');

        try {
            this.#filling = true;

            let playlist;

            if (this.#playlistOverrides.length > 0) {
                playlist = this.#playlistOverrides.pop();
                console.debug('queue: override', playlist);
            } else {
                playlist = getNextPlaylist(this.#previousPlaylist);
                console.debug(`queue: round robin: ${this.#previousPlaylist} -> ${playlist}`);
                this.#previousPlaylist = playlist;
            }

            if (playlist == null) {
                // fill() will be called again when a playlist is enabled
                return;
            }

            await queue.addRandomTrackFromPlaylist(playlist);
            // start next track if there is no current track playing (most likely when the page has just loaded)
            if (this.currentTrack == null) {
                console.info('queue: no current track, call next()');
                this.next();
            }

            this.#fillDelay = 0;
        } catch (error) {
            console.warn('queue: error');
            console.warn(error);
            if (this.#fillDelay < 30000) {
                this.#fillDelay += 1000;
            }
        } finally {
            this.#filling = false;
        }

        // maybe we have more tracks to fill
        setTimeout(() => this.#fill(), this.#fillDelay);
    };

    /**
     * @param {string} playlistName Playlist directory name
     */
    async addRandomTrackFromPlaylist(playlistName) {
        const playlist = music.playlist(playlistName);
        const track = await playlist.chooseRandomTrack(false, getTagFilter());
        this.add(track, false);
    };

    /**
     * Update queue HTML, if #queueChanged is true
     */
    #updateHtml() {
        const rows = /** @type {Array<HTMLElement>} */ ([]);
        let i = 0;
        let totalQueueDuration = 0;
        for (const queuedTrack of this.queuedTracks) {
            const rememberI = i++;

            const track = queuedTrack.track;

            if (track instanceof Track) {
                totalQueueDuration += track.duration;
            }

            const imageUrl = queuedTrack.track.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);

            const coverDiv = document.createElement("div");
            coverDiv.classList.add("box", "queue-cover");
            coverDiv.style.backgroundImage = `url("${imageUrl}")`;
            // previously, clicking on the cover image would remove a track
            // keep this behaviour for a little while
            coverDiv.onclick = () => queue.remove(rememberI);

            // Track title HTML
            const trackDiv = document.createElement('div');
            trackDiv.appendChild(trackDisplayHtml(track, true));

            const deleteElem = createIconButton("playlist-remove");
            deleteElem.classList.add('queue-remove-item');
            deleteElem.onclick = () => queue.remove(rememberI);

            // Add columns to <tr> row and add the row to the table
            const row = document.createElement('div');
            row.classList.add('queue-item', 'flex-vcenter');
            row.dataset.queuePos = rememberI + '';
            row.append(coverDiv, trackDiv, deleteElem);

            rows.push(row);
        }

        this.#htmlCurrentQueueSize.textContent = durationToString(totalQueueDuration);

        // Add events to <tr> elements
        queue.#dragDropTable(rows);

        this.#htmlQueue.replaceChildren(...rows);
    };

    // Based on https://code-boxx.com/drag-drop-sortable-list-javascript/
    /**
     * @param {Array<HTMLElement>} rows
     */
    #dragDropTable(rows) {
        function createLine() {
            const line = document.createElement('div');
            line.style.background = 'var(--background-color-active)';
            line.style.height = '2px';
            line.style.width = '100%';
            return line;
        }

        let current = /** @type {HTMLElement | null} */ (null); // Element that is being dragged
        let line = /** @type {HTMLElement | null} */ (null);

        const determinePosition = (/** @type {number} */ currentPos, /** @type {MouseEvent} */ event) => {
            let targetPos = rows.length - 1;

            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const rect = row.getBoundingClientRect();
                if (currentPos >= i && event.clientY < rect.y + rect.height / 2) {
                    targetPos = i;
                    break;
                } else if (currentPos < i && event.clientY < rect.y + rect.height / 2 + rect.height) {
                    targetPos = i;
                    break;
                }
            }
            console.debug('queue: drop: move from', currentPos, 'to', targetPos);
            return targetPos;
        };

        this.#htmlQueueBox.addEventListener('dragover', event => {
            event.preventDefault();

            if (current == null) {
                return;
            }

            if (line != null) {
                line.remove();
            }

            const currentPos = parseInt(/** @type {string} */(current.dataset.queuePos));
            const targetPos = determinePosition(currentPos, event);

            if (targetPos < currentPos) {
                rows[targetPos].before(line = createLine());
            } else if (targetPos > currentPos) {
                rows[targetPos].after(line = createLine());
            }
        });

        this.#htmlQueueBox.addEventListener('drop', event => {
            event.preventDefault();

            if (current == null) {
                return;
            }

            const currentPos = parseInt(/** @type {string} */(current.dataset.queuePos));
            const targetPos = determinePosition(currentPos, event);

            // Remove current (being dragged) track from queue
            const track = this.queuedTracks.splice(currentPos, 1)[0];
            // Add it to the place it was dropped
            this.queuedTracks.splice(targetPos, 0, track);
            // Now re-render the table
            eventBus.publish(MusicEvent.QUEUE_CHANGE);
            current = null;
        });

        for (let row of rows) {
            row.draggable = true; // Make draggable

            row.ondragstart = () => {
                current = row;
            };
        };
    };

    previous() {
        if (playerSync != null) {
            // Delegate action to remote player
            controlChannel.sendMessage(ControlCommand.CLIENT_PREVIOUS, { "player_id": playerSync });
            return;
        }

        if (!this.currentTrack) {
            return;
        }

        const previousTrack = this.previousTracks.pop();

        // Try to skip to beginning of current track first
        const position = player.getPosition();
        if ((position && position > 15) || previousTrack == undefined) {
            player.seek(0);
            return;
        }

        // Add current track to beginning of queue
        this.add(this.currentTrack, false, true);

        // Replace current track with last track in history
        this.currentTrack = previousTrack;

        eventBus.publish(MusicEvent.TRACK_CHANGE);
    };

    next() {
        if (playerSync != null) {
            // Delegate action to remote player
            controlChannel.sendMessage(ControlCommand.CLIENT_NEXT, { "player_id": playerSync });
            return;
        }

        // Remove first item from queue
        const track = this.queuedTracks.shift();
        if (track == undefined) {
            console.warn('queue: no next track available');
            return;
        }

        // Add current track to history
        if (this.currentTrack !== null) {
            this.previousTracks.push(this.currentTrack);
            // If history exceeded maximum length, remove first (oldest) element
            if (this.previousTracks.length > MAX_HISTORY_SIZE) {
                this.previousTracks.shift();
            }
        }

        // Replace current track with first item from queue
        this.currentTrack = track.track;
        eventBus.publish(MusicEvent.QUEUE_CHANGE);
        eventBus.publish(MusicEvent.TRACK_CHANGE);
    };
};

export const queue = new Queue();

// After first PLAYLIST_CHANGE event (on page load), start listening to clear the queue when playlists are changed.
eventBus.subscribe(MusicEvent.PLAYLIST_CHANGE, () => setTimeout(() => {
    const throttledClear = throttle(2000, false, () => queue.clear());

    eventBus.subscribe(MusicEvent.PLAYLIST_CHANGE, () => {
        if (Setting.AUTO_CLEAR_QUEUE.checked) {
            throttledClear();
        }
    })
}, 0));
