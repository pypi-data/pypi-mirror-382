"""
Occasionally, lyrics contain multi-byte unicode characters in place of normal ASCII characters. Probably to detect
when the lyrics are scraped and copied to some other website. It results in ugly rendering with the default music
player font, so we want to replace them by the appropriate characters.

The replacement is only performed if less than 25% of the text is a non-ASCII character. We don't want to
accidentally mangle text that uses unicode characters properly (e.g. Russian)
"""

import logging

_LOGGER = logging.getLogger("unicodefixer")

_TABLE: dict[int, str] = {
    0x0435: "e",
    0x0417: "3",
}


def fix(text: str):
    if sum(1 for c in text if ord(c) > 255) < len(text) / 4:
        text = text.translate(_TABLE)

        left_over = [c for c in text if ord(c) > 255]
        if left_over:
            _LOGGER.warning("unicode characters left over after translation: %s", " ".join(left_over))

    return text
