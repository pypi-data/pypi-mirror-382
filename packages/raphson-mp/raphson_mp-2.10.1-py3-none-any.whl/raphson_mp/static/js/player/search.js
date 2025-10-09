import { eventBus, MusicEvent } from "./event.js";
import { music, Track, Album } from "../api.js";
import { AlbumBrowse, ArtistBrowse, browse, getTracksTable } from "./browse.js";
import { windows } from "./window.js";
import { throttle } from "../util.js";

class Search {
    #searchResultParent = /** @type {HTMLDivElement} */ (document.getElementById('search-result-parent'));
    #searchResultTracks = /** @type {HTMLTableSectionElement} */ (document.getElementById('search-result-tracks'));
    #searchResultArtists = /** @type {HTMLDivElement} */ (document.getElementById('search-result-artists'));
    #searchResultAlbums = /** @type {HTMLDivElement} */ (document.getElementById('search-result-albums'));
    #queryInput = /** @type {HTMLInputElement} */ (document.getElementById('search-query'));
    #openButton = /** @type {HTMLButtonElement} */ (document.getElementById('open-window-search'));
    #abortController = /** @type {AbortController | null} */ (null);

    constructor() {
        eventBus.subscribe(MusicEvent.METADATA_CHANGE, () => {
            if (!windows.isOpen('window-search')) {
                console.debug('search: ignore METADATA_CHANGE, search window is not open');
                return;
            }
            console.debug('search: search again after receiving METADATA_CHANGE event');
            this.#performSearch();
        });

        this.#queryInput.addEventListener('input', throttle(100, true, () => this.#performSearch()));
        this.#openButton.addEventListener('click', () => this.openSearchWindow());
    }

    openSearchWindow() {
        const queryField =  /** @type {HTMLInputElement} */ (document.getElementById('search-query'));
        queryField.value = '';
        // @ts-ignore
        setTimeout(() => queryField.focus({ focusVisible: true }), 50); // high delay is necessary, I don't know why
        this.#searchResultParent.hidden = true;
    }

    async #performSearch() {
        // abort an existing search query request
        if (this.#abortController) {
            this.#abortController.abort();
        }

        const query = this.#queryInput.value;

        if (query.length < 3) {
            this.#searchResultParent.hidden = true;
            return;
        }

        let result;
        try {
            this.#abortController = new AbortController();
            result = await music.search(query, this.#abortController.signal);
            this.#abortController = null;
            console.debug('search: result:', result);
        } catch (err) {
            if (err instanceof DOMException && err.name == "AbortError") {
                console.info("search: aborted");
                return;
            }
            throw err;
        }

        // TODO hide track/artist/album sections separately
        if (result.tracks.length == 0 && result.artists.length == 0 && result.albums.length == 0) {
            this.#searchResultParent.hidden = true;
            return;
        }

        this.#searchResultParent.hidden = false;

        // Tracks
        {
            this.#searchResultTracks.replaceChildren(getTracksTable(result.tracks));
        }

        // Artists
        {
            const table = document.createElement('table');
            for (const artist of result.artists) {
                const artistLink = document.createElement('a');
                artistLink.textContent = artist;
                artistLink.onclick = () => browse.browse(new ArtistBrowse(artist));

                const td = document.createElement('td');
                td.append(artistLink);
                const row = document.createElement('tr');
                row.append(td);
                table.append(row);
            }

            this.#searchResultArtists.replaceChildren(table);
        }

        // Albums
        {
            const coverSize = '12rem';
            const newChildren = [];
            for (const album of result.albums) {
                const text = document.createElement('div');
                text.textContent = album.name;
                text.classList.add('box-header', 'line');

                const img = document.createElement('div');
                const imgUri = album.getCoverURL('low');
                img.style.background = `black url("${imgUri}") no-repeat center / cover`;
                img.style.height = coverSize;

                const result = document.createElement('div');
                result.classList.add('box');
                result.style.width = coverSize;
                result.addEventListener('click', () => browse.browse(new AlbumBrowse(album)));
                result.append(text, img);

                newChildren.push(result);

                if (newChildren.length > 6) {
                    break;
                }
            }

            this.#searchResultAlbums.replaceChildren(...newChildren);
        }
    }
}

export const search = new Search();
