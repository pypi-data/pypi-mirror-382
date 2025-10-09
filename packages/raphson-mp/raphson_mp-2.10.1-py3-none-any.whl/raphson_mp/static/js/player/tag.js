import { music } from "../api.js";
import { browse, TagBrowse } from "./browse.js";

async function updateTagCheckboxes() {
    const tags = await music.tags();

    const newChildren = [];

    let i = 0;
    for (const tag of tags) {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.classList.add('tag-checkbox');
        checkbox.id = 'tag-checkbox-' + i;
        checkbox.dataset.tag = tag;
        checkbox.checked = true;
        newChildren.push(checkbox);
        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        const link = document.createElement('a');
        link.textContent = tag;
        link.onclick = event => {
            event.preventDefault();
            browse.browse(new TagBrowse(tag));
        };
        label.appendChild(link);
        newChildren.push(label);
        newChildren.push(document.createElement('br'));
        i++;
    }

    const checkboxesContainer = /** @type {HTMLElement} */ (document.getElementById('tag-checkboxes'));
    checkboxesContainer.replaceChildren(...newChildren);
}

updateTagCheckboxes();

function getCheckboxes() {
    return /** @type{HTMLCollectionOf<HTMLInputElement>} */ (document.getElementsByClassName('tag-checkbox'));
}

export function getTagFilter() {
    const mode = /** @type{HTMLInputElement} */ (document.getElementById('tag-mode')).value;
    if (mode == 'none') {
        return {};
    }

    const tags = [];
    for (const checkbox of getCheckboxes()) {
        if (checkbox.checked) {
            tags.push(checkbox.dataset.tag);
        }
    }

    return {tag_mode: mode, tags: tags};
}

function areAllCheckboxesChecked() {
    for (const checkbox of getCheckboxes()) {
        if (!checkbox.checked) {
            return false;
        }
    }
    return true;
}

/**
 * @param {boolean} checked
 */
function setAllCheckboxesChecked(checked) {
    for (const checkbox of getCheckboxes()) {
        checkbox.checked = checked;
    }
}

const selectAllTagsButton = /** @type {HTMLButtonElement} */ (document.getElementById('tag-select-all'));
selectAllTagsButton.addEventListener('click', () => {
    setAllCheckboxesChecked(!areAllCheckboxesChecked());
});
