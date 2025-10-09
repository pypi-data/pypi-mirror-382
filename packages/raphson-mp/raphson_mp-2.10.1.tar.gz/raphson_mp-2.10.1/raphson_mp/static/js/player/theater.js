import { vars, createToast } from "../util.js";
import { setSettingChecked, Setting } from "./settings.js";

const THEATER_TIMEOUT = 5_000;

class Theater {
    /** @type {(() => void) | null} */
    #listenerFunction = null;
    /** @type {number} */
    #enableTimer = 0;

    constructor() {
        Setting.THEATER.addEventListener('change', () => {
            if (this.#listenerFunction) {
                console.debug('theater: unregistered listener');
                document.removeEventListener('pointermove', this.#listenerFunction);
                this.#listenerFunction = null;
            }

            if (Setting.THEATER.checked) {
                console.debug('theater: registered timer and listener');
                document.addEventListener('pointermove', this.#listenerFunction = () => this.#onMove());
                this.#startTimer();
                return;
            } else {
                clearInterval(this.#enableTimer);
                this.#deactivate();
            }
        });
    }

    toggle() {
        console.debug('theater: toggled setting');
        setSettingChecked(Setting.THEATER, !Setting.THEATER.checked);
        if (Setting.THEATER.checked) {
            createToast('fullscreen', vars.tTheaterModeEnabled, vars.tTheaterModeDisabled);
        } else {
            createToast('fullscreen-exit', vars.tTheaterModeDisabled, vars.tTheaterModeEnabled);
        }
    }

    #onMove() {
        clearTimeout(this.#enableTimer);
        this.#startTimer();
        requestAnimationFrame(() => {
            this.#deactivate();
        });
    }

    #startTimer() {
        // Activate theater mode, unless aborted by a mouse move
        this.#enableTimer = setTimeout(() => this.#activate(), THEATER_TIMEOUT);
    }

    #activate() {
        document.body.classList.add('theater');
    }

    #deactivate() {
        document.body.classList.remove('theater');
    }
}

export const theater = new Theater();
