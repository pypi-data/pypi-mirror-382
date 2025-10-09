export const Setting = {
    QUEUE_SIZE: /** @type {HTMLInputElement} */ (document.getElementById("settings-queue-size")),
    AUDIO_TYPE: /** @type {HTMLSelectElement} */ (document.getElementById("settings-audio-type")),
    VOLUME: /** @type {HTMLInputElement} */ (document.getElementById("settings-volume")),
    QUEUE_REMOVAL_BEHAVIOUR: /** @type {HTMLSelectElement} */ (document.getElementById("settings-queue-removal-behaviour")),
    AUDIO_GAIN: /** @type {HTMLInputElement} */ (document.getElementById("settings-audio-gain")),
    MEME_MODE: /** @type {HTMLInputElement} */ (document.getElementById("settings-meme-mode")),
    NEWS: /** @type {HTMLInputElement} */ (document.getElementById("settings-news")),
    THEATER: /** @type {HTMLInputElement} */ (document.getElementById("settings-theater")),
    TOUCH: /** @type {HTMLInputElement} */ (document.getElementById("settings-touch")),
    VISUALISER: /** @type {HTMLInputElement} */ (document.getElementById("settings-visualiser")),
    LYRICS: /** @type {HTMLInputElement} */ (document.getElementById("settings-lyrics")),
    NAME: /** @type {HTMLInputElement} */ (document.getElementById("settings-name")),
    AUTO_CLEAR_QUEUE: /** @type {HTMLInputElement} */ (document.getElementById("settings-auto-clear-queue")),
};

/**
 * @param {HTMLInputElement | HTMLSelectElement} elem
 * @returns {boolean}
 */
export function settingIsCheckbox(elem) {
    return elem.matches('input[type="checkbox"]');
}

/**
 * @param {HTMLInputElement | HTMLSelectElement} elem
 * @param {string} value
 */
export function setSettingValue(elem, value) {
    elem.value = value;
    elem.dispatchEvent(new Event('change'));
}

/**
 * @param {HTMLInputElement | HTMLSelectElement} elem
 * @param {boolean} checked
 */
export function setSettingChecked(elem, checked) {
    if (!(elem instanceof HTMLInputElement)) throw new Error();
    elem.checked = checked;
    elem.dispatchEvent(new Event('change'));
}

export function getImageQuality() {
    return Setting.AUDIO_TYPE.value == 'webm_opus_high' ? 'high' : 'low';
}

// Touch mode
Setting.TOUCH.addEventListener('change', () => document.body.classList.toggle('touch', Setting.TOUCH.checked));

{
    // Listener to update value in local storage
    for (const elem of Object.values(Setting)) {
        elem.addEventListener('change', () => {
            const isCheckbox = elem instanceof HTMLInputElement && settingIsCheckbox(elem);
            const value = isCheckbox ? elem.checked + '' : elem.value;
            window.localStorage.setItem(elem.id, value);
        });
    }

    // Load settings from local storage on page load
    // Slightly later, so other code can subscribe to the 'change' event first
    setTimeout(() => {
        for (const elem of Object.values(Setting)) {
            if (elem.dataset.restore == 'false') {
                continue;
            }

            // Initialize input form local storage
            const value = window.localStorage.getItem(elem.id);
            if (value !== null) {
                if (settingIsCheckbox(elem)) {
                    setSettingChecked(elem, value === 'true');
                } else {
                    setSettingValue(elem, value);
                }
            }
        }
    }, 0);
}
