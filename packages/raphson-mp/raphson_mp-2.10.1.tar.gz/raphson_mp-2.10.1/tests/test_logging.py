import logging
import random

from raphson_mp.server.logconfig import error_logfile_path


def _contains_message(message: str):
    errors_path = error_logfile_path()
    size = errors_path.stat().st_size
    with errors_path.open("rb") as fp:
        fp.seek(size - (len(message) + 1))
        return message in fp.read().decode()


def test_errors_file():
    logger = logging.getLogger(__name__)

    message = "test " + random.randbytes(4).hex()
    logger.warning(message)
    assert _contains_message(message)

    message = "test " + random.randbytes(4).hex()
    logger.error(message)
    assert _contains_message(message)

    message = "test " + random.randbytes(4).hex()
    logger.info(message)
    assert not _contains_message(message)
