// Ensures combined height of album cover and lyrics box never exceed 100vh
// I am convinced this should be possible with just CSS, but I can't figure it out yet.

class CoverSize {
    adjustSidebarWidth = false;
    #lyricsBox = /** @type {HTMLDivElement} */ (document.getElementById('lyrics-box'));
    #coverBox = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-box'));
    #leftSidebar = /** @type {HTMLDivElement} */ (document.getElementById('left-sidebar'));
    #rightSidebar = /** @type {HTMLDivElement} */ (document.getElementById('right-sidebar'));

    constructor() {
        const resizeObserver = new ResizeObserver(() => {
            // delay to avoid infinite resize loop
            requestAnimationFrame(() => this.resizeCover());
        });
        resizeObserver.observe(this.#lyricsBox);
        resizeObserver.observe(document.body);
    }

    /**
     * @param {string} value
     */
    #setMaxHeight(value) {
        this.#coverBox.style.maxHeight = value;
        if (this.adjustSidebarWidth) {
            this.#leftSidebar.style.maxWidth = value;
            this.#rightSidebar.style.maxWidth = value;
            this.#coverBox.style.maxWidth = '';
        } else {
            this.#leftSidebar.style.maxWidth = '';
            this.#rightSidebar.style.maxWidth = '';
            this.#coverBox.style.maxWidth = value;
        }
        console.debug('coversize: max height changed:', value);
    }

    resizeCover() {
        // Do not set max height in single column interface
        if (document.body.clientWidth <= 950) {
            this.#setMaxHeight('none');
            return;
        }

        if (this.#lyricsBox.hidden) {
            // No lyrics
            this.#setMaxHeight(`calc(100vh - 2*var(--gap))`);
            return;
        }

        this.#setMaxHeight(`calc(100vh - 3*var(--gap) - ${this.#lyricsBox.clientHeight}px)`);
    }
}

export const coverSize = new CoverSize();
