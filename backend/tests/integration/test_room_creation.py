import pytest
from pathlib import Path
from urllib.parse import urlparse
from pgsql_test import get_connections
from app.core.config import get_settings
from app.room import crud

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
    user_a = "0xaaa"
    user_b = "0xbbb"
    sorted_users = sorted([user_a, user_b])
    room_id = f"dm:{sorted_users[0]}:{sorted_users[1]}"

    crud.create_room(db, room_id, user_a, user_b)

    room = crud.get_room(db, room_id)
    assert room is not None
    assert room["user1"] == user_a
    assert room["user2"] == user_b
