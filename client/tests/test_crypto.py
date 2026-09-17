import pytest
import base64, json
from client import crypto, crypto_constants
from eth_account.messages import encode_defunct


def test_derive_master_key_exists():
    assert hasattr(crypto, "derive_master_key")
    assert callable(crypto.derive_master_key)


def test_derive_master_key_returns_32_bytes(test_account):
    message = encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account.sign_message(message).signature

    key = crypto.derive_master_key(signature)

    assert isinstance(key, bytes)
    assert len(key) == 32


def test_derive_master_key_deterministic(test_account):
    message = encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account.sign_message(message).signature

    key1 = crypto.derive_master_key(signature)
    key2 = crypto.derive_master_key(signature)

    assert key1 == key2


def test_derive_x25519_keypair_exists():
    assert hasattr(crypto, "derive_x25519_keypair")
    assert callable(crypto.derive_x25519_keypair)


def test_derive_x25519_keypair_deterministic():
    master_key = b"\x01" * 32

    priv1, pub1 = crypto.derive_x25519_keypair(master_key)
    priv2, pub2 = crypto.derive_x25519_keypair(master_key)

    assert priv1.private_bytes_raw() == priv2.private_bytes_raw()
    assert pub1.public_bytes_raw() == pub2.public_bytes_raw()


def test_derive_ed25519_keypair_exists():
    assert hasattr(crypto, "derive_ed25519_keypair")
    assert callable(crypto.derive_ed25519_keypair)


def test_derive_ed25519_keypair_deterministic():
    master_key = b"\x02" * 32

    priv1, pub1 = crypto.derive_ed25519_keypair(master_key)
    priv2, pub2 = crypto.derive_ed25519_keypair(master_key)

    assert priv1.private_bytes_raw() == priv2.private_bytes_raw()
    assert pub1.public_bytes_raw() == pub2.public_bytes_raw()


def test_compute_shared_secret_exists():
    assert hasattr(crypto, "compute_shared_secret")
    assert callable(crypto.compute_shared_secret)


def test_compute_shared_secret_symmetric(x25519_keypair_a, x25519_keypair_b):
    alice_priv, alice_pub = x25519_keypair_a
    bob_priv, bob_pub = x25519_keypair_b

    secret_alice = crypto.compute_shared_secret(alice_priv, bob_pub)
    secret_bob = crypto.compute_shared_secret(bob_priv, alice_pub)

    assert isinstance(secret_alice, bytes)
    assert len(secret_alice) == 32
    assert secret_alice == secret_bob


def test_encrypt_message_exists():
    assert hasattr(crypto, "encrypt_message")
    assert callable(crypto.encrypt_message)


def test_decrypt_message_exists():
    assert hasattr(crypto, "decrypt_message")
    assert callable(crypto.decrypt_message)


def test_encrypt_message_returns_ciphertext():
    key = b"\x11" * 32
    plaintext = b"Hello, Bob!"
    nonce = b"\x22" * 12

    ciphertext = crypto.encrypt_message(key, plaintext, nonce)

    assert isinstance(ciphertext, bytes)
    assert ciphertext != plaintext


def test_decrypt_message_returns_plaintext():
    key = b"\x11" * 32
    plaintext = b"Hello, Bob!"
    nonce = b"\x22" * 12

    ciphertext = crypto.encrypt_message(key, plaintext, nonce)
    decrypted = crypto.decrypt_message(key, ciphertext, nonce)

    assert decrypted == plaintext


def test_generate_timestamp_exists():
    assert hasattr(crypto, "generate_timestamp")
    assert callable(crypto.generate_timestamp)


def test_generate_timestamp_returns_positive_int():
    ts = crypto.generate_timestamp()

    assert isinstance(ts, int)
    assert ts > 0


def test_generate_nonce_exists():
    assert hasattr(crypto, "generate_nonce")
    assert callable(crypto.generate_nonce)


def test_generate_nonce_returns_12_bytes_unique():
    nonce1 = crypto.generate_nonce()
    nonce2 = crypto.generate_nonce()

    assert isinstance(nonce1, bytes)
    assert len(nonce1) == 12
    assert nonce1 != nonce2


def test_build_message_id_exists():
    assert hasattr(crypto, "build_message_id")
    assert callable(crypto.build_message_id)


def test_build_message_id_returns_20_bytes_with_timestamp_and_nonce():
    timestamp = 1000
    nonce = b"\x01" * 12

    message_id = crypto.build_message_id(timestamp, nonce)

    assert isinstance(message_id, bytes)
    assert len(message_id) == 20
    assert message_id[:8] == timestamp.to_bytes(8, "big")
    assert message_id[8:] == nonce


def test_compute_content_hash_exists():
    assert hasattr(crypto, "compute_content_hash")
    assert callable(crypto.compute_content_hash)


def test_compute_content_hash_deterministic():
    message_id = b"\x01" * 20
    content = b"Hello, Bob!"

    hash1 = crypto.compute_content_hash(message_id, content)
    hash2 = crypto.compute_content_hash(message_id, content)

    assert isinstance(hash1, bytes)
    assert len(hash1) == 32
    assert hash1 == hash2


def test_compute_content_hash_different_content_hashes():
    message_id = b"\x01" * 20
    content1 = b"Hello"
    content2 = b"Hell0"

    hash1 = crypto.compute_content_hash(message_id, content1)
    hash2 = crypto.compute_content_hash(message_id, content2)

    assert hash1 != hash2


def test_build_sign_payload_exists():
    assert hasattr(crypto, "build_sign_payload")
    assert callable(crypto.build_sign_payload)


def test_build_sign_payload_concatenates_fields_correctly():
    sender_address = "0xabc"
    room_id = "dm:0xaaa:0xbbb"
    message_id = b"\x01" * 20
    content_hash = b"\x02" * 32

    payload = crypto.build_sign_payload(
        sender_address, room_id, message_id, content_hash
    )

    assert (
        payload
        == sender_address.encode() + room_id.encode() + message_id + content_hash
    )


def test_sign_payload_exists():
    assert hasattr(crypto, "sign_payload")
    assert callable(crypto.sign_payload)


def test_sign_payload_returns_64_bytes_deterministic(ed25519_keypair):
    private_key, _ = ed25519_keypair
    payload = b"test payload"

    sig1 = crypto.sign_payload(private_key, payload)
    sig2 = crypto.sign_payload(private_key, payload)

    assert isinstance(sig1, bytes)
    assert len(sig1) == 64
    assert sig1 == sig2


def test_verify_payload_exists():
    assert hasattr(crypto, "verify_payload")
    assert callable(crypto.verify_payload)


def test_verify_payload_accepts_valid_signature(ed25519_keypair):
    private_key, public_key = ed25519_keypair
    payload = b"valid payload"
    signature = crypto.sign_payload(private_key, payload)

    assert crypto.verify_payload(public_key, payload, signature) is True


def test_verify_payload_rejects_invalid_signature(ed25519_keypair):
    _, public_key = ed25519_keypair
    payload = b"important payload"
    bad_signature = b"\x00" * 64

    assert crypto.verify_payload(public_key, payload, bad_signature) is False


def test_full_sign_verify_payload_cycle(ed25519_keypair):
    private_key, public_key = ed25519_keypair

    sender_address = "0xabc"
    room_id = "dm:0xaaa:0xbbb"
    timestamp = crypto.generate_timestamp()
    nonce = crypto.generate_nonce()
    message_id = crypto.build_message_id(timestamp, nonce)

    content = b"Hello, Bob!"
    content_hash = crypto.compute_content_hash(message_id, content)

    payload = crypto.build_sign_payload(
        sender_address, room_id, message_id, content_hash
    )
    signature = crypto.sign_payload(private_key, payload)

    assert crypto.verify_payload(public_key, payload, signature) is True


def test_derive_aes_key_exists():
    assert hasattr(crypto, "derive_aes_key")
    assert callable(crypto.derive_aes_key)


def test_derive_aes_key_returns_32_bytes_deterministic():
    shared_secret = b"\x09" * 32

    key1 = crypto.derive_aes_key(shared_secret)
    key2 = crypto.derive_aes_key(shared_secret)

    assert isinstance(key1, bytes)
    assert len(key1) == 32
    assert key1 == key2


def test_full_encryption_cycle_with_derived_key():
    master_key_a = b"\x0a" * 32
    master_key_b = b"\x0b" * 32

    alice_priv, alice_pub = crypto.derive_x25519_keypair(master_key_a)
    bob_priv, bob_pub = crypto.derive_x25519_keypair(master_key_b)

    shared_alice = crypto.compute_shared_secret(alice_priv, bob_pub)
    shared_bob = crypto.compute_shared_secret(bob_priv, alice_pub)

    aes_key = crypto.derive_aes_key(shared_alice)

    plaintext = b"Hello, Bob! This is encrypted."
    nonce = crypto.generate_nonce()
    ciphertext = crypto.encrypt_message(aes_key, plaintext, nonce)

    decrypted = crypto.decrypt_message(aes_key, ciphertext, nonce)

    assert decrypted == plaintext


def test_build_key_package_exists():
    assert hasattr(crypto, "build_key_package")
    assert callable(crypto.build_key_package)


def test_build_key_package_returns_base_package_without_signature(
    x25519_keypair, ed25519_keypair
):
    _, x_pub = x25519_keypair
    _, e_pub = ed25519_keypair
    address = "0xabc"

    package_id_bytes = crypto.build_message_id(
        crypto.generate_timestamp(), crypto.generate_nonce()
    )

    package = crypto.build_key_package(
        address,
        x_pub,
        e_pub,
        package_id_bytes,
    )

    assert set(package.keys()) == {
        "eth_address",
        "x25519_public_key",
        "ed25519_public_key",
        "package_id",
    }
    assert package["eth_address"] == address
    assert package["x25519_public_key"] == base64.b64encode(
        x_pub.public_bytes_raw()
    ).decode("ascii")
    assert package["ed25519_public_key"] == base64.b64encode(
        e_pub.public_bytes_raw()
    ).decode("ascii")
    assert package["package_id"] == base64.b64encode(package_id_bytes).decode("ascii")
    assert "eth_signature" not in package


def test_sign_key_package_exists():
    assert hasattr(crypto, "sign_key_package")
    assert callable(crypto.sign_key_package)


def test_sign_key_package_adds_eth_signature(
    test_account, x25519_keypair, ed25519_keypair
):
    _, x_pub = x25519_keypair
    _, e_pub = ed25519_keypair

    package_id_bytes = crypto.build_message_id(
        crypto.generate_timestamp(), crypto.generate_nonce()
    )
    base_package = crypto.build_key_package(
        test_account.address,
        x_pub,
        e_pub,
        package_id_bytes,
    )

    signed_package = crypto.sign_key_package(test_account, base_package)

    assert "eth_signature" in signed_package
    assert isinstance(signed_package["eth_signature"], str)
    assert signed_package["eth_signature"]
    assert signed_package["eth_address"] == base_package["eth_address"]
    assert signed_package["x25519_public_key"] == base_package["x25519_public_key"]
    assert signed_package["ed25519_public_key"] == base_package["ed25519_public_key"]
    assert signed_package["package_id"] == base_package["package_id"]


def test_verify_key_package_exists():
    assert hasattr(crypto, "verify_key_package")
    assert callable(crypto.verify_key_package)


def test_verify_key_package_accepts_valid_package(
    test_account, x25519_keypair, ed25519_keypair
):
    _, x_pub = x25519_keypair
    _, e_pub = ed25519_keypair

    package_id_bytes = crypto.build_message_id(
        crypto.generate_timestamp(), crypto.generate_nonce()
    )
    base_package = crypto.build_key_package(
        test_account.address,
        x_pub,
        e_pub,
        package_id_bytes,
    )

    signed_package = crypto.sign_key_package(test_account, base_package)

    assert crypto.verify_key_package(signed_package) is True


def test_verify_key_package_rejects_tampered_address(
    test_account, x25519_keypair, ed25519_keypair
):
    _, x_pub = x25519_keypair
    _, e_pub = ed25519_keypair

    package_id_bytes = crypto.build_message_id(
        crypto.generate_timestamp(), crypto.generate_nonce()
    )
    base_package = crypto.build_key_package(
        test_account.address,
        x_pub,
        e_pub,
        package_id_bytes,
    )
    signed_package = crypto.sign_key_package(test_account, base_package)

    tampered = dict(signed_package)
    tampered["eth_address"] = "0xdeadbeef"

    assert crypto.verify_key_package(tampered) is False


def test_request_key_package_exists():
    assert hasattr(crypto, "request_key_package")
    assert callable(crypto.request_key_package)


def test_key_package_response_exists():
    assert hasattr(crypto, "key_package_response")
    assert callable(crypto.key_package_response)


def test_store_key_package_exists():
    assert hasattr(crypto, "store_key_package")
    assert callable(crypto.store_key_package)


def test_get_current_key_package_exists():
    assert hasattr(crypto, "get_current_key_package")
    assert callable(crypto.get_current_key_package)


def test_clear_key_package_exists():
    assert hasattr(crypto, "clear_key_package")
    assert callable(crypto.clear_key_package)


def test_request_key_package_returns_expected_fields(test_account):
    sender_address = test_account.address

    request = crypto.request_key_package(sender_address)

    assert set(request.keys()) == {
        "type",
        "request_id",
        "sender_address",
        "requested_package_id",
    }
    assert request["type"] == "key_package_request"
    assert request["sender_address"] == sender_address
    assert request["request_id"]
    assert request["requested_package_id"] == "current"


def test_clear_key_package_removes_all(test_account, signed_package):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])

    crypto.clear_key_package(test_account.address)

    with pytest.raises(ValueError):
        crypto.get_current_key_package(test_account.address)
    assert (
        crypto.get_key_package_by_id(test_account.address, signed_package["package_id"])
        is None
    )


def test_store_key_package_stores_by_address_and_id(test_account, signed_package):
    crypto.store_key_package(signed_package)

    retrieved = crypto.get_key_package_by_id(
        test_account.address, signed_package["package_id"]
    )
    assert retrieved == signed_package


def test_store_key_package_does_not_set_current(test_account, signed_package):
    crypto.store_key_package(signed_package)

    with pytest.raises(ValueError):
        crypto.get_current_key_package(test_account.address)


def test_key_package_response_returns_current_package(test_account, signed_package):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])

    request = crypto.request_key_package(test_account.address)
    response = crypto.key_package_response(request, test_account.address)

    assert set(response.keys()) == {
        "type",
        "request_id",
        "sender_address",
        "content",
    }
    assert response["type"] == "key_package"
    assert response["request_id"] == request["request_id"]
    assert response["sender_address"] == test_account.address

    decoded = base64.b64decode(response["content"]).decode("utf-8")
    assert json.loads(decoded) == signed_package


def test_key_package_response_returns_empty_for_unknown_package_id(
    test_account, signed_package
):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])

    request = crypto.request_key_package(test_account.address)
    request["requested_package_id"] = "unknown"

    response = crypto.key_package_response(request, test_account.address)
    assert response == {}


def test_key_package_response_returns_by_requested_id(test_account, signed_package):
    crypto.store_key_package(signed_package)

    request = crypto.request_key_package(test_account.address)
    request["requested_package_id"] = signed_package["package_id"]

    response = crypto.key_package_response(request, test_account.address)

    decoded = base64.b64decode(response["content"]).decode("utf-8")
    assert json.loads(decoded) == signed_package


def test_process_key_package_response_exists():
    assert hasattr(crypto, "process_key_package_response")
    assert callable(crypto.process_key_package_response)


def test_process_key_package_response_returns_valid_package(
    test_account, signed_package
):
    content_bytes = json.dumps(
        signed_package, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    response = {
        "type": "key_package",
        "request_id": "test_request_id",
        "sender_address": signed_package["eth_address"],
        "content": base64.b64encode(content_bytes).decode("ascii"),
    }

    result = crypto.process_key_package_response(response)

    assert result == signed_package


def test_process_key_package_response_rejects_tampered_package(
    test_account, signed_package
):
    tampered = dict(signed_package)
    tampered["eth_address"] = "0xdeadbeef"

    content_bytes = json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    response = {
        "type": "key_package",
        "request_id": "test_request_id",
        "sender_address": tampered["eth_address"],
        "content": base64.b64encode(content_bytes).decode("ascii"),
    }

    result = crypto.process_key_package_response(response)

    assert result == {}


def test_load_x25519_public_key_exists():
    assert hasattr(crypto, "load_x25519_public_key")
    assert callable(crypto.load_x25519_public_key)


def test_load_x25519_public_key_roundtrip(x25519_keypair_a):
    _, x_pub = x25519_keypair_a
    encoded = base64.b64encode(x_pub.public_bytes_raw()).decode("ascii")

    loaded = crypto.load_x25519_public_key(encoded)

    assert loaded.public_bytes_raw() == x_pub.public_bytes_raw()


def test_full_key_exchange_cycle(
    test_account,
    test_account_b,
    x25519_keypair_a,
    x25519_keypair_b,
    signed_package,
    signed_package_b,
):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])
    crypto.store_key_package(signed_package_b)
    crypto.set_current_key_package(
        test_account_b.address, signed_package_b["package_id"]
    )

    request_from_a = crypto.request_key_package(test_account.address)
    response_from_b = crypto.key_package_response(
        request_from_a, test_account_b.address
    )
    package_from_b = crypto.process_key_package_response(response_from_b)

    request_from_b = crypto.request_key_package(test_account_b.address)
    response_from_a = crypto.key_package_response(request_from_b, test_account.address)
    package_from_a = crypto.process_key_package_response(response_from_a)

    assert package_from_b == signed_package_b
    assert package_from_a == signed_package

    x_priv_a, _ = x25519_keypair_a
    x_priv_b, _ = x25519_keypair_b

    b_x_pub = crypto.load_x25519_public_key(package_from_b["x25519_public_key"])
    a_x_pub = crypto.load_x25519_public_key(package_from_a["x25519_public_key"])

    secret_a = crypto.compute_shared_secret(x_priv_a, b_x_pub)
    secret_b = crypto.compute_shared_secret(x_priv_b, a_x_pub)

    assert secret_a == secret_b


def test_build_package_id_pair_exists():
    assert hasattr(crypto, "build_package_id_pair")
    assert callable(crypto.build_package_id_pair)


def test_build_package_id_pair_is_symmetric():
    pid_a = "AAAB"
    pid_b = "AAAC"

    pair_ab = crypto.build_package_id_pair(pid_a, pid_b)
    pair_ba = crypto.build_package_id_pair(pid_b, pid_a)

    assert pair_ab == pair_ba


def test_build_package_id_pair_returns_sorted_pair_with_colon():
    pid_a = "ZZZZ"
    pid_b = "AAAA"

    pair = crypto.build_package_id_pair(pid_a, pid_b)

    assert pair == "AAAA:ZZZZ"


def test_get_peer_key_package_exists():
    assert hasattr(crypto, "get_peer_key_package")
    assert callable(crypto.get_peer_key_package)


def test_get_peer_key_package_returns_latest(
    test_account, x25519_keypair_a, ed25519_keypair_a
):
    _, x_pub = x25519_keypair_a
    _, e_pub = ed25519_keypair_a

    old_pid = crypto.build_message_id(1000, b"\x01" * 12)
    old_base = crypto.build_key_package(test_account.address, x_pub, e_pub, old_pid)
    old_pkg = crypto.sign_key_package(test_account, old_base)

    new_pid = crypto.build_message_id(2000, b"\x02" * 12)
    new_base = crypto.build_key_package(test_account.address, x_pub, e_pub, new_pid)
    new_pkg = crypto.sign_key_package(test_account, new_base)

    crypto.store_key_package(old_pkg)
    crypto.store_key_package(new_pkg)

    result = crypto.get_peer_key_package(test_account.address)
    assert result == new_pkg


def test_get_peer_key_package_returns_none_when_empty(test_account):
    assert crypto.get_peer_key_package(test_account.address) is None


def test_ensure_peer_key_package_exists():
    assert hasattr(crypto, "ensure_peer_key_package")
    assert callable(crypto.ensure_peer_key_package)


def test_ensure_peer_key_package_returns_cached_package(
    test_account, test_account_b, signed_package_b
):
    crypto.store_key_package(signed_package_b)

    result = crypto.ensure_peer_key_package(
        test_account.address, test_account_b.address
    )

    assert result["action"] == "use_cached"
    assert result["package"] == signed_package_b


def test_build_key_exchange_request_exists():
    assert hasattr(crypto, "build_key_exchange_request")
    assert callable(crypto.build_key_exchange_request)


def test_build_key_exchange_request_returns_message_with_own_package(
    test_account, test_account_b, signed_package
):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])

    message = crypto.build_key_exchange_request(
        test_account.address, test_account_b.address
    )

    assert set(message.keys()) == {
        "type",
        "request_id",
        "sender_address",
        "requested_package_id",
        "sender_package",
    }
    assert message["type"] == "key_exchange_request"
    assert message["sender_address"] == test_account.address
    assert message["requested_package_id"] == "current"
    assert message["request_id"]
    assert message["sender_package"] == signed_package


def test_handle_key_exchange_request_exists():
    assert hasattr(crypto, "handle_key_exchange_request")
    assert callable(crypto.handle_key_exchange_request)


def test_handle_key_exchange_request_stores_sender_package_and_returns_response(
    test_account, test_account_b, signed_package, signed_package_b
):
    crypto.store_key_package(signed_package)
    crypto.set_current_key_package(test_account.address, signed_package["package_id"])

    message = {
        "type": "key_exchange_request",
        "request_id": "dGVzdF9yZXF1ZXN0X2lk",
        "sender_address": test_account_b.address,
        "requested_package_id": "current",
        "sender_package": signed_package_b,
    }

    response = crypto.handle_key_exchange_request(message, test_account.address)

    assert response["type"] == "key_exchange_response"
    assert response["request_id"] == message["request_id"]
    assert response["sender_address"] == test_account.address
    assert response["package"] == signed_package

    stored = crypto.get_key_package_by_id(
        test_account_b.address, signed_package_b["package_id"]
    )
    assert stored == signed_package_b


def test_handle_key_exchange_response_exists():
    assert hasattr(crypto, "handle_key_exchange_response")
    assert callable(crypto.handle_key_exchange_response)
