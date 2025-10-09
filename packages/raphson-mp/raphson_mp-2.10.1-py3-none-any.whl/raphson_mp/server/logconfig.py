from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, cast

from raphson_mp.server import settings

if TYPE_CHECKING:
    from logging.config import _DictConfigArgs  # pyright: ignore[reportPrivateUsage]


# Hardcoded settings
def get_config_dict() -> _DictConfigArgs:
    config: _DictConfigArgs = {
        "version": 1,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(process)d:%(thread)d] [%(levelname)s] [%(name)s:%(module)s:%(lineno)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
            },
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
            },
            "short": {
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "short" if settings.log_short else "default",
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["stdout"],
        },
        "disable_existing_loggers": False,
    }

    if settings.data_dir is not None:  # pyright: ignore[reportUnnecessaryComparison]
        cast(list[str], config["root"]["handlers"]).append("errors")
        config["handlers"]["errors"] = {
            "class": "logging.FileHandler",
            "filename": error_logfile_path().as_posix(),
            "level": "WARNING",
            "formatter": "detailed",
        }

    return config


def error_logfile_path():
    return Path(settings.data_dir, "errors.log")


def apply() -> None:
    """
    Apply dictionary config
    """
    import logging.config  # pylint: disable=import-outside-toplevel

    warnings.simplefilter("always")
    logging.config.dictConfig(get_config_dict())
