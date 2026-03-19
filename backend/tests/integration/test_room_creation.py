import pytest
from urllib.parse import urlparse
from pgsql_test import get_connections
from app.core.config import get_settings

settings = get_settings()


@pytest.fixture
def db():
    dsn = settings.test_database_url
    parsed = urlparse(dsn)
    pg_config = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
    }

    conn = get_connections(pg_config)
    db_client = conn.db

    db_client.execute(
        """
        CREATE TABLE rooms (
            id TEXT PRIMARY KEY,
            user1 TEXT NOT NULL,
            user2 TEXT NOT NULL
        )
    """
    )

    db_client.before_each()
    yield db_client
    db_client.after_each()

    conn.teardown()


def test_create_dm_room(db):
    room_id = "dm:0xaaa:0xbbb"
    user_a = "0xaaa"
    user_b = "0xbbb"

    db.execute(
        "INSERT INTO rooms (id, user1, user2) VALUES (%s, %s, %s)",
        (room_id, user_a, user_b),
    )

    result = db.one("SELECT * FROM rooms WHERE id = %s", (room_id,))
    assert result is not None
    assert result["user1"] == user_a
    assert result["user2"] == user_b
