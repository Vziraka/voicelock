"""Passphrase outer lock and on-disk Vault (F2)."""

from __future__ import annotations

import json
import struct
from pathlib import Path

from nacl import pwhash, secret, utils
from nacl.exceptions import CryptoError

MAGIC = b"VLCK"
FORMAT_VERSION = 1
_SALT_BYTES = pwhash.argon2id.SALTBYTES
_OPS = pwhash.argon2id.OPSLIMIT_MODERATE
_MEM = pwhash.argon2id.MEMLIMIT_MODERATE
# magic(4) + version(1) + opslimit(8) + memlimit(8) + salt
_HEADER_LEN = 4 + 1 + 8 + 8 + _SALT_BYTES


class VaultError(Exception):
    """Base error for Vault / outer-lock failures."""


class ValidationError(VaultError):
    """Enroll refused — empty or missing name/passphrase."""


class AuthError(VaultError):
    """Wrong passphrase — REJECT; no plaintext returned."""


class NoVaultError(VaultError):
    """No Vault file at the path — Booth copy: enroll first."""


def default_vault_path() -> Path:
    return Path.home() / ".voicelock" / "vault.vl"


def enroll(name: str, passphrase: str, path: Path | None = None) -> None:
    """Seal a profile Vault with the passphrase (outer lock)."""
    display = (name or "").strip()
    secret_text = passphrase or ""
    if not display or not secret_text:
        raise ValidationError("Name and passphrase are required")

    vault_path = path if path is not None else default_vault_path()
    salt = utils.random(_SALT_BYTES)
    key = _derive_key(secret_text, salt, _OPS, _MEM)
    plaintext = json.dumps(
        {"name": display, "schema_version": 1},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    ciphertext = secret.SecretBox(key).encrypt(plaintext)

    header = (
        MAGIC
        + bytes([FORMAT_VERSION])
        + struct.pack("<QQ", _OPS, _MEM)
        + salt
    )
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_path.write_bytes(header + ciphertext)


def unlock(passphrase: str, path: Path | None = None) -> str:
    """Open the outer lock; return the enrolled display name."""
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
    if version != FORMAT_VERSION:
        raise VaultError(f"Unsupported vault version: {version}")

    opslimit, memlimit = struct.unpack_from("<QQ", raw, 5)
    salt = raw[21 : 21 + _SALT_BYTES]
    ciphertext = raw[_HEADER_LEN:]

    key = _derive_key(secret_text, salt, opslimit, memlimit)
    try:
        plaintext = secret.SecretBox(key).decrypt(ciphertext)
    except CryptoError as exc:
        raise AuthError("Wrong passphrase") from exc

    try:
        payload = json.loads(plaintext.decode("utf-8"))
        display = payload["name"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise VaultError("Vault payload is corrupt") from exc
    if not isinstance(display, str) or not display:
        raise VaultError("Vault payload is corrupt")
    return display


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
