from typing import Optional

def create_room(db, room_id: str, user1: str, user2: str) -> None:
    db.execute(
        "INSERT INTO rooms (id, user1, user2) VALUES (%s, %s, %s)",
        (room_id, user1, user2)
    )

def get_room(db, room_id: str) -> Optional[dict]:
    return db.one_or_none("SELECT * FROM rooms WHERE id = %s", (room_id,))

def room_exists(db, user1: str, user2: str) -> bool:
    # Временно без utils
    sorted_users = sorted([user1, user2])
    room_id = f"dm:{sorted_users[0]}:{sorted_users[1]}"
    return get_room(db, room_id) is not None
