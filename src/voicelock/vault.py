"""Profile Vault — passphrase outer lock (F2) around a voice middle lock (F4).

The Vault is sealed by two nested AEAD layers, peeled in this order:

1. **Outer lock** — Argon2id over the typed passphrase (F2, unchanged). Opening it
   yields the non-secret helper data plus the still-sealed middle ciphertext.
2. **Middle lock** — a key reconciled from the speaker's voiceprint via the helper
   data (``middlelock``). Opening it yields the profile JSON.

Peel order is load-bearing: a wrong passphrase raises ``AuthError`` before the
voice is consulted at all, so the two reject reasons stay distinct and a wrong
passphrase never leaks whether the voice would have matched.

On-disk layout (``FORMAT_VERSION`` 2)::

    VLCK | version | opslimit | memlimit | salt | outer ciphertext
                                                  |
                    {helper_data, middle_ciphertext} sealed with the outer key
                                       |
                       {name, schema_version} sealed with the middle key

Helper data lives *inside* the outer box. It is non-secret by design, but there is
no reason to publish it at rest. A v1 (passphrase-only) vault has no voice layer
at all and is refused with ``LegacyVaultError`` — there is deliberately no
passphrase-only bypass, so "voice is now required" stays true.
"""

from __future__ import annotations

import base64
import json
import struct
from pathlib import Path

import numpy as np
from nacl import pwhash, secret, utils
from nacl.exceptions import CryptoError

from voicelock import middlelock

MAGIC = b"VLCK"
FORMAT_VERSION = 2
LEGACY_FORMAT_VERSION = 1
_SALT_BYTES = pwhash.argon2id.SALTBYTES
_OPS = pwhash.argon2id.OPSLIMIT_MODERATE
_MEM = pwhash.argon2id.MEMLIMIT_MODERATE
# magic(4) + version(1) + opslimit(8) + memlimit(8) + salt
_HEADER_LEN = 4 + 1 + 8 + 8 + _SALT_BYTES


class VaultError(Exception):
    """Base error for Vault / lock failures."""


class ValidationError(VaultError):
    """Enroll refused — empty or missing name/passphrase."""


class AuthError(VaultError):
    """Wrong passphrase — outer REJECT; no plaintext returned."""


class VoiceAuthError(VaultError):
    """Voice did not match — middle REJECT; no plaintext returned."""


class LegacyVaultError(VaultError):
    """A v1 vault predates the voice lock — re-enroll to add it."""


class NoVaultError(VaultError):
    """No Vault file at the path — Booth copy: enroll first."""


def default_vault_path() -> Path:
    return Path.home() / ".voicelock" / "vault.vl"


def enroll(
    name: str,
    passphrase: str,
    voiceprints: list[np.ndarray],
    path: Path | None = None,
) -> None:
    """Seal a profile Vault behind the passphrase and the enrolled voice.

    ``voiceprints`` are the enrollment embeddings (not audio — the DSP stays in
    ``voiceprint``), one per enrollment sentence. Always writes ``FORMAT_VERSION``.
    """
    display = (name or "").strip()
    secret_text = passphrase or ""
    if not display or not secret_text:
        raise ValidationError("Name and passphrase are required")

    vault_path = path if path is not None else default_vault_path()

    middle_secret, helper_data = middlelock.commit(voiceprints)
    middle_key = middlelock.derive_key(
        middle_secret, base64.b64decode(helper_data["salt"])
    )
    profile = _dumps({"name": display, "schema_version": 1})
    middle_ciphertext = secret.SecretBox(middle_key).encrypt(profile)

    outer_plaintext = _dumps(
        {
            "helper_data": helper_data,
            "middle_ciphertext": base64.b64encode(middle_ciphertext).decode("ascii"),
        }
    )
    salt = utils.random(_SALT_BYTES)
    outer_key = _derive_key(secret_text, salt, _OPS, _MEM)
    outer_ciphertext = secret.SecretBox(outer_key).encrypt(outer_plaintext)

    header = MAGIC + bytes([FORMAT_VERSION]) + struct.pack("<QQ", _OPS, _MEM) + salt
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_path.write_bytes(header + outer_ciphertext)


def unlock(
    passphrase: str, voiceprint: np.ndarray, path: Path | None = None
) -> str:
    """Peel the outer then the middle lock; return the enrolled display name.

    Raises ``AuthError`` for a wrong passphrase (raised *before* the voice is
    consulted), ``VoiceAuthError`` when the voice fails to reconcile or the middle
    box will not open, ``LegacyVaultError`` for a pre-voice v1 vault, and
    ``NoVaultError`` when there is nothing enrolled yet. No reject path returns a
    name or any other plaintext.
    """
    vault_path = path if path is not None else default_vault_path()
    if not vault_path.is_file():
        raise NoVaultError("No vault yet — enroll first")

    secret_text = passphrase or ""
    if not secret_text:
        raise AuthError("Wrong passphrase")

    raw = vault_path.read_bytes()
    if len(raw) < _HEADER_LEN + secret.SecretBox.NONCE_SIZE:
        raise AuthError("Wrong passphrase")
    if raw[:4] != MAGIC:
        raise AuthError("Wrong passphrase")

    version = raw[4]
    if version == LEGACY_FORMAT_VERSION:
        raise LegacyVaultError(
            "This vault predates voice — re-enroll to add the voice lock"
        )
    if version != FORMAT_VERSION:
        raise VaultError(f"Unsupported vault version: {version}")

    opslimit, memlimit = struct.unpack_from("<QQ", raw, 5)
    salt = raw[21 : 21 + _SALT_BYTES]
    outer_ciphertext = raw[_HEADER_LEN:]

    outer_key = _derive_key(secret_text, salt, opslimit, memlimit)
    try:
        outer_plaintext = secret.SecretBox(outer_key).decrypt(outer_ciphertext)
    except CryptoError as exc:
        raise AuthError("Wrong passphrase") from exc

    helper_data, middle_ciphertext = _parse_outer(outer_plaintext)

    # Only now is the voice consulted — the passphrase has already been proven.
    try:
        middle_secret = middlelock.reconcile(helper_data, voiceprint)
        middle_key = middlelock.derive_key(
            middle_secret, base64.b64decode(helper_data["salt"])
        )
        profile = secret.SecretBox(middle_key).decrypt(middle_ciphertext)
    except (middlelock.MiddleLockError, CryptoError) as exc:
        raise VoiceAuthError("Voice didn't match") from exc

    return _parse_profile(profile)


def _parse_outer(outer_plaintext: bytes) -> tuple[dict, bytes]:
    try:
        payload = json.loads(outer_plaintext.decode("utf-8"))
        helper_data = payload["helper_data"]
        middle_ciphertext = base64.b64decode(payload["middle_ciphertext"])
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise VaultError("Vault payload is corrupt") from exc
    if not isinstance(helper_data, dict):
        raise VaultError("Vault payload is corrupt")
    return helper_data, middle_ciphertext


def _parse_profile(profile: bytes) -> str:
    try:
        payload = json.loads(profile.decode("utf-8"))
        display = payload["name"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise VaultError("Vault payload is corrupt") from exc
    if not isinstance(display, str) or not display:
        raise VaultError("Vault payload is corrupt")
    return display


def _dumps(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _derive_key(
    passphrase: str,
    salt: bytes,
    opslimit: int,
    memlimit: int,
) -> bytes:
    return pwhash.argon2id.kdf(
        secret.SecretBox.KEY_SIZE,
        passphrase.encode("utf-8"),
        salt,
        opslimit=opslimit,
        memlimit=memlimit,
    )
