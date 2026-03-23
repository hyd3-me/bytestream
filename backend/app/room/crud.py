from typing import Optional
from . import utils


def create_room(db, room_id: str, user1: str, user2: str) -> None:
    db.execute(
        "INSERT INTO rooms (id, user1, user2) VALUES (%s, %s, %s)",
        (room_id, user1, user2),
    )


def get_room(db, room_id: str) -> Optional[dict]:
    result = db.one_or_none("SELECT * FROM rooms WHERE id = %s", (room_id,))
    return result


def room_exists(db, user1: str, user2: str) -> bool:
    room_id = utils.get_dm_room_id(user1, user2)
    return get_room(db, room_id) is not None
