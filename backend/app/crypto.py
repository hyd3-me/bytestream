from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature
import hashlib
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
    if not message_id:
        raise ValueError("message_id must not be empty")
    if not content:
        raise ValueError("content must not be empty")
    if not isinstance(message_id, bytes):
        raise TypeError("message_id must be bytes")
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    return hashlib.sha256(message_id + content).digest()


def build_sign_payload(
    sender_address: str,
    room_id: str,
    message_id: bytes,
    content_hash: bytes,
) -> bytes:
    return b"".join(
        [
            sender_address.encode(),
            room_id.encode(),
            message_id,
            content_hash,
        ]
    )


def sign_payload(private_key, payload: bytes) -> bytes:
    return private_key.sign(payload)


def verify_payload(public_key, payload: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, payload)
        return True
    except InvalidSignature:
        return False
