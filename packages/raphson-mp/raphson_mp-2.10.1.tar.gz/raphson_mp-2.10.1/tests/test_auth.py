import random
import secrets
from sqlite3 import Connection
from typing import cast

from raphson_mp.server import auth, theme
from tests import TEST_USERNAME


async def test_hash():
    password = secrets.token_urlsafe(random.randint(0, 100))
    notpassword = secrets.token_urlsafe(random.randint(0, 100))
    hash = await auth._hash_password(password)
    assert auth._verify_hash(hash, password)
    assert not auth._verify_hash(hash, notpassword)


async def test_user(conn: Connection):
    user_id = cast(int, conn.execute("SELECT id FROM user WHERE username=?", (TEST_USERNAME,)).fetchone()[0])
    user = auth.User.get(conn, user_id=user_id)
    assert isinstance(user, auth.StandardUser)
    assert user.conn is conn
    assert user.user_id == user_id
    assert user.username == TEST_USERNAME
    assert user.nickname is None
    assert user.admin == False
    assert user.primary_playlist is None
    assert user.language is None
    assert user.privacy is auth.PrivacyOption.NONE
    assert user.theme == theme.DEFAULT_THEME
