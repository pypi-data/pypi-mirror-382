import { player } from "./player.js";
import { eventBus, MusicEvent } from "./event.js";
import { vars, createToast } from "../util.js";
import { setSettingChecked, Setting } from "./settings.js";

class Visualiser {
    // Settings
    #barWidth = 10;
    #minFreq = 50;
    #maxFreq = 14000;
    #xToFreqExp = 2;

    #dataArray = new Uint8Array(player.fftSize);
    #canvas = /** @type {HTMLCanvasElement} */ (document.getElementById('visualiser'));
    /** @type {number | null} */
    #taskId = null;

    constructor() {
        Setting.VISUALISER.addEventListener('change', () => this.updateVisualiserState());
        eventBus.subscribe(MusicEvent.PLAYER_PLAY, () => this.updateVisualiserState());
        eventBus.subscribe(MusicEvent.PLAYER_PAUSE, () => this.updateVisualiserState());
        document.addEventListener('visibilitychange', () => this.updateVisualiserState());
    }

    toggleSetting() {
        setSettingChecked(Setting.VISUALISER, !Setting.VISUALISER.checked);
        if (Setting.VISUALISER.checked) {
            createToast('chart-bar', vars.tVisualiserEnabled, vars.tVisualiserDisabled);
        } else {
            createToast('chart-bar', vars.tVisualiserDisabled, vars.tVisualiserEnabled);
        }
    }

    updateVisualiserState() {
        if (Setting.VISUALISER.checked && !player.isPaused() && document.visibilityState == 'visible') {
            visualiser.#start();
        } else {
            visualiser.#stop();
        }
    }

    #stop() {
        console.debug('visualiser: stopped');
        this.#canvas.style.transform = 'translateY(100%)';
        if (this.#taskId != null) {
            clearInterval(this.#taskId);
        }
        if (this.#taskId != null) {
            cancelAnimationFrame(this.#taskId);
            this.#taskId = null;
        }
    }

    #start() {
        // Prevent double animation in case start() is accidentally called twice
        if (this.#taskId != null) {
            console.warn('visualiser: was already running');
            cancelAnimationFrame(this.#taskId);
        }

        console.debug('visualiser: started');
        this.#canvas.style.transform = '';
        this.#taskId = requestAnimationFrame(() => this.#draw());
    }

    #draw() {
        if (!player.analyser) {
            return;
        }

        const height = this.#canvas.clientHeight;
        const usedHeight = Math.round(0.25 * height);
        const width = this.#canvas.clientWidth;

        this.#canvas.height = height;
        this.#canvas.width = width;

        const draw = this.#canvas.getContext('2d');
        if (draw == null) {
            throw new Error();
        }

        draw.clearRect(0, 0, height, width);
        draw.fillStyle = "white";

        player.analyser.getByteFrequencyData(this.#dataArray);

        const minBin = this.#minFreq / 48000 * player.fftSize;
        const maxBin = this.#maxFreq / 48000 * player.fftSize;
        const multiplyX = (maxBin - minBin);

        for (let x = 0; x < width; x += this.#barWidth) {
            const i = Math.floor((x / width) ** this.#xToFreqExp * multiplyX + minBin);
            const barHeight = this.#dataArray[i] * usedHeight / 256;
            draw.fillRect(x, height - barHeight, this.#barWidth, barHeight);
        }

        this.#taskId = requestAnimationFrame(() => this.#draw());
    }
}

export const visualiser = new Visualiser();
