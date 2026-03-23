from typing import Optional
from . import utils


async def create_room(conn, room_id: str, user1: str, user2: str) -> None:
    await conn.execute(
        "INSERT INTO rooms (id, user1, user2) VALUES ($1, $2, $3)",
        room_id,
        user1,
        user2,
    )


async def get_room(conn, room_id: str) -> Optional[dict]:
    return await conn.fetchrow("SELECT * FROM rooms WHERE id = $1", room_id)


def room_exists(db, user1: str, user2: str) -> bool:
    room_id = utils.get_dm_room_id(user1, user2)
    return get_room(db, room_id) is not None


async def truncate_rooms(conn):
    """Delete all rows from the rooms table."""
    await conn.execute("TRUNCATE TABLE rooms;")
