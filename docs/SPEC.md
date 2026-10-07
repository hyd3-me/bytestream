# Bytestream Protocol Specification v1 (Draft)

## 1. Overview

Bytestream is a privacy-focused messenger where the server acts as a
mailman: it routes encrypted messages without storing message history.
All cryptographic operations are performed client-side; the server never
sees private keys.

This specification defines key derivation, storage layers, account
protection, key exchange, and message format. It is a living document
and evolves with the protocol.

## 2. Identity and Master Key

- The user signs a fixed message with their Ethereum wallet.
- The 65-byte signature is used as input to HKDF (SHA-256) to derive a
  32-byte master key.
- The master key never leaves the device and is not sent to the server.

The fixed message is defined in `client/crypto_constants.py`
(`FIXED_MESSAGE`).

## 3. Device Keys

From the master key, two key pairs are derived using HKDF:

- X25519 key pair for ECDH and encryption.
- Ed25519 key pair for message signing.

Each pair is derived with a distinct salt and info string.

## 4. Master Key ID

The identifier of a key pair set is content-addressed:

    master_key_id = SHA-256(x25519_public_raw || ed25519_public_raw)

Properties:

- Deterministic: the same keys always produce the same ID.
- Public: derived from public keys only.
- Replaces the earlier `package_id` concept: one key pair set has one ID.

## 5. Key Package

A key package contains public keys and is signed by the owner's Ethereum
wallet. It has the following fields:

- `eth_address` (string): Ethereum address of the key owner.
- `x25519_public_key` (string): base64-encoded X25519 public key.
- `ed25519_public_key` (string): base64-encoded Ed25519 public key.
- `master_key_id` (string): base64-encoded master key ID.
- `eth_signature` (string): base64-encoded Ethereum signature over the
  canonical JSON serialization of the other fields.

The canonical serialization is JSON with sorted keys and no extra
whitespace.

## 6. Client Storage Layers

Client state is divided by scope. This mirrors the browser equivalents
in parentheses.

### 6.1 Browser-wide (browser/, IndexedDB)

Shared across tabs on the same device.

- `device_key`: random 32-byte key, created once per device.
- `account_protection[eth_address]`: device_key or pin record.
- `attempts[eth_address]`: failed PIN attempts, lockout timestamp.
- `master_keys_for_recovery[master_key_id]`: encrypted master key,
  retrievable after a tab is closed.
- `packages[eth_address][master_key_id]`: public key packages (own and peers).
- `latest_peer_ids[eth_address]`: pointer to the most recent peer package.
- `secrets[master_key_id_pair]`: derived shared secrets and AES keys.

### 6.2 Tab-scoped (tab/, sessionStorage)

Per-tab, survives page reload, dies with the tab.

- `tab_secret`: random 32-byte key for per-tab encryption.
- `master_keys_for_tab[master_key_id]`: encrypted master key, used for
  reload recovery.
- `active_address`: address of the currently active account in this tab.
- `current_master_key_ids[eth_address]`: pointer to the current own key.

### 6.3 In-memory (memory/, JS memory)

Lives only while the tab is open and not reloaded.

- `sessions[eth_address][master_key_id]`: derived private and public
  X25519 and Ed25519 keys.

## 7. Account Protection

Each address has a protection type:

- `none`: no keys stored on this device for the address.
- `device_key`: keys encrypted with the browser-wide device_key.
  This is the default. No user prompt required.
- `pin`: keys encrypted with a key derived from a user PIN.

### 7.1 PIN

- `salt`: 16 random bytes.
- `hash`: PBKDF2-HMAC-SHA256(pin, salt, iterations=600000, dklen=32).
- Lockout: after MAX_ATTEMPTS (3) failed attempts, lock for
  LOCKOUT_SECONDS (900). Counter resets on lock.
- `pin_key`: same PBKDF2 derivation, used to encrypt/decrypt master key.

## 8. Account Lifecycle

### 8.1 First setup (setup_new_account)

1. Sign fixed message, derive master key.
2. Derive X25519 and Ed25519 key pairs.
3. Build and sign key package; extract master_key_id.
4. Get or create device_key, generate tab_secret.
5. Encrypt master key with device_key and with tab_secret.
6. Persist (in order): package, current pointer, protection type,
   recovery blob, tab secret, tab blob.
7. Unlock session and set active_address.

### 8.2 Unlock existing account (unlock_account)

- Reads protection type.
- For device_key: derive recovery key from device_key.
- For pin: verify PIN, then derive pin_key. Return pin_required,
  wrong_pin, or locked on failure.
- Decrypt master key, unlock session, set active_address.

### 8.3 Tab reload (restore_tab_session)

- Requires active_address and tab_secret.
- Decrypts master key from master_keys_for_tab and unlocks session.
- No PIN prompt, no wallet prompt.

## 9. Key Exchange

Two clients exchange key packages to derive a shared secret.

### 9.1 Request

    {
      "type": "key_exchange_request",
      "request_id": "<base64 20 bytes>",
      "sender_address": "0xA",
      "requested_master_key_id": "current",
      "sender_package": { }
    }

The requested_master_key_id is "current" by default, or a specific
master_key_id when responding to a message with a known sender ID.

### 9.2 Response

    {
      "type": "key_exchange_response",
      "request_id": "<same as request>",
      "sender_address": "0xB",
      "package": { }
    }

On receipt, the package is verified against its Ethereum signature and
stored.

### 9.3 Shared Secret

    shared_secret = X25519(own_private, peer_public)
    aes_key       = HKDF-SHA256(shared_secret, salt=AES_SALT, info=AES_INFO)

Stored under a canonical pair:

    master_key_id_pair = ":".join(sorted([own_mkid, peer_mkid]))

## 10. Message Format

    {
      "room_id": "dm:0xA:0xB",
      "type": "text",
      "content": "<plaintext or base64 ciphertext>",
      "message_id": "<base64 20 bytes>",
      "content_hash": "<base64 32 bytes>",
      "signature": "<base64 64 bytes>",
      "sender_address": "0xA",
      "sender_master_key_id": "<base64>",
      "master_key_id_pair": "own_mkid:peer_mkid",
      "is_encrypted": true
    }

Fields:

- `room_id`: room identifier.
- `type`: content type (text, file, webrtc_offer, webrtc_answer, webrtc_ice).
- `content`: plaintext (UTF-8) if not encrypted, base64 ciphertext if
  encrypted.
- `message_id`: base64 of timestamp_ms(8) || nonce(12).
- `content_hash`: base64 of SHA-256(message_id || content).
- `signature`: base64 Ed25519 signature over the signing payload.
- `sender_address`: Ethereum address of the sender.
- `sender_master_key_id`: identifier of the key used to sign.
- `master_key_id_pair`: canonical pair, used to locate the shared secret.
- `is_encrypted`: boolean.

## 11. Signing Payload

Binary concatenation, in order:

1. sender_address (UTF-8)
2. room_id (UTF-8)
3. message_id (20 bytes)

This binds the message to the sender and room.

## 12. Encryption

- AES-256-GCM with a per-message nonce equal to the last 12 bytes of
  message_id.
- AES key from the shared secret derived in section 9.3.
- The recipient finds the shared secret by master_key_id_pair. If the
  secret is missing, the recipient requests the peer's package for the
  given sender_master_key_id and recomputes the secret.

## 13. Message Flow

1. Sender builds the message, signs it, optionally encrypts the content.
2. Sender emits send_message over Socket.IO.
3. Server validates sender_address against the authenticated session and
   membership in room_id.
4. Server routes new_message to all participants of the room.
5. Recipients verify the signature, locate or derive the shared secret,
   decrypt, and validate content_hash.

## 14. Authentication (Planned)

Instead of JWT, the client authenticates over the WebSocket connection:

1. Client connects to the server.
2. Server sends an auth_challenge with a random nonce.
3. Client signs the nonce with its Ed25519 private key and replies with
   address, master_key_id, and signature, plus its signed key package.
4. Server verifies the Ethereum signature of the package and the Ed25519
   signature of the challenge. On success, the connection is associated
   with the address.

## 15. Security Considerations

- Replay protection: unique message_id per message; clients may cache
  seen IDs.
- Content privacy: content_hash is salted with message_id.
- Non-repudiation: signature covers the sender, room, and content hash.
- At-rest protection: private keys never stored in plaintext. device_key
  in the browser is a non-extractable CryptoKey.
- Forward secrecy: not provided (static ECDH keys). Planned for a
  future version.
- Server trust: server routes blobs and does not read or forge messages.
