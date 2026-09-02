from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import time
import secrets
import struct

import app.crypto_constants as constants


def derive_master_key(signature_bytes: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=constants.KEY_LENGTH,
        salt=constants.MASTER_KEY_SALT,
        info=constants.MASTER_KEY_INFO,
    )
    return hkdf.derive(signature_bytes)


def derive_x25519_keypair(master_key: bytes):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=constants.KEY_LENGTH,
        salt=constants.X25519_SALT,
        info=constants.X25519_INFO,
    )
    private_bytes = hkdf.derive(master_key)
    private_key = x25519.X25519PrivateKey.from_private_bytes(private_bytes)
    public_key = private_key.public_key()
    return private_key, public_key


def derive_ed25519_keypair(master_key: bytes):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=constants.KEY_LENGTH,
        salt=constants.ED25519_SALT,
        info=constants.ED25519_INFO,
    )
    private_bytes = hkdf.derive(master_key)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    public_key = private_key.public_key()
    return private_key, public_key


def compute_shared_secret(private_key, peer_public_key) -> bytes:
    return private_key.exchange(peer_public_key)


def encrypt_message(key: bytes, plaintext: bytes, nonce: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce, plaintext, None)


def decrypt_message(key: bytes, ciphertext: bytes, nonce: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def generate_timestamp() -> int:
    return time.time_ns() // 1_000_000


def generate_nonce() -> bytes:
    return secrets.token_bytes(12)


def build_message_id(timestamp: int, nonce: bytes) -> bytes:
    return struct.pack(">Q", timestamp) + nonce


def compute_content_hash(message_id: bytes, content: bytes) -> bytes:
    pass
