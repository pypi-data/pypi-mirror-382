from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, unique
from sqlite3 import Connection
from typing import TypedDict, cast, overload

from aiohttp import web
from typing_extensions import override

from raphson_mp.server import db, i18n, settings, theme

AUTH_TOKEN_EXPIRY_SECONDS = 3 * 30 * 24 * 60 * 60  # 3 months
TOKEN_COOKIE = "token"


log = logging.getLogger(__name__)


class PasswordHashDict(TypedDict):
    alg: str
    n: int
    r: int
    p: int
    salt: str
    hash: str


async def _hash_password(password: str):
    # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt
    salt_bytes = os.urandom(32)
    n = 2**14
    r = 8
    p = 5
    hash_bytes = await asyncio.to_thread(hashlib.scrypt, password.encode(), salt=salt_bytes, n=n, r=r, p=p)
    password_dict: PasswordHashDict = {
        "alg": "scrypt",
        "n": n,
        "r": r,
        "p": p,
        "salt": base64.b64encode(salt_bytes).decode(),
        "hash": base64.b64encode(hash_bytes).decode(),
    }
    return json.dumps(password_dict)


def _verify_hash(hashed_password: str, password: str):
    if hashed_password.startswith("$2b"):
        log.warning("user attempted to log in with legacy bcrypt password")
        log.warning("this is no longer possible, please set a new password")
        return False

    hash_dict = cast(PasswordHashDict, json.loads(hashed_password))
    if hash_dict["alg"] == "scrypt":
        hash_bytes = hashlib.scrypt(
            password.encode(),
            salt=base64.b64decode(hash_dict["salt"]),
            n=hash_dict["n"],
            r=hash_dict["r"],
            p=hash_dict["p"],
        )
        return hmac.compare_digest(hash_bytes, base64.b64decode(hash_dict["hash"]))

    raise ValueError("unsupported alg", hash_dict)


async def verify_password(conn: Connection, user_id: int, password: str) -> bool:
    hashed_password = cast(str | None, conn.execute("SELECT password FROM user WHERE id = ?", (user_id,)).fetchone()[0])

    if hashed_password is None:
        raise AuthError(reason=AuthErrorReason.NO_PASSWORD_SET)

    return await asyncio.to_thread(_verify_hash, hashed_password, password)


@dataclass
class Session:
    user_id: int
    token: str
    csrf_token: str
    creation_timestamp: int
    user_agent: str | None
    remote_address: str | None
    last_use: int

    @property
    def creation_date(self) -> str:
        """
        When session was created, formatted as time ago string
        """
        seconds_ago = self.creation_timestamp - int(time.time())
        return i18n.format_timedelta(seconds_ago, add_direction=True)

    @property
    def last_use_ago(self) -> str | i18n.LazyString:
        """
        When account was last used, formatted as time ago string
        """
        seconds_ago = int(time.time()) - self.last_use
        if seconds_ago < 3600:
            return i18n.gettext_lazy("Recently")
        return i18n.format_timedelta(-seconds_ago, add_direction=True, granularity="hour")

    @property
    def program(self) -> str | None:
        """
        Last program string, based on user agent string
        """
        if self.user_agent is None:
            return "?"

        if "Music-Player-Android" in self.user_agent:
            return "Raphson Music Player, Android"

        if self.user_agent.startswith("raphson-music-player"):
            return "Raphson Music Player"

        # old versions
        if "DanielKoomen/WebApp" in self.user_agent:
            return "Raphson Music Player"

        if self.user_agent == "rmp-playback-server" or self.user_agent == "Raphson-Music-Headless":
            return "Headless player"

        if self.user_agent.startswith("gvfs"):
            return "Gnome Files"

        if self.user_agent.startswith("Microsoft-WebDAV-MiniRedir"):
            return "Windows WebDAV"

        if "kioworker" in self.user_agent:
            return "KDE"

        if self.user_agent.startswith("DAVx5"):
            return "DAVx5"

        if self.user_agent == "client test suite":
            return "Tests"

        browsers = ["Firefox", "Chromium", "Chrome", "Vivaldi", "Opera", "Safari", "Ladybird"]
        systems = ["Windows", "macOS", "Android", "iOS", "Ubuntu", "Debian", "Fedora", "Linux"]

        browser = None
        for maybe_browser in browsers:
            if maybe_browser in self.user_agent:
                browser = maybe_browser
                break

        system = None
        for maybe_system in systems:
            if maybe_system in self.user_agent:
                system = maybe_system
                break

        if browser and system:
            return f"{browser}, {system}"
        elif browser:
            return browser
        elif system:
            return system
        else:
            log.warning("could not identify user agent: %s", self.user_agent)
            return "?"

    def set_cookie(self, response: web.Response):
        response.set_cookie(TOKEN_COOKIE, self.token, max_age=3600 * 24 * 30, samesite="Lax", httponly=True)


class PrivacyOption(Enum):
    NONE = None  # TODO change to empty string
    AGGREGATE = "aggregate"
    HIDDEN = "hidden"


class User(ABC):
    user_id: int
    username: str
    nickname: str | None
    admin: bool
    primary_playlist: str | None
    language: str | None
    privacy: PrivacyOption
    theme: str

    @property
    @abstractmethod
    def csrf(self) -> str:
        """Get CSRF token for current session"""

    @abstractmethod
    def sessions(self) -> list[Session]:
        """Get all user sessions"""

    @abstractmethod
    async def update_password(self, conn: Connection, new_password: str) -> None:
        """Change user password and delete all existing sessions."""

    @abstractmethod
    async def update_username(self, conn: Connection, new_username: str) -> None:
        """Change username"""

    @overload
    @staticmethod
    def get(conn: Connection, *, session: Session) -> User: ...

    @overload
    @staticmethod
    def get(conn: Connection, *, user_id: int) -> User: ...

    @staticmethod
    def get(conn: Connection, *, session: Session | None = None, user_id: int | None = None) -> User:
        if session is not None and user_id is None:
            real_user_id = session.user_id
        elif session is None and user_id is not None:
            real_user_id = user_id
        else:
            raise ValueError("either session or user_id must be provided")

        assert isinstance(real_user_id, int)

        if settings.offline_mode:
            assert real_user_id == 0
            return OFFLINE_DUMMY_USER
        else:
            username, nickname, admin, primary_playlist, language, privacy, theme = conn.execute(
                "SELECT username, nickname, admin, primary_playlist, language, privacy, theme FROM user WHERE id = ?",
                (real_user_id,),
            ).fetchone()
            return StandardUser(
                conn,
                session,
                real_user_id,
                username,
                nickname,
                admin == 1,
                primary_playlist,
                language,
                PrivacyOption(privacy),
                theme,
            )

    @staticmethod
    async def create(conn: Connection, username: str, password: str, admin: bool = False):
        assert not settings.offline_mode

        hashed_password = await _hash_password(password)
        conn.execute(
            "INSERT INTO user (username, password, admin) VALUES (?, ?, ?)", (username, hashed_password, admin)
        )


@dataclass
class StandardUser(User):
    conn: Connection
    session: Session | None
    user_id: int
    username: str
    nickname: str | None
    admin: bool
    primary_playlist: str | None
    language: str | None
    privacy: PrivacyOption
    theme: str

    @override
    def sessions(self) -> list[Session]:
        results = self.conn.execute(
            """
            SELECT user, token, csrf_token, creation_date, user_agent, remote_address, last_use
            FROM session WHERE user=?
            """,
            (self.user_id,),
        ).fetchall()
        return [Session(*row) for row in results]

    @property
    @override
    def csrf(self) -> str:
        if not self.session:
            raise ValueError("No session is known for this user")
        return self.session.csrf_token

    @override
    async def update_password(self, conn: Connection, new_password: str) -> None:
        password_hash = await _hash_password(new_password)
        conn.execute("UPDATE user SET password=? WHERE id=?", (password_hash, self.user_id))
        conn.execute("DELETE FROM session WHERE user=?", (self.user_id,))
        conn.execute("DELETE FROM user_webauthn WHERE user=?", (self.user_id,))

    @override
    async def update_username(self, conn: Connection, new_username: str) -> None:
        self.username = new_username
        conn.execute("UPDATE user SET username=? WHERE id=?", (new_username, self.user_id))


class OfflineUser(User):
    def __init__(self) -> None:
        self.user_id: int = 0
        self.username: str = "offline_user"
        self.nickname: str | None = None
        self.admin: bool = True
        self.primary_playlist: str | None = None
        self.language: str | None = None
        self.privacy: PrivacyOption = PrivacyOption.NONE
        self.theme: str = theme.DEFAULT_THEME
        self._csrf: str = secrets.token_urlsafe()

    @override
    def sessions(self) -> list[Session]:
        return []

    @property
    @override
    def csrf(self) -> str:
        return self._csrf

    @override
    async def update_password(self, conn: Connection, new_password: str) -> None:
        raise NotImplementedError

    @override
    async def update_username(self, conn: Connection, new_username: str) -> None:
        raise NotImplementedError


OFFLINE_DUMMY_USER = OfflineUser()


@unique
class AuthErrorReason(Enum):
    NO_TOKEN = 1
    INVALID_TOKEN = 2
    ADMIN_REQUIRED = 3
    NO_PASSWORD_SET = 4

    @property
    def message(self):
        """
        Get translated message corresponding to auth error reason
        """
        if self is AuthErrorReason.NO_TOKEN:
            return i18n.gettext("You are not logged in, please log in.")
        elif self is AuthErrorReason.INVALID_TOKEN:
            return i18n.gettext("Your current session is invalid, please log in again.")
        elif self is AuthErrorReason.ADMIN_REQUIRED:
            return i18n.gettext("Your are not an administrator, but this page requires administrative privileges")
        elif self is AuthErrorReason.NO_PASSWORD_SET:
            return i18n.gettext(
                "Your account has no password set. Either you have never set a password, or your old password expired. Please contact a system administrator."
            )
        return ValueError()

    @property
    def http_status(self):
        if self in {AuthErrorReason.NO_TOKEN, AuthErrorReason.INVALID_TOKEN, AuthErrorReason.NO_PASSWORD_SET}:
            return 401  # no valid credentials provided
        return 403  # valid credentials are provided, but forbidden for some other reason


@dataclass(kw_only=True)
class AuthError(Exception):
    reason: AuthErrorReason
    redirect_to_login: bool = False


async def create_session(conn: Connection, request: web.Request, user: int | User) -> Session:
    user_id = user if isinstance(user, int) else user.user_id
    token = secrets.token_urlsafe().replace("-", "")  # remove dashes so it is easier to copy
    csrf_token = secrets.token_urlsafe()
    remote_addr = request.remote
    user_agent = request.headers.get("User-Agent")

    conn.execute(
        """
        INSERT INTO session (user, token, csrf_token, creation_date, user_agent, remote_address, last_use)
        VALUES (?, ?, ?, unixepoch(), ?, ?, unixepoch())
        """,
        (user_id, token, csrf_token, user_agent, remote_addr),
    )
    session = Session(user_id, token, csrf_token, int(time.time()), None, None, int(time.time()))
    await update_session(conn, request, session)
    return session


async def update_session(conn: Connection, request: web.Request, session: Session):
    """
    Update last login and user agent for a session
    """
    remote_addr = request.remote
    user_agent = request.headers.get("User-Agent")
    log.info("update session: %s %s", remote_addr, user_agent)
    conn.execute(
        """
        UPDATE session
        SET user_agent=?, remote_address=?, last_use=unixepoch()
        WHERE token=?
        """,
        (user_agent, remote_addr, session.token),
    )


async def log_in(request: web.Request, conn: Connection, username: str, password: str) -> Session | None:
    """
    Log in using username and password.
    Args:
        conn: Read-write database connection
        username
        password
        user_agent
        remote_addr
    Returns: Session token, or None if the username+password combination is not valid
    """
    if settings.offline_mode:
        raise RuntimeError("Login not available in offline mode")

    result = cast(tuple[int] | None, conn.execute("SELECT id FROM user WHERE username=?", (username,)).fetchone())

    if result is None:
        log.warning("Login attempt with non-existent username: '%s'", username)
        return None

    (user_id,) = result

    if not await verify_password(conn, user_id, password):
        log.warning("Failed login for user %s", username)
        return None

    session = await create_session(conn, request, user_id)
    log.info("successful login for user %s", username)

    return session


async def verify_token(request: web.Request, token: str) -> Session | None:
    """
    Verify session token, and return corresponding user
    Args:
        conn: Read-only database connection
        token: Session token to verify
    Returns: User object if session token is valid, or None if invalid
    """
    with db.MUSIC.connect() as conn:
        result = conn.execute(
            """
            SELECT user, token, csrf_token, creation_date, user_agent, remote_address, last_use
            FROM session
            WHERE token=?
            """,
            (token,),
        ).fetchone()

        if result is None:
            log.warning("Invalid auth token: %s", token)
            return None

        session = Session(*result)

        if time.time() - session.last_use > 1800:
            await update_session(conn, request, session)

    return session


async def _verify_csrf(request: web.Request, expected_csrf_token: str):
    try:
        if request.content_type == "application/json":
            csrf_token = cast(str, (await request.json())["csrf"])
        elif request.content_type == "application/x-www-form-urlencoded" or (
            request.content_type and request.content_type.startswith("multipart/form-data")
        ):
            csrf_token = cast(str, (await request.post())["csrf"])
        else:
            raise KeyError()
    except KeyError:
        raise web.HTTPBadRequest(reason="missing CSRF token")

    if not hmac.compare_digest(csrf_token, expected_csrf_token):
        raise web.HTTPBadRequest(reason="invalid CSRF token")


async def verify_auth_cookie(
    conn: Connection,
    request: web.Request,
    require_admin: bool = False,
    redirect_to_login: bool = False,
    require_csrf: bool = False,
) -> User:
    """
    Verify auth token sent as cookie, raising AuthError if missing or not valid.
    Args:
        conn: Read-only database connection
        request
        require_admin: Whether logging in as a non-admin account should be treated as an authentication failure
        redirect_to_login: Whether the user should sent a redirect if authentication failed, instead
                           of showing a 403 page. Should be set to True for pages, and to False for API endpoints.
        require_csrf
    """
    if settings.offline_mode:
        return OFFLINE_DUMMY_USER

    token: str | None = None

    if auth_header := request.headers.get("Authorization"):
        require_csrf = False  # CSRF is only an issue with cookies
        if auth_header.startswith("Basic "):
            credentials = auth_header[len("Basic ") :]
            credentials = base64.b64decode(credentials).decode()
            token = credentials.partition(":")[2]
        elif auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :]
    elif "token" in request.cookies:
        token = request.cookies["token"]

    if token is None:
        log.info("request to %s without authentication from %s", request.rel_url, request.remote)
        raise AuthError(
            reason=AuthErrorReason.NO_TOKEN,
            redirect_to_login=redirect_to_login,
        )

    session = await verify_token(request, token)
    if session is None:
        raise AuthError(
            reason=AuthErrorReason.INVALID_TOKEN,
            redirect_to_login=redirect_to_login,
        )

    if require_csrf:
        await _verify_csrf(request, session.csrf_token)

    user = User.get(conn, session=session)

    if require_admin and not user.admin:
        raise AuthError(reason=AuthErrorReason.ADMIN_REQUIRED)

    return user


async def prune_old_session_tokens():
    """
    Prune old session tokens
    Args:
        conn: Read-write database connection
    Returns: Number of deleted tokens
    """
    with db.MUSIC.connect() as conn:
        delete_before = int(time.time()) - AUTH_TOKEN_EXPIRY_SECONDS
        count = conn.execute("DELETE FROM session WHERE last_use < ?", (delete_before,)).rowcount
        log.info("deleted %s session tokens", count)
