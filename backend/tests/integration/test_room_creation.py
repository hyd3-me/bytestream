import pytest
from pathlib import Path
from urllib.parse import urlparse
from pgsql_test import get_connections
from app.core.config import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
def db_connection():
    dsn = settings.test_database_url
    parsed = urlparse(dsn)
    pg_config = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
    }
    conn = get_connections(pg_config)
    yield conn
    conn.teardown()


@pytest.fixture
def db(db_connection):
    schema_path = Path(__file__).parent.parent / "fixtures" / "schema.sql"
    with open(schema_path) as f:
        schema_sql = f.read()
    db_connection.db.execute(schema_sql)
    db_connection.db.before_each()
    yield db_connection.db
    db_connection.db.after_each()


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
