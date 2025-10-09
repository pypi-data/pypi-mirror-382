import { AudioFormat, Track } from "./api.js";
import { jsonGet, replaceIconButton } from "./util.js";

const updateInterval = 1000;

class RadioTrack {
    /** @type {number} */
    startTime;
    /** @type {Track} */
    track;
    constructor(startTime, track) {
        this.startTime = startTime;
        this.track = track;
    }
}

const state = {
    /** @type {RadioTrack | null} */
    currentTrack: null,
    /** @type {RadioTrack | null} */
    nextTrack: null,
};

async function updateTracks() {
    if (state.currentTrack && state.nextTrack) {
        console.debug('radio: updateState: ok');
        return;
    }

    const json = await jsonGet('/radio/info');

    if (state.currentTrack == null) {
        console.debug('radio: updateState: init currentTrack');
        const download = await new Track(json.current);
        state.currentTrack = new RadioTrack(json.current_time, download);
    }

    if (state.nextTrack == null) {
        console.debug('radio: updateState: init nextTrack');
        const download = await new Track(json.next);
        state.nextTrack = new RadioTrack(json.next_time, download);
    }
}

setInterval(updateTracks, 10_000);
updateTracks();


const audio = /** @type {HTMLAudioElement} */ (document.getElementById('audio'));
const image = /** @type {HTMLImageElement} */ (document.getElementById('image'));
const current = /** @type {HTMLSpanElement} */ (document.getElementById('current'));
const next = /** @type {HTMLSpanElement} */ (document.getElementById('next'));
const status = /** @type {HTMLSpanElement} */ (document.getElementById('status'));
const play = /** @type {HTMLButtonElement} */ (document.getElementById('play'));
const lyrics = /** @type {HTMLButtonElement} */ (document.getElementById('lyrics'));

/**
 * @param {RadioTrack} track
 */
async function setSrc(track) {
    console.debug('radio: setSrc');
    audio.src = track.track.getAudioURL(AudioFormat.OPUS_HIGH);
    image.src = track.track.getCoverURL('high');
    lyrics.textContent = track.track.plainLyrics;

    try {
        await audio.play();
    } catch (err) {
        console.warn('cannot play, autoplay blocked?', err);
    }
}

async function update() {
    if (state.currentTrack != null) {
        current.textContent = state.currentTrack.track.displayText();
    } else {
        current.textContent = '';
    }

    if (state.nextTrack != null) {
        next.textContent = state.nextTrack.track.displayText();
    } else {
        next.textContent = '';
    }

    if (state.currentTrack == null) {
        return;
    }

    // load initial track, once available
    if (audio.src == '') {
        console.debug('radio: set initial audio');
        await setSrc(state.currentTrack);
    }

    if (audio.paused) {
        status.textContent = 'paused';
        return;
    }

    const currentPos = Date.now() - state.currentTrack.startTime;
    const offset = audio.currentTime * 1000 - currentPos;
    let rate = 1;

    if (Math.abs(offset) > 1000) {
        console.debug('radio: large offset', offset, 'skip from', audio.currentTime, 'to', currentPos / 1000);
        audio.currentTime = currentPos / 1000;
        audio.playbackRate = 1;
        status.textContent = 'very out of sync';
    } else {
        // Aim to be in sync in 60 seconds
        rate = 1 - offset / (60 * updateInterval);
        audio.playbackRate = rate;
        if (Math.abs(offset) < 100) {
            status.textContent = 'in sync';
        } else {
            status.textContent = 'out of sync';
        }
    }

    status.textContent += " | " + Math.round(offset / 10) / 100 + 's';
    status.textContent += " | " + Math.round(rate * 1000) / 1000 + 'x';
};

setInterval(update, updateInterval);

audio.addEventListener('ended', async () => {
    state.currentTrack = state.nextTrack;
    state.nextTrack = null;
    if (state.currentTrack) {
        await setSrc(state.currentTrack);
    }
});

console.log(play);

audio.addEventListener('play', () => replaceIconButton(play, 'pause'));
audio.addEventListener('pause', () => replaceIconButton(play, 'play'));

play.addEventListener('click', () => {
    if (audio.paused) {
        audio.play();
        update();
    } else {
        audio.pause();
    }
});
