import "./player/browse.js";
import "./player/control.js";
import "./player/coversize.js";
import "./player/editor.js";
import "./player/event.js";
import "./player/history.js";
import "./player/hotkey.js";
import "./player/lyrics.js";
import "./player/mediasession.js";
import "./player/news.js";
import "./player/player.js";
import "./player/queue.js";
import "./player/search.js";
import "./player/settings.js";
import "./player/share.js";
import "./player/tag.js";
import "./player/theater.js";
import "./player/track.js";
import "./player/video.js";
import "./player/visualise.js";
import "./player/window.js";

import { vars } from "./util.js";
import { controlChannel } from "./api.js";

// Browser "restore session" functionality can sometimes restore a very outdated version of the page
// In that case, trigger a reload
// This does have the side effect that any device with a significantly wrong clock cannot use the music player.
{
    const loadTimestamp = vars.loadTimestamp;
    const differenceSeconds = Date.now() / 1000 - loadTimestamp;

    console.debug('reload: page loaded ' + differenceSeconds + ' ago');

    if (differenceSeconds > 86400) {
        console.warn('page loaded long ago, reloading page!');
        window.location.reload();
    }
}

// Send stop signal to server when page is closed
window.addEventListener("pagehide", () => {
    if (vars) {
        return;
    }

    controlChannel.sendStopSignal();
});
