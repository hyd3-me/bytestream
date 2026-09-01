# Bytestream Protocol Specification v1 (Draft)

## 1. Overview

Bytestream is a privacy-focused messenger where the server acts as a
mailman, routing encrypted messages without storing message history.
All cryptographic operations are performed client-side; the server never
sees private keys.

This specification defines the key derivation, message format, signing,
and encryption used in the system. It is a living document and may be
updated as the protocol evolves.

## 2. Identity and Master Key

- The user signs a fixed message with their Ethereum wallet.
- The resulting 65-byte signature is used as input to HKDF (SHA-256)
  to derive a 32-byte master key.
- The master key never leaves the device and is not stored on the server.

## 3. Device Keys

From the master key, two key pairs are derived using HKDF:

- X25519 key pair for ECDH and encryption.
- Ed25519 key pair for message signing.

The public keys are registered on the server and associated with the
user's Ethereum address via a `key_id`.

## 4. Key Registration and key_id

Each user can register one or more device key profiles. A profile
contains:

- `signing_public_key` (Ed25519)
- `encryption_public_key` (X25519)

The `key_id` has the format:
<ethereum_address>:<unique_id>

For example: `0xabc123...:key_1`.

The server stores public keys and resolves `key_id` to the corresponding
public keys. It never stores private keys.

## 5. Message Format

A message sent by a client via the `send_message` Socket.IO event has the
following top-level fields:

```json
{
  "room_id": "dm:0xaaa:0xbbb",
  "type": "text",
  "content": "Hello!",
  "message_id": "<base64 20 bytes>",
  "content_hash": "<base64 32 bytes>",
  "signature": "<base64 64 bytes>",
  "sender_address": "0xaaa",
  "key_id": "0xaaa:key_1",
  "is_encrypted": false
}
Fields:

    room_id (string, required): identifier of the room.

    type (string, required): type of content. Allowed values: text,
    file, webrtc_offer, webrtc_answer, webrtc_ice.

    content (string, required): if is_encrypted is false, this is the
    plaintext (UTF-8 string). If true, this is base64 of the ciphertext.

    message_id (string, required): base64 of 20 bytes composed as
    timestamp_bytes(8) || nonce_bytes(12).

    content_hash (string, required): base64 of SHA-256(message_id + content).

    signature (string, required): base64 of Ed25519 signature over the
    signing payload (see below).

    sender_address (string, required): Ethereum address of the sender.

    key_id (string, required): identifier of the sender's registered key
    profile.

    is_encrypted (boolean, required): whether the content is encrypted.

6. Signing Payload

The signing payload is a binary concatenation of the following fields in
order:

    sender_address (UTF-8 bytes)

    room_id (UTF-8 bytes)

    message_id (20 bytes)

    timestamp (8 bytes, big-endian; extracted from the first 8 bytes of
    message_id)

    content_hash (32 bytes)

This binds the message to the sender, room, and exact content, preventing
replay or re-routing to another conversation.
7. Encryption

Messages may be encrypted using X25519 ECDH and AES-256-GCM.

    The sender and recipient compute a shared secret using their X25519
    private key and the peer's public key.

    The shared secret is passed through HKDF to derive an AES-256-GCM key.

    The nonce for AES-GCM is the last 12 bytes of message_id.

    The plaintext is encrypted and the ciphertext is base64-encoded in the
    content field with is_encrypted set to true.

8. Message Flow

    Sender builds the message, computes content_hash, creates message_id,
    signs the payload, and optionally encrypts the content.

    Sender emits send_message over Socket.IO with the message object.

    Server verifies that sender_address matches the authenticated session,
    checks that the sender is a participant of room_id, and that the
    message structure is valid.

    Server routes the message to all connected participants of the room by
    emitting new_message with the same message object plus a
    server_timestamp field.

    Recipients verify the signature using the sender's public key (obtained
    via key_id), optionally decrypt the content, and validate
    content_hash.

9. Security Considerations

    Replay protection: each message_id must be unique; clients should
    maintain a cache of seen message IDs to discard duplicates.

    Content privacy: content hash is salted with message_id.

    Non-repudiation: signature covers the original content (via hash), not
    just ciphertext.

    Forward secrecy: not provided in this version (static ECDH keys). Future
    versions may use ephemeral keys.

    Server trust: server only stores public keys and routes encrypted blobs;
    it cannot read or forge messages.
