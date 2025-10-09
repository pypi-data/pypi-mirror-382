from raphson_mp.server import i18n

DEFAULT_THEME = "default"
THEMES: dict[str, i18n.LazyString] = {
    "default": i18n.gettext_lazy("Default"),
    "win95": i18n.gettext_lazy("Windows 95"),
}
