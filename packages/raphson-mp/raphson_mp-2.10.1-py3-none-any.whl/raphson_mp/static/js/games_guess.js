import { AudioFormat, music, Track } from "./api.js";
import { PlaylistCheckboxes } from "./playlistcheckboxes.js";
import { choice, prefetch } from "./util.js";

const playlists = /** @type {HTMLDivElement} */ (document.getElementById('playlists'));
const cover =  /** @type {HTMLDivElement} */ (document.getElementById('cover'));
const audio = /** @type {HTMLAudioElement} */ (document.getElementById('audio'));
const loadingText = /** @type {HTMLDivElement} */ (document.getElementById('loading-text'));
const startText = /** @type {HTMLDivElement} */ (document.getElementById('start-text'));
const revealText = /** @type {HTMLDivElement} */ (document.getElementById('reveal-text'));
const nextText = /** @type {HTMLDivElement} */ (document.getElementById('next-text'));
const details = /** @type {HTMLDivElement} */ (document.getElementById('details'));

const upcomingTracks = /** @type {Array<Track>} */ ([]);
let currentTrack = /** @type {Track | null} */ (null);
let state = 'start'; // one of: start, playing, reveal

function start() {
    // Choose a random track, and display it blurred. Show start text
    state = 'start';
    console.info('start');

    audio.pause();
    details.textContent = '';

    const track = upcomingTracks.shift();
    if (!track) {
        console.debug('games_guess: upcomingTracks still empty')
        setTimeout(start, 500);
        return;
    }
    currentTrack = track;

    cover.style.backgroundImage = `url("${track.getCoverURL('high')}")`;
    audio.src = track.getAudioURL(AudioFormat.OPUS_HIGH);
    cover.classList.add('blurred');
    startText.hidden = false;
    nextText.hidden = true;
    loadingText.hidden = true;
}

function play() {
    // Hide start text, start playing audio, show reveal text
    state = 'playing';
    console.info('playing');
    startText.hidden = true;
    revealText.hidden = false;
    audio.play();
}

function reveal() {
    // Hide reveal text, show next text
    state = 'reveal'
    console.info('reveal');
    cover.classList.remove('blurred');
    revealText.hidden = true;
    nextText.hidden = false;
    if (!currentTrack) throw new Error();
    details.textContent = currentTrack.displayText();
}

function onClick() {
    if (state == "start") {
        play();
    } else if (state == "playing") {
        reveal();
    } else if (state == "reveal") {
        start();
    }
}

cover.addEventListener('click', onClick);
document.addEventListener('keydown', event => {
    if (event.key == ' ') {
        onClick();
    }
});

const onPlaylistChange = () => {
    upcomingTracks.length = 0;
    fillCachedTracks();
}

const playlistCheckboxes = new PlaylistCheckboxes(playlists, onPlaylistChange);

async function fillCachedTracks() {
    if (upcomingTracks.length > 2) {
        return;
    }

    const playlists = playlistCheckboxes.getActivePlaylists()
    if (playlists.length == 0) {
        return;
    }

    const playlist = music.playlist(choice(playlists));
    const track = await playlist.chooseRandomTrack(true, {});
    prefetch(track.getAudioURL(AudioFormat.OPUS_HIGH));
    prefetch(track.getCoverURL('high'));
    upcomingTracks.push(track);
}

async function init() {
    await music.loadPlaylists();
    start();
    playlistCheckboxes.createPlaylistCheckboxes();
    fillCachedTracks();
    setInterval(fillCachedTracks, 2000);
}

init();
