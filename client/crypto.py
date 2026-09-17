from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature
import hashlib
import time
import secrets
import struct
import base64
import json

import client.crypto_constants as constants
import app.auth.security as auth_security
from eth_account.messages import encode_defunct

_packages = {}
_current_package_ids = {}


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


def derive_aes_key(shared_secret: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=constants.KEY_LENGTH,
        salt=constants.AES_SALT,
        info=constants.AES_INFO,
    )
    return hkdf.derive(shared_secret)


def build_key_package(
    eth_address: str,
    x25519_public_key,
    ed25519_public_key,
    package_id_bytes: bytes,
) -> dict:
    return {
        "eth_address": eth_address,
        "x25519_public_key": base64.b64encode(
            x25519_public_key.public_bytes_raw()
        ).decode("ascii"),
        "ed25519_public_key": base64.b64encode(
            ed25519_public_key.public_bytes_raw()
        ).decode("ascii"),
        "package_id": base64.b64encode(package_id_bytes).decode("ascii"),
    }


def sign_key_package(eth_account, base_package: dict) -> dict:
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    message = encode_defunct(text=canonical)
    signature = eth_account.sign_message(message).signature
    package = {
        **base_package,
        "eth_signature": base64.b64encode(signature).decode("ascii"),
    }
    return package


def verify_key_package(package: dict) -> bool:
    base_package = {
        "eth_address": package["eth_address"],
        "x25519_public_key": package["x25519_public_key"],
        "ed25519_public_key": package["ed25519_public_key"],
        "package_id": package["package_id"],
    }
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    signature_bytes = base64.b64decode(package["eth_signature"])
    return auth_security.verify_signature(
        package["eth_address"],
        canonical,
        signature_bytes.hex(),
    )


def request_key_package(
    sender_address: str, requested_package_id: str = "current"
) -> dict:
    request_id = build_message_id(generate_timestamp(), generate_nonce())

    return {
        "type": "key_package_request",
        "request_id": base64.b64encode(request_id).decode("ascii"),
        "sender_address": sender_address,
        "requested_package_id": requested_package_id,
    }


def key_package_response(request: dict, eth_address: str) -> dict:
    if request.get("type") != "key_package_request":
        return {}
    if not request.get("request_id"):
        return {}

    requested_id = request.get("requested_package_id", "current")
    package = get_key_package(eth_address, requested_id)
    if package is None:
        return {}

    content_bytes = json.dumps(package, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )

    return {
        "type": "key_package",
        "request_id": request["request_id"],
        "sender_address": package["eth_address"],
        "content": base64.b64encode(content_bytes).decode("ascii"),
    }


def store_key_package(package: dict) -> None:
    eth_address = package["eth_address"]
    package_id = package["package_id"]
    if eth_address not in _packages:
        _packages[eth_address] = {}
    _packages[eth_address][package_id] = package


def set_current_key_package(eth_address: str, package_id: str) -> None:
    _current_package_ids[eth_address] = package_id


def get_current_key_package(eth_address: str) -> dict:
    package_id = _current_package_ids.get(eth_address)
    if package_id is None:
        raise ValueError("No current key package")
    package = _packages.get(eth_address, {}).get(package_id)
    if package is None:
        raise ValueError("Current package not found")
    return package


def get_key_package_by_id(eth_address: str, package_id: str):
    return _packages.get(eth_address, {}).get(package_id)


def get_key_package(eth_address: str, package_id: str = "current"):
    if package_id == "current":
        try:
            return get_current_key_package(eth_address)
        except ValueError:
            return None
    return get_key_package_by_id(eth_address, package_id)


def clear_key_package(eth_address: str) -> None:
    _packages.pop(eth_address, None)
    _current_package_ids.pop(eth_address, None)


def process_key_package_response(response: dict) -> dict:
    if response.get("type") != "key_package":
        return {}
    if not response.get("content"):
        return {}

    content_bytes = base64.b64decode(response["content"])
    package = json.loads(content_bytes.decode("utf-8"))

    if not verify_key_package(package):
        return {}

    return package


def load_x25519_public_key(public_key_b64: str):
    raw = base64.b64decode(public_key_b64)
    return x25519.X25519PublicKey.from_public_bytes(raw)


def build_package_id_pair(pid_1: str, pid_2: str) -> str:
    return ":".join(sorted([pid_1, pid_2]))


def get_peer_key_package(peer_address: str) -> dict | None:
    packages = _packages.get(peer_address)
    if not packages:
        return None
    latest_id = max(
        packages.keys(),
        key=lambda pid: base64.b64decode(pid)[:8],
    )
    return packages[latest_id]


def ensure_peer_key_package(own_address: str, peer_address: str) -> dict:
    package = get_peer_key_package(peer_address)
    if package:
        return {"action": "use_cached", "package": package}
    return None


def build_key_exchange_request(own_address: str, peer_address: str) -> dict:
    request_id = build_message_id(generate_timestamp(), generate_nonce())
    own_package = get_current_key_package(own_address)
    return {
        "type": "key_exchange_request",
        "request_id": base64.b64encode(request_id).decode("ascii"),
        "sender_address": own_address,
        "requested_package_id": "current",
        "sender_package": own_package,
    }


def handle_key_exchange_request(message: dict, own_address: str) -> dict:
    if message.get("type") != "key_exchange_request":
        return {}
    sender_package = message.get("sender_package")
    if not sender_package:
        return {}
    if not verify_key_package(sender_package):
        return {}
    if sender_package["eth_address"] != message.get("sender_address"):
        return {}

    store_key_package(sender_package)
    own_package = get_current_key_package(own_address)

    return {
        "type": "key_exchange_response",
        "request_id": message["request_id"],
        "sender_address": own_address,
        "package": own_package,
    }


def handle_key_exchange_response(response: dict, own_address: str) -> dict | None:
    if response.get("type") != "key_exchange_response":
        return None
    package = response.get("package")
    if not package:
        return None
    if not verify_key_package(package):
        return None
    if package["eth_address"] != response.get("sender_address"):
        return None

    store_key_package(package)
    return package
