from pathlib import Path

from raphson_mp.server import theme


def test_default_theme_exists():
    assert theme.DEFAULT_THEME in theme.THEMES


def test_files_exist():
    files = [
        theme_path.name.rstrip(".css")
        for theme_path in Path(Path(__file__).parent.parent, "raphson_mp", "static", "css", "theme").iterdir()
    ]
    for theme_name in theme.THEMES:
        assert theme_name in files, "file does not exist for theme: " + theme_name
