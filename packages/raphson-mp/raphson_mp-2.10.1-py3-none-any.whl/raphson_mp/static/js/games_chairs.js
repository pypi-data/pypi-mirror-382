import { AudioFormat, Track, music } from "./api.js";
import { choice, randInt } from "./util.js";

const trackChooseCount = 5;
const firstPlayRange = /** @type{[number, number]} */ ([5000, 30000]);
const playRange = /** @type{[number, number]} */ ([1000, 25000]);
const pauseRange = /** @type{[number, number]} */ ([1500, 8000]);


const boxes = /** @type {HTMLDivElement} */ (document.getElementById('boxes'));
const audio = /** @type {HTMLAudioElement} */ (document.getElementById('audio'));

const textChoose = /** @type {HTMLHeadingElement} */ (document.getElementById('text-choose'));
const textStart = /** @type {HTMLHeadingElement} */ (document.getElementById('text-start'));
const spinner = /** @type {HTMLDivElement} */ (document.getElementById('spinner'));

const cover = document.createElement('div');
cover.classList.add('box', 'padding', 'cover-img');
cover.id = 'cover';


/**
 * @param {Track} track
 */
async function choose(track) {
    textChoose.hidden = true;
    boxes.replaceChildren();

    spinner.hidden = false;

    cover.style.backgroundImage = `url("${track.getCoverURL('high')}")`;
    boxes.replaceChildren(cover);

    window.addEventListener('click', start);
    window.addEventListener('keydown', start);

    audio.src = track.getAudioURL(AudioFormat.OPUS_HIGH);

    spinner.hidden = true;
    textStart.hidden = false;
}

function start() {
    console.debug('games_chairs: start');
    window.removeEventListener('click', start);
    window.removeEventListener('keydown', start);
    textStart.hidden = true;
    audio.play();
    setTimeout(pause, randInt(...firstPlayRange));
}

function play() {
    console.debug('games_chairs: play');
    audio.play();
    cover.style.scale = '';
    setTimeout(pause, randInt(...playRange));
}

function pause() {
    console.debug('games_chairs: pause');
    audio.pause();
    cover.style.scale = '0';
    setTimeout(play, randInt(...pauseRange));
}

async function init() {
    await music.loadPlaylists();
    const playlists = music.playlists();

    let tracks = 0

    for (let tries = 0; tracks < trackChooseCount && tries < trackChooseCount * 2; tries++) {
        try {
            const playlist = choice(playlists);
            const track = await playlist.chooseRandomTrack(false, {});
            const box = document.createElement('div');
            box.classList.add('box', 'padding', 'choose');
            box.textContent = track.displayText();
            box.addEventListener('click', () => {
                choose(track);
            });
            boxes.append(box);
            tracks++;
        } catch (error) {
            console.error(error);
        }
    }
}

audio.addEventListener('ended', () => window.location.assign(''));

init();
