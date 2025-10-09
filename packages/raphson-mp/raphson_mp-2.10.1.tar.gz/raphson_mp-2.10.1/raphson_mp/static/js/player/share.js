import { queue } from "./queue.js";
import { vars, jsonPost } from "../util.js";

if (!vars.offlineMode) {
    const shareButton = /** @type {HTMLButtonElement} */(document.getElementById('button-share'));
    shareButton.addEventListener('click', async () => {
        if (!queue.currentTrack || queue.currentTrack.isVirtual()) {
            // Music not loaded yet or virtual track
            return;
        }

        const response = await jsonPost('/share/create', { track: queue.currentTrack.path });
        const json = await response.json();
        const absoluteShareUrl = new URL('/share/' + json.code, document.location.href).href;

        if (navigator.canShare) {
            const shareData = { url: absoluteShareUrl };
            if (navigator.canShare(shareData)) {
                navigator.share(shareData);
                return;
            } else {
                console.warn('share: canShare == false');
            }
        } else {
            console.warn('share: Share API is not available');
        }

        window.open(absoluteShareUrl, '_blank');
    });
}
