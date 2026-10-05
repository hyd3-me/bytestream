"""Key exchange protocol: request, response, and processing."""

# path: client/keystore/exchange.py

# --- Imports ---

import base64

import client.crypto as crypto
from client.keystore import package_ops
from client.keystore import packages as keystore_packages

# --- Public API ---


def build_package_id_pair(pid_1: str, pid_2: str) -> str:
    return ":".join(sorted([pid_1, pid_2]))


def ensure_peer_key_package(own_address: str, peer_address: str) -> dict | None:
    package = keystore_packages.get_peer_key_package(peer_address)
    if package:
        return {"action": "use_cached", "package": package}
    return None


def build_key_exchange_request(own_address: str, peer_address: str) -> dict:
    request_id = crypto.build_message_id(
        crypto.generate_timestamp(), crypto.generate_nonce()
    )
    own_package = keystore_packages.get_current_key_package(own_address)
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
    if not package_ops.verify_key_package(sender_package):
        return {}
    if sender_package["eth_address"] != message.get("sender_address"):
        return {}

    keystore_packages.store_key_package(sender_package)
    own_package = keystore_packages.get_current_key_package(own_address)

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
    if not package_ops.verify_key_package(package):
        return None
    if package["eth_address"] != response.get("sender_address"):
        return None

    keystore_packages.store_key_package(package)
    return package
