import { windows } from "./window.js";
import { eventBus, MusicEvent } from "./event.js";
import { Track } from "../api.js";
import { createToast, vars } from "../util.js";

class Editor {
    #saveButton = /** @type {HTMLButtonElement} */ (document.getElementById("editor-save"));
    #lookupButton = /** @type {HTMLButtonElement} */ (document.getElementById("editor-lookup"));
    #lookupNoResult = /** @type {HTMLTableElement} */ (document.getElementById("editor-lookup-no-result"));
    #lookupResultContainer = /** @type {HTMLTableElement} */ (document.getElementById("editor-lookup-result"));
    #lookupResultAcoustid = /** @type {HTMLAnchorElement} */ (document.getElementById("editor-lookup-acoustid"));
    #lookupResultTable = /** @type {HTMLTableSectionElement} */ (document.getElementById("editor-lookup-tbody"));
    #writingElem = /** @type {HTMLParagraphElement} */ (document.getElementById('editor-writing'));
    /** @type {Track | null} */
    #track = null;

    constructor() {
        this.#saveButton.addEventListener('click', () => this.#save());
        this.#lookupButton.addEventListener('click', () => this.#auto());
    };

    /**
     * Populate input fields and show metadata editor window
     * @param {Track} track
     */
    open(track) {
        if (track == null) {
            throw new Error('Track is null');
        }
        this.#track = track;
        this.#trackToHtml();

        this.#lookupNoResult.hidden = true;
        this.#lookupResultContainer.hidden = true;
        this.#lookupButton.hidden = false;

        // Make editor window window visible, and bring it to the top
        windows.open('window-editor');
    };

    /**
     * @param {string} id
     * @returns {string | null} Value of HTML input with the given id.
     */
    #getValue(id) {
        let value = /** @type {HTMLInputElement} */ (document.getElementById(id)).value;
        value = value.trim();
        return value === '' ? null : value;
    };

    /**
     * @param {string} id
     * @returns {Array<string>}
     */
    #getArrayValue(id) {
        let value = /** @type {HTMLInputElement} */ (document.getElementById(id)).value;
        const array = [];
        for (const item of value.split(';')) {
            const trimmed = item.trim();
            if (trimmed) {
                array.push(trimmed);
            }
        }
        return array;
    }

    /**
     * @param {string} id
     * @param {string | Array<string> | null} value
     */
    #setValue(id, value) {
        if (value == null) {
            value = '';
        } else if (value instanceof Array) {
            value = value.join('; ');
        }
        /** @type {HTMLInputElement} */ (document.getElementById(id)).value = value;
    }

    /**
     * Copy content from track object variables to HTML input fields
     */
    #trackToHtml() {
        if (!this.#track) {
            throw new Error();
        }
        this.#setValue('editor-path', this.#track.path);
        this.#setValue('editor-title', this.#track.title);
        this.#setValue('editor-album', this.#track.album);
        this.#setValue('editor-artists', this.#track.artists);
        this.#setValue('editor-album-artist', this.#track.albumArtist);
        this.#setValue('editor-tags', this.#track.tags);
        this.#setValue('editor-year', this.#track.year ? this.#track.year + '' : null);
        this.#setValue('editor-number', this.#track.trackNumber ? this.#track.trackNumber + '' : null);
        this.#setValue('editor-lyrics', this.#track.lyrics);
    }

    /**
     * Copy content from input fields to track object
     */
    #htmlToTrack() {
        if (!this.#track) {
            throw new Error();
        }
        this.#track.title = this.#getValue('editor-title');
        this.#track.album = this.#getValue('editor-album');
        this.#track.artists = this.#getArrayValue('editor-artists');
        this.#track.albumArtist = this.#getValue('editor-album-artist');
        this.#track.tags = this.#getArrayValue('editor-tags');
        const yearStr = this.#getValue('editor-year');
        this.#track.year = yearStr ? parseInt(yearStr) : null;
        const numberStr = this.#getValue('editor-number');
        this.#track.trackNumber = numberStr ? parseInt(numberStr) : null;
        this.#track.lyrics = this.#getValue('editor-lyrics');
    }

    /**
     * Save metadata and close metadata editor window
     */
    async #save() {
        if (this.#track == null) {
            throw new Error();
        }
        this.#htmlToTrack();

        // Loading text
        this.#saveButton.hidden = true;
        this.#writingElem.hidden = false;

        // Make request to update metadata
        try {
            await this.#track.saveMetadata();
        } catch (e) {
            alert('An error occurred while updating metadata.');
            return;
        } finally {
            this.#writingElem.hidden = true;
            this.#saveButton.hidden = false;
        }

        // Close window, and restore save button
        windows.close('window-editor');

        // Music player should update all track-related HTML with new metadata. This event must be
        // fired after the editor window is closed, so other windows can check whether they are open.
        eventBus.publish(MusicEvent.METADATA_CHANGE, this.#track);

        this.#track = null;
    };

    async #auto() {
        if (!this.#track) {
            throw new Error();
        }

        this.#lookupButton.hidden = true;
        this.#lookupResultContainer.hidden = true;
        this.#lookupNoResult.hidden = true;

        try {
            const result = await this.#track.acoustid();

            if (!result) {
                this.#lookupNoResult.hidden = false;
                return;
            }

            const rows = [];
            for (const release of result.releases) {
                const tdTitle = document.createElement('td');
                tdTitle.textContent = release.title;
                const tdArtist = document.createElement('td');
                tdArtist.textContent = release.artists.join(', ');
                const tdAlbum = document.createElement('td');
                tdAlbum.textContent = release.album;
                const tdYear = document.createElement('td');
                tdYear.textContent = release.year + '';
                const tdType = document.createElement('td');
                tdType.textContent = release.release_type;
                const tdPackaging = document.createElement('td');
                tdPackaging.textContent = release.packaging;
                const row = document.createElement('tr');
                row.append(tdTitle, tdArtist, tdAlbum, tdYear, tdType, tdPackaging);

                // Click a row to auto fill metadata
                row.style.cursor = 'pointer';
                row.addEventListener('click', () => {
                    this.#setValue('editor-title', release.title);
                    this.#setValue('editor-artists', release.artists);
                    this.#setValue('editor-album', release.album);
                    this.#setValue('editor-album-artist', release.album_artist);
                    this.#setValue('editor-year', release.year + '');
                });

                rows.push(row);
            }

            this.#lookupResultTable.replaceChildren(...rows);
            this.#lookupResultAcoustid.href = 'https://acoustid.org/track/' + result.acoustid;
            this.#lookupResultContainer.hidden = false;
        } catch (ex) {
            createToast('close', vars.tFingerprintFailed);
            console.warn(ex);
        } finally {
            this.#lookupButton.hidden = false;
        }
    }

};

export const editor = new Editor();
