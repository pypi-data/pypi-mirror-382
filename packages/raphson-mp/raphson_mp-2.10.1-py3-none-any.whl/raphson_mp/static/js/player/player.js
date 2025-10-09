import { eventBus, MusicEvent } from "./event.js";
import { trackDisplayHtml } from "./track.js";
import { queue } from "./queue.js";
import { controlChannel, ControlCommand, music, Track } from "../api.js";
import { clamp, durationToString, vars, TRANSITION_DURATION, createToast, removeToast } from "../util.js";
import { windows } from "./window.js";
import { editor } from "./editor.js";
import { PlaylistCheckboxes } from "../playlistcheckboxes.js";
import { playerSync } from "./control.js";
import { getImageQuality, setSettingValue, Setting } from "./settings.js";

class Player {
    audioElement = /** @type {HTMLAudioElement} */ (document.getElementById("audio"));
    #audioContext = /** @type {AudioContext | null} */ (null);
    #gainNode = /** @type {GainNode | null} */ (null);
    fftSize = 2 ** 13; // used by visualiser
    analyser = /** @type {AnalyserNode | null} */ (null); // used by visualiser

    constructor() {
        this.audioElement.addEventListener('play', () => eventBus.publish(MusicEvent.PLAYER_PLAY));
        this.audioElement.addEventListener('pause', () => eventBus.publish(MusicEvent.PLAYER_PAUSE));
        this.audioElement.addEventListener('timeupdate', () => eventBus.publish(MusicEvent.PLAYER_POSITION));
        this.audioElement.addEventListener('durationchange', () => eventBus.publish(MusicEvent.PLAYER_DURATION));
        this.audioElement.addEventListener('seeked', () => eventBus.publish(MusicEvent.PLAYER_SEEK));
        this.audioElement.addEventListener('ended', () => {
            if (playerSync != null) {
                // When following another player, that player is responsible for going to the next track. If we also
                // go to the next track, occasionally we will go to the next track twice.
                return;
            }
            queue.next();
        });

        // Audio element should always be playing at max volume
        // Volume is set using GainNode
        this.audioElement.volume = 1;

        Setting.AUDIO_GAIN.addEventListener('change', () => this.applyVolume());

        eventBus.subscribe(MusicEvent.TRACK_CHANGE, async () => {
            if (!queue.currentTrack) throw new Error();
            const audioUrl = queue.currentTrack.getAudioURL(Setting.AUDIO_TYPE.value);
            this.audioElement.src = audioUrl;
            this.play(true);
        });

        // Can only create AudioContext once media is playing
        eventBus.subscribe(MusicEvent.PLAYER_PLAY, () => {
            if (this.#audioContext) {
                return;
            }
            console.debug('audiocontext: create');
            this.#audioContext = new AudioContext();
            const source = this.#audioContext.createMediaElementSource(this.audioElement);
            this.analyser = this.#audioContext.createAnalyser();
            this.analyser.fftSize = this.fftSize;
            this.#gainNode = this.#audioContext.createGain();
            this.applyVolume(); // If gain or volume was changed while audio was still paused
            source.connect(this.analyser);
            source.connect(this.#gainNode);
            this.#gainNode.connect(this.#audioContext.destination);
        });

        // Safari
        if (this.audioElement.canPlayType("audio/webm;codecs=opus") != "probably") {
            alert("WEBM/OPUS audio not supported by your browser. Please update your browser or use a different browser.");
        }
    }

    isPaused() {
        return this.audioElement.paused;
    }

    async play(local = false) {
        if (!local && playerSync != null) {
            // Send action to remote player, but for responsiveness also immediately start playing locally
            controlChannel.sendMessage(ControlCommand.CLIENT_PLAY, {"player_id": playerSync});
        }

        try {
            await this.audioElement.play();
            removeToast(vars.tAutoPlayBlocked);
        } catch (err) {
            if (err instanceof Error && err.name == "NotAllowedError") {
                createToast("play", vars.tAutoPlayBlocked);
            }
        }
    }

    pause(local = false) {
        if (!local && playerSync != null) {
            // Send action to remote player, but for responsiveness also immediately pause locally
            controlChannel.sendMessage(ControlCommand.CLIENT_PAUSE, {"player_id": playerSync});
        }

        return this.audioElement.pause();
    }

    getDuration() {
        return isFinite(this.audioElement.duration) && !isNaN(this.audioElement.duration) ? this.audioElement.duration : null;
    }

    getPosition() {
        return isFinite(this.audioElement.currentTime) && !isNaN(this.audioElement.currentTime) ? this.audioElement.currentTime : null;
    }

    /**
     * @param {number} position
     */
    seek(position, local = false) {
        if (!local && playerSync != null) {
            controlChannel.sendMessage(ControlCommand.CLIENT_SEEK, {"player_id": playerSync, position: position});
            return;
        }

        if (!isFinite(position) || isNaN(position)) {
            return;
        }
        this.audioElement.currentTime = position;
    }

    /**
     * @param {number} delta number of seconds to seek forwards, negative for backwards
     * @returns {void}
     */
    seekRelative(delta) {
        const position = this.getPosition();
        const duration = this.getDuration();
        if (position === null || !duration) return;
        const newTime = position + delta;
        if (newTime < 0) {
            this.seek(0);
        } else if (newTime > duration) {
            this.seek(duration);
        } else {
            this.seek(newTime);
        }
    }

    /**
     * Apply gain and volume changes
     */
    applyVolume() {
        // If gain node is available, we can immediately set the gain
        // Otherwise, the 'play' event listener will call this method again
        if (!this.#gainNode || !this.#audioContext) {
            console.debug('audiocontext: gainNode not available yet');
            return;
        }
        const gain = parseInt(Setting.AUDIO_GAIN.value);
        const volume = this.#getTransformedVolume();
        console.debug('audiocontext: set gain:', gain, volume, gain * volume);
        // exponential function cannot handle 0 value, so clamp to tiny minimum value instead
        this.#gainNode.gain.exponentialRampToValueAtTime(Math.max(gain * volume, 0.0001), this.#audioContext.currentTime + 0.1);
    }

    #getTransformedVolume() {
        // https://www.dr-lex.be/info-stuff/volumecontrols.html
        return Math.pow(playerControls.getVolume(), 3);
    }
}

export const player = new Player();

class PlayerControls {
    #seekBar = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar'));
    #textPosition = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-position'));
    #textDuration = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-duration'));

    constructor() {
        this.#initSeekBar();
        this.#initHomeButton();
        this.#initSkipButtons();
        this.#initPlayPauseButtons();
        if (!vars.offlineMode) {
            this.#initFileActionButtons();
            this.#initWebButton();
        }
        this.#initVolume();
        eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => this.#replaceAlbumImages());
        eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => this.#replaceTrackDisplayTitle());
        eventBus.subscribe(MusicEvent.METADATA_CHANGE, (/** @type {Track} */ updatedTrack) => {
            if (queue.currentTrack
                && queue.currentTrack.path == updatedTrack.path) {
                console.debug('player: updating currently playing display title following METADATA_CHANGE event');
                this.#replaceTrackDisplayTitle();
            }
        });
    }

    /**
     * @returns {number} volume 0.0-1.0
     */
    getVolume() {
        return parseInt(Setting.VOLUME.value) / 100.0;
    }

    /**
     * @param {number} volume volume 0.0-1.0
     */
    setVolume(volume) {
        setSettingValue(Setting.VOLUME, clamp(Math.round(volume * 100), 0, 100) + '');
    }

    #updateSeekBar() {
        // Save resources updating seek bar if it's not visible
        if (document.visibilityState != 'visible') {
            return;
        }

        const position = player.getPosition();
        const duration = player.getDuration();
        let barCurrent;
        let barDuration;
        let barWidth;

        if (position != null && duration != null) {
            barCurrent = durationToString(Math.round(position));
            barDuration = durationToString(Math.round(duration));
            barWidth = ((position / duration) * 100);
        } else {
            barCurrent = vars.tLoading;
            barDuration = '';
            barWidth = 0;
        }

        requestAnimationFrame(() => {
            this.#textPosition.textContent = barCurrent;
            this.#textDuration.textContent = barDuration;
            // Previously, the seek bar used an inner div with changing width. However, that causes an expensive
            // layout update. Instead, set a background gradient which is nearly free to update.
            this.#seekBar.style.background = `linear-gradient(90deg, var(--seek-bar-color) ${barWidth}%, var(--background-color) 0%)`;
        });
    }

    #initSeekBar() {
        const doSeek = (/** @type {MouseEvent} */ event) => {
            const duration = player.getDuration();
            if (!duration) return;

            const relativePosition = ((event.clientX - this.#seekBar.offsetLeft) / this.#seekBar.offsetWidth);
            if (relativePosition < 0 || relativePosition > 1) {
                // user has moved outside of seekbar, stop seeking
                document.removeEventListener('mousemove', onMove);
                return;
            }

            const newTime = relativePosition * duration;
            player.seek(newTime);
        };

        const onMove = (/** @type {MouseEvent} */ event) => {
            doSeek(event);
            event.preventDefault(); // Prevent accidental text selection
        };

        const onUp = () => {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };

        this.#seekBar.addEventListener('mousedown', event => {
            doSeek(event);

            // Keep updating while mouse is moving
            document.addEventListener('mousemove', onMove);

            // Unregister events on mouseup event
            document.addEventListener('mouseup', onUp);

            event.preventDefault(); // Prevent accidental text selection
        });

        // Scroll to seek
        this.#seekBar.addEventListener('wheel', event => {
            player.seekRelative(event.deltaY < 0 ? 3 : -3);
        }, { passive: true });

        eventBus.subscribe(MusicEvent.PLAYER_POSITION, () => this.#updateSeekBar());
        eventBus.subscribe(MusicEvent.PLAYER_DURATION, () => this.#updateSeekBar());

        // Seek bar is not updated when page is not visible. Immediately update it when the page does become visible.
        document.addEventListener('visibilitychange', () => this.#updateSeekBar());
    }

    #initHomeButton() {
        const homeButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-home'));
        homeButton.addEventListener('click', () => window.open('/', '_blank'));
    }

    #initSkipButtons() {
        const prevButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-prev'));
        const nextButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-next'));
        prevButton.addEventListener('click', () => queue.previous());
        nextButton.addEventListener('click', () => queue.next());
    }

    #initPlayPauseButtons() {
        const pauseButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-pause'));
        const playButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-play'));

        // Play pause click actions
        pauseButton.addEventListener('click', () => player.pause());
        playButton.addEventListener('click', () => player.play());

        const updateButtons = () => {
            requestAnimationFrame(() => {
                pauseButton.hidden = player.isPaused();
                playButton.hidden = !player.isPaused();
            })
        };

        eventBus.subscribe(MusicEvent.PLAYER_PLAY, updateButtons);
        eventBus.subscribe(MusicEvent.PLAYER_PAUSE, updateButtons);

        // Hide pause button on initial page load, otherwise both play and pause will show
        pauseButton.hidden = true;
    }

    /**
     * Handle presence of buttons that perform file actions: dislike, copy, share, edit, delete
     */
    #initFileActionButtons() {
        const dislikeButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-dislike'));
        const copyButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-copy'));
        const shareButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-share'));
        const problemButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-problem'));
        const editButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-edit'));
        const deleteButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-delete'));

        const requiresRealTrack = [dislikeButton, copyButton, shareButton, problemButton];
        const requiresWriteAccess = [editButton, deleteButton];

        async function updateButtons() {
            requestAnimationFrame(() => {
                for (const button of requiresRealTrack) {
                    button.hidden = !queue.currentTrack || queue.currentTrack.isVirtual();
                }

                const hasWriteAccess = queue.currentTrack
                        && !queue.currentTrack.isVirtual()
                        && (music.playlist(queue.currentTrack.playlistName)).write;
                for (const button of requiresWriteAccess) {
                    button.hidden = !hasWriteAccess;
                }
            });
        }

        eventBus.subscribe(MusicEvent.TRACK_CHANGE, updateButtons);

        // Hide all buttons initially
        for (const button of [...requiresRealTrack, ...requiresWriteAccess]) {
            button.hidden = true;
        }

        // Dislike button
        dislikeButton.addEventListener('click', async () => {
            if (queue.currentTrack && !queue.currentTrack.isVirtual()) {
                await queue.currentTrack.dislike();
                queue.next();
            } else {
                throw new Error();
            }
        });

        // Copy button
        const copyTrack = /** @type {HTMLButtonElement} */ (document.getElementById('copy-track'));
        const copyPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('copy-playlist'));
        const copyDoButton = /** @type {HTMLButtonElement} */ (document.getElementById('copy-do-button'));
        copyButton.addEventListener('click', () => {
            if (!queue.currentTrack || queue.currentTrack.isVirtual()) {
                throw new Error();
            }
            copyTrack.value = queue.currentTrack.path;
            windows.open('window-copy');
        });
        copyDoButton.addEventListener('click', async () => {
            if (!queue.currentTrack) throw new Error();
            if (copyPlaylist.value == '') return;
            copyDoButton.disabled = true;
            try {
                await queue.currentTrack.copyTo(copyPlaylist.value);
            } catch (err) {
                console.error(err);
                alert('Error: ' + err);
            }
            windows.close('window-copy');
            copyDoButton.disabled = false;
        });

        // Share button is handled by share.js

        // Problem button
        problemButton.addEventListener('click', async () => {
            if (queue.currentTrack) {
                await queue.currentTrack.reportProblem();
                createToast('alert-circle', vars.tTrackProblemReported);
            }
        })

        // Edit button
        editButton.addEventListener('click', () => {
            if (queue.currentTrack) {
                editor.open(queue.currentTrack);
            }
        });

        // Delete button
        const deleteSpinner = /** @type {HTMLDivElement} */ (document.getElementById('delete-spinner'));
        deleteButton.addEventListener('click', async () => {
            if (!queue.currentTrack) {
                return;
            }
            deleteSpinner.hidden = false;
            await queue.currentTrack.delete();
            queue.next();
            deleteSpinner.hidden = true;
        });
    }

    #initWebButton() {
        const addButton = /** @type {HTMLButtonElement} */ (document.getElementById('online-add'));
        const urlInput = /** @type {HTMLInputElement} */ (document.getElementById('online-url'));

        addButton.addEventListener('click', async () => {
            windows.close('window-online');
            alert('TODO');
            // const track = await music.downloadTrackFromWeb(urlInput.value);
            // queue.add(track, true);
        });
    }

    #updateVolumeIcon() {
        const volume = parseInt(Setting.VOLUME.value);
        requestAnimationFrame(() => {
            Setting.VOLUME.classList.remove('input-volume-high', 'input-volume-medium', 'input-volume-low');
            if (volume > 60) {
                Setting.VOLUME.classList.add('input-volume-high');
            } else if (volume > 30) {
                Setting.VOLUME.classList.add('input-volume-medium');
            } else {
                Setting.VOLUME.classList.add('input-volume-low');
            }
        });
    }

    #initVolume() {
        // Unfocus after use so arrow hotkeys still work for switching tracks
        Setting.VOLUME.addEventListener('mouseup', () => Setting.VOLUME.blur());

        // Respond to volume button changes
        // Event fired when input value changes, also manually when code changes the value
        Setting.VOLUME.addEventListener('change', () => {
            this.#updateVolumeIcon();
            player.applyVolume();
        });
        // Also respond to input event, so volume changes immediately while user is dragging slider
        Setting.VOLUME.addEventListener('input', () => Setting.VOLUME.dispatchEvent(new Event('change')));
        // Set icon on page load
        this.#updateVolumeIcon();

        // Scroll to change volume
        Setting.VOLUME.addEventListener('wheel', event => {
            this.setVolume(this.getVolume() + (event.deltaY < 0 ? 0.05 : -0.05));
        }, { passive: true });
    }

    #replaceAlbumImages() {
        if (!queue.currentTrack) throw new Error();
        const track = queue.currentTrack;
        const imageUrl = track.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);
        const cssUrl = `url("${imageUrl}")`;

        const bgBottom = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-1'));
        const bgTop = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-2'));
        const fgBottom = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-1'));
        const fgTop = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-2'));

        // Set bottom to new image
        bgBottom.style.backgroundImage = cssUrl;
        fgBottom.style.backgroundImage = cssUrl;

        // Slowly fade out old top image
        bgTop.style.opacity = '0';
        fgTop.style.opacity = '0';

        setTimeout(() => {
            // To prepare for next replacement, move bottom image to top image
            bgTop.style.backgroundImage = cssUrl;
            fgTop.style.backgroundImage = cssUrl;
            // Make it visible
            bgTop.style.opacity = '1';
            fgTop.style.opacity = '1';
        }, TRANSITION_DURATION);
    }

    #replaceTrackDisplayTitle() {
        if (!queue.currentTrack) throw new Error();
        const track = queue.currentTrack;
        const currentTrackElem = /** @type {HTMLSpanElement} */ (document.getElementById('current-track'));
        currentTrackElem.replaceChildren(trackDisplayHtml(track, true));
        document.title = track.displayText();
    }
}

export const playerControls = new PlayerControls();

const PRIMARY_PLAYLIST = /** @type {HTMLDivElement} */ (document.getElementById('primary-playlist')).textContent;

/**
 * @param {boolean} onlyWritable
 */
export function createPlaylistDropdown(onlyWritable) {
    const select = document.createElement('select');

    for (const playlist of music.playlists()) {
        if (onlyWritable && !playlist.write) continue;
        const option = document.createElement('option');
        option.value = playlist.name;
        option.textContent = playlist.name;
        select.appendChild(option);
    }

    select.value = PRIMARY_PLAYLIST;
    return select;
}

function updatePlaylistDropdowns() {
    console.debug('playlist: updating dropdowns');

    const selects = /** @type {HTMLCollectionOf<HTMLSelectElement>} */ (document.getElementsByClassName('playlist-select'));
    for (const select of selects) {
        const previousValue = select.value;
        const newSelect = createPlaylistDropdown(select.classList.contains('playlist-select-writable'));
        select.replaceChildren(...newSelect.children);
        select.value = previousValue ? previousValue : PRIMARY_PLAYLIST;
    }
}

const checkboxesParent = /** @type {HTMLDivElement} */ (document.getElementById('playlist-checkboxes'));
const onPlaylistChange = () => eventBus.publish(MusicEvent.PLAYLIST_CHANGE);
export const playlistCheckboxes = new PlaylistCheckboxes(checkboxesParent, onPlaylistChange)

export async function updatePlaylists() {
    await music.loadPlaylists();
    updatePlaylistDropdowns();
    playlistCheckboxes.createPlaylistCheckboxes();
}

updatePlaylists();
