/** @type {import("./types").Vars} */
export const vars = JSON.parse(/** @type {string} */(/** @type {HTMLScriptElement} */ (document.getElementById('vars')).textContent));

/**
 * @param {number} seconds
 * @returns {string} formatted duration
 */
export function durationToString(seconds) {
    const isoString = new Date(1000 * seconds).toISOString();
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = parseInt(isoString.substring(11, 13)) + (days * 24);
    const mmss = isoString.substring(14, 19);
    if (hours == 0) {
        return mmss;
    } else {
        return hours + ':' + mmss;
    }
}

/**
 * @param {number} seconds
 * @returns {string}
 */
export function timestampToString(seconds) {
    if (seconds == 0) {
        return '-';
    } else {
        return new Date(1000 * seconds).toLocaleString();
    }
}

/**
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
export function randInt(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

/**
 * @template T
 * @param {Array<T>} arr
 * @returns {T}
 */
export function choice(arr) {
    return arr[randInt(0, arr.length)];
}

/**
 * @param {number} number
 * @returns {string}
 */
export function formatLargeNumber(number) {
    if (number > 1_000_000) {
        return (number / 1_000_000).toFixed(1) + 'M';
    } else if (number > 1_000) {
        return (number / 1_000).toFixed(1) + 'k';
    } else {
        return number + '';
    }
}

/**
 * @param {string} iconName
 * @returns {HTMLDivElement}
 */
export function createIcon(iconName) {
    const icon = document.createElement('div');
    icon.classList.add('icon', 'icon-' + iconName);
    return icon;
}

/**
 * Create button element containing an icon
 * @param {string} iconName
 * @param {string|null} tooltip
 * @returns {HTMLButtonElement}
 */
export function createIconButton(iconName, tooltip = null) {
    const button = document.createElement('button');
    button.classList.add('icon-button');
    button.appendChild(createIcon(iconName));
    if (tooltip) {
        button.title = tooltip;
    }
    return button;
}

/**
 * Replace icon in icon button
 * @param {HTMLButtonElement} iconButton
 * @param {string} iconName
 */
export function replaceIconButton(iconButton, iconName) {
    const icon = /** @type {HTMLElement} */ (iconButton.firstElementChild);
    icon.classList.remove(...icon.classList.values());
    icon.classList.add('icon', 'icon-' + iconName);
    if (iconName == 'loading') {
        icon.classList.add('spinning');
    } else {
        icon.classList.remove('spinning');
    }
}

// https://stackoverflow.com/a/2117523
export function uuidv4() {
    return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
        (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
    );
}

/**
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
export function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

/**
 * Throw error if response status code is an error code
 * @param {Response} response
 */
export function checkResponseCode(response) {
    if (!response.ok) {
        throw Error('response code ' + response.status + ' for url ' + response.url);
    }
}

/**
 * @param {string} url
 * @param {object} postDataObject
 * @returns {Promise<Response>}
 */
export async function jsonPost(url, postDataObject, checkError = true) {
    postDataObject.csrf = vars.csrfToken;
    const options = {
        method: 'POST',
        body: JSON.stringify(postDataObject),
        headers: new Headers({
            'Content-Type': 'application/json'
        }),
    };
    const response = await fetch(new Request(url, options));
    if (checkError) {
        checkResponseCode(response);
    }
    return response;
}

/**
 *
 * @param {string} url
 * @param {boolean} checkError
 * @returns {Promise<any>}
 */
export async function jsonGet(url, checkError = true) {
    const options = {
        headers: new Headers({
            'Accept': 'application/json'
        }),
    };
    const response = await fetch(new Request(url, options));
    if (checkError) {
        checkResponseCode(response);
    }
    if (response.status == 204) {  // HTTP No Content
        return null;
    }
    return await response.json();
}

function errorObjectToJson(error) {
    if (error instanceof ErrorEvent) {
        return {
            type: 'ErrorEvent',
            message: error.message,
            file: error.filename,
            line: error.lineno,
            error: errorObjectToJson(error.error),
        };
    }

    if (error instanceof PromiseRejectionEvent) {
        return {
            type: 'PromiseRejectionEvent',
            reason: errorObjectToJson(error.reason),
        };
    }

    if (['string', 'number', 'boolean'].includes(typeof (error))) {
        return {
            type: 'literal',
            value: error,
        };
    }

    if (error instanceof Error) {
        return {
            type: 'Error',
            name: error.name,
            message: error.message,
            stack: error.stack,
        };
    }

    if (error == null) {
        return null;
    }

    return {
        name: 'unknown error object',
        type: typeof (error),
        string: String(error),
    };
}

export async function sendErrorReport(error) {
    console.error(error);
    try {
        const errorJson = JSON.stringify(errorObjectToJson(error));
        await fetch('/report_error', { method: 'POST', body: errorJson, headers: { 'Content-Type': 'application/json' } });
        createToast('icon-close', vars.tErrorOccurredReported);
    } catch (error2) {
        // need to catch errors, this function must never throw an error or a loop is created
        console.error('unable to report error:', error2);
        createToast('icon-close', vars.tErrorOccurredUnreported);
    }
}

// https://stackoverflow.com/a/30546115/4833737
/**
 * @param {string} s
 * @returns {number}
 */
function cssToMS(s) {
    return parseFloat(s) * (/\ds$/.test(s) ? 1000 : 1);
}

export const TRANSITION_DURATION = cssToMS(window.getComputedStyle(document.body).getPropertyValue('--transition-duration'));

const TOAST_HIDE_TIME = 5000;
const TOAST_CONTAINER = /** @type {HTMLDivElement} */ (document.getElementById('toasts'));

/**
 * @param {string} text
 */
export function removeToast(text) {
    for (const child of TOAST_CONTAINER.children) {
        if (child.textContent == text) {
            child.remove();
            break;
        }
    }
}

/**
 * @param {string} iconName
 * @param {string} text
 * @param {string | null} replace
 */
export function createToast(iconName, text, replace = null) {
    // Do not create duplicate toast
    for (const child of TOAST_CONTAINER.children) {
        if (child.textContent == text) {
            return;
        }
    }

    // Optionally, replace existing toast
    if (replace) {
        removeToast(replace);
    }

    const textElem = document.createElement('div');
    textElem.textContent = text;

    const toastElem = document.createElement("div");
    toastElem.classList.add("toast", "hidden", "box", "padding");
    toastElem.append(createIcon(iconName), textElem);

    TOAST_CONTAINER.prepend(toastElem);
    setTimeout(() => toastElem.classList.remove("hidden"), 0);
    setTimeout(() => toastElem.classList.add("hidden"), TOAST_HIDE_TIME);
    setTimeout(() => toastElem.remove(), TOAST_HIDE_TIME + TRANSITION_DURATION);
}

/**
 * @param {(key: string) => void} callback
 */
export function registerHotKeyListener(callback) {
    document.addEventListener('keydown', event => {
        // Ignore hotkey when in combination with modifier keys
        if (event.ctrlKey || event.altKey || event.metaKey) {
            return;
        }

        const key = event.key;

        // Ignore F<N> keys
        if (event.key.length >= 2 && event.key[0] == 'F') {
            return;
        }

        // Don't perform hotkey actions when user is typing in a text field
        // But do still allow escape key
        if (document.activeElement &&
            ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) &&
            key !== 'Escape') {
            console.debug('hotkey: ignoring keypress:', key);
            return;
        }

        event.preventDefault();

        callback(key);
    });
}

const prefetching = new Set();

/**
 * @param {string} url
 */
export async function prefetch(url) {
    if (!prefetching.has(url)) {
        prefetching.add(url);
        try {
            await fetch(url);
        } finally {
            prefetching.delete(url);
        }
    }
}

/**
 * @template {Array<any>} CallbackArgs
 * @param {number} delay
 * @param {boolean} deadline
 * @param {(...args: CallbackArgs) => void} callback
 * @returns {(...args: CallbackArgs) => void}
 */
export function throttle(delay, deadline, callback) {
    let timer = 0;

    if (deadline) {
        return (...args) => {
            if (timer == 0) {
                timer = setTimeout(() => {
                    timer = 0;
                    callback(...args);
                }, delay);
            }
        }
    } else {
        return (...args) => {
            if (timer != 0) clearTimeout(timer);

            timer = setTimeout(() => {
                timer = 0;
                callback(...args);
            }, delay);
        }
    }
}
