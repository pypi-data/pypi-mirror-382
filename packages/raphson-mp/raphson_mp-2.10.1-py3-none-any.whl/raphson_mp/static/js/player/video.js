import { vars } from "../util.js";
import { player } from "./player.js";
import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";

if (!vars.offlineMode) {
    const videoButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-video'));
    const videoBox = /** @type {HTMLDivElement} */ (document.getElementById('video-box'));
    const albumCoverBox = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-box'));

    videoButton.hidden = true;

    function blur() {
        for (const elem of document.getElementsByClassName('cover-img')) {
            if (elem instanceof HTMLElement) {
                elem.style.filter = 'blur(10px)';
            }
        };
    }

    function resetBlur() {
        for (const elem of document.getElementsByClassName('cover-img')) {
            if (elem instanceof HTMLElement) {
                elem.style.filter = '';
            }
        };
    }

    /**
     * @returns {HTMLVideoElement}
     */
    function getVideoElement() {
        return /** @type {HTMLVideoElement} */ (document.getElementById('video'));
    }

    // Replace album cover with video
    videoButton.addEventListener('click', () => {
        if (!queue.currentTrack) {
            throw new Error();
        }
        videoButton.hidden = true;
        const url = queue.currentTrack.getVideoURL();
        console.info('video: set source', url);
        const videoElem = document.createElement('video');
        videoElem.setAttribute('muted', '');
        videoElem.src = url;
        videoElem.id = 'video';
        blur();
        videoBox.replaceChildren(videoElem);
        videoBox.hidden = false;
        albumCoverBox.hidden = true;
        if (!player.isPaused()) {
            videoElem.play();
        }
    });

    // Sync video time with audio
    eventBus.subscribe(MusicEvent.PLAYER_POSITION, () => {
        const videoElem = getVideoElement();
        const duration = player.getDuration();
        const position = player.getPosition();

        if (!videoElem || position === null || !duration) {
            return;
        }

        if (position >= videoElem.duration) {
            return;
        }

        // Large difference => skip
        if (Math.abs(position - videoElem.currentTime) > 1) {
            console.info('video: skip from', videoElem.currentTime, 'to', position);
            videoElem.currentTime = position;
            return;
        }

        // Small difference => speed up or slow down video to catch up
        if (Math.abs(position - videoElem.currentTime) > 0.2) {
            if (videoElem.currentTime > position) {
                console.debug('video: slow down');
                videoElem.playbackRate = 0.9;
            } else {
                console.debug('video: speed up');
                videoElem.playbackRate = 1.1;
            }
            return;
        }

        console.debug('video: in sync');
    });

    eventBus.subscribe(MusicEvent.PLAYER_PLAY, () => {
        const videoElem = getVideoElement();
        if (videoElem) videoElem.play();
    });
    eventBus.subscribe(MusicEvent.PLAYER_PLAY, () => {
        const videoElem = getVideoElement();
        if (videoElem) videoElem.pause();
    });

    eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => {
        resetBlur();

        // cannot reliably remove source from video element, so we must remove the entire element
        // https://stackoverflow.com/q/79162209/4833737
        videoBox.replaceChildren();
        videoBox.hidden = true;

        // Make cover visible again
        albumCoverBox.hidden = false;

        videoButton.hidden = !(queue.currentTrack && queue.currentTrack.video);
    });
};
