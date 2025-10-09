import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";
import { player, playerControls } from "./player.js";
import { music } from "../api.js";

const PLAYED_TIMER_INTERVAL_SECONDS = 5;

class History {
    hasScrobbled = false;
    playingCounter = 0;
    requiredPlayingCounter = /** @type {number | null} */ (null);

    constructor() {
        eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => this.#onNewTrack());
        setInterval(() => this.#update(), PLAYED_TIMER_INTERVAL_SECONDS * 1000);
    }

    #onNewTrack() {
        this.hasScrobbled = false;
        this.playingCounter = 0;
        // last.fm requires track to be played for half its duration or for 4 minutes (whichever is less)
        if (queue.currentTrack) {
            this.requiredPlayingCounter = Math.min(4 * 60, Math.round(queue.currentTrack.duration / 2));
        } else {
            this.requiredPlayingCounter = null;
        }
    }

    async #update() {
        if (this.hasScrobbled || !queue.currentTrack) {
            return;
        }

        if (this.requiredPlayingCounter == null) {
            console.debug('history: no current track');
            return;
        }

        if (player.isPaused()) {
            console.debug('history: audio element paused');
            return;
        }

        if (playerControls.getVolume() == 0) {
            console.debug('history: volume is zero');
            return;
        }

        this.playingCounter += PLAYED_TIMER_INTERVAL_SECONDS;

        console.debug('history: playing, counter:', this.playingCounter, '/', this.requiredPlayingCounter);

        if (this.playingCounter > this.requiredPlayingCounter) {
            console.info('history: played');
            this.hasScrobbled = true;
            await music.played(queue.currentTrack);
        }
    }
}

const history = new History();
