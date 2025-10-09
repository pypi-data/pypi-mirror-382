import { initNowPlayingCards } from "./now_playing.js";

const nowPlayingDiv = document.getElementById('now-playing');
if (nowPlayingDiv) {
    initNowPlayingCards(nowPlayingDiv, true);
}
