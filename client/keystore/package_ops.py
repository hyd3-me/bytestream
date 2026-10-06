"""Package operations: build, sign, verify public key packages."""

# path: client/keystore/package_ops.py

# --- Imports ---

import base64
import json

from eth_account.messages import encode_defunct

import app.auth.security as auth_security

import client.crypto as crypto


# --- Public API ---

def build_key_package(
    eth_address: str,
    x25519_public_key,
    ed25519_public_key,
) -> dict:
    master_key_id = crypto.compute_master_key_id(
        x25519_public_key, ed25519_public_key
    )
    return {
        "eth_address": eth_address,
        "x25519_public_key": base64.b64encode(
            x25519_public_key.public_bytes_raw()
        ).decode("ascii"),
        "ed25519_public_key": base64.b64encode(
            ed25519_public_key.public_bytes_raw()
        ).decode("ascii"),
        "master_key_id": base64.b64encode(master_key_id).decode("ascii"),
    }


def sign_key_package(eth_account, base_package: dict) -> dict:
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    message = encode_defunct(text=canonical)
    signature = eth_account.sign_message(message).signature
    return {
        **base_package,
        "eth_signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_key_package(package: dict) -> bool:
    base_package = {
        "eth_address": package["eth_address"],
        "x25519_public_key": package["x25519_public_key"],
        "ed25519_public_key": package["ed25519_public_key"],
        "master_key_id": package["master_key_id"],
    }
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    signature_bytes = base64.b64decode(package["eth_signature"])
    return auth_security.verify_signature(
        package["eth_address"],
        canonical,
        signature_bytes.hex(),
    )
