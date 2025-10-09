import { windows } from "./window.js";
import { queue } from "./queue.js";
import { player, playerControls } from "./player.js";
import { lyrics } from "./lyrics.js";
import { theater } from "./theater.js";
import { visualiser } from "./visualise.js";
import { registerHotKeyListener } from "../util.js";

const VOLUME_HOTKEY_CHANGE = 0.05;

registerHotKeyListener(key => {
    if (key == 'p' || key == ' ') {
        player.isPaused() ? player.play() : player.pause();
    } else if (key == 'ArrowLeft') {
        queue.previous();
    } else if (key == 'ArrowRight') {
        queue.next();
    } else if (key == 'ArrowUp') {
        playerControls.setVolume(playerControls.getVolume() + VOLUME_HOTKEY_CHANGE);
    } else if (key == 'ArrowDown') {
        playerControls.setVolume(playerControls.getVolume() - VOLUME_HOTKEY_CHANGE);
    } else if (key == '.' || key == '>') {
        player.seekRelative(3);
    } else if (key == ',' || key == '<') {
        player.seekRelative(-3);
    } else if (key == 'Escape') {
        windows.closeTop();
    } else if (key == '/') {
        document.getElementById('open-window-search')?.click();
    } else if (key == "c") {
        queue.clear();
    } else if (key == "l") {
        lyrics.toggleLyrics();
    } else if (key == "t") {
        theater.toggle();
    } else if (key == "v") {
        visualiser.toggleSetting();
    } else if (key == "d") {
        windows.open('window-debug');
    }
});
