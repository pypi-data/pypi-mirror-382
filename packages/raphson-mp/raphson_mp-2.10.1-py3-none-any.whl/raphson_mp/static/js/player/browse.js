import { eventBus, MusicEvent } from "./event.js";
import { vars, createIconButton, durationToString } from "../util.js";
import { windows } from "./window.js";
import { Album, music, RAPHSON_SMALL_URL, Track } from "../api.js";
import { trackDisplayHtml } from "./track.js";
import { editor } from "./editor.js";
import { queue } from "./queue.js";
import { createPlaylistDropdown } from "./player.js";

const BROWSE_CONTENT = /** @type {HTMLDivElement} */ (document.getElementById('browse-content'));

/**
 * @param {Track} track
 * @returns {HTMLTableRowElement}
 */
export function getTrackRow(track) {
    const colPlaylist = document.createElement('td');
    colPlaylist.textContent = track.playlistName;

    const colDuration = document.createElement('td');
    colDuration.textContent = durationToString(track.duration);

    const colTitle = document.createElement('td');
    colTitle.appendChild(trackDisplayHtml(track));
    colTitle.style.width = '100%'; // make title column as large as possible

    const playNowButton = createIconButton('play', vars.tTooltipPlayNow);
    playNowButton.addEventListener('click', async () => {
        try {
            queue.playNow(track);
        } catch (ex) {
            console.error('browse: error playing track now', ex);
        }
    });
    const colPlayNow = document.createElement('td');
    colPlayNow.appendChild(playNowButton)

    const addButton = createIconButton('playlist-plus', vars.tTooltipAddToQueue);
    addButton.addEventListener('click', () => queue.add(track, true));
    const colAdd = document.createElement('td');
    colAdd.appendChild(addButton);

    const colEdit = document.createElement('td');

    if (!vars.offlineMode && (music.playlist(track.playlistName)).write) {
        const editButton = createIconButton('pencil', vars.tTooltipEditMetadata);
        editButton.addEventListener('click', () => editor.open(track));
        colEdit.appendChild(editButton);
    }

    const row = document.createElement('tr');
    row.append(colPlaylist, colDuration, colTitle, colPlayNow, colAdd, colEdit);
    return row;
}

const LAZY_TRACK_LIST_THRESHOLD = 100;

/**
 * @param {Array<Track>} tracks
 * @returns {HTMLTableElement}
 */
export function getTracksTable(tracks) {
    const table = document.createElement('table');
    table.classList.add('track-list');
    const tbody = document.createElement('tbody');
    table.append(tbody);

    if (tracks.length < LAZY_TRACK_LIST_THRESHOLD) {
        for (const track of tracks) {
            tbody.append(getTrackRow(track));
        }
        return table;
    }

    // Use one row to determine the height of the track placeholder
    const placeholderHeight = getTrackRow(tracks[0]);
    console.debug('placeholder height:', placeholderHeight);

    const placeholder = document.createElement('tr');
    placeholder.dataset.placeholder = '1';
    const placeholderCell = document.createElement('td');
    placeholderCell.style.height = '45px'; // TODO how to determine this programmatically?
    placeholderCell.colSpan = 5;
    placeholder.append(placeholderCell);

    /**
     * @param {Array<IntersectionObserverEntry>} entries
     * @param {IntersectionObserver} observer
     */
    function observerCallback(entries, observer) {
        if (!document.body.contains(table)) {
            // the table no longer exists, unregister ourselves
            console.debug('browse: disconnect observer');
            observer.disconnect();
            return;
        }

        for (const entry of entries) {
            const elem = /** @type {HTMLElement} */ (entry.target);
            let newElem;
            if (entry.isIntersecting && elem.dataset.placeholder == '1') {
                // console.debug('browse: placeholder -> row', elem.dataset.index)
                const track = tracks[parseInt(/** @type {string} */(elem.dataset.index))];
                newElem = getTrackRow(track);
            } else if (!entry.isIntersecting && elem.dataset.placeholder != '1') {
                // console.debug('browse: row -> placeholder', elem.dataset.index)
                newElem = /** @type {HTMLElement} */ (placeholder.cloneNode(true));
            }

            if (newElem) {
                newElem.dataset.index = elem.dataset.index;
                requestAnimationFrame(() => {
                    elem.replaceWith(newElem);
                    observer.unobserve(elem);
                    observer.observe(newElem);
                });
            }
        }
    };

    // @ts-ignore delay property is only supported by Chrome
    // Without the delay property, Chrome lags when scrolling. Firefox doesn't, so it doesn't need the delay either :)
    const observer = new IntersectionObserver(observerCallback, { root: null, scrollMargin: '1000px', delay: 100 });

    for (let i = 0; i < tracks.length; i++) {
        const row = /** @type {HTMLElement} */ (placeholder.cloneNode(true));
        row.dataset.index = '' + i;
        observer.observe(row);
        tbody.append(row);
    }

    return table;
}

/**
 * @param {Album | null} album
 * @param {Array<Track>} tracks
 * @returns
 */
function getAlbumHTML(album, tracks) {
    const image = document.createElement('img');
    image.src = album ? album.getCoverURL('low') : RAPHSON_SMALL_URL;
    image.style.height = image.style.width = '5rem';
    image.style.borderRadius = 'var(--border-radius)';

    const text = document.createElement('div');
    const name = document.createElement('h3');
    name.textContent = album ? album.name : vars.tUnknownAlbum;
    name.style.margin = '0';
    text.append(name);

    for (const track of tracks) {
        if (track.year) {
            const year = document.createElement('p');
            year.textContent = '' + track.year;
            year.classList.add('secondary');
            text.append(year);
            break;
        }
    }

    const header = document.createElement('div');
    header.append(image, text);
    header.classList.add('flex-vcenter', 'flex-gap');

    const table = getTracksTable(tracks);

    return [header, table];
}

/**
 * @param {Array<Track>} tracks
 */
function getArtistHTML(tracks) {
    const albums = /** @type {Array<Album>} */ ([]);
    const looseTracks = /** @type {Array<Track>} */ ([]);

    for (const track of tracks) {
        const album = track.getAlbum();
        if (album) {
            let foundAlbum = false;
            for (const album2 of albums) {
                if (album2.name.toLowerCase() == album.name.toLowerCase()) {
                    foundAlbum = true;
                    break;
                }
            }
            if (!foundAlbum) {
                albums.push(album);
            }
        } else {
            looseTracks.push(track);
        }
    }

    const children = [];

    for (const album of albums) {
        const albumTracks = [];
        for (const track of tracks) {
            if (track.album && track.album.toLowerCase() == album.name.toLowerCase()) {
                albumTracks.push(track);
            }
        }
        children.push(...getAlbumHTML(album, albumTracks));
    }

    if (looseTracks.length > 0) {
        children.push(...getAlbumHTML(null, looseTracks));
    }

    return children;
}

class AbstractBrowse {
    /** @type {string} */
    title;
    /**
     * @param {string} title
     */
    constructor(title) {
        this.title = title;
    }

    async render() {
        throw new Error("abstract method");
    }
}

export class HomeBrowse extends AbstractBrowse {
    constructor() {
        super(vars.tBrowseNothing);
    }

    async render() {
        const playlistSelect = createPlaylistDropdown(false);
        const noPlaylistOption = document.createElement('option');
        noPlaylistOption.textContent = vars.tPlaylist;
        playlistSelect.value = "";
        playlistSelect.prepend(noPlaylistOption);
        playlistSelect.addEventListener('input', () => browse.browse(new PlaylistBrowse(playlistSelect.value)));

        const recentlyAddedButton = document.createElement('button');
        recentlyAddedButton.textContent = vars.tBrowseRecentlyAdded;
        recentlyAddedButton.addEventListener("click", () => browse.browse(new RecentlyAddedBrowse()));

        const recentlyReleasedButton = document.createElement('button');
        recentlyReleasedButton.textContent = vars.tBrowseRecentlyReleased;
        recentlyReleasedButton.addEventListener("click", () => browse.browse(new RecentlyReleasedBrowse()));

        const randomButton = document.createElement('button');
        randomButton.textContent = vars.tBrowseRandom;
        randomButton.addEventListener("click", () => browse.browse(new RandomBrowse()));

        const missingMetadataButton = document.createElement('button');
        missingMetadataButton.textContent = vars.tBrowseMissingMetadata;
        missingMetadataButton.addEventListener("click", () => browse.browse(new MissingMetadataBrowse()));

        const buttonsContainer = document.createElement('div');
        buttonsContainer.append(playlistSelect, recentlyAddedButton, recentlyReleasedButton, randomButton, missingMetadataButton);
        buttonsContainer.classList.add('flex-halfgap');

        BROWSE_CONTENT.replaceChildren(buttonsContainer);
    }
}

export class TracksBrowse extends AbstractBrowse {
    filters;
    /**
     * @param {string} title
     * @param {import("../types.js").FilterJson} filters
     */
    constructor(title, filters) {
        super(title);
        this.filters = filters;
    }

    async render() {
        const tracks = await music.filter(this.filters);
        BROWSE_CONTENT.replaceChildren(getTracksTable(tracks));
    }
}

export class ArtistBrowse extends AbstractBrowse {
    /** @type {string} */
    artist;

    /**
     * @param {string} artist
     */
    constructor(artist) {
        super(vars.tBrowseArtist + artist);
        this.artist = artist;
    }

    async render() {
        const tracks = await music.filter({ artist: this.artist, order: 'number,title' });
        BROWSE_CONTENT.replaceChildren(...getArtistHTML(tracks));
    }
}

export class AlbumBrowse extends AbstractBrowse {
    /** @type {Album} */
    album;

    /**
     * @param {Album} album
     */
    constructor(album) {
        const title = vars.tBrowseAlbum + (album.artist === null ? '' : album.artist + ' - ') + album.name;
        super(title);
        this.album = album;
    }

    async render() {
        /** @type {import("../types.js").FilterJson} */
        const filters = { album: this.album.name, order: 'number,title' };
        if (this.album.artist) {
            filters.album_artist = this.album.artist;
        }
        const tracks = await music.filter(filters);
        BROWSE_CONTENT.replaceChildren(...getAlbumHTML(this.album, tracks));
    }
}

export class TagBrowse extends TracksBrowse {
    /**
     * @param {string} tagName
     */
    constructor(tagName) {
        super(vars.tBrowseTag + tagName, { tag: tagName });
    }
}

export class PlaylistBrowse extends TracksBrowse {
    /**
     * @param {string} playlistName
     */
    constructor(playlistName) {
        super(vars.tBrowsePlaylist + playlistName, { playlist: playlistName, order: 'ctime_asc' });
    }
}

export class YearBrowse extends TracksBrowse {
    /**
     * @param {number} year
     */
    constructor(year) {
        super(vars.tBrowseYear + year, { year: year, order: 'title' });
    }
}

export class TitleBrowse extends TracksBrowse {
    /**
     * @param {string} title
     */
    constructor(title) {
        super(vars.tBrowseTitle + title, { title: title, order: 'ctime_asc' });
    }
}

export class RecentlyAddedBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRecentlyAdded, { order: "ctime_desc", limit: 100 });
    }
}

export class RecentlyReleasedBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRecentlyReleased, { order: "year_desc", limit: 100 });
    }
}

export class RandomBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRandom, { order: "random", limit: 100 });
    }
}

export class MissingMetadataBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseMissingMetadata, { has_metadata: "0", order: "random", limit: 100 });
    }
}

class Browse {
    /** @type {Array<AbstractBrowse>} */
    #history = [];
    /** @type {AbstractBrowse | null} */
    #current = null;
    #allButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-all'));
    #backButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-back'));

    constructor() {
        // Button to open browse window
        this.#allButton.addEventListener('click', () => browse.browse(new HomeBrowse()));

        // Back button in top left corner of browse window
        this.#backButton.addEventListener('click', () => browse.back());

        eventBus.subscribe(MusicEvent.METADATA_CHANGE, () => {
            if (!windows.isOpen('window-browse')) {
                console.debug('browse: ignore METADATA_CHANGE, browse window is not open. Is editor open: ', windows.isOpen('window-editor'));
                return;
            }

            console.debug('browse: received METADATA_CHANGE, updating content');
            this.updateContent();
        });
    };

    /**
     * @param {string} textContent
     */
    setHeader(textContent) {
        const browseWindow = /** @type {HTMLDivElement} */ (document.getElementById('window-browse'));
        browseWindow.getElementsByTagName('h2')[0].textContent = textContent;
    };

    /**
     * @param {AbstractBrowse} nextBrowse
     */
    async browse(nextBrowse) {
        if (this.#current != null) {
            this.#history.push(this.#current);
        }
        this.#current = nextBrowse;
        await this.updateContent();
        windows.open('window-browse');
    };

    back() {
        const last = this.#history.pop();
        if (last) {
            this.#current = last;
            this.updateContent();
        }
    };

    async updateContent() {
        if (!this.#current) {
            throw new Error("current is null");
        }
        console.debug('browse:', this.#current);

        this.setHeader(this.#current.title);
        await this.#current.render();

        this.#backButton.disabled = this.#history.length == 0;
    }
};

export const browse = new Browse();
