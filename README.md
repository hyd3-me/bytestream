# Bytestream

**Bytestream** is a private Web3 messenger based on the principle "server as postman, client as fortress". The server validates permissions and command structure but never stores message history. Clients are responsible for content validation and sanitization.

## Current Features

- Authentication via Ethereum wallet (address as primary ID)
  - Nonce generation (`GET /auth/nonce/{address}`)
  - Signature verification and JWT issuance (`POST /auth/verify`)
- Health check endpoint
- Redis integration for nonce storage (configurable TTL and key prefix)
- Comprehensive tests (unit + integration) following TDD
- Structured logging with environment-aware configuration (development console, production file with rotation)

## Technology Stack

- **Backend**: FastAPI (Python 3.12), python-socketio, Pydantic, PostgreSQL, Redis, Alembic
- **Frontend** (planned): React + TypeScript, Vite, Wagmi/Viem, Socket.IO-client, Zustand, IndexedDB
- **Authentication**: JWT based on signed nonce
- **Transport**: WebSocket (with JWT handshake), WebRTC for P2P content

## Getting Started

### Prerequisites

- Python 3.12+
- Redis server (local or remote)
- PostgreSQL (optional, for future features)

### Installation

1. Clone the repository:

```bash
   git clone https://github.com/hyd3-me/bytestream.git
```

2. Create and activate virtual environment:

```bash
python3.12 -m venv env
source env/bin/activate
cd bytestream/source
```

3. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Configure environment variables:

- Set REDIS_URL (e.g., redis://:password@localhost:6379/1)

- Generate a strong JWT_SECRET_KEY (e.g., openssl rand -hex 32)

- (Optional) Set TEST_ACCOUNT_PRIVATE_KEY for testing

5. Run the server:

```bash
uvicorn main:app --reload
```

### Testing

Run all tests:

```bash
pytest backend/tests/ -v
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `REDIS_KEY_PREFIX` | Prefix for Redis keys | `bytestream:` |
| `NONCE_TTL_SECONDS` | Nonce lifetime in seconds | `300` |
| `JWT_SECRET_KEY` | Secret for signing JWTs | **required** |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | JWT expiration time | `30` |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, etc.) | `INFO` |
| `LOG_FILE` | Path to log file (required in production) | `None` |
| `LOG_MAX_BYTES` | Max log file size before rotation | `2097152` (2 MB) |
| `LOG_BACKUP_COUNT` | Number of rotated logs to keep | `3` |
