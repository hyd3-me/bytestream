from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

SALT = b"bytestream_salt_v1"
KEY_LENGTH = 32


def derive_master_key(signature_bytes: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=SALT,
        info=b"master_key",
    )
    return hkdf.derive(signature_bytes)
