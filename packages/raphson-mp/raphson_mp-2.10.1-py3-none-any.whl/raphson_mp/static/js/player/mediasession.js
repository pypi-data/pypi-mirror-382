import { player } from "./player.js"
import { eventBus, MusicEvent } from "./event.js"
import { queue } from "./queue.js";
import { Setting } from "./settings.js";

class MediaSessionUpdater {
    constructor() {
        eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => this.updateMetadata());

        eventBus.subscribe(MusicEvent.PLAYER_PLAY, () => this.updateState());
        eventBus.subscribe(MusicEvent.PLAYER_PAUSE, () => this.updateState());

        // Media session events
        navigator.mediaSession.setActionHandler('play', () => player.play());
        navigator.mediaSession.setActionHandler('pause', () => player.pause());
        navigator.mediaSession.setActionHandler('seekto', callback => {
            if (!callback.seekTime) {
                throw new Error("If the action is seekto, seekTime must be present");
            }
            player.seek(callback.seekTime);
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => queue.previous());
        navigator.mediaSession.setActionHandler('nexttrack', () => queue.next());
    }

    updateState() {
        navigator.mediaSession.playbackState = player.isPaused() ? 'paused' : 'playing';
    }

    updatePosition() {
        const position = player.getPosition();
        const duration = player.getDuration();
        if (!duration || position === null) {
            console.debug('mediasession: skip update, invalid value');
            return;
        }

        const positionState = {
            position: position,
            duration: duration,
        }
        console.debug('mediasession: do update', positionState);
        navigator.mediaSession.setPositionState(positionState);
    }

    updateMetadata() {
        if (!queue.currentTrack) {
            navigator.mediaSession.metadata = null;
            return;
        }

        const track = queue.currentTrack;

        const imageUrl = track.getCoverURL('low', Setting.MEME_MODE.checked);

        /** @type {MediaMetadataInit} */
        const metaObj = {
            // Chromium on Linux works. Firefox on Linux works, except for cover art.
            // Firefox mobile doesn't support the MediaSession API at all.
            artwork: [{src: imageUrl}],
        }

        if (track.title && track.artists.length > 0) {
            metaObj.title = track.title;
            metaObj.artist = track.artists.join(', ');
            if (track.album) {
                metaObj.album = track.album;
            }
        } else {
            metaObj.title = track.displayText();
        }

        console.debug('mediasession: set metadata', metaObj);
        navigator.mediaSession.metadata = new MediaMetadata(metaObj);
    }
}

if ("mediaSession" in navigator) {
    new MediaSessionUpdater();
} else {
    console.warn("mediasession: browser does not support MediaSession API")
}
