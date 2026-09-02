from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

import app.crypto_constants as constants


def derive_master_key(signature_bytes: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=constants.KEY_LENGTH,
        salt=constants.MASTER_KEY_SALT,
        info=constants.MASTER_KEY_INFO,
    )
    return hkdf.derive(signature_bytes)
