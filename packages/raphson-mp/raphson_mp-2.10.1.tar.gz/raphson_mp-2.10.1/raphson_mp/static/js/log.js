const scrollButton = /** @type {HTMLButtonElement} */ (document.getElementById('scroll-button'));
scrollButton.addEventListener('click', () => {
    window.scroll({top: document.body.scrollHeight, behavior: 'smooth'})
})
