import base64
import hashlib
import json
import secrets
from sqlite3 import Connection
from typing import cast

from aiohttp import web
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    SECP256K1,
    generate_private_key,
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from raphson_mp.server import cache

from . import TEST_USERNAME, T_client

private_key = generate_private_key(SECP256K1())
public_key_der = private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)


def _challenge():
    challenge = secrets.token_urlsafe()
    cache.memory_store("webauthn" + challenge, b"", 15 * 60)
    return challenge


def _client_data_b64(type: str, challenge: str, origin: str = "http://127.0.0.1") -> str:
    client_data = {
        "type": type,
        "challenge": base64.urlsafe_b64encode(challenge.encode()).rstrip(b"=").decode(),
        "origin": origin,
    }
    return base64.b64encode(json.dumps(client_data).encode()).decode()


async def test_setup(http_client: T_client, csrf_token: str, conn: Connection):
    conn.execute("DELETE FROM user_webauthn WHERE user = (SELECT id FROM user WHERE username = ?)", (TEST_USERNAME,))

    async with http_client.post(
        "/account/webauthn_setup",
        json={
            "client": _client_data_b64("webauthn.create", _challenge()),
            "public_key": base64.b64encode(public_key_der).decode(),
            "csrf": csrf_token,
        },
    ) as response:
        assert response.status == web.HTTPNoContent.status_code


async def test_setup_invalid_type(http_client: T_client, csrf_token: str):
    async with http_client.post(
        "/account/webauthn_setup",
        json={
            "client": _client_data_b64("webauthn.get", _challenge()),
            "public_key": base64.b64encode(public_key_der).decode(),
            "csrf": csrf_token,
        },
    ) as response:
        assert response.status == web.HTTPBadRequest.status_code
        assert await response.text() == "400: invalid type"


async def test_setup_invalid_challenge(http_client: T_client, csrf_token: str):
    async with http_client.post(
        "/account/webauthn_setup",
        json={
            "client": _client_data_b64("webauthn.create", secrets.token_urlsafe()),
            "public_key": base64.b64encode(public_key_der).decode(),
            "csrf": csrf_token,
        },
    ) as response:
        assert response.status == web.HTTPBadRequest.status_code
        assert await response.text() == "400: invalid challenge"


async def test_login(http_client: T_client, conn: Connection):
    # set up token
    conn.execute(
        "INSERT INTO user_webauthn VALUES ((SELECT id FROM user WHERE username=?), ?)",
        (TEST_USERNAME, public_key_der),
    )

    authenticator_data = secrets.token_bytes()  # unused attestation data, just needed as part of signature
    client_data = _client_data_b64("webauthn.get", _challenge())
    signed_data = authenticator_data + hashlib.sha256(base64.b64decode(client_data)).digest()
    signature = private_key.sign(signed_data, ECDSA(SHA256()))
    user_id = cast(int, conn.execute("SELECT id FROM user WHERE username = ?", (TEST_USERNAME,)).fetchone()[0])
    user_handle = base64.b64encode(str(user_id).encode()).decode()

    async with http_client.post(
        "/auth/webauthn_login",
        json={
            "authenticator_data": base64.b64encode(authenticator_data).decode(),
            "client_data": client_data,
            "signature": base64.b64encode(signature).decode(),
            "user_handle": user_handle,
        },
    ) as response:
        assert response.status == web.HTTPNoContent.status_code, await response.text()
        assert "token" in response.cookies
