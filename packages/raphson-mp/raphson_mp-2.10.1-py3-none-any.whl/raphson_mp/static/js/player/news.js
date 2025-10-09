import { queue } from "./queue.js";
import { player } from "./player.js";
import { music, NEWS_PATH } from "../api.js";
import { Setting } from "./settings.js";

class News {
    constructor() {
        setInterval(() => this.check(), 60_000);
    }

    #hasQueuedNews() {
        return (queue.currentTrack && queue.currentTrack.path == NEWS_PATH)
            || queue.queuedTracks.some(track => track.track.path == NEWS_PATH)
            || queue.previousTracks.some(track => track.path == NEWS_PATH);
    }

    /**
     * Called every minute. Checks if news should be queued.
     * @returns {void}
     */
    check() {
        if (!Setting.NEWS.checked) {
            console.debug('news: is disabled');
            return;
        }

        const minutes = new Date().getMinutes();
        const isNewsTime = minutes >= 10 && minutes < 15;
        if (!isNewsTime) {
            console.debug('news: not news time');
            return;
        }

        if (this.#hasQueuedNews()) {
            console.debug('news: already queued');
            return;
        }

        if (player.isPaused()) {
            console.debug('news: will not queue, audio paused');
            return;
        }

        console.info('news: queueing news');
        this.queue();
    }

    /**
     * Downloads news, and add it to the queue
     */
    async queue() {
        const track = await music.track(NEWS_PATH)
        queue.add(track, true, true);
    }
}

export const news = new News();
