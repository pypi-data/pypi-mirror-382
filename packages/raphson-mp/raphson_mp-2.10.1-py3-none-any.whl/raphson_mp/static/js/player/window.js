import { coverSize } from "./coversize.js";
import { news } from "./news.js";
import { queue } from "./queue.js";

class Windows {
    baseIndex;
    /** @type {Array<string>} */
    #openWindows;

    constructor() {
        this.baseIndex = 100;
        this.#openWindows = [];

        // Window open buttons
        for (const elem of document.getElementsByClassName('window-overlay')) {
            const openButton = document.getElementById('open-' + elem.id);
            if (openButton === null) {
                continue;
            }
            const id = elem.id;
            openButton.addEventListener('click', () => windows.open(id));
        }

        // Window close buttons
        for (const elem of document.getElementsByClassName('window-close-button')) {
            if (!(elem instanceof HTMLElement)) continue;
            const id = elem.dataset.for;
            if (id === undefined) {
                console.warn('Window close button has no data-for attribute');
                continue;
            }
            elem.addEventListener('click', () => windows.close(id));
        }

        // Click outside window to close
        for (const elem of document.getElementsByClassName('window-overlay')) {
            elem.addEventListener('mousedown', event => {
                if (!event.currentTarget || event.target != event.currentTarget || !(event.currentTarget instanceof HTMLElement)) {
                    return; // clicked inside window
                }
                console.debug('window: clicked outside, closing window');
                windows.close(event.currentTarget.id);
            });
        }
    }

    /**
     * Open a window, above other windows. If the window is already opens, it is just moved to the top.
     * @param {string} idToOpen HTML id of window element
     */
    open(idToOpen) {
        console.debug('window: open:', idToOpen);

        const windowToOpen = /** @type {HTMLElement} */ (document.getElementById(idToOpen));
        if (!windowToOpen.classList.contains('window-overlay')) {
            throw new Error('Window is missing window-overlay class');
        }

        if (this.#openWindows.includes(idToOpen)) {
            // Already open, elevate existing window to top

            // Create new array with window to open removed, then add it on top
            this.#openWindows = this.#openWindows.filter(openWindow => openWindow !== idToOpen);
            this.#openWindows.push(idToOpen);

            // Change z-index of all open windows
            let i = 1;
            for (const openWindow of this.#openWindows) {
                console.debug('window: is open:', openWindow);
                const windowElem = /** @type {HTMLElement} */ (document.getElementById(openWindow));
                windowElem.style.zIndex = (this.baseIndex + i++) + '';
            }
        } else {
            // Add window to top (end of array), set z-index and make visible
            this.#openWindows.push(idToOpen);
            windowToOpen.style.zIndex = this.baseIndex + this.#openWindows.indexOf(idToOpen) + '';
            windowToOpen.classList.remove('overlay-hidden');
        }

        // Prevent scrolling body, double scrolling is annoying, especially on touch screen devices
        document.body.classList.add("no-scroll");
    }

    /**
     * Close a specific window
     * @param {string} idToClose HTML id of window element
     */
    close(idToClose) {
        console.debug('window: close:', idToClose);

        // Hide closed window
        const windowElem = /** @type {HTMLElement} */ (document.getElementById(idToClose));

        windowElem.classList.add('overlay-hidden');
        windowElem.style.zIndex = '';

        // Remove closed window from array
        this.#openWindows = this.#openWindows.filter(id => id !== idToClose);

        // Update z-index for open windows
        let zIndex = 0;
        for (const id of this.#openWindows) {
            const windowElem2 = /** @type {HTMLElement} */ (document.getElementById(id));
            windowElem2.style.zIndex = (this.baseIndex + zIndex++) + '';
        }

        // If this window was the last one to close, allow scrolling body again
        if (this.#openWindows.length == 0) {
            document.body.classList.remove("no-scroll");
        }
    }

    /**
     * Close top window
     */
    closeTop() {
        const top = this.#openWindows.pop();
        if (top) {
            this.close(top);
        }
    }

    /**
     * @param {string} id
     * @returns
     */
    isOpen(id) {
        return !document.getElementById(id)?.classList.contains('overlay-hidden');
    }

}

export const windows = new Windows();


// debug window
document.getElementById('debug-error')?.addEventListener('click', () => { throw new Error("debug"); });
document.getElementById('debug-news')?.addEventListener('click', () => news.queue());
document.getElementById('debug-queue')?.addEventListener('click', () => console.debug(queue.queuedTracks));
document.getElementById('debug-layout')?.addEventListener('click', () => {
    console.log(coverSize.adjustSidebarWidth);
    coverSize.adjustSidebarWidth = !coverSize.adjustSidebarWidth;
    coverSize.resizeCover();
});
