import { AlbumBrowse, ArtistBrowse, browse, PlaylistBrowse, TitleBrowse, YearBrowse } from "./browse.js";
import { Track } from "../api.js";


/**
 * @param {Track} track
 */
function getPrimaryLine(track) {
    const primary = document.createElement('div');

    if (track.title) {
        let first = true;
        for (const artist of track.artists) {
            if (first) {
                first = false;
            } else {
                primary.append(', ');
            }

            const artistHtml = document.createElement('a');
            artistHtml.textContent = artist;
            artistHtml.addEventListener("click", () => browse.browse(new ArtistBrowse(artist)));
            primary.append(artistHtml);
        }

        if (track.artists.length > 0) {
            primary.append(' - ');
        }

        const titleHtml = document.createElement(track.isVirtual() ? 'span' : 'a');
        titleHtml.textContent = track.title;
        titleHtml.style.color = 'var(--text-color)';
        const title = track.title;
        if (!track.isVirtual()) {
            titleHtml.addEventListener("click", () => browse.browse(new TitleBrowse(title)));
        }
        primary.append(titleHtml);
    } else {
        const span = document.createElement('span');
        span.style.color = "var(--text-color-warning)";
        span.textContent = track.path.substring(track.path.indexOf('/') + 1);
        primary.append(span);
    }
    return primary;
}

/**
 * @param {Track} track
 * @param {boolean} showPlaylist
 */
function getSecondaryLine(track, showPlaylist) {
    const secondary = document.createElement('div');
    secondary.classList.add('secondary');
    secondary.style.marginTop = 'var(--smallgap)';

    if (showPlaylist && !track.isVirtual()) {
        const playlistHtml = document.createElement('a');
        playlistHtml.addEventListener("click", () => browse.browse(new PlaylistBrowse(track.playlistName)));
        playlistHtml.textContent = track.playlistName;
        secondary.append(playlistHtml);
    }

    const year = track.year;
    const album = track.getAlbum()

    if (year || track.album) {
        if (showPlaylist && !track.isVirtual()) {
            secondary.append(', ');
        }

        if (album) {
            const albumHtml = document.createElement('a');
            albumHtml.addEventListener("click", () => browse.browse(new AlbumBrowse(album)));
            if (album.artist) {
                albumHtml.textContent = album.artist + ' - ' + album.name;
            } else {
                albumHtml.textContent = album.name;
            }
            secondary.append(albumHtml);
            if (track.year) {
                secondary.append(', ');
            }
        }

        if (year) {
            const yearHtml = document.createElement('a');
            yearHtml.textContent = year + '';
            yearHtml.addEventListener('click', () => browse.browse(new YearBrowse(year)));
            secondary.append(yearHtml);
        }
    }
    return secondary;
}

/**
 * Get display HTML for a track
 * @param {Track} track
 * @param {boolean} showPlaylist
 * @returns {HTMLSpanElement}
 */
export function trackDisplayHtml(track, showPlaylist = false) {
    const html = document.createElement('div');
    html.classList.add('track-display-html');

    html.append(getPrimaryLine(track), getSecondaryLine(track, showPlaylist));

    return html;
};
