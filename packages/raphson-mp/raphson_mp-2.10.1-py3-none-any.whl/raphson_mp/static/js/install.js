// @ts-ignore Non standard event; linter doesn't know of its existence
let deferredPrompt = /** @type {BeforeInstallPromptEvent | null} */ (null);

window.addEventListener('beforeinstallprompt', event => {
    // Prevents the default mini-infobar or install dialog from appearing on mobile
    event.preventDefault();

    deferredPrompt = event;

    const no = /** @type {HTMLElement} */ (document.getElementById('no-support'));
    const yes = /** @type {HTMLElement} */ (document.getElementById('yes-support'));
    yes.hidden = false;
    no.hidden = true;

    const installButton = /** @type {HTMLButtonElement} */ (document.getElementById('install-button'));
    installButton.addEventListener('click', () => {
        deferredPrompt.prompt();
    })
});
